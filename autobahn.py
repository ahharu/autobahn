#!/usr/bin/env python
"""Detect Bad bots!

Usage: autobahn.py   [--window_minutes=<int>]
                            [--request_treshold=<int>]
                            [--country=<str>]
                            [--project=<str>]
       autobahn.py [--help | --version]

Options:
  -h --help                           Show this screen.
  --window_minutes=<str>              Minutes in the log to look [default: 5]
  --request_treshold=<str>            Threshold to fire an alarm [default: 300]
  --country=<str>                     The country where this is running
  --project=<str>                     The project
"""

import re
import os
import random
from datetime import datetime
from datetime import timedelta
import socket
import threading
import logging
from datadog import initialize, api, statsd
from boto3.dynamodb.conditions import Key
import json
import calendar

__version__ = '0.1'
WHITELISTED_BOTS = ['googlebot.com', 'google.com',
                    'bing.com', 'msn.com', 'search.msn.com', 'yse.yahoo.net']
WHITELISTED_IPS = ['217.126.85.82', '81.45.44.180', '213.98.123.229']

NACL_RULE_LIMIT = 37
NACL_RULE_MAX = 100


try:
    import boto3
    from botocore.exceptions import ClientError
    from docopt import docopt
    import threading
    import logging
    from datadog import initialize, api, statsd
    import json
#    from schema import Schema, Optional, SchemaError
except ImportError:
    from subprocess import call
    if not call(["pip", "install", "--upgrade", "boto3", "docopt", "datadog"]):
        call(["python", __file__])
        exit(0)
    else:
        exit(1)
args = docopt(__doc__, options_first=True, version=__version__)
datadog_credential_path = os.path.join(
    os.path.dirname(__file__), "datadogKeys.json")

country = args['--country']
project = args['--project']
window_minutes = args['--window_minutes']
request_treshold = args['--request_treshold']

ip_hash_map = {}


class datadog_client():
    api = None

    def __init__(self):
        '''
        Class initialization:
        Once the class is called, the script reads data used to auth with datadog
        '''
        options_string = open(datadog_credential_path).read()
        options = json.loads(options_string)
        initialize(**options)
        self.api = api

    def send_datadog_event(self, title, text, tags):
        api.Event.create(title=title, text=text, tags=tags)

    def send_datadog_metric(self, metric, points, tags):
        api.Metric.send(metric=metric, points=points, tags=tags)

    def send_statsd_set(self, set_name, value):
        statsd.set(set_name, value)


class LookupThread(threading.Thread):
    def __init__(self, ip, result, pool):
        self.ip = ip
        self.result = result
        self.pool = pool
        threading.Thread.__init__(self)

    def run(self):
        self.pool.acquire()
        try:
            logging.debug('Starting')
            self.lookup(self.ip)
        finally:
            self.pool.release()
            logging.debug('Exiting')

    def lookup(self, ip):
        """Try to find the host of IP.

        Returns a dict:
            {ip: {'host': host, 'aliases': aliases}}
        If host is not found, then the dict will hold:
            {ip: {'host': 'No host found', 'aliases': ''}}

        """

        try:
            host, aliases, _ = socket.gethostbyaddr(ip)
            self.result[ip] = {
                'host': host,
                'aliases': aliases if aliases else ''
            }
        except socket.herror:
            self.result[ip] = {'host': 'No host found', 'aliases': ''}


def discard_good_bots():
    result = {}
    nb_threads = 100

    chunks = len(ip_hash_map.keys()) / nb_threads + 1
    chunked = [ip_hash_map.keys()[i::chunks] for i in xrange(chunks)]

    for i in range(chunks):

        # Limit the number of concurrent threads to 20
        pool = threading.BoundedSemaphore(20)

        lookup_threads = [LookupThread(ip, result, pool)
                          for ip in chunked[i]]
        # Start the threads
        for t in lookup_threads:
            t.start()

        # Tell main to wait for all of them
        main_thread = threading.currentThread()
        for thread in threading.enumerate():
            if thread is main_thread:
                continue
            logging.debug('Joining %s', thread.getName())
            thread.join()

        for key, value in result.iteritems():
            try:
                if value['host'].partition('.')[2] in WHITELISTED_BOTS:
                    ip_hash_map.pop(key)
                    print("Removing " + key + "because it is a good bot")
                if key in WHITELISTED_IPS:
                    ip_hash_map.pop(key)
                    print("Removing ") + key + "because it is from the office"
            except:
                pass


def parseline(line):
    regex = r'([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:\-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) ([^ ]*) (- |[^ ]*)\" (\"[^$]*\") ([A-Z0-9-]+) ([A-Za-z0-9.-]*)'
    parsed = re.findall(regex, line.rstrip())
    if len(parsed[0]) < 17:
        throw(Exception("Could not parse line"))
    return parsed[0][2], parsed[0][0], parsed[0][16]


def processIp(ip):
    if ip in ip_hash_map:
        ip_hash_map[ip] = ip_hash_map[ip] + 1
    else:
        ip_hash_map[ip] = 1


def UTC_time_to_epoch(timestamp):
    epoch = calendar.timegm(timestamp.utctimetuple())
    return epoch


def get_vpc(country):
    ec2_client = boto3.client('ec2')

    vpcs = ec2_client.describe_vpcs(Filters=[
        {
            'Name': 'tag:Name',
            'Values': ["vpc-{}".format(country)]
        }
    ])
    if len(vpcs['Vpcs']) == 0:
        return None
    else:
        return vpcs['Vpcs'][0]['VpcId']


def get_nacls(vpc_id):
    ec2_client = boto3.client('ec2')

    nacls = ec2_client.describe_network_acls(Filters=[
        {
            'Name': 'vpc-id',
            'Values': [vpc_id]
        }
    ])
    return nacls['NetworkAcls']


def upsert_dynamodb(ip):
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.Table('AutobahnTest')

    times_seen = 1

    response = table.query(
        KeyConditionExpression=Key('ip').eq(ip)
    )
    if len(response['Items']) == 1:
        times_seen = response['Items'][0]['times_seen']

    table.put_item(
        Item={
            'ip': ip,
            'last_seen': UTC_time_to_epoch(datetime.utcnow()),
            'times_seen': times_seen,
            'banned': False
        }
    )

def get_available_nacl_and_proposed_rulenumber(nacls, my_vpc):
    # Check if any available NACL has free space
    updated = False
    for nacl in nacls:
        if ( len(nacl['Entries']) < NACL_RULE_LIMIT ):
            entries = nacl['Entries']
            rulenumbers = [ x['RuleNumber'] for x in sorted(entries, key=lambda item:item['RuleNumber'])]
            proposed_rulenumber = list ( set(range(100)) - set(rulenumbers) )
            return nacl['NetworkAclId'], proposed_rulenumber  

def not_already_banned(ip, vpc_id):
    cidr = ip + "/32"
    nacls = ec2_client.describe_network_acls(Filters=[
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
        cidrs = [ x['CidrBlock'] for x in nacl['Entries'] ]
        if cidr in cidrs:
            return False
    return True

def ban_ip(ip , nacl, proposed_rulenumber):
    ec2_client.create_network_acl_entry(
        CidrBlock="{}/32".format(ip),
        Egress=False,
        Protocol="-1",
        RuleAction="deny",
        RuleNumber=proposed_rulenumber,
        NetworkAclId=nacl
    )
    

def ban_ips(list_of_ips, nacl, proposed_rulenumber, vpc_id):
    for ip in list_of_ips:
        if not_already_banned(ip, vpc_id):
            ban_ip(ip, nacl, proposed_rulenumber.pop())



logs_client = boto3.client('logs')
logs_paginator = logs_client.get_paginator('filter_log_events')

logs_iterator = logs_paginator.paginate(
    logGroupName="{}-elb-logs".format(country),
    logStreamNames=[
        project,
    ],
    startTime=int((datetime.utcnow() -
                   timedelta(minutes=int(window_minutes))).strftime('%s')) * 1000,
    endTime=int(UTC_time_to_epoch(datetime.utcnow())) * 1000,
    PaginationConfig={
        'PageSize': 10000
    }
)


for event_page in logs_iterator:
    for event in event_page['events']:
        line = event['message']
        try:
            ip, timestamp, agent = parseline(line)
            processIp(ip)
        except Exception as e:
            pass

datadog_client = datadog_client()

ip_hash_map = {k: v for k, v in ip_hash_map.iteritems() if v >=
               int(args['--request_treshold'])}
discard_good_bots()
list_of_ips = [k for k, v in ip_hash_map.iteritems()]

list_of_ips = ['244.244.244.244']
print(list_of_ips)

tags = ['badbot:true',
        "project:{}".format(args['--project']),
        "country:{}".format(args['--country'])]

ec2_client = boto3.client('ec2')

my_vpc = get_vpc(country)

nacls = get_nacls(my_vpc)

nacl, proposed_rulenumber = get_available_nacl_and_proposed_rulenumber(nacls, my_vpc)

print(nacls)

print(nacl)

print(proposed_rulenumber)

ban_ips(list_of_ips, nacl, proposed_rulenumber, my_vpc)

# for ip in list_of_ips:
#     upsert_dynamodb(ip)

# for ip in list_of_ips:
#     datadog_client.send_datadog_event(
#         'Bad Bot Detected',
#         "Ip {} is a suspected bot".format(ip),
#         tags=tags
#     )
#     datadog_client.send_statsd_set(set_name='bots.uniques', value=ip)
#     datadog_client.send_datadog_metric(
#         metric='bots.last.number', points=len(list_of_ips), tags=tags)
