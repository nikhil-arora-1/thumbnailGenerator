#!/bin/bash
aws configure set region us-east-1
source ps_env/bin/activate
python tnProcessor.py