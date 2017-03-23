# healthdata_influx
Imports Apple Health Data into InfluxDB

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