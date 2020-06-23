FROM python:3.8-slim

RUN pip install cognite-sdk-experimental

COPY . /
CMD python /src/index.py