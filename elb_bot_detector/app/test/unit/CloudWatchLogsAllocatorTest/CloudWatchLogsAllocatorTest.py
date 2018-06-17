from src.CloudWatchLogsAllocator.dao.CloudWatchLogsAllocator import CloudWatchLogsAllocator
from src.UTCConverter.UTCConverter import UTCConverter
from datetime import datetime
from moto import mock_logs, settings
import unittest
import logging
from unittest.mock import Mock
from mock import patch, MagicMock
import json
import os
import boto3

class UTCConverterTest(unittest.TestCase):

    @patch.dict(os.environ,{'WINDOW_MINUTES':"999"})
    @mock_logs
    def cloudwatchfixtures(self):
        conn = boto3.client('logs', 'eu-west-1')
        log_group_name = 'test-elb-logs'
        conn.create_log_group(logGroupName=log_group_name)
        log_stream_name = 'test'
        conn.create_log_stream(
            logGroupName=log_group_name,
            logStreamName=log_stream_name
        )
        conn.put_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            logEvents=[
                {
                'timestamp': int(UTCConverter().UTC_time_to_epoch(datetime.utcnow())) * 1000,
                'message': 'thisisatest'
                },
            ],
        )

    @mock_logs
    @patch.dict(os.environ,{"WINDOW_MINUTES":"999"})
    def test_log_iterator(self):
        cloudwatch_allocator = CloudWatchLogsAllocator()
        region="eu-west-1"
        project="test"
        country="test"
        self.cloudwatchfixtures()
        for event_page in cloudwatch_allocator.iterator(region, country, project):
            assert len(event_page['events']) == 1
            for event in event_page['events']:
                line = event['message']
                assert line == "thisisatest"

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))