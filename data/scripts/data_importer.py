"""
Employee Data Importer with Semantic Embeddings
===============================================
Imports monthly employee data from Excel file (employee_data.xlsx) and stores 
in PostgreSQL with semantic embeddings for advanced search capabilities.

Features:
- Reads Excel with proper header handling (skips first 6 rows)
- Generates semantic embeddings using Azure OpenAI or BGE model
- Stores in PostgreSQL with pgvector support
- UPSERT functionality for (EeID, Month) primary key
- Comprehensive error handling and logging
"""

import os
# Suppress TensorFlow warnings before importing other libraries
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import pandas as pd
import numpy as np
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Database imports
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Embedding imports
from sentence_transformers import SentenceTransformer
import openai

# Load environment variables
script_dir = Path(__file__).parent
data_dir = script_dir.parent
config_file = data_dir / 'config' / '.env'
load_dotenv(config_file)

# Configure logging with proper path handling
log_dir = data_dir / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'employee_data_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmployeeDataImporter:
    """Main class for importing employee data with embeddings"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.embedding_service = None
        self.db_engine = None
        self.connection = None
        
        # Database configuration
        self.db_config = {
            'host': config.get('database_host', os.getenv('DATABASE_HOST')),
            'port': config.get('database_port', int(os.getenv('DATABASE_PORT', 5432))),
            'database': config.get('database_name', os.getenv('DATABASE_NAME')),
            'user': config.get('database_user', os.getenv('DATABASE_USER')),
            'password': config.get('database_password', os.getenv('DATABASE_PASSWORD')),
        }
        
        # Embedding configuration
        self.embedding_type = config.get('embedding_type', 'opensource')  # 'azure' or 'opensource'
        self.embedding_dimension = 768 if self.embedding_type == 'opensource' else 1536
        
    def initialize_embedding_service(self):
        """Initialize the embedding service based on configuration"""
        try:
            if self.embedding_type == 'azure':
                logger.info("Initializing Azure OpenAI embedding service...")
                openai.api_type = "azure"
                openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
                openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')
                openai.api_version = "2023-12-01-preview"
                self.embedding_service = 'azure'
                logger.info("Azure OpenAI embedding service initialized")
                
            else:  # opensource
                logger.info("Initializing BGE embedding service...")
                # Suppress warnings
                os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
                os.environ['TOKENIZERS_PARALLELISM'] = 'false'
                
                self.embedding_service = SentenceTransformer('BAAI/bge-base-en')
                logger.info("BGE embedding service initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text"""
        try:
            if self.embedding_type == 'azure':
                response = openai.Embedding.create(
                    engine="text-embedding-3-small",
                    input=text
                )
                return response['data'][0]['embedding']
            else:
                return self.embedding_service.encode(text).tolist()
                
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {text[:100]}... Error: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently"""
        try:
            if self.embedding_type == 'azure':
                # Azure OpenAI batch processing
                embeddings = []
                batch_size = 100  # Azure limit
                
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    response = openai.Embedding.create(
                        engine="text-embedding-3-small",
                        input=batch
                    )
                    batch_embeddings = [data['embedding'] for data in response['data']]
                    embeddings.extend(batch_embeddings)
                
                return embeddings
            else:
                # BGE batch processing
                return [emb.tolist() for emb in self.embedding_service.encode(texts)]
                
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    def setup_database_connection(self):
        """Setup database connection and ensure pgvector extension"""
        try:
            # Create SQLAlchemy engine with proper URL encoding
            from urllib.parse import quote_plus
            password_encoded = quote_plus(self.db_config['password'])
            db_url = f"postgresql://{self.db_config['user']}:{password_encoded}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}?sslmode=require"
            
            self.db_engine = create_engine(db_url, echo=False)
            
            # Test connection and setup pgvector
            with self.db_engine.connect() as conn:
                # Enable pgvector extension
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                logger.info("Database connection established and pgvector enabled")
                
        except Exception as e:
            logger.error(f"Failed to setup database connection: {e}")
            raise
    
    def create_monthly_revenue_table(self):
        """Create the monthly_revenue_data table with all required columns"""
        try:
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS monthly_revenue_data (
                -- Original Excel columns
                month DATE,
                client_code VARCHAR(50),
                client VARCHAR(255),
                project_code VARCHAR(50),
                occurrence INTEGER,
                project VARCHAR(255),
                eeid VARCHAR(50),
                resource_name VARCHAR(255),
                geo VARCHAR(100),
                techgroup VARCHAR(100),
                cadre VARCHAR(100),
                salary_dollars DECIMAL(15,2),
                eetype VARCHAR(50),
                involve INTEGER,
                available_hrs DECIMAL(10,2),
                billing_type VARCHAR(100),
                rate_per_hr DECIMAL(10,2),
                billhrs DECIMAL(10,2),
                bill_dollars DECIMAL(15,2),
                cost DECIMAL(15,2),
                margin DECIMAL(15,2),
                margin_percent DECIMAL(8,4),
                onsiterev DECIMAL(15,2),
                offshorerev DECIMAL(15,2),
                fixed_amount DECIMAL(15,2),
                t_and_m DECIMAL(15,2),
                fte DECIMAL(10,2),
                subcon DECIMAL(15,2),
                offshore_hours DECIMAL(10,2),
                onsite_hours DECIMAL(10,2),
                techgroup_1 VARCHAR(100),
                
                -- Additional columns for embeddings
                serialized_row TEXT,
                embedding VECTOR({self.embedding_dimension}),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                
                -- Primary key
                PRIMARY KEY (eeid, month)
            );
            
            -- Create indexes for performance
            CREATE INDEX IF NOT EXISTS idx_monthly_revenue_embedding 
            ON monthly_revenue_data USING ivfflat (embedding vector_cosine_ops);
            
            CREATE INDEX IF NOT EXISTS idx_monthly_revenue_client 
            ON monthly_revenue_data (client_code, client);
            
            CREATE INDEX IF NOT EXISTS idx_monthly_revenue_project 
            ON monthly_revenue_data (project_code, project);
            
            CREATE INDEX IF NOT EXISTS idx_monthly_revenue_resource 
            ON monthly_revenue_data (eeid, resource_name);
            
            CREATE INDEX IF NOT EXISTS idx_monthly_revenue_date 
            ON monthly_revenue_data (month);
            """
            
            with self.db_engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
                logger.info("monthly_revenue_data table created/verified")
                
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            raise
    
    def load_excel_data(self, file_path: str) -> pd.DataFrame:
        """Load Excel data with proper header handling"""
        try:
            logger.info(f"Loading Excel file: {file_path}")
            
            # Read Excel file, skipping first 6 rows and using row 6 as headers
            df = pd.read_excel(file_path, header=6)
            
            logger.info(f"Loaded {len(df)} rows with {len(df.columns)} columns")
            logger.info(f"Columns: {list(df.columns)}")
            
            # Clean column names (replace spaces and special characters)
            df.columns = df.columns.str.replace(' ', '_').str.replace('/', '_per_').str.replace('%', '_percent').str.replace('$', '_dollars').str.replace('&', '_and_').str.lower()
            
            # Fix specific column mappings to match database schema
            df = df.rename(columns={
                'fixed': 'fixed_amount',
                'techgroup.1': 'techgroup_1'
            })
            
            # Handle data types
            if 'month' in df.columns:
                df['month'] = pd.to_datetime(df['month'], errors='coerce')
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Remove rows where critical fields are missing (month, eeid are required for primary key)
            initial_count = len(df)
            df = df.dropna(subset=['month', 'eeid'])
            filtered_count = len(df)
            
            if initial_count != filtered_count:
                logger.info(f"Filtered out {initial_count - filtered_count} rows with missing critical fields (month/eeid)")
            
            logger.info(f"After cleaning: {len(df)} rows with columns: {list(df.columns)}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load Excel file: {e}")
            raise
    
    def serialize_row(self, row: pd.Series) -> str:
        """Convert a data row into a descriptive sentence for embedding"""
        try:
            # Build descriptive sentence
            parts = []
            
            # Employee info
            if pd.notna(row.get('resource_name')):
                parts.append(f"Employee {row['resource_name']} (ID: {row.get('eeid', 'N/A')})")
            
            # Project and client info
            if pd.notna(row.get('project')) and pd.notna(row.get('client')):
                parts.append(f"worked on project {row['project']} for client {row['client']}")
            
            # Tech group and location
            if pd.notna(row.get('techgroup')):
                parts.append(f"in {row['techgroup']} team")
            
            if pd.notna(row.get('geo')):
                parts.append(f"located in {row['geo']}")
            
            # Time period
            if pd.notna(row.get('month')):
                month_str = row['month'].strftime('%B %Y') if hasattr(row['month'], 'strftime') else str(row['month'])
                parts.append(f"during {month_str}")
            
            # Financial metrics
            financial_parts = []
            if pd.notna(row.get('margin_percent')):
                financial_parts.append(f"margin was {row['margin_percent']:.2%}")
            
            if pd.notna(row.get('bill_dollars')):
                financial_parts.append(f"bill amount ${row['bill_dollars']:,.2f}")
            
            if pd.notna(row.get('billhrs')):
                financial_parts.append(f"billed {row['billhrs']} hours")
            
            if pd.notna(row.get('fte')):
                financial_parts.append(f"FTE {row['fte']}")
            
            if financial_parts:
                parts.append("with " + ", ".join(financial_parts))
            
            # Combine all parts
            if parts:
                sentence = "Represent this sentence for searching: " + " ".join(parts) + "."
            else:
                sentence = f"Represent this sentence for searching: Employee record for {row.get('eeid', 'unknown')} in {row.get('month', 'unknown period')}."
            
            return sentence
            
        except Exception as e:
            logger.error(f"Failed to serialize row: {e}")
            return f"Represent this sentence for searching: Employee record {row.get('eeid', 'unknown')}."
    
    def upsert_batch_data(self, df_batch: pd.DataFrame, batch_embeddings: List[List[float]]):
        """Insert or update batch data with embeddings using individual transactions"""
        success_count = 0
        error_count = 0
        
        for idx, (_, row) in enumerate(df_batch.iterrows()):
            # Use individual transaction for each row to avoid transaction rollback issues
            try:
                with self.db_engine.connect() as conn:
                    with conn.begin():  # Start transaction for this row
                        # Prepare data for insertion
                        embedding_json = json.dumps(batch_embeddings[idx])
                        serialized_text = self.serialize_row(row)
                        
                        # Convert pandas types to Python types with proper type handling
                        data = {}
                        
                        # Define integer columns that need special handling
                        integer_columns = {'occurrence', 'involve'}
                        
                        for col in df_batch.columns:
                            value = row[col]
                            if pd.isna(value):
                                data[col] = None
                            elif col in integer_columns:
                                # Convert string numbers like "1.0" to integers
                                try:
                                    data[col] = int(float(str(value)))
                                except (ValueError, TypeError):
                                    data[col] = None
                            elif isinstance(value, (np.integer, np.floating)):
                                data[col] = float(value) if isinstance(value, np.floating) else int(value)
                            elif isinstance(value, pd.Timestamp):
                                data[col] = value.date()
                            else:
                                data[col] = str(value)
                        
                        # UPSERT query using named parameters
                        upsert_sql = text("""
                        INSERT INTO monthly_revenue_data (
                            month, client_code, client, project_code, occurrence, project,
                            eeid, resource_name, geo, techgroup, cadre, salary_dollars,
                            eetype, involve, available_hrs, billing_type, rate_per_hr,
                            billhrs, bill_dollars, cost, margin, margin_percent,
                            onsiterev, offshorerev, fixed_amount, t_and_m, fte, subcon,
                            offshore_hours, onsite_hours, techgroup_1,
                            serialized_row, embedding, updated_at
                        ) VALUES (
                            :month, :client_code, :client, :project_code, :occurrence, :project,
                            :eeid, :resource_name, :geo, :techgroup, :cadre, :salary_dollars,
                            :eetype, :involve, :available_hrs, :billing_type, :rate_per_hr,
                            :billhrs, :bill_dollars, :cost, :margin, :margin_percent,
                            :onsiterev, :offshorerev, :fixed_amount, :t_and_m, :fte, :subcon,
                            :offshore_hours, :onsite_hours, :techgroup_1,
                            :serialized_row, CAST(:embedding AS vector), NOW()
                        )
                        ON CONFLICT (eeid, month) 
                        DO UPDATE SET
                            client_code = EXCLUDED.client_code,
                            client = EXCLUDED.client,
                            project_code = EXCLUDED.project_code,
                            occurrence = EXCLUDED.occurrence,
                            project = EXCLUDED.project,
                            resource_name = EXCLUDED.resource_name,
                            geo = EXCLUDED.geo,
                            techgroup = EXCLUDED.techgroup,
                            cadre = EXCLUDED.cadre,
                            salary_dollars = EXCLUDED.salary_dollars,
                            eetype = EXCLUDED.eetype,
                            involve = EXCLUDED.involve,
                            available_hrs = EXCLUDED.available_hrs,
                            billing_type = EXCLUDED.billing_type,
                            rate_per_hr = EXCLUDED.rate_per_hr,
                            billhrs = EXCLUDED.billhrs,
                            bill_dollars = EXCLUDED.bill_dollars,
                            cost = EXCLUDED.cost,
                            margin = EXCLUDED.margin,
                            margin_percent = EXCLUDED.margin_percent,
                            onsiterev = EXCLUDED.onsiterev,
                            offshorerev = EXCLUDED.offshorerev,
                            fixed_amount = EXCLUDED.fixed_amount,
                            t_and_m = EXCLUDED.t_and_m,
                            fte = EXCLUDED.fte,
                            subcon = EXCLUDED.subcon,
                            offshore_hours = EXCLUDED.offshore_hours,
                            onsite_hours = EXCLUDED.onsite_hours,
                            techgroup_1 = EXCLUDED.techgroup_1,
                            serialized_row = EXCLUDED.serialized_row,
                            embedding = EXCLUDED.embedding,
                            updated_at = NOW()
                        """)
                        
                        # Execute upsert
                        data.update({
                            'serialized_row': serialized_text,
                            'embedding': embedding_json
                        })
                        
                        conn.execute(upsert_sql, data)
                        success_count += 1
                        
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to upsert row {idx} (EeID: {row.get('eeid', 'unknown')}): {e}")
                continue
        
        logger.info(f"Batch completed: {success_count} successful, {error_count} errors")
        return success_count, error_count
    
    def process_excel_file(self, file_path: str, batch_size: int = 50):
        """Main processing function"""
        try:
            logger.info("=" * 70)
            logger.info("Employee Data Import with Semantic Embeddings")
            logger.info("=" * 70)
            
            # Initialize services
            self.initialize_embedding_service()
            self.setup_database_connection()
            self.create_monthly_revenue_table()
            
            # Load Excel data
            df = self.load_excel_data(file_path)
            
            # Process in batches
            total_rows = len(df)
            total_success = 0
            total_errors = 0
            
            logger.info(f"Processing {total_rows} rows in batches of {batch_size}")
            
            for i in range(0, total_rows, batch_size):
                batch_df = df.iloc[i:i + batch_size].copy()
                batch_num = (i // batch_size) + 1
                total_batches = (total_rows + batch_size - 1) // batch_size
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_df)} rows)")
                
                try:
                    # Generate serialized text for each row
                    serialized_texts = [self.serialize_row(row) for _, row in batch_df.iterrows()]
                    
                    # Generate embeddings in batch
                    batch_embeddings = self.generate_embeddings_batch(serialized_texts)
                    
                    # Upsert to database
                    success, errors = self.upsert_batch_data(batch_df, batch_embeddings)
                    
                    total_success += success
                    total_errors += errors
                    
                    logger.info(f"Batch {batch_num} completed: {success} successful, {errors} errors")
                    
                except Exception as e:
                    logger.error(f"Failed to process batch {batch_num}: {e}")
                    total_errors += len(batch_df)
                    continue
            
            # Final summary
            logger.info("=" * 70)
            logger.info("Import Summary:")
            logger.info(f"   • Total rows processed: {total_rows}")
            logger.info(f"   • Successful imports: {total_success}")
            logger.info(f"   • Errors: {total_errors}")
            logger.info(f"   • Success rate: {(total_success/total_rows)*100:.1f}%")
            
            # Test semantic search
            self.test_semantic_search()
            
            logger.info("Employee data import completed successfully!")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Failed to process Excel file: {e}")
            raise
    
    def test_semantic_search(self):
        """Test the semantic search functionality"""
        try:
            logger.info("\nTesting semantic search functionality...")
            
            # Test query
            query_text = "offshore developer working on mobile app project"
            query_embedding = self.generate_embedding(query_text)
            embedding_json = json.dumps(query_embedding)
            
            test_sql = """
            SELECT 
                eeid, resource_name, client, project, techgroup, geo,
                margin_percent, bill_dollars,
                embedding <-> CAST(:embedding AS vector) as similarity_distance
            FROM monthly_revenue_data 
            WHERE embedding IS NOT NULL
            ORDER BY similarity_distance
            LIMIT 5
            """
            
            with self.db_engine.connect() as conn:
                result = conn.execute(text(test_sql), {'embedding': embedding_json})
                rows = result.fetchall()
                
                logger.info(f"Top 5 matches for '{query_text}':")
                for row in rows:
                    logger.info(f"   • {row.resource_name} ({row.eeid}) - {row.client}/{row.project}")
                    logger.info(f"     {row.techgroup} in {row.geo} - Distance: {row.similarity_distance:.3f}")
                
                logger.info("Semantic search test completed successfully!")
                
        except Exception as e:
            logger.error(f"Semantic search test failed: {e}")

def main():
    """Main execution function"""
    
    # Configuration
    config = {
        'embedding_type': 'opensource',  # Change to 'azure' for Azure OpenAI
        'database_host': os.getenv('DATABASE_HOST', 'az-psdb-eastus.postgres.database.azure.com'),
        'database_port': int(os.getenv('DATABASE_PORT', 5432)),
        'database_name': os.getenv('DATABASE_NAME', 'finance_insights_db'),
        'database_user': os.getenv('DATABASE_USER', 'neethu'),
        'database_password': os.getenv('DATABASE_PASSWORD', 'Vijaya@7722'),
    }
    
    # File path using absolute path
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent
    excel_file = data_dir / 'source' / 'employee_data.xlsx'
    
    # Check if file exists
    if not excel_file.exists():
        logger.error(f"Excel file not found: {excel_file}")
        return
    
    # Create importer and process
    importer = EmployeeDataImporter(config)
    importer.process_excel_file(str(excel_file), batch_size=50)

if __name__ == "__main__":
    main()
