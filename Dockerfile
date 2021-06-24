FROM python:3.7-buster

ADD requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

ADD main.py /
ADD intents.py /
ADD utils.py /
ADD config / /config/
ADD database.py /

CMD [ "python", "./main.py" ]
