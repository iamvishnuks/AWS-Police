# AWS-Police
This is a tool for monitoring AWS resources like EC2 instances, elastic loadbalancers,
NAT gateways etc. This tool will search for an active or stopped resource in all regions.
There are 15 regions as of now in AWS. And we can't remember what all resources are running on
which region. In that case we can simply run this tool and wait for the results. AWS-Police will
search and find the hidden resources which are eating your money.

# Installation
Install dependecies
pip install -r requirements.txt

# Usage
Create a user in your AWS account with programatic access and give EC2 full access permission 
for that user. Then do aws configure to set aws access key and secret key. 
After setting key run the tool by typing:
python aws-police.py
