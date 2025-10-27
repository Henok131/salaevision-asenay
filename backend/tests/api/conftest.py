import sys
import types
import pytest
from datetime import timedelta

# --------- Stubs for heavy third-party libraries ---------

# Basic stubs for common heavy imports to prevent ImportError during router imports
for name in [
    'numpy', 'PIL', 'PIL.Image', 'PIL.ImageStat', 'stripe'
]:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

# Minimal numpy stub to satisfy imports and a few calls in routers
if isinstance(sys.modules.get('numpy'), types.ModuleType) and not hasattr(sys.modules['numpy'], 'random'):
    _np = sys.modules['numpy']
    class _Random:
        @staticmethod
        def normal(mu=0.0, sigma=1.0, size=None):
            size = size or 1
            # deterministic simple sequence
            return [float(mu) for _ in range(size)]
        @staticmethod
        def exponential(lam=1.0, size=None):
            size = size or 1
            return [0.1 for _ in range(size)]
        @staticmethod
        def random():
            return 0.5
        @staticmethod
        def seed(_=0):
            return None
    def linspace(start, stop, num):
        if num <= 1:
            return [float(start)]
        step = (stop - start) / (num - 1)
        return [start + i * step for i in range(num)]
    _np.random = _Random()
    _np.linspace = linspace

# Minimal pandas stub sufficient for router logic
if 'pandas' not in sys.modules:
    pandas_mod = types.ModuleType('pandas')

    class _Columns(list):
        def tolist(self):
            return list(self)

    class _DF:
        def __init__(self, data):
            self._data = data  # dict of column -> list
            # normalize lengths
            lens = [len(v) for v in data.values()] or [0]
            self._rows = max(lens)
        def __len__(self):
            return self._rows
        @property
        def shape(self):
            return (self._rows, len(self._data))
        @property
        def columns(self):
            return _Columns(list(self._data.keys()))
        @property
        def empty(self):
            return self._rows == 0
        def head(self, n=5):
            # return a shallow copy limited to first n rows
            truncated = {k: v[:n] for k, v in self._data.items()}
            return _DF(truncated)
        def to_dict(self, *_, **__):
            return {k: list(v) for k, v in self._data.items()}
        def __getitem__(self, key):
            # Return a minimal Series-like wrapper
            data = self._data[key]
            class _Series(list):
                def __init__(self, items):
                    super().__init__(items)
                def min(self):
                    return builtins.min(self) if len(self) > 0 else None
                def max(self):
                    return builtins.max(self) if len(self) > 0 else None
            import builtins
            return _Series(list(data))
        def select_dtypes(self, include=None):
            include = include or []
            cols = []
            if 'number' in include:
                for k, v in self._data.items():
                    try:
                        float(v[0])
                        cols.append(k)
                    except Exception:
                        pass
            if 'datetime' in include:
                # very naive: detect columns named 'date'
                for k in self._data.keys():
                    if 'date' in k:
                        cols.append(k)
            class _R:
                def __init__(self, cols):
                    self.columns = _Columns(cols)
            return _R(cols)

    def _read_csv(file_like):
        text = file_like.read()
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
        if not lines:
            return _DF({})
        headers = [h.strip() for h in lines[0].split(',')]
        cols = {h: [] for h in headers}
        for ln in lines[1:]:
            parts = [p.strip() for p in ln.split(',')]
            for i, h in enumerate(headers):
                if i < len(parts):
                    val = parts[i]
                    # try to coerce numbers
                    try:
                        cols[h].append(float(val))
                    except Exception:
                        cols[h].append(val)
                else:
                    cols[h].append('')
        return _DF(cols)

    pandas_mod.read_csv = _read_csv
    pandas_mod.DataFrame = _DF
    sys.modules['pandas'] = pandas_mod

# Stub prophet.Prophet with a lightweight implementation
if 'prophet' not in sys.modules:
    prophet_mod = types.ModuleType('prophet')

    class StubProphet:
        def __init__(self, **_kwargs):
            self._df = None
        def fit(self, df):
            self._df = df.copy()
            return self
        def make_future_dataframe(self, periods):
            # Use a minimal inline date generator to avoid pandas dependency
            from datetime import datetime, timedelta as _td
            if self._df is None or 'ds' not in getattr(self._df, '__dict__', {}):
                start = datetime(2024, 1, 1)
                base = [start + _td(days=i) for i in range(periods)]
            else:
                last = max(self._df['ds'])
                base = [last + _td(days=i+1) for i in range(periods)]
            return {'ds': base}
        def predict(self, future):
            # Return a minimal dict-like structure that code expects access to
            n = len(future['ds'])
            yhat = [1000 + (10 * i) / max(n - 1, 1) for i in range(n)]
            return {
                'ds': future['ds'],
                'yhat': yhat,
                'yhat_lower': [v * 0.9 for v in yhat],
                'yhat_upper': [v * 1.1 for v in yhat],
                'trend': [i / max(n - 1, 1) for i in range(n)],
            }

    prophet_mod.Prophet = StubProphet
    sys.modules['prophet'] = prophet_mod

# Stub openai.ChatCompletion.create to return deterministic JSON content
if 'openai' not in sys.modules:
    openai_mod = types.ModuleType('openai')

    class _Choice:
        def __init__(self, content: str):
            self.message = types.SimpleNamespace(content=content)

    class ChatCompletion:
        @staticmethod
        def create(**_kwargs):
            content = (
                '{"summary":"AI summary","key_factors":["Factor A"],'
                '"recommendations":["Do X"],"visual_insight":"visual",'
                '"text_insight":"text"}'
            )
            return types.SimpleNamespace(choices=[_Choice(content)])

    openai_mod.ChatCompletion = ChatCompletion
    # allow setting openai.api_key at import time
    openai_mod.api_key = None
    sys.modules['openai'] = openai_mod

# Ensure stripe stub exposes Webhook to be monkeypatched in tests
import types as _types
stripe_mod = sys.modules.get('stripe')
if isinstance(stripe_mod, _types.ModuleType) and not hasattr(stripe_mod, 'Webhook'):
    class _Webhook:
        @staticmethod
        def construct_event(payload, sig, secret):
            return { 'type': 'noop', 'data': { 'object': {} } }
    stripe_mod.Webhook = _Webhook


# --------- Reusable Supabase mock factory ---------

def make_supabase_client(select_map=None, insert_map=None, update_map=None, auth_sign_in_user=None, auth_sign_up_user=None):
    select_map = select_map or {}
    insert_map = insert_map or {}
    update_map = update_map or {}

    class _Exec:
        def __init__(self, data):
            self._data = data
        @property
        def data(self):
            return self._data
        def execute(self):
            return self

    class _Table:
        def __init__(self, name: str):
            self._name = name
            self._op = None
            self._latest_obj = None
        def select(self, *_a, **_k):
            self._op = 'select'
            return self
        def insert(self, obj):
            self._op = 'insert'
            self._latest_obj = obj
            return self
        def update(self, obj):
            self._op = 'update'
            self._latest_obj = obj
            return self
        def eq(self, *_a, **_k):
            return self
        def execute(self):
            if self._op == 'select':
                data = select_map.get(self._name, [])
            elif self._op == 'insert':
                data = insert_map.get(self._name, [self._latest_obj])
            elif self._op == 'update':
                data = update_map.get(self._name, [self._latest_obj or {}])
            else:
                data = []
            return _Exec(data)
        @property
        def data(self):
            # Convenience to mimic some chained access in tests
            return self.execute().data

    class _Auth:
        def sign_in_with_password(self, _creds):
            return types.SimpleNamespace(user=auth_sign_in_user)
        def sign_up(self, _creds):
            return types.SimpleNamespace(user=auth_sign_up_user)

    class SupabaseClient:
        def __init__(self):
            self.auth = _Auth()
        def table(self, name: str):
            return _Table(name)

    return SupabaseClient()


@pytest.fixture
def supabase_factory():
    return make_supabase_client


@pytest.fixture
def valid_user():
    return {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "plan": "free",
    }


@pytest.fixture
def auth_header():
    return {"Authorization": "Bearer test"}
