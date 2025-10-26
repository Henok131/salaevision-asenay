from slowapi import Limiter
from slowapi.util import get_remote_address


def auth_key(request):
    # Approximate per-user key: use auth header prefix, fallback to IP
    auth = request.headers.get("authorization", "")
    token_fingerprint = auth[:32] if auth else None
    return token_fingerprint or get_remote_address(request)


limiter = Limiter(key_func=get_remote_address)
