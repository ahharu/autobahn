from src.GoodUrlDiscarder.GoodUrlDiscarder import GoodUrlDiscarder
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
    def test_ajax_call_discarded(self):
        url = "https://www.ofertia.com:443/ajax/autocompleteSearchBox?search=Eu&_=1504576339"
        
        assert GoodUrlDiscarder().is_ignored(url) == True

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))