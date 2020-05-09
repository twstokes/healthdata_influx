FROM python:3

WORKDIR /app

RUN apt-get update && apt-get install -y python3-lxml

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY healthdata_influx /app

CMD [ "python3", "import.py", "/data/export.xml" ]
