#!/usr/bin/python

import boto3
import argparse
import xlsxwriter
import datetime
from dateutil.tz import tzutc


REGIONS = {
            "us-east-1":"N.Virginia"
          }

def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--output',
        dest = 'output_file',
        nargs = '?',
        default = './ec2_instances.xlsx',
        required = False,
        type = str,
        help = 'Output file path. default: ec2_instances.xlsx'
    )
    return parser.parse_args()

def format_output_data(instances):
    rows = []
    headers = ["id", "state", "instance_type", "ip_address", "private_ip_address", \
            "EbsOptimized", "vpc_id", "subnet_id", "image_id", "monitored", "launch_time", "key_name"]
    rows.append(headers)
    for i in instances:
      row = [i['InstanceId'], i['State']['Name'], i['InstanceType'],i['PublicIpAddress'],i['PrivateIpAddress'], \
            i['EbsOptimized'], i['VpcId'], i['SubnetId'], i['ImageId'], i['Monitoring']['State'], i['LaunchTime'].strftime("%Y/%m/%d %H:%M:%S"), i['KeyName']]
      rows.append(row)
    return rows

def write_excel(sheet, data):
    sheet.set_column(0, len(data[0]), 23.0)
    sheet.write(0, 0, "Last updated: ")
    sheet.write(1, 0, "The number of instances: ")
    # time
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sheet.write(0, 1, now)
    # total instances
    sheet.write(1, 1, len(data))
    # data
    start_row = 3
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            print(i+start_row, j, val)
            sheet.write(i+start_row, j, val)


if __name__ == '__main__':
    opts = get_options()
    excel = xlsxwriter.Workbook(opts.output_file)
    print("start")
    for region_code, region_name in REGIONS.items():
        print("processing %s region") % region_name
        con = boto3.client('ec2',region_name=region_code)
        instances = con.describe_instances()
        instances = instances['Reservations']
        instances = instances[0]
        instances = instances['Instances']
        #print instances
        if len(instances) == 0:
            continue
        data = format_output_data(instances)
        sheet = excel.add_worksheet(region_name)
        write_excel(sheet, data)
    
    excel.close()
    print("finish")
