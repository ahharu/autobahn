from boto3.dynamodb.conditions import Key
# Class to map the dynamoDB events!

class VpcFinder():

    @staticmethod
    def get_vpc(client, country):

        vpcs = client.describe_vpcs(Filters=[
            {
                'Name': 'tag:Name',
                'Values': ["vpc-{}".format(country)]
            }
        ])
        if len(vpcs['Vpcs']) == 0:
            return None
        else:
            return vpcs['Vpcs'][0]['VpcId']
