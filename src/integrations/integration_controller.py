import os
import json
import logging
import requests

class IntegrationClient:
    def __init__(self):
        self.clients = {}
        self.status = {}
        self._init_all()

    def _enable(self, key: str) -> bool:
        return str(os.getenv(f'ENABLE_{key}', 'false')).lower() == 'true'

    def _init_all(self):
        if self._enable('SLACK'):
            self.clients['slack'] = { 'webhook': os.getenv('SLACK_WEBHOOK_URL') }
            self.status['slack'] = bool(self.clients['slack']['webhook'])
        if self._enable('SAP'):
            self.clients['sap'] = {
                'client_id': os.getenv('SAP_CLIENT_ID'),
                'client_secret': os.getenv('SAP_CLIENT_SECRET'),
                'base_url': os.getenv('SAP_BASE_URL'),
            }
            self.status['sap'] = all(self.clients['sap'].values())
        if self._enable('OUTLOOK'):
            self.clients['outlook'] = {
                'client_id': os.getenv('OUTLOOK_CLIENT_ID'),
                'client_secret': os.getenv('OUTLOOK_CLIENT_SECRET'),
                'redirect_uri': os.getenv('OUTLOOK_REDIRECT_URI'),
            }
            self.status['outlook'] = all(self.clients['outlook'].values())
        if self._enable('DRIVE'):
            self.clients['drive'] = { 'service_account_json': os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON') }
            self.status['drive'] = bool(self.clients['drive']['service_account_json'])
        # Add more connectors similarly...
        for key in ['HUBSPOT', 'SALESFORCE', 'MAILCHIMP', 'SENDINBLUE', 'GMAIL']:
            if self._enable(key):
                self.clients[key.lower()] = { 'enabled': True }
                self.status[key.lower()] = True
            else:
                self.status[key.lower()] = False

    def connect_tool(self, tool_name: str):
        t = tool_name.lower()
        if t not in self.clients:
            raise ValueError('Tool not enabled or unsupported')
        return self.clients[t]

    def send_slack(self, text: str, extra: dict | None = None):
        if not self.status.get('slack'):
            return False
        try:
            payload = { 'text': text }
            if extra:
                payload['attachments'] = [{ 'text': json.dumps(extra)[:1900] }]
            r = requests.post(self.clients['slack']['webhook'], json=payload, timeout=5)
            return r.status_code < 400
        except Exception as e:
            logging.exception('Slack send error: %s', e)
            return False

    def get_status(self):
        return self.status

integration_client = IntegrationClient()
