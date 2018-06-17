import boto3
from boto3.dynamodb.conditions import Key
from src.Environment.get_env_variables import get_dynamo_table
from src.DynamoUpserter.utils.UTCConvert import UTC_time_to_epoch
from datetime import datetime
import logging

# This class is responsible for managing dynamodb resources

class DynamoUpserter():

    @staticmethod
    def upsert_ip_in_table(dynamo_resource, ip):

        table = dynamo_resource.Table(get_dynamo_table())

        times_seen = 0
        
        response = table.query(
            KeyConditionExpression=Key('ip').eq(ip)
        )
        
        if len(response['Items']) == 1:
            times_seen = response['Items'][0]['times_seen']

        table.put_item(
            Item={
                'ip': ip,
                'last_seen': UTC_time_to_epoch(datetime.utcnow()),
                'times_seen': times_seen+1,
                'banned': True
            }
        )
        
        logging.getLogger().info('Banned ip {}'.format(ip))
