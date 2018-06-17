import boto3
from datetime import datetime
from datetime import timedelta
from boto3.dynamodb.conditions import Key
from src.Environment.get_env_variables import get_time_window
from src.UTCConverter.UTCConverter import UTCConverter

class CloudWatchLogsAllocator():

    def client(self, region_name):
        return boto3.client('logs', region_name=region_name)

    def resource(self, region_name):
        return boto3.resource('logs', region_name=region_name)

    def iterator(self, region_name, country, project):
        logs_client = self.client(region_name)
        logs_paginator = logs_client.get_paginator('filter_log_events')
        logs_iterator = logs_paginator.paginate(
            logGroupName="{}-elb-logs".format(country),
            logStreamNames=[
                project,
            ],
            startTime=int((datetime.utcnow() -
                           timedelta(minutes=int(get_time_window()))).strftime('%s')) * 1000,
            endTime=int(UTCConverter().UTC_time_to_epoch(datetime.utcnow())) * 1000,
            PaginationConfig={
                'PageSize': 10000
            }
        )
        return logs_iterator
