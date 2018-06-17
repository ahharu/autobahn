from src.Environment.get_env_variables import get_time_window
from src.Environment.get_env_variables import get_log_group_name
from src.Environment.get_env_variables import get_dynamo_table
from src.Environment.get_env_variables import get_region_from_country
from src.Environment.get_env_variables import get_whitelisted_bots
from src.Environment.get_env_variables import get_whitelisted_ips
from src.Environment.get_env_variables import get_request_treshold
from src.Environment.exceptions.exceptions import CountryNotFoundException
from moto import mock_logs, settings
import unittest
import logging
from unittest.mock import Mock
from mock import patch, MagicMock
import json
import os
import boto3

class EnvironmentTest(unittest.TestCase):

    @patch.dict(os.environ,{"WINDOW_MINUTES":"999"})
    def test_time_window(self):
        assert get_time_window() == 999

    @patch.dict(os.environ,{"LOG_GROUP_NAME":"test"})
    def test_log_group_name(self):
        assert get_log_group_name() == "test"

    @patch.dict(os.environ,{"DYNAMO_TABLE":"test"})
    def test_dynamo_table(self):
        assert get_dynamo_table() == "test"
    
    def test_get_region_from_country(self):
        assert get_region_from_country("dev") == "eu-west-1"

    def test_get_region_from_country_missing(self):
        self.assertRaises(CountryNotFoundException, get_region_from_country, "random") 

    @patch.dict(os.environ,{"WHITELISTED_BOTS":'googlebot.com'})
    def test_whitelisted_bots(self):
        assert get_whitelisted_bots() == ['googlebot.com']

    @patch.dict(os.environ,{"WHITELISTED_IPS":'0.0.0.0'})
    def test_whitelisted_ips(self):
        assert get_whitelisted_ips() == ['0.0.0.0']

    @patch.dict(os.environ,{"REQUEST_TRESHOLD":"4444"})
    def test_request_treshold(self):
        assert get_request_treshold() == 4444

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))