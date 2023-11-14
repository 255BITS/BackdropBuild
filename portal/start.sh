#!/bin/bash
echo """[default]
region = us-west-2""" > /root/.aws/config
echo """[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY""" > /root/.aws/credentials
PYTHONUNBUFFERED=1 gunicorn -w 1 prototype:app -b 0.0.0.0:8999
