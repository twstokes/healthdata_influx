"""
Parses an Apple Health export file
and imports into InfluxDB
"""
import sys
import argparse
from datetime import datetime
import xml.etree.ElementTree as et
import db


def parse_points(file_path):
    """
    Takes in a path to an Apple Health Data
    export file, returns points
    """
    with open(file_path) as file:
        tree = et.parse(file)

    print("XML loaded.")

    points = []
    records = tree.findall('Record')

    for record in records:
        try:
            point = mung_record_to_point(record)
            points.append(point)
        except ValueError as error:
            print("Couldn't convert record to point:", error)
            et.dump(record)
        except:
            raise

    return points

def mung_record_to_point(record):
    """
    Returns an InfluxDB point for a health record XML element
    """
    attr = record.attrib

    if ('endDate' not in attr
            or 'value' not in attr
            or 'type' not in attr):
        raise ValueError('Failed to find all required fields.')

    tags = {}
    fields = {}

    value = attr['value']
    end_date = attr['endDate']
    measurement = attr['type']

    try:
        # try to convert to a number
        value = float(value)
    except ValueError:
        # carry on as a string
        pass

    # set the fields
    fields['value'] = value
    # convert to datetime obj
    time = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S %z')

    if 'unit' in attr:
        tags['unit'] = attr['unit']
    if 'sourceName' in attr:
        tags['source'] = attr['sourceName']

    point = db.create_point(measurement, time, fields, tags)

    return point

def parse_and_upload(config_path, export_path, dry_run=False):
    """
    Takes InfluxDB configuration and Apple Health Data file paths
    Uploads to InfluxDB
    """
    try:
        print('Parsing data points...')
        data = parse_points(export_path)

        print('Uploading {0} points...'.format(len(data)))
        if not dry_run:
            db.upload(config_path, data)
        else:
            print('Dry run - no database changes made.')

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
    PARSER.add_argument('--dry', help='Dry run - no DB changes', action='store_true', default=False)
    PARSER.add_argument('export_path', help='Apple Health Data export file path')

    ARGS = PARSER.parse_args()

    parse_and_upload(ARGS.config_path, ARGS.export_path, ARGS.dry)
