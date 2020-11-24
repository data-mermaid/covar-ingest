# NPP ingest task
Task for converting Net Primary Productivity (NPP) files from NOAA in NetCDF format into Cloud Optimized GeoTIFFs
 (COGs), writing out Spatial Temporal Asset Catalog (STAC) metadata, and writing both data and metadata to an S3 
 bucket and STAC database. There is one NPP dataset per day, and they seem to be released ~2-3 days after the day 
 they represent. 

## environment
```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_BUCKET=
ENV=
STAC_API=
```

## invocation
The last command in `Dockerfile` is `CMD python src.py` so the task can be run by simply building and running the 
Docker container. For local development it may be easier to comment that command and do 
`docker run -it -v $PWD:/usr/src/app npp_ingest sh` and then run `python src.py` from inside the container, using 
the IDE of your choice on the host system.

One argument may be passed to `src.py`: `timewindow`. This is the number of days before the date the task is run
 (`now()`) for which daily NPP datasets should be processed. The default is `5`, so a default invocation will
 typically not find available data for the most recent three days, then process a new dataset, and then re-process an
 existing dataset (which will overwrite the COG and STAC json file but skip STAC API update).

## TODOs
The current MVP simply converts, creates metadata, and uploads. But further processing for near-shore environments is
 required. Additional TODOs are noted in the code, listed here in rough order of priority:
- See about crosswalking with older NPP products 
  (https://coastwatch.pfeg.noaa.gov/erddap/griddap/index.html?page=1&itemsPerPage=1000). The current version only
  goes back to 2015.
- Incorporate near-shore correction: https://github.com/pmarchand1/msec/tree/master/npp
- Write data["bbox"] dynamically
- Abstract out an IngestTask base class that all jobs can inherit from
- Abstract away `netcdf2cog`, perhaps as part of an IngestTask class, perhaps as an installable module
- Handle timezones in date calculations if necessary
- Check STAC to see if this day exists before reprocessing
- Get STAC API to allow updating of existing assets (not this repo but related)
