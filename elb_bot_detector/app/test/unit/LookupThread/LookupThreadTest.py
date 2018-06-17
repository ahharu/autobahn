from src.LookupThread.LookupThread import LookupThread
import threading
import unittest
import logging
from unittest.mock import Mock
from unittest.mock import patch
import json

class LookupThreadTest(unittest.TestCase):

    def test_googlebot(self):
        result = {}
        google_ip = ["66.249.66.1"]
        pool = threading.BoundedSemaphore(20)

        lookup_threads = [LookupThread(ip, result, pool)
                          for ip in google_ip]
        # Start the threads
        for t in lookup_threads:
            t.start()

        # Tell main to wait for all of them
        main_thread = threading.currentThread()
        for thread in threading.enumerate():
            if thread is main_thread:
                continue
            thread.join()
        print(result)
        assert "googlebot" in result['66.249.66.1']['host']

    def test_normal_ip(self):
        result = {}
        random_ip = ["244.244.244.244"]
        pool = threading.BoundedSemaphore(20)

        lookup_threads = [LookupThread(ip, result, pool)
                          for ip in random_ip]
        # Start the threads
        for t in lookup_threads:
            t.start()

        # Tell main to wait for all of them
        main_thread = threading.currentThread()
        for thread in threading.enumerate():
            if thread is main_thread:
                continue
            thread.join()
        print(result)
        assert "googlebot" not in result["244.244.244.244"]['host']

if __name__ == "__main__":
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))