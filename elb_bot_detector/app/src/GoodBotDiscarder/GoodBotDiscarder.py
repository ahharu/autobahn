import threading
import logging
import socket
from src.Environment.get_env_variables import get_whitelisted_bots
from src.Environment.get_env_variables import get_whitelisted_ips
from src.LookupThread.LookupThread import LookupThread

class GoodBotDiscarder():

    @staticmethod
    def discard_good_bots(ip_hash_map):
        WHITELISTED_BOTS = get_whitelisted_bots()
        WHITELISTED_IPS = get_whitelisted_ips()
        result = {}
        nb_threads = 100

        chunks = len(ip_hash_map.keys()) // nb_threads + 1
        chunked = [list(ip_hash_map.keys())[i::chunks] for i in range(chunks)]

        for i in range(chunks):

            # Limit the number of concurrent threads to 20
            pool = threading.BoundedSemaphore(20)

            lookup_threads = [LookupThread(ip, result, pool)
                              for ip in chunked[i]]
            # Start the threads
            for t in lookup_threads:
                t.start()

            # Tell main to wait for all of them
            main_thread = threading.currentThread()
            for thread in threading.enumerate():
                if thread is main_thread:
                    continue
                logging.debug('Joining %s', thread.getName())
                thread.join()
            for key, value in result.items():
                try:
                    if value['host'] == "No host found":
                        logging.getLogger().debug("No match found, skipping")
                        continue
                    if value['host'].partition('.')[2] in WHITELISTED_BOTS:
                        ip_hash_map.pop(key)
                        logging.getLogger().debug("Removing " + key + " because it is a good bot")
                    if key in WHITELISTED_IPS:
                        ip_hash_map.pop(key)
                        logging.getLogger().debug("Removing ") + key + " because it is from the office"
                except:
                    pass
        return ip_hash_map