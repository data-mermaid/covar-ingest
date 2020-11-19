from osgeo import gdal

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
    
input_tif_dir = "/Users/alex_spark/Documents/MermaidQGIS/TIFs"

input_tif = f"{input_tif_dir}/Gravity_NC_10km.tif"
output_cog = f"{input_tif_dir}/Gravity_NC_10km_cog.tif"

tif_to_cog(input_tif, output_cog)