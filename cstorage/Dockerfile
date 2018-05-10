FROM python:2.7-slim

RUN apt-get update
RUN apt-get install -y python-dev gcc
RUN pip install --upgrade google-cloud-pubsub

ADD controller-incluster.py /controller.py

CMD ["python", "-u", "/controller.py"]
