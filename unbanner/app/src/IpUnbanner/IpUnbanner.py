from src.DynamoUpserter.dao.DynamoUpserter import DynamoUpserter
from src.DynamoAllocator.dao.DynamoAllocator import DynamoAllocator
from src.Environment.get_env_variables import get_dynamo_table
import logging

class IpUnbanner():

    def __init__(self, ec2_client):
        self.ec2_client = ec2_client

    def remove_nacl_entry(self, ip, vpc_id):
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
            cidrs = [x['CidrBlock'] for x in nacl['Entries']]
            match_nacl_entry = [x['RuleNumber']
                                for x in nacl['Entries'] if x['CidrBlock'] == cidr]
            if cidr in cidrs:
                self.ec2_client.delete_network_acl_entry(
                    Egress=False,
                    NetworkAclId=nacl['NetworkAclId'],
                    RuleNumber=match_nacl_entry[0])

    def unban_ip(self, ip, nacl, vpc_id):
        self.remove_nacl_entry(ip, vpc_id)
        dynamo_resource = DynamoAllocator().resource()
        DynamoUpserter().upsert_ip_in_table(dynamo_resource, ip)
        logging.getLogger().info('Marked as Unbanned in Dynamo : ip {}'.format(ip))

    def unban_ips(self, list_of_ips, nacl, vpc_id):
        for ip in list_of_ips:
            self.unban_ip(ip, nacl, vpc_id)
