FROM python:alpine

RUN mkdir /usr/src/app

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./src.py .

CMD python src.py