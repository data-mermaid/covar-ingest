import boto3
import requests
import zipfile
from io import BytesIO

def download(url):
    r = requests.get(url, )

    if r.status_code == 200:
        if r.headers['content-type'] == 'application/zip':
            z = zipfile.ZipFile(BytesIO(r.content))
            return z
        else:
            print ("Wrong file type")
            return
    else:
        print('File not downloaded. Encountered error code', r.status_code)
        return


def invoke():
    pass


if __name__ == "__main__":
    invoke()
