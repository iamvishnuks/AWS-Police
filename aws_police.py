# -*- coding: utf-8 -*-
import boto3
from tqdm import *
client=boto3.client('ec2')
a=''

print '''
 █████╗ ██╗    ██╗███████╗    ██████╗  ██████╗ ██╗     ██╗ ██████╗███████╗    
██╔══██╗██║    ██║██╔════╝    ██╔══██╗██╔═══██╗██║     ██║██╔════╝██╔════╝    
███████║██║ █╗ ██║███████╗    ██████╔╝██║   ██║██║     ██║██║     █████╗      
██╔══██║██║███╗██║╚════██║    ██╔═══╝ ██║   ██║██║     ██║██║     ██╔══╝      
██║  ██║╚███╔███╔╝███████║    ██║     ╚██████╔╝███████╗██║╚██████╗███████╗    
╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝    ╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝╚══════╝    
                                                                              
                                            
         +-+-+-+-+-+-+ +-+-+
author : |V|i|s|h|n|u| |K|S|
         +-+-+-+-+-+-+ +-+-+
Development of this tool is still in progress. Currently you can view your running instances in a single run.
This program will search in all regions for ec2 instances. You have to create a user with programatic access and attach a role
with full access to ec2. Configure aws credentials in your environment by running 'aws configure' command in your CLI.
If you want to delete all the instances that also you can perform easily without going to the never loading aws dashboard.
'''
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

#Get all nat gateway info
def get_all_natgw():
  natgws={}
  for region in regions['Regions']:
    nat_client=boto3.client('ec2',region_name=region['RegionName'])
    nat_response=nat_client.describe_nat_gateways()
    natgw=[]
    for natg in nat_response['NatGateways']:
      natgw.append(natg)
    natgws[region['RegionName']]=natgw
  return natgws
      
#Get all elasticbeanstalk environments and applications
def get_all_ebstalk():
  ebstalks={}
  for region in regions['Regions']:
    ebstalk_client=boto3.client('elasticbeanstalk',region_name=region['RegionName'])
    ebstalk_response=ebstalk_client.describe_environments()
    apps_response=ebstalk_client.describe_applications()
    #print ebstalk_response,apps_response

#Get all load balancer informations
def get_all_elbs():
  elbs={}
  for region in regions['Regions']:
    elb_client=boto3.client('elb',region_name=region['RegionName'])
    elb_response=elb_client.describe_load_balancers()
    elbl=[]
    for elb in elb_response['LoadBalancerDescriptions']:
      elbl.append(elb)
    elbs[region['RegionName']]=elbl
  return elbl

#Get all volumes
def get_all_volumes():
  volumes={}
  for region in regions['Regions']:
    vol_client=boto3.client('ec2',region_name=region['RegionName'])
    vol_response=vol_client.describe_volumes()
    volids=[]
    for v in vol_response['Volumes']:
      volids.append(v['VolumeId'])
    volumes[region['RegionName']]=volids
  return volumes
  

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

results=[]
allfunctions=[get_all_vpcs,get_all_subnets,get_all_ec2,get_all_elbs,get_all_volumes,get_all_natgw]
count=0
for i in tqdm(allfunctions,desc='Patroling in progress'):
  if count==0:
    print "\nSearching VPC information"
  elif count==1:
    print "\nSearching Subnets"
  elif count==2:
    print "\nSearching ec2's"
  elif count==3:
    print "Searching for elbs"
  elif count==4:
    print "Searching for volumes"
  elif count==5:
    print "Searching for Nat gateways"
  results.append(i())
  count+=1

def kill_all_ec2(results):
  for region in results.keys():
    client=boto3.client('ec2',region_name=region)
    return client.terminate_instances(InstanceIds=results[region])

vpcs=results[0] 
subnet=results[1]
ec2=results[2]
elb=results[3]
volumes=results[4]
ngws=results[5]
if len(results[2][1])!=0:
  print "Running instances are listed below: ",results[2][1]
  a=raw_input("Do you want to kill all instances?(y/n): ")
else:
  print "There's no running instances, your account looks clean"

if a=='y':
  print "Executing house party protocol.. ;-)"
  k=kill_all_ec2(results[2][1])
  print "Everything is cleaned"

while True:
  print "1) VPC's\n2) Subnets\n3) Ec2's\n4) Load balancers\n5) Volumes\n6) NAT GWs\n7) Exit"
  b=input("Enter an option to see the results : ")
  if b==1:
    print results[0]
  elif b==2:
    print results[1]
  elif b==3:
    print results[2]
  elif b==4:
    print results[3]
  elif b==5:
    print results[4]
  elif b==6:
    print results[5]
  else:
    print "Enjoy your day.. Bye ;-)"
    break












