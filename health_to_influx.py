import sys
import yaml
import argparse
import xml.etree.ElementTree as ET
from influxdb import InfluxDBClient
from datetime import datetime, timezone


def upload(config, data=[]):
    if len(data):
        client = InfluxDBClient(**config['influxdb']['client'])
        client.create_database(config['influxdb']['client']['database'])
        client.write_points(points=data, **config['influxdb']['write_points'])

def parse(file):
    with open(file) as f:
        tree = ET.parse(f)

    formattedData = []
    # get all records
    records = tree.findall('Record')
    # we only want records with numeric values
    points = [x for x in records[0:10] if createPoint(x)]

    return points

    # for record in records:
    #     attr = record.attrib

    #     # unit = attr['unit']

    #     value = attr['value']
    #     date = attr['endDate']
    #     measurement = attr['type']
    #     # source = attr['sourceName']
        
    #     # chop off prefix if detected
    #     if measurement[0:24] == 'HKQuantityTypeIdentifier':
    #         measurement = measurement[24:]

    #     # parse the time string
    #     parsedTime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %z')
    #     # save as correct format in UTC timezone
    #     time = parsedTime.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    #     recordDict = {
    #         'measurement': measurement,
    #         'tags': {},
    #         'time': time,
    #         'fields': {
    #             'value': value
    #         }
    #     }

    #     if unit in attr:
    #         recordDict['tags']['unit'] = attr['unit']
    #     if source in attr:
    #         recordDict['tags']['source'] = attr['source']

    #     formattedData.append(recordDict)

    # return formattedData

def createPoint(record):
    attr = record.attrib

    date = attr.get('date')
    unit = attr.get('unit')
    value = attr.get('value')
    source = attr.get('source')
    measurement = attr.get('type')

    if date is None or value is None or measurement is None:
        return False

    # chop off prefix if detected
    if measurement[0:24] == 'HKQuantityTypeIdentifier':
        measurement = measurement[24:]

    # parse the time string
    parsedTime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %z')
    # save as correct format in UTC timezone
    time = parsedTime.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    recordDict = {
        'measurement': measurement,
        'tags': {},
        'time': time,
        'fields': {
            'value': value
        }
    }

    if not unit:
        recordDict['tags']['unit'] = unit
    if not source:
        recordDict['tags']['source'] = source

    return recordDict

def loadConfig(configFile):
    with open(configFile) as f:
        config = yaml.safe_load(f)

    return config

def main(configFile, exportFile):
    try:
        config = loadConfig(configFile)
        data = parse(exportFile)
        print(len(data))
        upload(config, data)

        print('Total upload success!')
    except Exception as e:
        print('Failure!')
        e = sys.exc_info()[0]
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Uploads HealthKit data to InfluxDB')
    parser.add_argument('config_file', help='InfluxDB config file location', default='./config.yml')
    parser.add_argument('export_file', help='Apple Health data export file')

    args = parser.parse_args()

    main(args.config_file, args.export_file)