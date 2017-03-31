"""
Parses an Apple Health export file and imports into
InfluxDB
"""
import sys
import argparse
import xml.etree.ElementTree as et
from datetime import datetime, timezone
import db


def parse_points(file_path):
    """
    Takes in a path to an Apple Health Data
    export file, returns points
    """
    with open(file_path) as file:
        tree = et.parse(file)

    points = []
    records = tree.findall('Record')

    for record in records:
        try:
            point = create_point(record)
            points.append(point)
        except ValueError:
            print("Couldn't convert record to point:")
            et.dump(record)
        except:
            raise

    return points

def create_point(record):
    """
    Returns an InfluxDB point for a health record XML element
    """
    attr = record.attrib

    unit = attr.get('unit')
    value = attr.get('value')
    date = attr.get('endDate')
    measurement = attr.get('type')
    source = attr.get('sourceName')

    # these values are required
    if date is None or value is None or measurement is None:
        raise ValueError

    # parse the time string
    parsed_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %z')
    # save as correct format in UTC timezone
    time = parsed_time.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # try to convert to a number
    try:
        value = float(value)
    except ValueError:
        # carry on as a string
        pass

    point = {
        'measurement': measurement,
        'tags': {},
        'time': time,
        'fields': {
            'value': value
        }
    }

    if unit is not None:
        point['tags']['unit'] = unit
    if source is not None:
        point['tags']['source'] = source

    return point

def parse_and_upload(config_path, export_path):
    """
    Takes InfluxDB configuration and Apple Health Data file paths
    Uploads to InfluxDB
    """
    try:
        print('Parsing data points...')
        data = parse_points(export_path)

        print('Uploading {0} points...'.format(len(data)))
        db.upload(config_path, data)

        print('Success!')
    except et.ParseError:
        print('Failed to parse data export!')
    except Exception as error:
        print('Failure!')
        print(sys.exc_info())
        print(error)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Uploads Apple Health Data to InfluxDB')

    PARSER.add_argument('--config_path', help='InfluxDB config file path', default='./config.yml')
    PARSER.add_argument('export_path', help='Apple Health Data export file path')

    ARGS = PARSER.parse_args()

    parse_and_upload(ARGS.config_path, ARGS.export_path)
