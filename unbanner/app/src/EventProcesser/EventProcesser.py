import logging
import os
import boto3
from src.VpcFinder.dao.VpcFinder import VpcFinder
from src.Environment.get_env_variables import get_countries
from src.Environment.get_env_variables import get_dynamo_table
from src.Environment.get_env_variables import get_region_from_country
from src.EC2Allocator.dao.EC2Allocator import EC2Allocator
from src.DynamoGetUnbannable.dao.DynamoGetUnbannable import DynamoGetUnbannable
from src.DynamoAllocator.dao.DynamoAllocator import DynamoAllocator
from src.VpcNaclElector.dao.VpcNaclElector import VpcNaclElector
from src.IpUnbanner.IpUnbanner import IpUnbanner

class EventProcesser():
    
    @staticmethod
    def process(event):
        dynamo_db_allocator = DynamoAllocator()
        dynamo_resource = dynamo_db_allocator.resource()
        dynamo_client = dynamo_db_allocator.client()
        unbannable_ips = DynamoGetUnbannable().get_unbannables(dynamo_client, dynamo_resource)

        for country in get_countries():
            region = get_region_from_country(country)
            ec2_client = EC2Allocator().client(region_name=region)
            ip_unbanner = IpUnbanner(ec2_client=ec2_client)
            vpc_id = VpcFinder().get_vpc(ec2_client, country)
            nacl, proposed_rulenumber = VpcNaclElector(
            ).get_available_nacl_and_proposed_rulenumber(ec2_client, vpc_id, 100)
            ip_unbanner.unban_ips(unbannable_ips, nacl, vpc_id)
