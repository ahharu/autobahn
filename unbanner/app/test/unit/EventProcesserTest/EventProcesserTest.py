from src.VpcFinder.dao.VpcFinder import VpcFinder
from src.Environment.get_env_variables import get_countries
from src.Environment.get_env_variables import get_dynamo_table
from src.Environment.get_env_variables import get_region_from_country
from src.EC2Allocator.dao.EC2Allocator import EC2Allocator
from src.DynamoGetUnbannable.dao.DynamoGetUnbannable import DynamoGetUnbannable
from src.DynamoAllocator.dao.DynamoAllocator import DynamoAllocator
from src.VpcNaclElector.dao.VpcNaclElector import VpcNaclElector
from src.EventProcesser.EventProcesser import EventProcesser
from src.DynamoUpserter.utils.UTCConvert import UTC_time_to_epoch
from src.IpUnbanner.IpUnbanner import IpUnbanner
from boto3.dynamodb.conditions import Key
from moto import mock_logs, settings, mock_dynamodb2, mock_ec2

import moto
import unittest
import logging
from unittest.mock import Mock
from datetime import datetime
from mock import patch, MagicMock
import json
import os
import boto3

class EventProcesserTest(unittest.TestCase):

    def fake_get_region_from_country(country):
        return 'eu-west-1'

    def create_table(self):
        dynamo_allocator = DynamoAllocator()
        dynamo_resource = dynamo_allocator.resource()
        dynamo_resource.create_table(
            TableName='Autobahn',
            KeySchema=[
                {
                    'AttributeName': 'ip',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'ip',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    def fake_filter_value(self, filter_name):
        if filter_name == "default":
            return self.default
        elif filter_name == "vpc-id":
            return self.vpc_id
        elif filter_name == "association.network-acl-id":
            return self.id
        elif filter_name == "association.subnet-id":
            return [assoc.subnet_id for assoc in self.associations.values()]
        elif filter_name == "entry.cidr":
            return '244.244.244.244/32'
        else:
            return super(NetworkAcl, self).get_filter_value(
                filter_name, 'DescribeNetworkAcls')

    @mock_dynamodb2
    @mock_ec2
    def create_resources(self):
        # Create Dynamo and user
        dynamo_allocator = DynamoAllocator()
        self.create_table()
        dynamo_table = dynamo_allocator.table('Autobahn')
        
        ec2_client = EC2Allocator().client('eu-west-1')
        vpc_response = ec2_client.create_vpc(
            CidrBlock='10.1.0.0/24',
            AmazonProvidedIpv6CidrBlock=False,
            DryRun=False,
            InstanceTenancy='default'
        )
        self.vpc_id = vpc_response['Vpc']['VpcId']
        ec2_client.create_tags(
            DryRun=False,
            Resources=[self.vpc_id],
            Tags=[
                {
                    'Key': 'Name',
                    'Value': "vpc-dev"
                }
            ]
        )

        acl_response = ec2_client.create_network_acl(
            DryRun=False,
            VpcId=self.vpc_id
        )
        
        self.acl_id = acl_response['NetworkAcl']['NetworkAclId']
        entry_response = ec2_client.create_network_acl_entry(
            CidrBlock='244.244.244.244/32',
            DryRun=False,
            Egress=False,
            NetworkAclId=self.acl_id,
            Protocol='-1',
            RuleAction='deny',
            RuleNumber=77
        )
        return self.vpc_id, self.acl_id

    @mock_dynamodb2
    @mock_ec2
    @patch.dict(os.environ,{
                "DYNAMO_TABLE":"Autobahn",
                "COUNTRIES": "dev",
                "BAN_TIME_MINUTES": "5"
            }
        )
    @patch.object(moto.ec2.models.NetworkAcl, 'get_filter_value', fake_filter_value)
    def test_event_processer(self):
        vpc_id, acl_id = self.create_resources()
        ip_hash_map = {
            '244.244.244.244': 1
        }
        ec2_client = EC2Allocator().client('eu-west-1')
        dynamo_allocator = DynamoAllocator()
        dynamo_resource = dynamo_allocator.resource()
        table = dynamo_resource.Table(get_dynamo_table())
        struct_time = datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M")
        epoch = UTC_time_to_epoch(struct_time)
        table.put_item(
            Item={
                'ip': '244.244.244.244',
                'last_seen': epoch,
                'times_seen': 1,
                'banned': True
            }
        )

        EventProcesser().process({})

        response = table.query(
            KeyConditionExpression=Key('ip').eq('244.244.244.244')
        )

        assert response['Items'][0]['banned'] == False

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))