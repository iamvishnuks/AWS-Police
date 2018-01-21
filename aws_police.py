import boto3
from tqdm import *
client=boto3.client('ec2')

#Get all region names
regions = client.describe_regions()
  #print "Number of available regions :", len(regions['Regions'])
  #print "Regions are :"
  #for region in regions['Regions']:
    #print region['RegionName']

#Get all vpc's in all region
def get_all_vpcs():
  vpcs={}
  for region in regions['Regions']:
    vpc_client=boto3.client('ec2',region_name=region['RegionName'])
    vpc_response=vpc_client.describe_vpcs()
    vpcids=[]
    for vpcid in vpc_response['Vpcs']:
      vpcids.append(vpcid['VpcId'])
    vpcs[region['RegionName']]=vpcids
    return vpcs

#Get all subnet information
def get_all_subnets():
  subnets={}
  for region in regions['Regions']:
    subnet_client=boto3.client('ec2',region_name=region['RegionName'])
    sub_response=subnet_client.describe_subnets()
    sub_ids=[]
    for subid in sub_response['Subnets']:
      sub_ids.append(subid['SubnetId'])
    subnets[region['RegionName']]=sub_ids
    return subnets

#Get all ec2 informations
def get_all_ec2():
  instances={}
  ec2_running={}
  for region in regions['Regions']:
    ec2_client=boto3.client('ec2',region_name=region['RegionName'])
    ec2_response=ec2_client.describe_instances()
    ec2ids=[]
    ec2_run_ids=[]
    for r in ec2_response['Reservations']:
      for instance in r['Instances']:
        if instance['State']['Name']=="running":
          ec2_run_ids.append(instance['InstanceId'])
        ec2ids.append((instance['InstanceId'],instance['State']['Name'],instance['InstanceType']))
      instances[region['RegionName']]=ec2ids
      ec2_running[region['RegionName']]=ec2_run_ids
      #print region['RegionName'],instance['InstanceId'],instance['State']['Name'],instance['InstanceType']
  ec2_running=dict((k, v) for k, v in ec2_running.iteritems() if v)
  return instances,ec2_running

allfunctions=[get_all_vpcs,get_all_subnets,get_all_ec2]
results=[]
count=0
for i in tqdm(allfunctions,desc='Patroling in progress'):
  if count==0:
    print "\nSearching VPC information"
  elif count==1:
    print "\nSearching Subnets"
  elif count==2:
    print "\nSearching ec2's"
  results.append(i())
  count+=1

def kill_all_ec2(results):
  for region in results.keys():
    client=boto3.client('ec2',region_name=region)
    print client.terminate_instances(InstanceIds=results[region])
    
if len(results[2][1])!=0:
  print "Running instances are listed below: ",results[2][1]
  a=raw_input("Do you want to kill all instances?(y/n): ")
else:
  print "There's no running instances, your account looks clean"

if a=='y':
  k=kill_all_ec2(results[2][1])
  print "Everything is cleaned"
