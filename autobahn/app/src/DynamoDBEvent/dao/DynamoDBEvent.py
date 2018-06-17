from src.DynamoDBEvent.utils.deserialize_dynamo_db import deserialize_dynamo_db
from boto3.dynamodb.conditions import Key
from src.DynamoDBEvent.event_types.EventType import EventType
# Class to map the dynamoDB events!


class DynamoDBEvent:

    def __init__(self, event):
        self.new_image = deserialize_dynamo_db(
            event['dynamodb']['NewImage']) if 'NewImage' in event['dynamodb'].keys() else None
        self.old_image = deserialize_dynamo_db(
            event['dynamodb']['NewImage']) if 'OldImage' in event['dynamodb'].keys() else None
        self.eventType = EventType(event['eventName'])

    def is_insert_or_update(self):
        if self.eventType == EventType.INSERT or self.eventType == EventType.MODIFY:
            return True
        return False

    def get_ip(self):
        return self.new_image['ip']

    def get_new_image(self):
        return self.new_image
