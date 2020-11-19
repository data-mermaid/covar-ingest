import argparse
import json
import requests
from datetime import datetime, timedelta
from os.path import basename, join, splitext
from osgeo import gdal, osr


# TODO: abstract out an IngestTask base class that all jobs can inherit from
class IngestNetCDFTask(object):
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    ROOT = "/usr/src/app"
    nc_pattern = "A{startyear}{startday}_{endyear}{endday}.L3m_8day_primprod.nc"
    # TODO: see about crosswalking with older NPP products
    #  (https://coastwatch.pfeg.noaa.gov/erddap/griddap/index.html?page=1&itemsPerPage=1000)
    inputs = {
        "npp": {
            "source": "https://coastwatch.pfeg.noaa.gov/erddap/files/erdMH1pp8day",
            "subdataset": "MHPProd",
            "crs": 4326,
            "composite": 7,  # days
        }
    }

    def __init__(self, *args, **kwargs):
        # TODO: timezone?
        _taskdate = datetime.now().date()
        try:
            _taskdate = datetime.strptime(
                kwargs.pop("taskdate", None), self.DATE_FORMAT
            ).date()
        except (TypeError, ValueError):
            pass
        self.taskdate = _taskdate

        startdate = self.taskdate - timedelta(days=self.inputs["npp"]["composite"])
        self.netcdf_filename = self.nc_pattern.format(
            startyear=startdate.timetuple().tm_year,
            startday=startdate.timetuple().tm_yday,
            endyear=self.taskdate.timetuple().tm_year,
            endday=self.taskdate.timetuple().tm_yday,
        )

    def get_stac_datetimes(self):
        end_datetime = self.taskdate
        end_datetime_str = end_datetime.strftime(self.DATETIME_FORMAT)
        start_datetime = end_datetime - timedelta(days=self.inputs["npp"]["composite"])
        start_datetime_str = start_datetime.strftime(self.DATETIME_FORMAT)

        return start_datetime_str, end_datetime_str

    def invoke(self):
        print(f"Beginning NPP ingest for {self.taskdate}")

        self.get_netcdf()
        cog = self.netcdf2cog()
        # TODO: incorporate near-shore correction: https://github.com/pmarchand1/msec/tree/master/npp
        self.stac(cog)
        # self.cleanup()  # TODO
        print("Done!")

    def get_netcdf(self):
        url = f"{self.inputs['npp']['source']}/{self.netcdf_filename}"
        local_nc = join(self.ROOT, "data", self.netcdf_filename)
        print(f"Downloading netcdf data from {url}")
        r = requests.get(url, allow_redirects=True)
        r.raise_for_status()
        open(local_nc, "wb").write(r.content)

    def netcdf2cog(self):
        local_nc = join(self.ROOT, "data", self.netcdf_filename)
        gdal.UseExceptions()
        print("Converting downloaded NetCDF file to COG")
        data = gdal.Open(f"NETCDF:{local_nc}:{self.inputs['npp']['subdataset']}")

        data_geotrans = data.GetGeoTransform()
        crs = osr.SpatialReference()
        crs.ImportFromEPSG(self.inputs["npp"]["crs"])
        x_size = data.RasterXSize
        y_size = data.RasterYSize
        datatype = data.GetRasterBand(1).DataType
        nodataval = data.GetRasterBand(1).GetNoDataValue()
        data_array = data.ReadAsArray(0, 0, x_size, y_size)
        # print(data_array[1000][1000])
        data = None

        driver = gdal.GetDriverByName("MEM")
        data_set = driver.Create("", x_size, y_size, 1, datatype)
        data_set_lyr = data_set.GetRasterBand(1)
        data_set_lyr.WriteArray(data_array)
        data_set_lyr.SetNoDataValue(nodataval)
        data_set.SetGeoTransform(data_geotrans)
        data_set.SetProjection(crs.ExportToWkt())
        data_set.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64])
        driver = gdal.GetDriverByName("GTiff")
        output_name = splitext(basename(self.netcdf_filename))[0]
        output_file = join(self.ROOT, "data", f"cog_{output_name}.tif")
        data_set2 = driver.CreateCopy(
            output_file,
            data_set,
            options=["COPY_SRC_OVERVIEWS=YES", "TILED=YES", "COMPRESS=LZW"],
        )
        data_set = None
        data_set2 = None

        return output_file

    def stac(self, filename):
        id = basename(filename)[0:-4]
        stacname = f"{id}.json"
        print(f"Writing STAC metadata to {stacname}")
        start, end = self.get_stac_datetimes()

        with open(join(self.ROOT, "stac_items", "template.json")) as f:
            data = json.load(f)
        data["id"] = id
        data["links"][0]["href"] = stacname
        data["properties"]["datetime"] = end
        data["properties"]["start_datetime"] = start
        data["properties"]["end_datetime"] = end
        data["assets"]["image"]["href"] = basename(filename)
        data["assets"]["thumbnail"]["href"] = basename(filename)

        with open(join(self.ROOT, "stac_items", stacname), "w") as json_file:
            json.dump(data, json_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--taskdate")
    options = parser.parse_args()
    test_task = IngestNetCDFTask(**vars(options))

    test_task.invoke()
