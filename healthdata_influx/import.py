"""
Parses an Apple Health export file
and imports into InfluxDB
"""
import sys
import argparse
from datetime import datetime
from lxml import etree
from db import InfluxDBUploader

class Importer:
    """
    Importer parses an Apple Health XML file
    and uploads Records to a database
    """
    def __init__(self, uploader, dry=False, buffer_size=50000):
        if dry:
            print('Dry run - no database changes will be made.')

        self.dry = dry
        self.uploader = uploader
        # how many records to Buffer before flushing to the database
        # adjusting this will affect memory consumption
        self.buffer_size = buffer_size

    def upload(self, points):
        """
        Sends points to the uploader if not a dry run.
        """
        if not self.dry:
            self.uploader.upload(points)
    
    def parse_and_upload(self, export_path):
        """
        Takes InfluxDB configuration and Apple Health Data file paths
        Uploads to InfluxDB
        """

        def create_flusher(buffer, size):
            def flusher(records):
                print("Flushing {} points to DB. Current total: {}".format(size, records))
                self.upload(buffer[:size])
                # clean up
                del buffer[:size]
            return flusher

        try:
            print('Opening export file...')
            with open(export_path, mode='rb') as file:
                context = self.get_record_iterator(file)

                point_buffer = []
                total_records, success_records = (0, 0)
                flusher = create_flusher(point_buffer, self.buffer_size)

                for idx, (_, record) in enumerate(context):
                    total_records += 1

                    try:
                        point = self.mung_record_to_point(record)
                        point_buffer.append(point)
                        success_records += 1
                    except Exception as error:
                        output_mung_error(error, record, idx+1)

                    if len(point_buffer) > self.buffer_size - 1:
                        flusher(total_records)

                    # memory cleanup
                    record.clear()
                    while record.getprevious() is not None:
                        del record.getparent()[0]

                # upload the rest
                self.upload(point_buffer)

            print("Successful uploads: {}".format(success_records))
            print("Total records: {}".format(total_records))
        except Exception as error:
            print('Failure!')
            print(sys.exc_info())
            print(error)

    def mung_record_to_point(self, record):
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

        point = self.uploader.create_point(measurement, time, fields, tags)

        return point

    def get_record_iterator(self, file):
        """
        Takes in an Apple Health Data
        export file, returns iterator for Record elements
        """
        return etree.iterparse(file, events=('end',), tag='Record')

def output_mung_error(error, record, index):
    print("Couldn't convert record to point:", error)
    print(etree.tostring(record))
    print("Record index: {}".format(index))

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Imports Apple Health Data to InfluxDB')

    PARSER.add_argument('--config_path', help='InfluxDB config file path', default='./config.yml')
    PARSER.add_argument('--dry', help='Dry run - no DB changes', action='store_true', default=False)
    PARSER.add_argument('export_path', help='Apple Health Data export file path')

    ARGS = PARSER.parse_args()

    try:
        UPLOADER = InfluxDBUploader(ARGS.config_path)
        print('InfluxDB uploader loaded.')
        IMPORTER = Importer(UPLOADER, ARGS.dry)
        print('Importer loaded.')
        IMPORTER.parse_and_upload(ARGS.export_path)
    except FileNotFoundError:
        print('Could not load InfluxDB configuration file!')
    except Exception as error:
        print('Failed to initialize InfluxDB!')
        print(error)
