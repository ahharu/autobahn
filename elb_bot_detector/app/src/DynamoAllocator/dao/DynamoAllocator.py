import boto3

# This class is responsible for managing dynamodb resources

class DynamoAllocator():

    def client(self):
        return boto3.client('dynamodb', region_name='eu-west-1')

    def resource(self):
        return boto3.resource('dynamodb', region_name='eu-west-1')

    def table(self, name):
        dynamodb = self.resource()
        return dynamodb.Table(name)
