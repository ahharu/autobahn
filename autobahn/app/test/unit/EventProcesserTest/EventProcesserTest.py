from src.VpcFinder.dao.VpcFinder import VpcFinder
from src.Environment.get_env_variables import get_countries
from src.Environment.get_env_variables import get_nacl_rule_limit
from src.Environment.get_env_variables import get_region_from_country
from src.Environment.get_env_variables import get_dynamo_table
from src.EventProcesser.EventProcesser import EventProcesser
from src.EC2Allocator.dao.EC2Allocator import EC2Allocator
from src.IpBanner.IpBanner import IpBanner
from src.VpcNaclElector.dao.VpcNaclElector import VpcNaclElector
from src.DynamoDBEvent.dao.DynamoDBEvent import DynamoDBEvent
from src.DynamoAllocator.dao.DynamoAllocator import DynamoAllocator
from src.DynamoUpserter.utils.UTCConvert import UTC_time_to_epoch
from src.IpBanner.IpBanner import IpBanner
from src.DatadogClient.DatadogClient import DatadogClient
from src.TimeDecision.TimeDecision import TimeDecision
from boto3.dynamodb.conditions import Key
from moto import mock_logs, settings, mock_dynamodb2, mock_ec2
import moto
import unittest
import logging
import src
from datetime import datetime
from unittest.mock import Mock
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

        return self.vpc_id, self.acl_id

    @mock_dynamodb2
    @mock_ec2
    @mock_logs
    @patch.dict(os.environ,{
                "DYNAMO_TABLE":"Autobahn",
                "NACL_RULE_LIMIT": "37",
                "NACL_RULE_MAX": "100",
                "COUNTRIES": 'dev',
                "BAN_TIME_MINUTES": '5'
            }
        )
    @patch.object(moto.ec2.models.NetworkAcl, 'get_filter_value', fake_filter_value)
    def test_event_processer(self):
        print(__name__)
        vpc_id, acl_id = self.create_resources()
        struct_time = datetime.utcnow()
        epoch = UTC_time_to_epoch(struct_time)
        record = {
            'country': 'dev',
            'project': 'test'
        }
        ip_hash_map = {
            '244.244.244.244': 1
        }
        event = {
                    "eventID":"1",
                    "eventVersion":"1.0",
                    "dynamodb":{
                        "Keys":{
                            "ip":{
                                "S":"244.244.244.244"
                            },
                            "times_seen":{
                                "S":"244.244.244.244"
                            },
                            "last_seen":{
                                "N": "{}".format(epoch)
                            },
                            "banned":{
                                "BOOL": False
                            }
                        },
                        "NewImage":{
                            "ip":{
                                "S":"244.244.244.244"
                            },
                            "times_seen":{
                                "S":"244.244.244.244"
                            },
                            "last_seen":{
                                "N": "{}".format(epoch)
                            },
                            "banned":{
                                "BOOL": False
                            }
                        },
                        "StreamViewType":"NEW_AND_OLD_IMAGES",
                        "SequenceNumber":"111",
                        "SizeBytes":26
                    },
                    "awsRegion":"eu-west-1",
                    "eventName":"INSERT",
                    "eventSourceARN":'testarn',
                    "eventSource":"aws:dynamodb"
                }
        ec2_client = EC2Allocator().client('eu-west-1')
        dynamo_allocator = DynamoAllocator()
        dynamo_resource = dynamo_allocator.resource()
        table = dynamo_resource.Table(get_dynamo_table())
        
        table.put_item(
            Item={
                'ip': '244.244.244.244',
                'last_seen': epoch,
                'times_seen': 1,
                'banned': False
            }
        )
        
        EventProcesser().process(event)
        response = table.query(
            KeyConditionExpression=Key('ip').eq('244.244.244.244')
        )
        datadog_client = DatadogClient()
        ip_banner = IpBanner(ec2_client, datadog_client)
        assert response['Items'][0]['banned'] == True
        assert ip_banner.not_already_banned('244.244.244.244', vpc_id) == False

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))