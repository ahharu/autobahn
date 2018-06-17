from src.GoodBotDiscarder.GoodBotDiscarder import GoodBotDiscarder
from moto import mock_logs, settings
import unittest
import logging
from unittest.mock import Mock
from mock import patch, MagicMock
import json
import os
import boto3

class EnvironmentTest(unittest.TestCase):

    @patch.dict(os.environ,{"WHITELISTED_BOTS":'googlebot.com'})
    @patch.dict(os.environ,{"WHITELISTED_IPS":''})
    def test_googlebot_is_discarded(self):
        ip_hash_map = {'66.249.66.1':99}
        ip_hash_map = GoodBotDiscarder.discard_good_bots(ip_hash_map)
        assert '66.249.66.1' not in ip_hash_map

    @patch.dict(os.environ,{"WHITELISTED_BOTS":'googlebot.com'})
    @patch.dict(os.environ,{"WHITELISTED_IPS":''})
    def test_nasty_bot_is_banned(self):
        ip_hash_map = {'244.244.244.244':99}
        ip_hash_map = GoodBotDiscarder.discard_good_bots(ip_hash_map)
        assert '244.244.244.244' in ip_hash_map

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))