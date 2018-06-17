from src.ElbEntryParser.ElbEntryParser import ElbEntryParser
from moto import mock_logs, settings, mock_dynamodb2, mock_ec2
import moto
import unittest
import logging
from unittest.mock import Mock
from mock import patch, MagicMock
import json
import os
import boto3

class ElbEntryParserTest(unittest.TestCase):

    def test_elb_entry_parser(self):

        cloudwatch_line = """2018-03-21T10:10:20.748821Z es-web 80.253.202.218:61979 10.0.11.138:80 0.000052 0.442002 0.000043 200 200 0 4484 "GET https://www.ofertia.com:443/api/v1/brochure/dynamic/2135608833?lat=41.388&lng=2.17&source=PROSPECTUS_SECTOR_CHANGE&device=ofertiaVisualizer HTTP/1.1" "trollbot" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2"""

        ip, timestamp, agent, url = ElbEntryParser().parseline(cloudwatch_line)
        print(agent)
        assert ip == '80.253.202.218'
        assert timestamp == '2018-03-21T10:10:20.748821Z'
        assert agent == 'trollbot'

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))