SCHEMA_SQL = """
-- Leads
CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  company TEXT,
  title TEXT,
  source TEXT,
  score INT,
  reason TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Contacts (emails sent)
CREATE TABLE IF NOT EXISTS contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  message TEXT,
  status TEXT,
  sent_at TIMESTAMP DEFAULT NOW()
);

-- Usage events
CREATE TABLE IF NOT EXISTS usage_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  tokens_used INT NOT NULL,
  event_type TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Users profile
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY,
  role TEXT DEFAULT 'viewer',
  email TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Logs
CREATE TABLE IF NOT EXISTS logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message TEXT,
  level TEXT,
  timestamp TIMESTAMP DEFAULT NOW()
);
"""
