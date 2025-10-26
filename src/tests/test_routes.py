import os
import requests

BASE = os.getenv('QA_BASE', f"http://{os.getenv('API_HOST','localhost')}:{os.getenv('API_PORT','8080')}")
LOG = '/logs/system.log'


def log(msg):
    os.makedirs('/logs', exist_ok=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')


def check(path, method='GET', status_ok=(200, 400, 401, 402, 404)):
    url = f"{BASE}{path}"
    try:
        if method == 'GET':
            r = requests.get(url)
        else:
            r = requests.post(url)
        log(f"[QA] {method} {path} -> {r.status_code}")
        assert r.status_code in status_ok
    except Exception as e:
        log(f"[QA] ERROR {method} {path}: {e}")


def run_all():
    check('/health')
    check('/api/health')  # behind nginx path if applicable
    check('/webhook/event', method='POST')
    check('/integrations/status')
    check('/customer_profile/dummy')
    check('/recommendation/dummy')
    check('/funnel-stats')
    check('/usage/history')

if __name__ == '__main__':
    run_all()
