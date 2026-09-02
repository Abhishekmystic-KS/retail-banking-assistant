import os
import boto3

def get_dynamodb_resource():
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    region = os.getenv("AWS_REGION", "us-east-1")
    return boto3.resource('dynamodb', endpoint_url=endpoint_url, region_name=region)

def get_cloudwatch_client():
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    region = os.getenv("AWS_REGION", "us-east-1")
    return boto3.client('cloudwatch', endpoint_url=endpoint_url, region_name=region)

def get_s3_client():
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    region = os.getenv("AWS_REGION", "us-east-1")
    return boto3.client('s3', endpoint_url=endpoint_url, region_name=region)
