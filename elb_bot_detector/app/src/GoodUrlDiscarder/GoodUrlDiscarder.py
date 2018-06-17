import threading
import logging
import socket
from src.Environment.get_env_variables import get_whitelisted_bots
from src.Environment.get_env_variables import get_whitelisted_ips
from src.LookupThread.LookupThread import LookupThread

IGNORED_URLS = ['/ajax/', 'apple-app-site-association', 'PROSPECTUS_NEXT_BROCHURE', 'PROSPECTUS_SIMILAR_BROCHURE', '.js', 'favicon.ico', 'relatedBrochures' , 'pushengage', 'static', 'FS_NEXT_BROCHURE']

class GoodUrlDiscarder():

    @staticmethod
    def is_ignored(url):
        for ignored_pattern in IGNORED_URLS:
            if ignored_pattern in url:
                return True
        return False
