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

def get_ban_time():
    return int(os.getenv('BAN_TIME_MINUTES'))

def get_dynamo_table():
    return os.getenv('DYNAMO_TABLE')

def get_countries():
    return os.getenv('COUNTRIES').split(',')

def get_region_from_country(country):
    return COUNTRY_TO_REGION[country]

