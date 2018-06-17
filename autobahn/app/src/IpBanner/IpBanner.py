from src.DynamoUpserter.dao.DynamoUpserter import DynamoUpserter
from src.DynamoAllocator.dao.DynamoAllocator import DynamoAllocator
from src.Environment.get_env_variables import get_dynamo_table
import logging

class IpBanner():

    def __init__(self, ec2_client, datadog_client):
        self.ec2_client = ec2_client
        self.datadog_client = datadog_client

    def not_already_banned(self, ip, vpc_id):
        cidr = ip + "/32"
        nacls = self.ec2_client.describe_network_acls(Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            },
            {
                'Name': 'entry.cidr',
                'Values': ["{}/32".format(ip)]
            }
        ])
        for nacl in nacls['NetworkAcls']:
            cidrs = [ x['CidrBlock'] for x in nacl['Entries'] ]
            if cidr in cidrs:
                return False
        return True

    def ban_ip(self, ip , nacl, proposed_rulenumber):
        self.ec2_client.create_network_acl_entry(
            CidrBlock="{}/32".format(ip),
            Egress=False,
            Protocol="-1",
            RuleAction="deny",
            RuleNumber=proposed_rulenumber,
            NetworkAclId=nacl
        )
        dynamo_resource = DynamoAllocator().resource()
        DynamoUpserter().upsert_ip_in_table(dynamo_resource, ip)
        logging.getLogger().info('Marked as Banned in Dynamo : ip {}'.format(ip))

    def ban_ips(self, list_of_ips, nacl, proposed_rulenumber, vpc_id):
        for ip in list_of_ips:
            if self.not_already_banned(ip, vpc_id):
                self.ban_ip(ip, nacl, proposed_rulenumber.pop())
                try:
                    self.datadog_client.report_bad_bot(ip)
                except:
                    logging.getLogger().warn("Failed reporting to datadog")
        self.datadog_client.report_bots(len(list_of_ips))