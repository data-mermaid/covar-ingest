# FROM python:alpine
# FROM petkr/gdal-python-alpine
FROM osgeo/gdal:alpine-normal-latest

RUN apk update
RUN apk add py-pip

# RUN apk add make automake gcc g++ subversion python3-dev

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY ./requirements.txt .

# RUN set -xe \
#     && apt-get update \
#     && apt-get install python-pip

RUN pip install -r requirements.txt

COPY ./src.py .

CMD python src.py