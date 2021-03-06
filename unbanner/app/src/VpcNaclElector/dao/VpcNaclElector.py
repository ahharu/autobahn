from boto3.dynamodb.conditions import Key
# Class to map the dynamoDB events!

class VpcNaclElector():

    @staticmethod
    def get_available_nacl_and_proposed_rulenumber(client, vpc_id, nacl_rule_limit):
        nacls = client.describe_network_acls(Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            }
        ])

        updated = False
        for nacl in nacls['NetworkAcls']:
            if ( len(nacl['Entries']) < nacl_rule_limit ):
                entries = nacl['Entries']
                rulenumbers = [ x['RuleNumber'] for x in sorted(entries, key=lambda item:item['RuleNumber'])]
                proposed_rulenumber = list ( set(range(100)) - set(rulenumbers) )
                return nacl['NetworkAclId'], proposed_rulenumber
