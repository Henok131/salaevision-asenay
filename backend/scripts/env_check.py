#!/usr/bin/env python3
import os
import sys

REQUIRED_KEYS = [
    'SUPABASE_URL',
    'SUPABASE_ANON_KEY',
    'OPENAI_API_KEY',
    'STRIPE_SECRET_KEY',
    'STRIPE_WEBHOOK_SECRET',
    'BACKEND_URL',
    'FRONTEND_URL',
    'JWT_SECRET_KEY',
]

missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
if missing:
    print('Missing required environment variables:', ', '.join(missing))
    sys.exit(1)
else:
    print('All required environment variables are set.')
    sys.exit(0)
