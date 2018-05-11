FROM python:2.7-slim

RUN apt-get update
RUN apt-get install -y python-dev gcc
RUN pip install --upgrade google-cloud-pubsub
RUN pip install kubernetes

ADD controller-incluster.py /controller.py
ADD crd.py /crd.py

CMD ["python", "-u", "/controller.py"]
