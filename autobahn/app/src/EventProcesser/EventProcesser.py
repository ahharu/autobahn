import logging
import os
import boto3
from src.VpcFinder.dao.VpcFinder import VpcFinder
from src.Environment.get_env_variables import get_countries
from src.Environment.get_env_variables import get_nacl_rule_limit
from src.Environment.get_env_variables import get_region_from_country
from src.EC2Allocator.dao.EC2Allocator import EC2Allocator
from src.VpcNaclElector.dao.VpcNaclElector import VpcNaclElector
from src.DynamoDBEvent.dao.DynamoDBEvent import DynamoDBEvent
from src.IpBanner.IpBanner import IpBanner
from src.DatadogClient.DatadogClient import DatadogClient
from src.TimeDecision.TimeDecision import TimeDecision

class EventProcesser():
    
    @staticmethod
    def process(event):
        dynamo_db_event = DynamoDBEvent(event)
        datadog_client = DatadogClient()
        if dynamo_db_event.is_insert_or_update() and TimeDecision.is_recent(dynamo_db_event):
            ban_ips = [dynamo_db_event.get_ip()]
            for country in get_countries():
                region = get_region_from_country(country)
                ec2_client = EC2Allocator().client(region_name=region)
                vpc = VpcFinder().get_vpc(ec2_client, country)
                nacl, proposed_rulenumber = VpcNaclElector(
                ).get_available_nacl_and_proposed_rulenumber(ec2_client, vpc, get_nacl_rule_limit())
                ip_banner = IpBanner(ec2_client=ec2_client, datadog_client=datadog_client)
                ip_banner.ban_ips(ban_ips, nacl, proposed_rulenumber, vpc)
