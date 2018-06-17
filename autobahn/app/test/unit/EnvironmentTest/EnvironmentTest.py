from src.Environment.get_env_variables import get_ban_time
from src.Environment.get_env_variables import get_dynamo_table
from src.Environment.get_env_variables import get_region_from_country
from src.Environment.get_env_variables import get_datadog_api_key
from src.Environment.get_env_variables import get_datadog_app_key
from src.Environment.get_env_variables import get_nacl_rule_max
from src.Environment.get_env_variables import get_nacl_rule_limit
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

    @patch.dict(os.environ,{"DATADOG_API_KEY":"test"})
    def test_datadog_api_key(self):
        assert get_datadog_api_key() == "test"

    @patch.dict(os.environ,{"DATADOG_APP_KEY":"test"})
    def test_datadog_app_key(self):
        assert get_datadog_app_key() == "test"

    @patch.dict(os.environ,{"NACL_RULE_MAX":"999"})
    def test_nacl_rule_max(self):
        assert get_nacl_rule_max() == 999

    @patch.dict(os.environ,{"NACL_RULE_LIMIT":"999"})
    def test_nacl_rule_limit(self):
        assert get_nacl_rule_limit() == 999

    def test_get_region_from_country(self):
        assert get_region_from_country("dev") == "eu-west-1"

    @patch.dict(os.environ,{"COUNTRIES":"dev1,dev2"})
    def test_dynamo_table(self):
        assert get_countries() == ['dev1','dev2']

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))