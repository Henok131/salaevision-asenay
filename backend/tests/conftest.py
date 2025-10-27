import os
import sys
import types
import json
import base64
import random
import math
import pytest

# Ensure backend package-relative imports (e.g., 'routers', 'services') resolve
_HERE = os.path.dirname(__file__)
_BACKEND_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

# Ensure required env vars for app startup
os.environ.setdefault("JWT_SECRET_KEY", "testsecret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("CORS_ALLOW_ORIGINS", "http://localhost:3000")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "anon_test_key")
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_123")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test")

# Stub openai
fake_openai = types.SimpleNamespace()

class _FakeChatCompletion:
    @staticmethod
    def create(model: str, messages, max_tokens: int, temperature: float):
        class _Choice:
            def __init__(self):
                self.message = types.SimpleNamespace(content="Test analysis output with positive sentiment")
        return types.SimpleNamespace(choices=[_Choice()])

fake_openai.ChatCompletion = _FakeChatCompletion
sys.modules.setdefault("openai", fake_openai)

# Stub supabase module so import in services.supabase_client succeeds
fake_supabase_mod = types.ModuleType("supabase")
class _SupabaseClient:  # placeholder for type annotation in code
    pass
def _fake_create_client(url, key):
    return _SupabaseClient()
fake_supabase_mod.create_client = _fake_create_client
fake_supabase_mod.Client = _SupabaseClient
sys.modules.setdefault("supabase", fake_supabase_mod)

# Stub supabase client behavior used in code
class _FakeAuth:
    def sign_in_with_password(self, payload):
        email = payload.get("email", "user@example.com")
        return types.SimpleNamespace(user=types.SimpleNamespace(id="user_1", email=email, created_at="2023-01-01"))

    def sign_up(self, payload):
        email = payload.get("email", "user@example.com")
        return types.SimpleNamespace(user=types.SimpleNamespace(id="user_2", email=email, created_at="2023-01-01"))

class _FakeQuery:
    def __init__(self, table_name):
        self.table_name = table_name
        self._op = None
        self._filters = []
        self._payload = None

    def select(self, *_args, **_kwargs):
        self._op = "select"
        return self

    def eq(self, column, value):
        self._filters.append((column, value))
        return self

    def update(self, payload):
        self._op = "update"
        self._payload = payload
        return self

    def insert(self, payload):
        self._op = "insert"
        self._payload = payload
        return self

    def execute(self):
        # Return shapes compatible with code expectations
        if self._op == "select":
            # Ensure existence checks pass
            return types.SimpleNamespace(data=[{"id": "row_1"}])
        if self._op == "insert":
            return types.SimpleNamespace(data=[{"id": "new_id"}])
        if self._op == "update":
            return types.SimpleNamespace(data=[{"updated": True}])
        return types.SimpleNamespace(data=[])

class _FakeSupabase:
    def __init__(self):
        self.auth = _FakeAuth()

    def table(self, name):
        return _FakeQuery(name)

# Monkeypatch get_supabase_client to return fake
@pytest.fixture(autouse=True)
def _stub_supabase(monkeypatch):
    from backend import services
    def _get_fake_client():
        return _FakeSupabase()
    # Patch the service function
    import backend.services.supabase_client as sc
    monkeypatch.setattr(sc, "get_supabase_client", _get_fake_client)
    yield

# Stub stripe
fake_stripe = types.ModuleType("stripe")
class _FakeWebhook:
    @staticmethod
    def construct_event(payload, sig_header, secret):
        return {"type": "invoice.payment_succeeded", "data": {"object": {"customer": "cus_test"}}}
class _FakeError(Exception):
    pass
fake_stripe.Webhook = _FakeWebhook
fake_stripe.error = types.SimpleNamespace(SignatureVerificationError=_FakeError)
class _FakeCheckoutSession:
    @staticmethod
    def create(**kwargs):
        return types.SimpleNamespace(url="https://checkout.example/ok", id="cs_test_123")
fake_stripe.checkout = types.SimpleNamespace(Session=_FakeCheckoutSession)
class _FakePrice:
    @staticmethod
    def list(**kwargs):
        price = types.SimpleNamespace(
            id="price_test",
            unit_amount=1000,
            currency="usd",
            recurring=types.SimpleNamespace(interval="month"),
            product="prod_test",
        )
        return types.SimpleNamespace(data=[price])
fake_stripe.Price = _FakePrice
sys.modules.setdefault("stripe", fake_stripe)

# Stub prophet
fake_prophet = types.ModuleType("prophet")
class _FakeProphet:
    def __init__(self, *args, **kwargs):
        pass
    def fit(self, df):
        self.df = df
        return self
    def make_future_dataframe(self, periods: int):
        import pandas as pd
        last_date = pd.to_datetime("2024-01-01")
        return pd.DataFrame({"ds": pd.date_range(start=last_date, periods=periods)})
    def predict(self, future_df):
        import numpy as np
        df = future_df.copy()
        n = len(df)
        df["yhat"] = np.linspace(100, 100 + n - 1, n)
        df["yhat_lower"] = df["yhat"] - 10
        df["yhat_upper"] = df["yhat"] + 10
        df["trend"] = np.linspace(0, 1, n)
        df["weekly"] = np.sin(np.linspace(0, 2 * np.pi, n))
        df["yearly"] = np.cos(np.linspace(0, 2 * np.pi, n))
        return df
fake_prophet.Prophet = _FakeProphet
sys.modules.setdefault("prophet", fake_prophet)

# Stub numpy
fake_numpy = types.ModuleType("numpy")

def _linspace(start, stop, num):
    if num <= 1:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]

class _FakeRandomNS:
    @staticmethod
    def normal(loc=0.0, scale=1.0, size=1):
        if isinstance(size, int):
            return [loc for _ in range(size)]
        return loc

fake_numpy.linspace = _linspace
fake_numpy.random = _FakeRandomNS()
sys.modules.setdefault("numpy", fake_numpy)

# Stub pandas with minimal functionality used by app
fake_pandas = types.ModuleType("pandas")

class _FakeSeries(list):
    @property
    def dt(self):
        # return object with strftime that returns the same values for simplicity
        class _DT:
            def __init__(self, data):
                self._data = data
            def strftime(self, _fmt):
                return [str(v) for v in self._data]
        return _DT(self)

class _FakeDF:
    def __init__(self, rows):
        # rows: list of dicts
        self._rows = rows
        self._columns = list(rows[0].keys()) if rows else []
    @property
    def empty(self):
        return len(self._rows) == 0
    @property
    def columns(self):
        return self._columns
    def __len__(self):
        return len(self._rows)
    def select_dtypes(self, include=None):
        cols = []
        for c in self._columns:
            if c.lower() == "date":
                continue
            cols.append(c)
        class _Obj:
            def __init__(self, cols):
                self.columns = cols
        return _Obj(cols)
    def head(self, n=5):
        return _FakeDF(self._rows[:n])
    def to_dict(self):
        out = {}
        for c in self._columns:
            out[c] = [r[c] for r in self._rows[:5]]
        return out
    def __getitem__(self, key):
        return _FakeSeries([r.get(key) for r in self._rows])

def _read_csv(buffer):
    text = buffer.read()
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    headers = [h.strip() for h in lines[0].split(",")]
    rows = []
    for line in lines[1:]:
        parts = [p.strip() for p in line.split(",")]
        row = {headers[i]: parts[i] for i in range(min(len(headers), len(parts)))}
        rows.append(row)
    return _FakeDF(rows)

def _date_range(start, end=None, freq=None):
    # minimal: return list of iso-date strings; not heavily used in tests due to prophet stub
    return _FakeSeries([start, end] if end else [start])

fake_pandas.read_csv = _read_csv
fake_pandas.DataFrame = _FakeDF
fake_pandas.date_range = _date_range
sys.modules.setdefault("pandas", fake_pandas)

# Stub passlib CryptContext
fake_passlib = types.ModuleType("passlib")
fake_context_mod = types.ModuleType("passlib.context")
class _CryptContext:
    def __init__(self, *args, **kwargs):
        pass
    def verify(self, plain, hashed):
        return True
    def hash(self, password):
        return password
fake_context_mod.CryptContext = _CryptContext
sys.modules.setdefault("passlib", fake_passlib)
sys.modules.setdefault("passlib.context", fake_context_mod)

# Stub jose.jwt
fake_jose = types.ModuleType("jose")
fake_jwt_mod = types.ModuleType("jose.jwt")
class JWTError(Exception):
    pass
def _jwt_encode(payload, secret, algorithm=None):
    data = json.dumps(payload).encode("utf-8")
    return base64.urlsafe_b64encode(data).decode("ascii")
def _jwt_decode(token, secret, algorithms=None):
    try:
        data = base64.urlsafe_b64decode(token.encode("ascii"))
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        raise JWTError(str(e))
fake_jwt_mod.encode = _jwt_encode
fake_jwt_mod.decode = _jwt_decode
fake_jose.JWTError = JWTError
sys.modules.setdefault("jose", fake_jose)
sys.modules.setdefault("jose.jwt", fake_jwt_mod)
