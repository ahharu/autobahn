from src.DynamoUpserter.utils.UTCConvert import UTC_time_to_epoch
import threading
import unittest
import logging
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch
import json

class UTCConverterTest(unittest.TestCase):

    def test_utc_convert(self):
        struct_time = datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M")
        epoch = UTC_time_to_epoch(struct_time)
        
        assert epoch == 1164126600

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))