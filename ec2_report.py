#!/usr/bin/python

import boto3
import argparse
import xlsxwriter
import datetime
from dateutil.tz import tzutc


REGIONS = {
            "ap-south-1":"Mumbai"
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
    headers = ["id", "state", "instance_type", "public_ip_address", "private_ip_address", \
            "EbsOptimized", "vpc_id", "subnet_id", "image_id", "monitored", "launch_time", "key_name"]
    rows.append(headers)
    for i in instances:
      if(i['Instances'][0]['State']['Name']=='running'):
        row = [i['Instances'][0]['InstanceId'], i['Instances'][0]['State']['Name'], i['Instances'][0]['InstanceType'],i['Instances'][0]['PublicIpAddress'],i['Instances'][0]['PrivateIpAddress'], \
            i['Instances'][0]['EbsOptimized'], i['Instances'][0]['VpcId'], i['Instances'][0]['SubnetId'], i['Instances'][0]['ImageId'], i['Instances'][0]['Monitoring']['State'], i['Instances'][0]['LaunchTime'].strftime("%Y/%m/%d %H:%M:%S"), i['Instances'][0]	['KeyName']]
        rows.append(row)
      else:
        row = [i['Instances'][0]['InstanceId'], i['Instances'][0]['State']['Name'], i['Instances'][0]['InstanceType'],'Null','Null', \
            i['Instances'][0]['EbsOptimized'], 'Null', 'Null', i['Instances'][0]['ImageId'], i['Instances'][0]['Monitoring']['State'], i['Instances'][0]['LaunchTime'].strftime("%Y/%m/%d %H:%M:%S"), i['Instances'][0]	['KeyName']]
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
        #instances = instances[0]
        #instances = instances['Instances']
        #print instances
        if len(instances) == 0:
            continue
        data = format_output_data(instances)
        sheet = excel.add_worksheet(region_name)
        write_excel(sheet, data)
    
    excel.close()
    print("finish")
