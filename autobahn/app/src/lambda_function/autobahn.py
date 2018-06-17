import logging
import os
import boto3
from raven import Client as Raven_client
from raven.handlers.logging import SentryHandler
from src.EventProcesser.EventProcesser import EventProcesser
from raven.conf import setup_logging
import logging
from aws_xray_sdk.core import patch_all

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.debug(event)
    raven_client = Raven_client()  # Needs SENTRY_DSN env var
    sentry_handler = SentryHandler(raven_client)
    sentry_handler.setLevel(logging.WARNING)
    setup_logging(sentry_handler)
    logger.setLevel(logging.INFO)
    enable_xray()
    try:
        for event in event['Records']:
            EventProcesser().process(event)
        logger.info('processed event {}'.format(event))

    except Exception as e:
        logger.error('error processing event {}'.format(event))
        raise e

def enable_xray():
    patch_all()
