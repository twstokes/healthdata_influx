"""Loads a configuration and imports data points into InfluxDB"""
import yaml
from influxdb import InfluxDBClient

def upload(configpath, datapoints=None):
    """Uploads data points to InfluxDB"""
    config = _loadconfig(configpath)

    if datapoints is not None and len(datapoints):
        client = InfluxDBClient(**config['influxdb']['client'])
        client.create_database(config['influxdb']['client']['database'])
        client.write_points(points=datapoints, **config['influxdb']['write_points'])


def _loadconfig(configpath):
    """Loads config for this script"""
    with open(configpath) as file:
        config = yaml.safe_load(file)
    return config
