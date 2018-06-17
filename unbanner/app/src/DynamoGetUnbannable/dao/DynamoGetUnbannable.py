import boto3
from boto3.dynamodb.conditions import Key
from src.Environment.get_env_variables import get_dynamo_table
from src.DynamoGetUnbannable.utils.UTCConvert import UTC_time_to_epoch
from src.DynamoGetUnbannable.utils.deserialize_dynamo_db import deserialize_dynamo_db
from datetime import datetime
from src.TimeDecision.TimeDecision import TimeDecision
import logging

# This class is responsible for managing dynamodb resources

class DynamoGetUnbannable():

    @staticmethod
    def get_unbannables(dynamo_client, dynamo_resource):
        paginator = dynamo_client.get_paginator('scan')
        
        unbannables = []
        dynamo_iterator = paginator.paginate(TableName=get_dynamo_table())

        for page in dynamo_iterator:
            for item in page['Items']:
                python_item = deserialize_dynamo_db(item)
                if 'last_seen' in python_item and python_item['banned']:
                    should_unban = TimeDecision().should_unban(python_item['last_seen'])
                    if should_unban:
                        unbannables.append(python_item['ip'])

        return unbannables
