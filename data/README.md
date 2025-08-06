# Employee Data Import System

This directory contains the standardized data import system for processing employee revenue data with semantic embeddings.

## 📁 Directory Structure

```
data/
├── config/                     # Configuration files
│   └── .env.template          # Environment variables template
├── scripts/                   # Core processing scripts
│   ├── data_importer.py       # Main data import with embeddings
│   └── database_cleanup.py    # Database reset utility
├── source/                    # Source data files
│   └── employee_data.xlsx     # Employee revenue data (Excel format)
├── logs/                      # Log files directory
│   └── employee_data_import.log
├── run_import.py              # Main execution script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy and configure environment variables
cp config/.env.template config/.env
# Edit config/.env with your database and embedding settings
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Import
```bash
# Clean import (recommended for first run)
python run_import.py --clean

# Regular import (data already exists)
python run_import.py
```

## ⚙️ Configuration

Edit `config/.env` with your settings:

```env
# Database Configuration (PostgreSQL with pgvector)
DATABASE_HOST=your-postgres-host
DATABASE_PORT=5432
DATABASE_NAME=your-database
DATABASE_USER=your-username
DATABASE_PASSWORD=your-password

# Embedding Model Selection
EMBEDDING_MODEL=bge  # Options: 'bge' or 'azure'

# Azure OpenAI (if using EMBEDDING_MODEL=azure)
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_DEPLOYMENT_NAME=text-embedding-ada-002
```

## 📊 Data Processing Features

- **Excel Processing**: Handles employee revenue data from Excel files
- **Semantic Embeddings**: Generates 768-dimensional BGE embeddings for semantic search
- **PostgreSQL Storage**: Uses pgvector extension for efficient vector operations
- **UPSERT Operations**: Prevents duplicates using (EeID, Month) composite key
- **Batch Processing**: Processes data in configurable batches for memory efficiency
- **Error Handling**: Individual row transaction handling prevents cascade failures
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 🔧 Individual Script Usage

### Data Import Only
```bash
cd scripts
python data_importer.py
```

### Database Cleanup Only
```bash
cd scripts
python database_cleanup.py
```

## 📈 Performance Metrics

- **Success Rate**: Achieves 100% import success with proper data validation
- **Embedding Generation**: ~7-8 seconds per 50-record batch using BGE model
- **Database Operations**: Individual transactions prevent cascade failures
- **Semantic Search**: Cosine similarity search with 0.63-0.64 relevance scores

## 🎯 Use Cases

1. **Initial Data Load**: Complete employee revenue data import
2. **Incremental Updates**: Monthly data updates with UPSERT handling
3. **Semantic Search**: Find employees by skills, projects, or work descriptions
4. **Data Analytics**: Revenue analysis with embedded semantic context

## 🔍 Troubleshooting

- **Import Errors**: Check logs in `logs/employee_data_import.log`
- **Database Issues**: Ensure pgvector extension is installed
- **Environment Setup**: Verify all variables in `config/.env`
- **File Paths**: Ensure `source/employee_data.xlsx` exists

## 📝 Notes

- Supports both Azure OpenAI and open-source BGE embeddings
- Filters out empty rows automatically during processing
- Uses PostgreSQL with SSL requirement for security
- Optimized for Azure PostgreSQL Flexible Server
