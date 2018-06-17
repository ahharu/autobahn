from src.TimeDecision.TimeDecision import TimeDecision
from boto3.dynamodb.conditions import Key
from moto import mock_logs, settings, mock_dynamodb2, mock_ec2
from src.DynamoUpserter.utils.UTCConvert import UTC_time_to_epoch
import moto
import unittest
import logging
from unittest.mock import Mock
from datetime import datetime
from mock import patch, MagicMock
import json
import os
import boto3

class TimeDecisionTest(unittest.TestCase):

    @mock_dynamodb2
    @mock_ec2
    @patch.dict(os.environ,{
                "DYNAMO_TABLE":"Autobahn",
                "COUNTRIES": "dev",
                "BAN_TIME_MINUTES": "5"
            }
        )

    def test_time_decision(self):

        struct_time = datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M")
        epoch = UTC_time_to_epoch(struct_time)

        assert True == TimeDecision().should_unban(epoch)

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))