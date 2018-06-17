from src.TimeDecision.TimeDecision import TimeDecision
from boto3.dynamodb.conditions import Key
from moto import mock_logs, settings, mock_dynamodb2, mock_ec2
from src.DynamoUpserter.utils.UTCConvert import UTC_time_to_epoch
from src.DynamoDBEvent.dao.DynamoDBEvent import DynamoDBEvent
import moto
import unittest
import logging
from unittest.mock import Mock
from datetime import datetime
from mock import patch, MagicMock
import json
import os
import boto3


class DynamoDBEventTest(unittest.TestCase):

    @mock_dynamodb2
    @mock_ec2
    def test_dynamodb_event(self):
        struct_time= datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M")
        epoch= UTC_time_to_epoch(struct_time)
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

        assert '244.244.244.244' == DynamoDBEvent(event).get_new_image()['ip']

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
