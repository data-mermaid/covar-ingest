import boto3
import urllib.request
from osgeo import gdal
import json
from datetime import datetime, timedelta
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dhw_5km.geotif?CRW_DHW%5B(2020-11-15T12:00:00Z):1:(2020-11-15T12:00:00Z)%5D%5B(89.975):1:(-89.975)%5D%5B(-179.975):1:(179.975)%5D
# dhw_5km_00c3_7b6f_8b8a.tif

def invoke():
    try: 
        start_time = f"2020-11-12T12:00:00Z"
        numdays = 1
        for i in range(numdays):
            dtime = end_times(start_time)
            start_time = dtime
            filename = request(dtime)
            print(f"starting cog transformation: {filename}")
            output_cog = cog(filename)          
            stac_item = stac(output_cog, dtime)
            to_aws(output_cog, filename, stac_item)
    except urllib.error.URLError as e:
        print(f'The server couldn\'t fulfill the request.')
        print(f'Error code: {e.code}')
    except urllib.error.HTTPError as e:
        print(f'We failed to reach a server.')
        print(f'Reason: {e.reason}')

def request(datetime):
    url = f'https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dhw_5km.geotif?CRW_DHW%5B({datetime}):1:({datetime})%5D%5B(89.975):1:(-89.975)%5D%5B(-179.975):1:(179.975)%5D'
    req = urllib.request.Request(url)
    filedata = urllib.request.urlopen(req)
    filename = filedata.info().get_filename()
    filepath = f"data/{filename}"
    # print(filepath)

    datatowrite = filedata.read()
    with open(filepath, 'wb') as f:
        f.write(datatowrite)
    return filename

def stac(filename, datetime):
    start = datetime
    end = end_times(datetime)
    
    with open('stac_items/template.json') as f:
        data = json.load(f)
    idstring = filename[5:-4]
    data["id"] = idstring
    data["properties"]["datetime"] = datetime
    data["properties"]["start_datetime"] = start
    data["properties"]["end_datetime"] = end
    data["assets"]["image"]["href"] = f"s3://covariate-ingest-data-dev/dhw/cogs/{idstring}.tif"
    data["assets"]["image"]["href"] = f"s3://covariate-ingest-data-dev/dhw/cogs/{idstring}.tif"
    data["assets"]["thumbnail"]["href"] = f"s3://covariate-ingest-data-dev/dhw/cogs/{idstring}.tif"
    data["links"][0] = {
        "rel":"self",
        "href":f"s3://covariate-ingest-data-dev/dhw/stac_items/{idstring}.json"
    }
    data["links"][1] = {
        "rel":"collection",
        "href":f"s3://covariate-ingest-data-dev/dhw/collection.json"
    }
    data["links"][2] = {
        "rel":"parent",
        "href":f"s3://covariate-ingest-data-dev/dhw/collection.json"
    }
    print(data)

    with open(f'stac_items/{idstring}.json', 'w') as json_file:
        json.dump(data, json_file)

    return f'stac_items/{idstring}.json'

def end_times(dtime):
    dtime_strt = datetime.strptime(dtime, "%Y-%m-%dT%H:%M:%SZ")
    hours = 24
    hours_added = timedelta(hours = hours)
    dtime_end = dtime_strt + hours_added
    dtime_end = dtime_end.strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(dtime_end)

def cog(filename):
    input_dir = "data/"
    input_tif = f"{input_dir}{filename}"
    output_cog = f"{input_dir}cog_{filename}"
    tif_to_cog(input_tif, output_cog)
    if os.path.exists(f'{input_dir}{filename}'):
        os.remove(f'{input_dir}{filename}')
    else:
        print(f'Intermediate file {input_dir}{filename} does not exist')
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
        options = [
                "COPY_SRC_OVERVIEWS=YES",
                "TILED=YES",
                "COMPRESS=LZW"
            ]
        )
    data_set = None
    data_set2 = None

def to_aws(cog_file, filename, stac_item): 
    filename = f"dhw/cogs/cog_{filename}"
    stac_aws = f"dhw/{stac_item}"
    upload_cog = upload_to_aws(cog_file, 'covariate-ingest-data-dev', filename)
    upload_stac = upload_to_aws(stac_item, 'covariate-ingest-data-dev', stac_aws)

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

if __name__ == "__main__":
    invoke()
