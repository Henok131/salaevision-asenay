import os
import json
import logging
import requests

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

def send_slack(message: str, level: str = 'info', extra: dict | None = None) -> None:
    """Send a Slack notification if SLACK_WEBHOOK_URL is configured.
    Fails silently (logs error) if request fails.
    """
    if not SLACK_WEBHOOK_URL:
        return
    try:
        payload = {
            'text': f"[{level.upper()}] {message}",
        }
        if extra:
            payload['attachments'] = [{ 'text': json.dumps(extra)[:1900] }]
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        if resp.status_code >= 400:
            logging.warning('Slack webhook returned status %s', resp.status_code)
    except Exception as e:
        logging.exception('Slack webhook error: %s', e)
