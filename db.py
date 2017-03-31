"""Loads a configuration and imports data points into InfluxDB"""
import yaml
from influxdb import InfluxDBClient

def upload(config_path, data_points=None):
    """Uploads data points to InfluxDB"""
    config = _load_config(config_path)

    if data_points is not None and len(data_points):
        client = InfluxDBClient(**config['influxdb']['client'])
        client.create_database(config['influxdb']['client']['database'])
        client.write_points(points=data_points, **config['influxdb']['write_points'])


def _load_config(config_path):
    """Loads config for this script"""
    with open(config_path) as file:
        config = yaml.safe_load(file)
    return config
