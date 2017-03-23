import yaml
from influxdb import InfluxDBClient

"""
Uploads data points to InfluxDB
"""
def upload(configPath, dataPoints=[]):
    config = _loadConfig(configPath)

    if len(dataPoints):
        client = InfluxDBClient(**config['influxdb']['client'])
        client.create_database(config['influxdb']['client']['database'])
        client.write_points(points=dataPoints, **config['influxdb']['write_points'])

"""
Loads config for this script
"""
def _loadConfig(configPath):
    with open(configPath) as f:
        config = yaml.safe_load(f)
    return config
