from src.CloudWatchLogsAllocator.dao.CloudWatchLogsAllocator import CloudWatchLogsAllocator
from src.Environment.get_env_variables import get_region_from_country
from src.Environment.get_env_variables import get_request_treshold
from src.ElbEntryParser.ElbEntryParser import ElbEntryParser
from src.IpCounter.IpCounter import IpCounter
from src.GoodBotDiscarder.GoodBotDiscarder import GoodBotDiscarder
from src.DynamoAllocator.dao.DynamoAllocator import DynamoAllocator
from src.DynamoUpserter.dao.DynamoUpserter import DynamoUpserter
from src.GoodUrlDiscarder.GoodUrlDiscarder import GoodUrlDiscarder

class RecordProcesser():
    
    @staticmethod
    def process(record):
        ip_hash_map = {}
        country = record['country']
        project = record['project']
        dynamo_allocator = DynamoAllocator()
        dynamo_resource = dynamo_allocator.resource()
        region = get_region_from_country(country)
        cloudwatch_allocator = CloudWatchLogsAllocator()
        for event_page in cloudwatch_allocator.iterator(region, country, project):
            print(len(event_page['events']))
            for event in event_page['events']:
                line = event['message']
                try:
                    ip, timestamp, agent, url = ElbEntryParser.parseline(line)
                    if not GoodUrlDiscarder().is_ignored(url):
                        ip_hash_map = IpCounter().processIp(ip, ip_hash_map)
                except Exception as e:
                    pass
        ip_hash_map = {k: v for k, v in ip_hash_map.items() if v >=
                       get_request_treshold()}
        ip_hash_map = GoodBotDiscarder().discard_good_bots(ip_hash_map)
        list_of_ips = [k for k, v in ip_hash_map.items()]
        for ip in list_of_ips:
            DynamoUpserter.upsert_ip_in_table(dynamo_resource,ip)
