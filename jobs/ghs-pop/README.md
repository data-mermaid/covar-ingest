# Sample Ingest Job

This is a ingest pipeline for the static population data found at https://ghsl.jrc.ec.europa.eu/ghs_pop2019.php

Running this pipeline is only necessary when new datasets are added to the collection.

## Environment Variables:

Save `.env_sample` as `.env` and update the following values for the S3 bucket you want to upload data to:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
AWS_BUCKET
```

## Data Sources

Sample datasource URLs for this job can be found in `sources_sample.txt` This file contains URLs for the four highest resolution datasets for 1975, 1990, 2000, and 2015, and they are a good place to start for the first time executing this pipeline.

Before running the tool, save the `sources_sample.txt` as `sources.txt`, and add or remove source URLs as needed.

## TO DO:
1. Add function to convert/upload STAC version of data.
2. Add checks to see if data already exists in S3, as data sources are large and static, recreating them isn't necessary.