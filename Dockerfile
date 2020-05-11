FROM debian:buster

WORKDIR /app

RUN apt-get update && apt-get install -y python3-lxml python3-pip

COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt

COPY healthdata_influx /app

CMD [ "python3", "import.py", "/data/export.xml" ]
