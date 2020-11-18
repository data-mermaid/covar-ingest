import boto3
import urllib.request
from osgeo import gdal

# https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dhw_5km.geotif?CRW_DHW%5B(2020-11-15T12:00:00Z):1:(2020-11-15T12:00:00Z)%5D%5B(89.975):1:(-89.975)%5D%5B(-179.975):1:(179.975)%5D
# dhw_5km_00c3_7b6f_8b8a.tif

def invoke():
    req = urllib.request.Request('https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dhw_5km.geotif?CRW_DHW%5B(2020-11-15T12:00:00Z):1:(2020-11-15T12:00:00Z)%5D%5B(89.975):1:(-89.975)%5D%5B(-179.975):1:(179.975)%5D')
    try: 
        filedata = urllib.request.urlopen(req)

        filename = filedata.info().get_filename()
     
        filepath = f"data/{filename}"

        print(filepath)
        #filepath = "data/" + filename
        datatowrite = filedata.read()
        with open(filepath, 'wb') as f:
            f.write(datatowrite)
        print("starting cog transformation")
        cog(filename)
    except urllib.error.URLError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except urllib.error.HTTPError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)

def cog(filename):
    input_tif_dir = "data/"
    input_tif = f"{input_tif_dir}{filename}"
    output_cog = f"{input_tif_dir}cog_{filename}"
    tif_to_cog(input_tif, output_cog)

def tif_to_cog(input_tif, output_cog):
    data = gdal.Open(input_tif)
    data_geotrans = data.GetGeoTransform()
    data_proj = data.GetProjection()
    data_array = data.ReadAsArray()
    x_size = data.RasterXSize
    y_size = data.RasterYSize
    num_bands = data.RasterCount
    datatype = data.GetRasterBand(1).DataType
    data = None
    driver = gdal.GetDriverByName('MEM')
    data_set = driver.Create('', x_size, y_size, num_bands, datatype)
    for i in range(num_bands):
        data_set_lyr = data_set.GetRasterBand(i + 1)
        if len(data_array.shape) == 2:
            data_set_lyr.WriteArray(data_array)
        else:
            data_set_lyr.WriteArray(data_array[i])
    data_set.SetGeoTransform(data_geotrans)
    data_set.SetProjection(data_proj)
    data_set.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64])
    driver = gdal.GetDriverByName('GTiff')
    data_set2 = driver.CreateCopy(
        output_cog,
        data_set,
        options = [
                "COPY_SRC_OVERVIEWS=YES",
                "TILED=YES",
                "COMPRESS=LZW"
            ]
        )
    data_set = None
    data_set2 = None



if __name__ == "__main__":
    invoke()
