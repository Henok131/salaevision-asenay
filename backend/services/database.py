import os
from supabase import create_client
from services.supabase_client import get_supabase_client
from sqlalchemy import create_engine, text

async def init_db():
    """
    Initialize database tables and setup
    """
    try:
        # Attempt to run migrations using DATABASE_URL if provided
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            engine = create_engine(database_url)
            with engine.begin() as conn:
                conn.execute(text(create_tables_sql()))
            print("Database migrations applied via SQLAlchemy")
        else:
            # Fallback: no direct DB connection available (e.g., Supabase). Log SQL for manual application.
            print("DATABASE_URL not set; skipping automatic migrations. Apply the following SQL in Supabase:")
            print(create_tables_sql())
        
        print("Database initialization completed")
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise e

def create_tables_sql():
    """
    SQL for creating required tables
    This would typically be run as Supabase migrations
    """
    return """
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        plan VARCHAR(50) DEFAULT 'free',
        tokens_remaining INTEGER DEFAULT 200,
        weekly_digest_enabled BOOLEAN DEFAULT true,
        weekly_digest_mode VARCHAR(20) DEFAULT 'both', -- 'text' | 'voice' | 'both'
        stripe_customer_id VARCHAR(255),
        subscription_id VARCHAR(255),
        subscription_status VARCHAR(50),
        payment_status VARCHAR(50),
        last_payment_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

    -- Ensure new columns exist for older deployments
    ALTER TABLE users ADD COLUMN IF NOT EXISTS tokens_remaining INTEGER DEFAULT 200;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS weekly_digest_enabled BOOLEAN DEFAULT true;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS weekly_digest_mode VARCHAR(20) DEFAULT 'both';

    -- Sales data table
    CREATE TABLE IF NOT EXISTS sales_data (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        filename VARCHAR(255) NOT NULL,
        file_size INTEGER,
        upload_date TIMESTAMP DEFAULT NOW(),
        data_points INTEGER,
        columns JSONB
    );

    -- Analysis results table
    CREATE TABLE IF NOT EXISTS analysis_results (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        sales_data_id UUID REFERENCES sales_data(id) ON DELETE CASCADE,
        summary TEXT,
        key_factors JSONB,
        recommendations JSONB,
        data_points INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- Forecast results table
    CREATE TABLE IF NOT EXISTS forecast_results (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
        forecast_days INTEGER,
        forecast_data JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- Explanation results table
    CREATE TABLE IF NOT EXISTS explanation_results (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
        feature_importance JSONB,
        shap_values JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_sales_data_user_id ON sales_data(user_id);
    CREATE INDEX IF NOT EXISTS idx_analysis_results_user_id ON analysis_results(user_id);
    CREATE INDEX IF NOT EXISTS idx_forecast_results_user_id ON forecast_results(user_id);
    CREATE INDEX IF NOT EXISTS idx_explanation_results_user_id ON explanation_results(user_id);
    """

