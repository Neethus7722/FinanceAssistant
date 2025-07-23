"""
Import Skeleton Data Script for NextGen Revenue Insights Assistant
Imports data from Skeleton.xlsx into PostgreSQL database
"""

import asyncio
import asyncpg
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
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
        return None

def load_skeleton_data():
    """Load data from Skeleton.xlsx"""
    # Look for Skeleton.xlsx in data directory
    excel_file = Path(__file__).parent / "Skeleton.xlsx"
    
    if not excel_file.exists():
        print(f"📝 Skeleton.xlsx file not found at {excel_file}")
        print("   Will generate sample data instead...")
        return None
    
    try:
        print(f"📊 Loading data from {excel_file}...")
        
        # Load all sheets
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        print("📋 Available sheets:")
        for sheet_name in excel_data.keys():
            print(f"   • {sheet_name}: {len(excel_data[sheet_name])} rows")
        
        return excel_data
    
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return None

def process_clients_data(excel_data):
    """Process and prepare clients data"""
    try:
        # Try different possible sheet names for clients
        clients_sheet = None
        possible_names = ['Clients', 'clients', 'Client', 'client', 'Customer', 'customers']
        
        if excel_data:
            for name in possible_names:
                if name in excel_data:
                    clients_sheet = excel_data[name]
                    print(f"📊 Found client data in sheet: {name}")
                    break
        
        if clients_sheet is None:
            # Create sample clients data
            print("📝 Creating sample clients data...")
            clients_data = [
                ('TechCorp Solutions', 'Technology', 'New York', 'contact@techcorp.com'),
                ('Global Manufacturing Inc', 'Manufacturing', 'Chicago', 'info@globalmanuf.com'),
                ('Healthcare Partners', 'Healthcare', 'Los Angeles', 'admin@healthpartners.com'),
                ('Financial Services Ltd', 'Finance', 'Boston', 'contact@finservices.com'),
                ('Retail Chain Corp', 'Retail', 'Seattle', 'hello@retailchain.com'),
                ('Energy Solutions LLC', 'Energy', 'Houston', 'info@energysolutions.com'),
                ('Education Institute', 'Education', 'Philadelphia', 'admin@eduinstitute.com'),
                ('Media & Entertainment', 'Media', 'Miami', 'contact@mediaent.com'),
                ('Construction Group', 'Construction', 'Denver', 'info@constructiongroup.com'),
                ('Consulting Partners', 'Consulting', 'San Francisco', 'hello@consultingpartners.com')
            ]
            return clients_data
        else:
            # Process existing clients data
            processed_clients = []
            for _, row in clients_sheet.iterrows():
                # Adapt column names based on what's available
                client_name = row.get('Client Name', row.get('client_name', row.get('Name', f'Client {len(processed_clients) + 1}')))
                industry = row.get('Industry', row.get('industry', 'Technology'))
                location = row.get('Location', row.get('location', 'New York'))
                email = row.get('Email', row.get('email', f'contact@{client_name.lower().replace(" ", "")}.com'))
                
                processed_clients.append((str(client_name), str(industry), str(location), str(email)))
            
            print(f"✅ Processed {len(processed_clients)} clients from Excel")
            return processed_clients
    
    except Exception as e:
        print(f"⚠️ Error processing clients data: {e}")
        # Return default sample data
        return [
            ('TechCorp Solutions', 'Technology', 'New York', 'contact@techcorp.com'),
            ('Global Manufacturing Inc', 'Manufacturing', 'Chicago', 'info@globalmanuf.com'),
            ('Healthcare Partners', 'Healthcare', 'Los Angeles', 'admin@healthpartners.com')
        ]

def generate_projects_data(num_clients):
    """Generate sample projects data"""
    project_types = ['Web Development', 'Mobile App', 'Data Analytics', 'Cloud Migration', 
                    'System Integration', 'Consulting', 'Training', 'Support', 'AI Implementation',
                    'Digital Transformation', 'Security Audit', 'Infrastructure Upgrade']
    
    projects = []
    project_id = 1
    
    for client_id in range(1, num_clients + 1):
        # Generate 2-5 projects per client
        num_projects = random.randint(2, 5)
        
        for _ in range(num_projects):
            project_name = f"Project {project_id} - {random.choice(project_types)}"
            project_type = random.choice(project_types)
            
            # Random dates within last 2 years
            start_date = datetime.now() - timedelta(days=random.randint(30, 730))
            end_date = start_date + timedelta(days=random.randint(30, 365))
            
            budget = random.randint(50000, 800000)
            actual_cost = budget * random.uniform(0.65, 1.15)
            margin = ((budget - actual_cost) / budget) * 100
            
            status = random.choice(['Active', 'Completed', 'On Hold', 'In Progress'])
            
            projects.append((
                project_name, client_id, project_type, start_date.date(), 
                end_date.date(), status, budget, actual_cost, margin
            ))
            project_id += 1
    
    return projects

def generate_revenue_data(num_projects, num_clients):
    """Generate sample revenue data"""
    revenue_data = []
    revenue_id = 1
    
    for project_id in range(1, num_projects + 1):
        # Calculate which client this project belongs to
        client_id = ((project_id - 1) // 4) + 1  # Distribute projects across clients
        if client_id > num_clients:
            client_id = num_clients
        
        # Generate 8-15 revenue entries per project
        num_entries = random.randint(8, 15)
        
        for i in range(num_entries):
            # Revenue dates over the past 18 months
            revenue_date = datetime.now() - timedelta(days=random.randint(1, 540))
            
            # Varying revenue amounts based on project phase
            base_amount = random.randint(15000, 75000)
            revenue_amount = base_amount
            cost_amount = revenue_amount * random.uniform(0.55, 0.85)
            profit_amount = revenue_amount - cost_amount
            margin_percentage = (profit_amount / revenue_amount) * 100
            
            quarter = f"Q{((revenue_date.month - 1) // 3) + 1}"
            year = revenue_date.year
            
            revenue_types = ['Project Revenue', 'Milestone Payment', 'Consulting Fee', 
                           'Support Revenue', 'License Fee']
            revenue_type = random.choice(revenue_types)
            
            revenue_data.append((
                project_id, client_id, revenue_date.date(), revenue_amount,
                cost_amount, profit_amount, margin_percentage, quarter, year, revenue_type
            ))
            revenue_id += 1
    
    return revenue_data

async def import_clients(conn, clients_data):
    """Import clients data"""
    print("👥 Importing clients data...")
    
    try:
        # Clear existing data in reverse order
        await conn.execute("DELETE FROM revenue_data")
        await conn.execute("DELETE FROM projects") 
        await conn.execute("DELETE FROM clients")
        
        # Reset sequences
        await conn.execute("ALTER SEQUENCE clients_client_id_seq RESTART WITH 1")
        
        # Insert clients
        insert_query = """
            INSERT INTO clients (client_name, industry, location, contact_email)
            VALUES ($1, $2, $3, $4)
        """
        
        for client_data in clients_data:
            await conn.execute(insert_query, *client_data)
        
        # Get count
        count = await conn.fetchval("SELECT COUNT(*) FROM clients")
        print(f"   ✅ Imported {count} clients")
        
        return count
    
    except Exception as e:
        print(f"❌ Error importing clients: {e}")
        return 0

async def import_projects(conn, projects_data):
    """Import projects data"""
    print("🎯 Importing projects data...")
    
    try:
        # Reset sequence
        await conn.execute("ALTER SEQUENCE projects_project_id_seq RESTART WITH 1")
        
        # Insert projects
        insert_query = """
            INSERT INTO projects (project_name, client_id, project_type, start_date, 
                                end_date, status, budget, actual_cost, margin_percentage)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        
        for project_data in projects_data:
            await conn.execute(insert_query, *project_data)
        
        # Get count
        count = await conn.fetchval("SELECT COUNT(*) FROM projects")
        print(f"   ✅ Imported {count} projects")
        
        return count
    
    except Exception as e:
        print(f"❌ Error importing projects: {e}")
        return 0

async def import_revenue_data(conn, revenue_data):
    """Import revenue data"""
    print("💰 Importing revenue data...")
    
    try:
        # Reset sequence
        await conn.execute("ALTER SEQUENCE revenue_data_revenue_id_seq RESTART WITH 1")
        
        # Insert revenue data in batches for better performance
        insert_query = """
            INSERT INTO revenue_data (project_id, client_id, revenue_date, revenue_amount,
                                    cost_amount, profit_amount, margin_percentage, quarter, 
                                    year, revenue_type)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        
        batch_size = 100
        for i in range(0, len(revenue_data), batch_size):
            batch = revenue_data[i:i + batch_size]
            for revenue_entry in batch:
                await conn.execute(insert_query, *revenue_entry)
        
        # Get count
        count = await conn.fetchval("SELECT COUNT(*) FROM revenue_data")
        print(f"   ✅ Imported {count} revenue records")
        
        return count
    
    except Exception as e:
        print(f"❌ Error importing revenue data: {e}")
        return 0

async def verify_import(conn):
    """Verify imported data"""
    print("\n🔍 Verifying imported data...")
    
    try:
        # Check record counts
        clients_count = await conn.fetchval("SELECT COUNT(*) FROM clients")
        projects_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
        revenue_count = await conn.fetchval("SELECT COUNT(*) FROM revenue_data")
        
        print(f"📊 Data Summary:")
        print(f"   • Clients: {clients_count}")
        print(f"   • Projects: {projects_count}")
        print(f"   • Revenue Records: {revenue_count}")
        
        # Test views
        view_tests = [
            ("client_revenue_summary", "SELECT COUNT(*) FROM client_revenue_summary"),
            ("project_performance", "SELECT COUNT(*) FROM project_performance"),
            ("monthly_revenue_trends", "SELECT COUNT(*) FROM monthly_revenue_trends")
        ]
        
        print(f"\n📈 Analytics Views:")
        for view_name, query in view_tests:
            try:
                count = await conn.fetchval(query)
                print(f"   • {view_name}: {count} records")
            except Exception as e:
                print(f"   ❌ {view_name}: Error - {e}")
        
        # Sample data preview
        print(f"\n📋 Sample Client Data:")
        clients = await conn.fetch("SELECT client_name, industry FROM clients LIMIT 5")
        for client in clients:
            print(f"   • {client['client_name']} ({client['industry']})")
        
        # Revenue summary
        total_revenue = await conn.fetchval("SELECT SUM(revenue_amount) FROM revenue_data")
        total_profit = await conn.fetchval("SELECT SUM(profit_amount) FROM revenue_data")
        avg_margin = await conn.fetchval("SELECT AVG(margin_percentage) FROM revenue_data")
        
        print(f"\n💰 Financial Summary:")
        print(f"   • Total Revenue: ${total_revenue:,.2f}")
        print(f"   • Total Profit: ${total_profit:,.2f}")
        print(f"   • Average Margin: {avg_margin:.2f}%")
        
        return True
    
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        return False

async def main():
    """Main import function"""
    print("=" * 60)
    print("📊 NextGen Revenue Insights - Data Import")
    print("=" * 60)
    
    # Load Excel data
    excel_data = load_skeleton_data()
    
    # Connect to database
    conn = await create_database_connection()
    if not conn:
        return
    
    try:
        # Process and import data
        print("\n🔄 Processing data...")
        
        # 1. Import clients
        clients_data = process_clients_data(excel_data)
        clients_count = await import_clients(conn, clients_data)
        
        if clients_count == 0:
            print("❌ Failed to import clients. Aborting.")
            return
        
        # 2. Generate and import projects
        projects_data = generate_projects_data(clients_count)
        projects_count = await import_projects(conn, projects_data)
        
        if projects_count == 0:
            print("❌ Failed to import projects. Aborting.")
            return
        
        # 3. Generate and import revenue data
        revenue_data = generate_revenue_data(projects_count, clients_count)
        revenue_count = await import_revenue_data(conn, revenue_data)
        
        # 4. Verify import
        await verify_import(conn)
        
        print("\n" + "=" * 60)
        print("🎉 Data import completed successfully!")
        print("🚀 Ready to launch: python launch_portal.py")
        print("=" * 60)
    
    except Exception as e:
        print(f"❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await conn.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    asyncio.run(main())
