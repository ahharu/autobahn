from src.Environment.get_env_variables import get_ban_time
from src.Environment.get_env_variables import get_dynamo_table
from src.Environment.get_env_variables import get_region_from_country
from src.Environment.get_env_variables import get_countries
from moto import mock_logs, settings
import unittest
import logging
from unittest.mock import Mock
from mock import patch, MagicMock
import json
import os
import boto3

class EnvironmentTest(unittest.TestCase):

    @patch.dict(os.environ,{"BAN_TIME_MINUTES":"999"})
    def test_ban_time(self):
        assert get_ban_time() == 999

    @patch.dict(os.environ,{"DYNAMO_TABLE":"test"})
    def test_dynamo_table(self):
        assert get_dynamo_table() == "test"
    
    def test_get_region_from_country(self):
        assert get_region_from_country("dev") == "eu-west-1"

    @patch.dict(os.environ,{"COUNTRIES":"dev1,dev2"})
    def test_dynamo_table(self):
        assert get_countries() == ['dev1','dev2']

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))