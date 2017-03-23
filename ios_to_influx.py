import sys
import argparse
import influx_import as importer
import xml.etree.ElementTree as et
from datetime import datetime, timezone


"""
Takes in a path to an Apple Health Data export file, returns points
"""
def parseToPoints(filePath):
    with open(filePath) as f:
        tree = et.parse(f)

    points = []
    records = tree.findall('Record')

    for record in records:
        try:
            point = createPoint(record)
            points.append(point)
        except ValueError:
            print("Couldn't convert record to point - skipping.")
            pass
        except:
            raise

    return points

"""
Returns an InfluxDB point for a health record XML element
"""
def createPoint(record):
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
    parsedTime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %z')
    # save as correct format in UTC timezone
    time = parsedTime.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

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

"""
Takes InfluxDB configuration and Apple Health Data file paths
Uploads to InfluxDB
"""
def parseAndUpload(configPath, exportPath):
    try:
        print('Parsing data points...')
        data = parseToPoints(exportPath)

        print('Uploading {0} points...'.format(len(data)))
        importer.upload(configPath, data)

        print('Success!')
    except et.ParseError:
        print('Failed to parse data export!')
    except Exception as e:
        print('Failure!')
        print(sys.exc_info())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Uploads Apple Health Data to InfluxDB')

    parser.add_argument('--config_path', help='InfluxDB config file path', default='./config.yml')
    parser.add_argument('export_path', help='Apple Health Data export file path')

    args = parser.parse_args()

    parseAndUpload(args.config_path, args.export_path)
