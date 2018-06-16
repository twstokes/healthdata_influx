FROM python:3

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY healthdata_influx /app

CMD [ "python3", "import.py", "/data/export.xml" ]