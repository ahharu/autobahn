import os

COUNTRY_TO_REGION = {

'cl': 'us-west-1',
'co': 'us-west-1',
'mx': 'us-west-1',
'es': 'eu-west-1',
'se': 'eu-central-1',
'dk': 'eu-central-1',
'no': 'eu-central-1,',
'staging': 'eu-west-1',
'dev': 'eu-west-1'

}

def get_dynamo_table():
    return os.getenv('DYNAMO_TABLE')

def get_datadog_api_key():
    return os.getenv('DATADOG_API_KEY')

def get_datadog_app_key():
    return os.getenv('DATADOG_APP_KEY')

def get_dynamo_table():
    return os.getenv('DYNAMO_TABLE')

def get_nacl_rule_limit():
    return int(os.getenv('NACL_RULE_LIMIT'))

def get_nacl_rule_max():
    return int(os.getenv('NACL_RULE_MAX'))

def get_ban_time():
    return int(os.getenv('BAN_TIME_MINUTES'))

def get_countries():
    return os.getenv('COUNTRIES').split(',')

def get_region_from_country(country):
    return COUNTRY_TO_REGION[country]

