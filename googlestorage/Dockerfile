FROM python:buster

RUN apt-get update

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY gstorage.py /
CMD ["python", "-u", "/gstorage.py"]
