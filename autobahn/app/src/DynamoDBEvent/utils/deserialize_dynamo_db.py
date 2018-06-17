import os
from boto3.dynamodb.types import TypeDeserializer

# returns the bucket where to read the data from
def deserialize_dynamo_db(dynamo_format_dict):
    deserializer = TypeDeserializer()
    python_data = {k: deserializer.deserialize(v) for k,v in dynamo_format_dict.items()}

    return python_data