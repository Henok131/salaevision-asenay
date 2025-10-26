from typing import Dict
import re

# Very naive parser; replace with a robust extraction later

def extract_invoice_fields(text: str) -> Dict:
    date = None
    m = re.search(r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", text)
    if m:
        date = m.group(1)
    amount = None
    m2 = re.search(r"\$?\s?(\d+[\.,]\d{2})", text)
    if m2:
        amount = m2.group(1)
    company = None
    m3 = re.search(r"Company:\s*(.*)", text)
    if m3:
        company = m3.group(1)[:120]
    items = []
    return {
        'date': date,
        'amount': amount,
        'company_name': company,
        'items': items,
    }
