import os
from boto3.dynamodb.types import TypeDeserializer
import json
import ast
import decimal

def replace_decimals(obj):
    if isinstance(obj, list):
        for i in xrange(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def deserialize_dynamo_db(dynamo_format_dict):
    deserializer = TypeDeserializer()
    python_data = {k: deserializer.deserialize(v) for k,v in dynamo_format_dict.items()}
    return replace_decimals(python_data)