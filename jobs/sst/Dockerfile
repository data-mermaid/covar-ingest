FROM osgeo/gdal:alpine-normal-latest

RUN apk update
RUN apk add py-pip

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./src.py .

CMD python src.py