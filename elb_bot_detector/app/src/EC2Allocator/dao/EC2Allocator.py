import boto3
from boto3.dynamodb.conditions import Key
# Class to map the dynamoDB events!

class EC2Allocator():

    @staticmethod
    def client(region_name):
        return boto3.client('ec2', region_name=region_name)
    @staticmethod
    def resource(region_name):
        return boto3.resource('ec2', region_name=region_name)