import boto3
import  os
import requests
import zipfile
from io import BytesIO
from osgeo import gdal

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET = os.getenv("AWS_BUCKET")

def download(zipfile_url):
    r = requests.get(zipfile_url)

    if r.status_code == 200:
        if r.headers['content-type'] == 'application/zip':
            print('Downloading data from', zipfile_url)
            z = zipfile.ZipFile(BytesIO(r.content))
            return z
        else:
            print ("Wrong file type at", zipfile_url)
            return
    else:
        print('File not downloaded. Encountered error code', r.status_code)
        return


def validate(zipfile):
    if not True in [info.filename.endswith('tif') for info in zipfile.infolist()]:
        print("Datasource doesn't contain TIF file")
        return False
    else:
        return True


def delete(path):
    if os.path.exists(f'{path}'):
        os.remove(f'{path}')


def cog(filename):
    input_dir = "./data/"
    input_tif = f"{input_dir}{filename}"
    output_cog = f"{input_dir}cog_{filename}"
    tif_to_cog(input_tif, output_cog)
    delete(input_tif)
    return output_cog


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
        options=[
            "COPY_SRC_OVERVIEWS=YES",
            "TILED=YES",
            "COMPRESS=LZW"
        ]
    )
    data_set = None
    data_set2 = None


def upload_to_aws(file, bucket, destination):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3.upload_file(file, bucket, destination)
    return


def process(zipfile, dataset):
    zipfile.extractall("./data")
    tif = dataset + '.tif'
    output_cog = cog(tif)
    output_cog_path = "ghs-pop/cog/" + tif
    upload_to_aws(output_cog, AWS_BUCKET, output_cog_path)
    print("Processing", tif)
    return


def invoke():
    with open('sources.txt') as urls:
        for url in urls:
            url = url.strip('\r\n')
            zipfile = download(url)
            if zipfile:
                if validate(zipfile):
                    dataset_name = os.path.splitext(os.path.basename(url))[0]
                    process(zipfile, dataset_name)
    pass


if __name__ == "__main__":
    invoke()
