import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')


def send_followup(to_email: str, subject: str, content: str, from_email: str) -> dict:
    if not SENDGRID_API_KEY:
        raise RuntimeError('Missing SENDGRID_API_KEY')
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    message = Mail(from_email=from_email, to_emails=to_email, subject=subject, html_content=content)
    response = sg.send(message)
    return {"status_code": response.status_code}
