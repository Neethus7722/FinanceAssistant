"""
Interactive Database Manager for NextGen Revenue Insights
Provides menu-driven database management capabilities
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from tabulate import tabulate
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

class DatabaseManager:
    def __init__(self):
        self.conn = None
        
    async def connect(self):
        """Establish database connection"""
        try:
            self.conn = await asyncpg.connect(
                host=DATABASE_CONFIG['host'],
                port=DATABASE_CONFIG['port'],
                database=DATABASE_CONFIG['database'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                ssl=DATABASE_CONFIG['ssl']
            )
            print("✅ Connected to Azure PostgreSQL database")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
    
    async def disconnect(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            print("🔌 Database connection closed")
    
    async def display_table_info(self):
        """Display information about database tables"""
        try:
            print("\n📊 Database Tables Information")
            print("=" * 50)
            
            # Get table information
            query = """
            SELECT 
                table_name,
                (SELECT COUNT(*) FROM information_schema.columns 
                 WHERE table_name = t.table_name AND table_schema = 'public') as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
            
            tables = await self.conn.fetch(query)
            
            table_data = []
            for table in tables:
                table_name = table['table_name']
                # Get row count
                row_count = await self.conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                table_data.append([table_name, table['column_count'], row_count])
            
            print(tabulate(table_data, headers=['Table Name', 'Columns', 'Rows'], tablefmt='grid'))
            
            # Display views
            view_query = """
            SELECT table_name as view_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
            
            views = await self.conn.fetch(view_query)
            if views:
                print("\n📈 Available Views:")
                for view in views:
                    print(f"   • {view['view_name']}")
            
        except Exception as e:
            print(f"❌ Error displaying table info: {e}")
    
    async def display_sample_data(self, table_name, limit=10):
        """Display sample data from a table"""
        try:
            print(f"\n📋 Sample data from '{table_name}' (top {limit} records):")
            print("=" * 60)
            
            # Get column information
            col_query = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = $1 AND table_schema = 'public'
            ORDER BY ordinal_position
            """
            columns = await self.conn.fetch(col_query, table_name)
            
            if not columns:
                print(f"❌ Table '{table_name}' not found")
                return
            
            # Get sample data
            data = await self.conn.fetch(f"SELECT * FROM {table_name} LIMIT $1", limit)
            
            if not data:
                print(f"📭 No data found in table '{table_name}'")
                return
            
            # Convert to pandas for better display
            df = pd.DataFrame([dict(row) for row in data])
            print(df.to_string(index=False))
            
        except Exception as e:
            print(f"❌ Error displaying sample data: {e}")
    
    async def display_analytics_summary(self):
        """Display analytics summary using views"""
        try:
            print("\n📊 Analytics Summary")
            print("=" * 50)
            
            # Client Revenue Summary
            print("\n💰 Top 5 Clients by Revenue:")
            client_revenue = await self.conn.fetch("""
                SELECT client_name, total_revenue, total_profit, avg_margin
                FROM client_revenue_summary
                ORDER BY total_revenue DESC
                LIMIT 5
            """)
            
            if client_revenue:
                client_data = []
                for row in client_revenue:
                    client_data.append([
                        row['client_name'], 
                        f"${row['total_revenue']:,.2f}",
                        f"${row['total_profit']:,.2f}",
                        f"{row['avg_margin']:.1f}%"
                    ])
                print(tabulate(client_data, headers=['Client', 'Revenue', 'Profit', 'Margin'], tablefmt='grid'))
            
            # Project Performance
            print("\n🎯 Project Performance Summary:")
            project_performance = await self.conn.fetch("""
                SELECT project_name, client_name, status, budget, actual_cost, margin_percentage
                FROM project_performance
                ORDER BY margin_percentage DESC
                LIMIT 5
            """)
            
            if project_performance:
                project_data = []
                for row in project_performance:
                    project_data.append([
                        row['project_name'][:30] + "...",
                        row['client_name'][:20],
                        row['status'],
                        f"${row['budget']:,.0f}",
                        f"${row['actual_cost']:,.0f}",
                        f"{row['margin_percentage']:.1f}%"
                    ])
                print(tabulate(project_data, headers=['Project', 'Client', 'Status', 'Budget', 'Cost', 'Margin'], tablefmt='grid'))
            
            # Monthly Trends (Last 6 months)
            print("\n📈 Monthly Revenue Trends (Last 6 months):")
            monthly_trends = await self.conn.fetch("""
                SELECT year, month, total_revenue, total_profit, avg_margin
                FROM monthly_revenue_trends
                ORDER BY year DESC, month DESC
                LIMIT 6
            """)
            
            if monthly_trends:
                trend_data = []
                for row in monthly_trends:
                    month_year = f"{row['year']}-{row['month']:02d}"
                    trend_data.append([
                        month_year,
                        f"${row['total_revenue']:,.0f}",
                        f"${row['total_profit']:,.0f}",
                        f"{row['avg_margin']:.1f}%"
                    ])
                print(tabulate(trend_data, headers=['Month', 'Revenue', 'Profit', 'Margin'], tablefmt='grid'))
            
            # Overall Statistics
            print("\n📋 Overall Database Statistics:")
            stats = await self.conn.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM clients) as total_clients,
                    (SELECT COUNT(*) FROM projects) as total_projects,
                    (SELECT COUNT(*) FROM revenue_data) as total_revenue_records,
                    (SELECT SUM(revenue_amount) FROM revenue_data) as total_revenue,
                    (SELECT SUM(profit_amount) FROM revenue_data) as total_profit,
                    (SELECT AVG(margin_percentage) FROM revenue_data) as avg_margin
            """)
            
            if stats:
                stats_data = [
                    ["Total Clients", stats['total_clients']],
                    ["Total Projects", stats['total_projects']],
                    ["Revenue Records", stats['total_revenue_records']],
                    ["Total Revenue", f"${stats['total_revenue']:,.2f}"],
                    ["Total Profit", f"${stats['total_profit']:,.2f}"],
                    ["Average Margin", f"{stats['avg_margin']:.2f}%"]
                ]
                print(tabulate(stats_data, headers=['Metric', 'Value'], tablefmt='grid'))
            
        except Exception as e:
            print(f"❌ Error displaying analytics: {e}")
    
    async def execute_custom_query(self):
        """Allow user to execute custom SQL queries"""
        print("\n🔍 Custom Query Executor")
        print("=" * 40)
        print("⚠️  Use SELECT queries only for safety")
        print("💡 Type 'exit' to return to main menu")
        
        while True:
            query = input("\nSQL> ").strip()
            
            if query.lower() == 'exit':
                break
            
            if not query:
                continue
            
            # Safety check - only allow SELECT statements
            if not query.upper().startswith('SELECT'):
                print("❌ Only SELECT queries are allowed for safety")
                continue
            
            try:
                result = await self.conn.fetch(query)
                
                if result:
                    # Convert to pandas for better display
                    df = pd.DataFrame([dict(row) for row in result])
                    print(f"\n📊 Query Results ({len(result)} rows):")
                    print(df.to_string(index=False))
                else:
                    print("📭 No results returned")
                    
            except Exception as e:
                print(f"❌ Query error: {e}")
    
    async def backup_data(self):
        """Create data backup (export to CSV)"""
        try:
            print("\n💾 Creating Data Backup...")
            
            # Create backup directory
            backup_dir = Path(__file__).parent.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export each table
            tables = ['clients', 'projects', 'revenue_data']
            
            for table in tables:
                print(f"   📄 Exporting {table}...")
                data = await self.conn.fetch(f"SELECT * FROM {table}")
                
                if data:
                    df = pd.DataFrame([dict(row) for row in data])
                    filename = backup_dir / f"{table}_{timestamp}.csv"
                    df.to_csv(filename, index=False)
                    print(f"      ✅ Saved to {filename}")
                else:
                    print(f"      ⚠️  No data in {table}")
            
            print(f"\n✅ Backup completed in: {backup_dir}")
            
        except Exception as e:
            print(f"❌ Backup error: {e}")
    
    async def clear_all_data(self):
        """Clear all data from tables (with confirmation)"""
        print("\n⚠️  DANGER: Clear All Data")
        print("=" * 30)
        print("This will delete ALL data from the database!")
        
        confirm1 = input("Type 'DELETE ALL DATA' to confirm: ").strip()
        if confirm1 != "DELETE ALL DATA":
            print("❌ Operation cancelled")
            return
        
        confirm2 = input("Are you absolutely sure? (yes/no): ").strip().lower()
        if confirm2 != "yes":
            print("❌ Operation cancelled")
            return
        
        try:
            print("\n🗑️ Clearing all data...")
            
            # Delete in reverse dependency order
            await self.conn.execute("DELETE FROM revenue_data")
            await self.conn.execute("DELETE FROM projects")
            await self.conn.execute("DELETE FROM clients")
            
            # Reset sequences
            await self.conn.execute("ALTER SEQUENCE clients_client_id_seq RESTART WITH 1")
            await self.conn.execute("ALTER SEQUENCE projects_project_id_seq RESTART WITH 1")
            await self.conn.execute("ALTER SEQUENCE revenue_data_revenue_id_seq RESTART WITH 1")
            
            print("✅ All data cleared successfully")
            print("💡 Run import_skeleton_data.py to reload sample data")
            
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
    
    async def show_menu(self):
        """Display main menu"""
        print("\n" + "=" * 60)
        print("🗄️  NextGen Revenue Insights - Database Manager")
        print("=" * 60)
        print("1. 📊 Show Table Information")
        print("2. 📋 Display Sample Data")
        print("3. 📈 Analytics Summary")
        print("4. 🔍 Execute Custom Query")
        print("5. 💾 Backup Data")
        print("6. 🗑️  Clear All Data")
        print("7. 🔄 Reconnect to Database")
        print("8. 🚪 Exit")
        print("=" * 60)
    
    async def run(self):
        """Main interactive loop"""
        print("🚀 Starting Database Manager...")
        
        # Connect to database
        if not await self.connect():
            return
        
        try:
            while True:
                await self.show_menu()
                choice = input("Select option (1-8): ").strip()
                
                if choice == '1':
                    await self.display_table_info()
                
                elif choice == '2':
                    table_name = input("Enter table name (clients/projects/revenue_data): ").strip()
                    limit = input("Enter number of records to show (default 10): ").strip()
                    limit = int(limit) if limit.isdigit() else 10
                    await self.display_sample_data(table_name, limit)
                
                elif choice == '3':
                    await self.display_analytics_summary()
                
                elif choice == '4':
                    await self.execute_custom_query()
                
                elif choice == '5':
                    await self.backup_data()
                
                elif choice == '6':
                    await self.clear_all_data()
                
                elif choice == '7':
                    await self.disconnect()
                    if not await self.connect():
                        break
                
                elif choice == '8':
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid choice. Please select 1-8.")
                
                input("\n⏸️  Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupted by user")
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        
        finally:
            await self.disconnect()

async def main():
    """Main function"""
    db_manager = DatabaseManager()
    await db_manager.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
