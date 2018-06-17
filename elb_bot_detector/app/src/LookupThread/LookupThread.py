import threading
import socket
import logging

class LookupThread(threading.Thread):
    def __init__(self, ip, result, pool):
        self.ip = ip
        self.result = result
        self.pool = pool
        threading.Thread.__init__(self)

    def run(self):
        self.pool.acquire()
        try:
            logging.debug('Starting')
            self.lookup(self.ip)
        finally:
            self.pool.release()
            logging.debug('Exiting')

    def lookup(self, ip):
        """Try to find the host of IP.

        Returns a dict:
            {ip: {'host': host, 'aliases': aliases}}
        If host is not found, then the dict will hold:
            {ip: {'host': 'No host found', 'aliases': ''}}

        """

        try:
            host, aliases, _ = socket.gethostbyaddr(ip)
            self.result[ip] = {
                'host': host,
                'aliases': aliases if aliases else ''
            }
        except socket.herror:
            self.result[ip] = {'host': 'No host found', 'aliases': ''}