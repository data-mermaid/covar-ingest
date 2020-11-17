import boto3
import urllib.request

# https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dhw_5km.geotif?CRW_DHW%5B(2020-11-15T12:00:00Z):1:(2020-11-15T12:00:00Z)%5D%5B(89.975):1:(-89.975)%5D%5B(-179.975):1:(179.975)%5D
# dhw_5km_00c3_7b6f_8b8a.tif

def invoke():
    req = urllib.request.Request('https://pae-paha.pacioos.hawaii.edu/erddap/griddap/dhw_5km.geotif?CRW_DHW%5B(2020-11-15T12:00:00Z):1:(2020-11-15T12:00:00Z)%5D%5B(89.975):1:(-89.975)%5D%5B(-179.975):1:(179.975)%5D')
    try: 
        filedata = urllib.request.urlopen(req)

        filename = filedata.info().get_filename()
        print(filename)
        filepath = "data/" + filename
        datatowrite = filedata.read()
        with open(filepath, 'wb') as f:
            f.write(datatowrite)
    except urllib.error.URLError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except urllib.error.HTTPError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)

    print("hello")

if __name__ == "__main__":
    invoke()
