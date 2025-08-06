#!/usr/bin/env python3
"""
Database Cleanup Script
======================

This script clears all data from the database tables and resets the schema.
Use this before running fresh imports.

Author: Finance Assistant Team
Date: August 2025
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import psycopg2
from urllib.parse import quote_plus

# Load environment variables from config directory
script_dir = Path(__file__).parent
data_dir = script_dir.parent
config_file = data_dir / 'config' / '.env'
load_dotenv(config_file)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseCleaner:
    def __init__(self, config: dict):
        """Initialize database cleaner"""
        self.config = config
        self.db_engine = None
        
    def connect_database(self):
        """Establish database connection"""
        try:
            # Create SQLAlchemy engine with proper URL encoding
            db_url = (
                f"postgresql://{quote_plus(self.config['database_user'])}:"
                f"{quote_plus(self.config['database_password'])}@"
                f"{self.config['database_host']}:"
                f"{self.config['database_port']}/"
                f"{self.config['database_name']}?sslmode=require"
            )
            
            self.db_engine = create_engine(db_url)
            
            # Test connection
            with self.db_engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"Connected to PostgreSQL: {version}")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def cleanup_tables(self):
        """Drop and recreate all revenue-related tables and views"""
        try:
            with self.db_engine.connect() as conn:
                logger.info("Starting database cleanup...")
                
                # First, get all revenue-related tables
                result = conn.execute(text("""
                    SELECT table_name, table_type
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND (table_name LIKE '%revenue%' OR table_name LIKE '%client%')
                    ORDER BY table_name
                """))
                
                existing_objects = result.fetchall()
                logger.info(f"Found existing objects to drop: {[(obj[0], obj[1]) for obj in existing_objects]}")
                
                # Drop all existing revenue-related tables and views
                for obj_name, obj_type in existing_objects:
                    try:
                        if obj_type == 'VIEW':
                            drop_query = f"DROP VIEW IF EXISTS {obj_name} CASCADE;"
                        else:
                            drop_query = f"DROP TABLE IF EXISTS {obj_name} CASCADE;"
                        
                        conn.execute(text(drop_query))
                        logger.info(f"Dropped {obj_type.lower()}: {obj_name}")
                    except Exception as e:
                        logger.warning(f"Failed to drop {obj_type.lower()} {obj_name}: {e}")
                        continue
                
                # Drop specific indexes that might exist
                drop_indexes = [
                    "DROP INDEX IF EXISTS idx_monthly_revenue_embedding;",
                    "DROP INDEX IF EXISTS idx_monthly_revenue_client;",
                    "DROP INDEX IF EXISTS idx_monthly_revenue_project;",
                    "DROP INDEX IF EXISTS idx_monthly_revenue_resource;",
                    "DROP INDEX IF EXISTS idx_monthly_revenue_date;",
                    "DROP INDEX IF EXISTS idx_revenue_data_embedding;",
                    "DROP INDEX IF EXISTS idx_client_revenue_date;",
                    "DROP INDEX IF EXISTS idx_monthly_trends_date;"
                ]
                
                for index_query in drop_indexes:
                    try:
                        conn.execute(text(index_query))
                        logger.info(f"Executed: {index_query}")
                    except Exception as e:
                        logger.warning(f"Index cleanup warning: {e}")
                        continue
                
                conn.commit()
                logger.info("All revenue tables/views and indexes dropped successfully!")
                
        except Exception as e:
            logger.error(f"Failed to cleanup tables: {e}")
            raise
    
    def reset_pgvector(self):
        """Reset pgvector extension"""
        try:
            with self.db_engine.connect() as conn:
                logger.info("Resetting pgvector extension...")
                
                # Drop and recreate pgvector extension
                conn.execute(text("DROP EXTENSION IF EXISTS vector CASCADE;"))
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                
                conn.commit()
                logger.info("pgvector extension reset successfully!")
                
        except Exception as e:
            logger.error(f"Failed to reset pgvector: {e}")
            raise
    
    def verify_cleanup(self):
        """Verify that cleanup was successful"""
        try:
            with self.db_engine.connect() as conn:
                # Check if any revenue-related tables exist
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND (table_name LIKE '%revenue%' OR table_name LIKE '%client%')
                """))
                
                tables = result.fetchall()
                if tables:
                    logger.warning(f"Some revenue tables still exist: {[t[0] for t in tables]}")
                    return False
                else:
                    logger.info("✅ Database cleanup verified - no revenue tables found")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to verify cleanup: {e}")
            return False
    
    def full_cleanup(self):
        """Perform complete database cleanup"""
        try:
            logger.info("=" * 70)
            logger.info("Database Cleanup Process")
            logger.info("=" * 70)
            
            # Connect to database
            if not self.connect_database():
                raise Exception("Could not connect to database")
            
            # Cleanup tables
            self.cleanup_tables()
            
            # Reset pgvector
            self.reset_pgvector()
            
            # Verify cleanup
            if self.verify_cleanup():
                logger.info("✅ Database cleanup completed successfully!")
                logger.info("Ready for fresh data import.")
            else:
                logger.warning("⚠️ Cleanup verification failed")
                
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Database cleanup failed: {e}")
            raise

def main():
    """Main execution function"""
    
    # Configuration
    config = {
        'database_host': os.getenv('DATABASE_HOST', 'az-psdb-eastus.postgres.database.azure.com'),
        'database_port': int(os.getenv('DATABASE_PORT', 5432)),
        'database_name': os.getenv('DATABASE_NAME', 'finance_insights_db'),
        'database_user': os.getenv('DATABASE_USER', 'neethu'),
        'database_password': os.getenv('DATABASE_PASSWORD', 'Vijaya@7722'),
    }
    
    # Create cleaner and run cleanup
    cleaner = DatabaseCleaner(config)
    cleaner.full_cleanup()

if __name__ == "__main__":
    main()
