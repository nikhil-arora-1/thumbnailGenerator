#!/bin/bash
# export AWS_DEFAULT_REGION = $REGION
aws configure set region us-east-1
yum install python3 -y
python3 -m venv ps_env
source ps_env/bin/activate
pip install boto3
pip install pillow