from src.IpCounter.IpCounter import IpCounter
import threading
import unittest
import logging
from unittest.mock import Mock
from unittest.mock import patch
import json

class IpCounterTest(unittest.TestCase):

    def test_count_ip(self):
        ip_hash_map = {
            '244.244.244.244': 1
        }
        ip_hash_map = IpCounter().processIp('244.244.244.244', ip_hash_map)

        assert ip_hash_map['244.244.244.244'] == 2

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))