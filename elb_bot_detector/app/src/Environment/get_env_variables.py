import os
from src.Environment.exceptions.exceptions import CountryNotFoundException

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

def get_time_window():
    return int(os.getenv('WINDOW_MINUTES'))

def get_log_group_name():
    return os.getenv('LOG_GROUP_NAME')

def get_dynamo_table():
    return os.getenv('DYNAMO_TABLE')

def get_region_from_country(country):
    if country not in COUNTRY_TO_REGION:
        raise CountryNotFoundException("Country {} not found".format(country))
    return COUNTRY_TO_REGION[country]

def get_whitelisted_bots():
    return os.getenv('WHITELISTED_BOTS').split(',')

def get_whitelisted_ips():
    return os.getenv('WHITELISTED_IPS').split(',')

def get_request_treshold():
    return int(os.getenv('REQUEST_TRESHOLD'))