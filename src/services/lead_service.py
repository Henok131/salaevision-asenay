import logging
from utils.db_utils import supabase
from integrations.integration_controller import integration_client

# Event hooks mapping SalesVision events to third-party tools

def on_new_lead(lead: dict):
  # Sync to CRM (placeholder)
  logging.info('[HOOK] New lead: %s', lead.get('email'))
  # Slack alert when enabled
  integration_client.send_slack(f"New lead: {lead.get('name')} <{lead.get('email')}>")


def on_score_updated(lead_id: str, score: int):
  logging.info('[HOOK] Score updated: %s -> %s', lead_id, score)
  if score >= 80:
    integration_client.send_slack(f"Hot lead! Score={score}")


def on_invoice_uploaded(lead_id: str, file_path: str, parsed: dict):
  logging.info('[HOOK] Invoice uploaded: %s %s', lead_id, file_path)
  # Future: push totals to ERP or upload copy to Drive
  # integration_client.connect_tool('drive')
