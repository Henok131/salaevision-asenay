import os
import requests

BASE = os.getenv('QA_BASE', 'http://localhost:8080')


def log(msg):
    os.makedirs('/logs', exist_ok=True)
    with open('/logs/system.log', 'a') as f:
        f.write(msg + '\n')


def test_health():
    r = requests.get(f"{BASE}/health")
    log(f"/health -> {r.status_code}")
    assert r.status_code == 200


def run_all():
    try:
        test_health()
        log('QA tests completed')
    except Exception as e:
        log(f"QA error: {e}")

if __name__ == '__main__':
    run_all()
