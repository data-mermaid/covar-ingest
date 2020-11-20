FROM osgeo/gdal:alpine-normal-latest

RUN apk update
RUN apk add py-pip

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY ./requirements.txt .

ADD ./data /usr/src/app/data

RUN pip install -r requirements.txt

COPY ./src.py .
COPY ./sources.txt .

CMD python src.py
