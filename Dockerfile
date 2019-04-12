FROM python:3.7-alpine

RUN mkdir /usr/src/app
RUN mkdir /usr/src/app/tmp

COPY config /usr/src/app/config
COPY main.py /usr/src/app/main.py
COPY requirements.txt /usr/src/app
COPY tmp/31_12_2019_23_59_59.txt /usr/src/app/tmp

WORKDIR /usr/src/app
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD python main.py