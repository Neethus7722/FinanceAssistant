"""
Database Setup Script for NextGen Revenue Insights Assistant
Creates database tables and initial schema setup
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from root directory
load_dotenv(Path(__file__).parent.parent / '.env')

# Database configuration
DATABASE_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'az-psdb-eastus.postgres.database.azure.com'),
    'port': int(os.getenv('DATABASE_PORT', 5432)),
    'database': os.getenv('DATABASE_NAME', 'finance_insights_db'),
    'user': os.getenv('DATABASE_USER', 'neethu'),
    'password': os.getenv('DATABASE_PASSWORD', 'Vijaya@7722'),
    'ssl': os.getenv('DATABASE_SSL', 'require')
}

# SQL schema creation scripts
CREATE_TABLES_SQL = """
-- Drop existing tables if they exist
DROP TABLE IF EXISTS revenue_data CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS clients CASCADE;

-- Create clients table
CREATE TABLE IF NOT EXISTS clients (
    client_id SERIAL PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    location VARCHAR(100),
    contact_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    client_id INTEGER REFERENCES clients(client_id),
    project_type VARCHAR(100),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'Active',
    budget DECIMAL(15,2),
    actual_cost DECIMAL(15,2),
    margin_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create revenue_data table
CREATE TABLE IF NOT EXISTS revenue_data (
    revenue_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    client_id INTEGER REFERENCES clients(client_id),
    revenue_date DATE NOT NULL,
    revenue_amount DECIMAL(15,2) NOT NULL,
    cost_amount DECIMAL(15,2),
    profit_amount DECIMAL(15,2),
    margin_percentage DECIMAL(5,2),
    quarter VARCHAR(10),
    year INTEGER,
    revenue_type VARCHAR(50) DEFAULT 'Project Revenue',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_revenue_data_date ON revenue_data(revenue_date);
CREATE INDEX IF NOT EXISTS idx_revenue_data_client ON revenue_data(client_id);
CREATE INDEX IF NOT EXISTS idx_revenue_data_project ON revenue_data(project_id);
CREATE INDEX IF NOT EXISTS idx_projects_client ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Create views for analytics
CREATE OR REPLACE VIEW client_revenue_summary AS
SELECT 
    c.client_id,
    c.client_name,
    c.industry,
    COUNT(DISTINCT p.project_id) as total_projects,
    COALESCE(SUM(rd.revenue_amount), 0) as total_revenue,
    COALESCE(SUM(rd.cost_amount), 0) as total_cost,
    COALESCE(SUM(rd.profit_amount), 0) as total_profit,
    COALESCE(AVG(rd.margin_percentage), 0) as avg_margin,
    MAX(rd.revenue_date) as last_revenue_date
FROM clients c
LEFT JOIN projects p ON c.client_id = p.client_id
LEFT JOIN revenue_data rd ON c.client_id = rd.client_id
GROUP BY c.client_id, c.client_name, c.industry;

CREATE OR REPLACE VIEW project_performance AS
SELECT 
    p.project_id,
    p.project_name,
    c.client_name,
    p.project_type,
    p.status,
    p.budget,
    p.actual_cost,
    p.margin_percentage as project_margin,
    COALESCE(SUM(rd.revenue_amount), 0) as total_revenue,
    COALESCE(SUM(rd.profit_amount), 0) as total_profit,
    COUNT(rd.revenue_id) as revenue_entries
FROM projects p
LEFT JOIN clients c ON p.client_id = c.client_id
LEFT JOIN revenue_data rd ON p.project_id = rd.project_id
GROUP BY p.project_id, p.project_name, c.client_name, p.project_type, 
         p.status, p.budget, p.actual_cost, p.margin_percentage;

CREATE OR REPLACE VIEW monthly_revenue_trends AS
SELECT 
    DATE_TRUNC('month', revenue_date) as month,
    SUM(revenue_amount) as monthly_revenue,
    SUM(cost_amount) as monthly_cost,
    SUM(profit_amount) as monthly_profit,
    AVG(margin_percentage) as avg_margin,
    COUNT(DISTINCT client_id) as active_clients,
    COUNT(DISTINCT project_id) as active_projects
FROM revenue_data
GROUP BY DATE_TRUNC('month', revenue_date)
ORDER BY month;
"""

async def create_database_connection():
    """Create async database connection"""
    try:
        conn = await asyncpg.connect(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            ssl=DATABASE_CONFIG['ssl']
        )
        print("✅ Successfully connected to Azure PostgreSQL database")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print(f"   Connection details: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")
        return None

async def setup_database():
    """Setup database tables and schema"""
    print("🏗️ Starting database setup...")
    
    conn = await create_database_connection()
    if not conn:
        return False
    
    try:
        # Execute schema creation
        print("📊 Creating tables and schema...")
        await conn.execute(CREATE_TABLES_SQL)
        print("✅ Tables created successfully")
        
        # Verify tables exist
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        print("📋 Created tables:")
        for table in tables:
            print(f"   • {table['table_name']}")
        
        # Verify views exist
        views = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        print("📊 Created views:")
        for view in views:
            print(f"   • {view['table_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    finally:
        await conn.close()
        print("🔌 Database connection closed")

async def test_database_setup():
    """Test database setup by running basic queries"""
    print("\n🧪 Testing database setup...")
    
    conn = await create_database_connection()
    if not conn:
        return False
    
    try:
        # Test basic table access
        test_queries = [
            ("clients", "SELECT COUNT(*) FROM clients"),
            ("projects", "SELECT COUNT(*) FROM projects"), 
            ("revenue_data", "SELECT COUNT(*) FROM revenue_data"),
            ("client_revenue_summary", "SELECT COUNT(*) FROM client_revenue_summary"),
            ("project_performance", "SELECT COUNT(*) FROM project_performance"),
            ("monthly_revenue_trends", "SELECT COUNT(*) FROM monthly_revenue_trends")
        ]
        
        for table_name, query in test_queries:
            try:
                result = await conn.fetchval(query)
                print(f"   ✅ {table_name}: {result} records")
            except Exception as e:
                print(f"   ❌ {table_name}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False
    finally:
        await conn.close()

def main():
    """Main setup function"""
    print("=" * 60)
    print("🏦 NextGen Revenue Insights - Database Setup")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / '.env'
    if not env_file.exists():
        print(f"⚠️  Warning: .env file not found at {env_file}")
        print("   Using default configuration.")
    else:
        print(f"✅ Using configuration from {env_file}")
    
    print(f"📊 Database: {DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}")
    
    # Run database setup
    setup_result = asyncio.run(setup_database())
    
    if setup_result:
        # Test setup
        asyncio.run(test_database_setup())
        
        print("\n" + "=" * 60)
        print("🎯 Database setup completed successfully!")
        print("📝 Next step: Run 'python import_skeleton_data.py' to load sample data")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Database setup failed!")
        print("📝 Please check your database configuration and try again")
        print("=" * 60)

if __name__ == "__main__":
    main()
