from src.Environment.get_env_variables import get_datadog_api_key
from src.Environment.get_env_variables import get_datadog_app_key
from datadog import initialize, api

class DatadogClient():
    api = None

    def __init__(self):
        '''
        Class initialization:
        Once the class is called, the script reads data used to auth with datadog
        '''

        options = {
            'api_key': get_datadog_api_key(),
            'app_key': get_datadog_app_key(),
            'host_name': 'lambda'
        }
        
        initialize(**options)
        self.api = api

    def send_datadog_event(self, title, text, tags):
        self.api.Event.create(title=title, text=text, tags=tags)

    def send_datadog_metric(self, metric, points, tags):
        self.api.Metric.send(metric=metric, points=points, tags=tags)

    def report_bots(self, nbots):
        self.send_datadog_metric(
            metric='botbans.last.number', points=nbots, tags=tags)

    def report_bad_bot(self, ip):
        tags = ['badbotban:true']

        self.send_datadog_event(
            'Bad Bot Detected',
            "Ip {} has been banned".format(ip),
            tags=tags
        )
