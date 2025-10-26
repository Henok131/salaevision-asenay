from slowapi import Limiter
from slowapi.util import get_remote_address


def auth_key(request):
  auth = request.headers.get('authorization', '')
  fp = auth[:32] if auth else None
  return fp or get_remote_address(request)


limiter = Limiter(key_func=get_remote_address)
