FROM alpine:python

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src.py .

CMD python src.py