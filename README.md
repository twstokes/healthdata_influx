# healthdata_influx
Imports Apple Health Data into InfluxDB.

![Grafana Screenshot](https://www.tannr.com/wp-content/uploads/2017/03/grafana.png "Grafana Screenshot")
Visualizing InfluxDB using [Grafana](https://grafana.com/).

### Requirements:

 * [Python 3](https://www.python.org/)
 * [InfluxDB](https://www.influxdata.com/)

### Installation:

* `pip install -r requirements.txt`
* Rename `config_sample.yml` to `config.yml`

### Configuration:

* Edit `config.yml`

### Usage:

1. Export Health Data from iOS device
2. `python3 import.py export.xml`

### Notes:
* Does not support "Mindful Sessions"

### Docker:

Building `docker build -t nickbusey/healthdata_influx -f Dockerfile .`

Run once `docker run -v ${PWD}/config.yml:/config.yml -v ${PWD}/export.xml:/export.xml nickbusey/healthdata_influx`

Run with docker-compose

```
  apple_health_influx:
    image: nickbusey/healthdata_influx
    volumes:
      - /home/user/export.xml:/export.xml
      - /home/user/config.yml:/config.yml
```

### Docker with Cron:

Expects a .zip file since that is what Apple exports.

Building `docker build -t nickbusey/healthdata_influx:cron -f Dockerfile.cron .`

Run once `docker run -v ${PWD}/config.yml:/config.yml -v ${PWD}/export.xml:/export.xml nickbusey/healthdata_influx:cron`

Run with docker-compose

```
  apple_health_influx:
    image: nickbusey/healthdata_influx:cron
    volumes:
      - /home/user/export.zip:/export.zip
      - /home/user/config.yml:/config.yml
```