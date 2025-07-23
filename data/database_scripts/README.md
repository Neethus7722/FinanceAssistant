# Database Management Scripts

This folder contains standalone database management tools for the NextGen Revenue Insights Assistant project.

## 📁 Scripts Overview

### 🔧 setup_database.py
**Purpose**: Initialize and set up the PostgreSQL database schema
- Creates database tables (clients, projects, revenue_data)
- Sets up indexes for optimal performance
- Creates analytics views for reporting
- Tests database connectivity and functionality

**Usage**:
```bash
python data/database_scripts/setup_database.py
```

**Features**:
- ✅ Database connection testing
- 📊 Complete schema creation
- 🎯 Performance indexes
- 📈 Analytics views (client_revenue_summary, project_performance, monthly_revenue_trends)
- 🔍 Validation and testing

---

### 📊 import_skeleton_data.py
**Purpose**: Import data from Skeleton.xlsx and generate sample data
- Loads client data from Excel file (if available)
- Generates realistic project and revenue data
- Populates the database with comprehensive sample data

**Usage**:
```bash
python data/database_scripts/import_skeleton_data.py
```

**Features**:
- 📋 Excel file processing (data/Skeleton.xlsx)
- 👥 Client data import/generation
- 🎯 Project data generation (2-5 projects per client)
- 💰 Revenue data generation (8-15 entries per project)
- 🔍 Data verification and analytics summary
- 📊 Sample data includes 10 clients, 25-50 projects, 200-750 revenue records

**Generated Data Types**:
- **Clients**: Technology, Manufacturing, Healthcare, Finance, Retail, etc.
- **Projects**: Web Development, Mobile Apps, Cloud Migration, AI Implementation, etc.
- **Revenue**: Project milestones, consulting fees, support revenue, license fees

---

### 🗄️ db_manager.py
**Purpose**: Interactive database management and analytics tool
- Menu-driven interface for database operations
- Data viewing, analytics, and maintenance capabilities
- Backup and data management functions

**Usage**:
```bash
python data/database_scripts/db_manager.py
```

**Features**:
- 📊 **Table Information**: View database structure and record counts
- 📋 **Sample Data**: Display records from any table
- 📈 **Analytics Summary**: Top clients, project performance, revenue trends
- 🔍 **Custom Queries**: Execute SELECT queries safely
- 💾 **Data Backup**: Export tables to CSV files
- 🗑️ **Data Cleanup**: Clear all data (with safety confirmations)
- 🔄 **Connection Management**: Reconnect and manage database connections

**Menu Options**:
1. Show Table Information
2. Display Sample Data
3. Analytics Summary
4. Execute Custom Query
5. Backup Data
6. Clear All Data
7. Reconnect to Database
8. Exit

---

## 🚀 Quick Start Guide

### 1. First Time Setup
```bash
# 1. Set up the database schema
python data/database_scripts/setup_database.py

# 2. Import sample data
python data/database_scripts/import_skeleton_data.py

# 3. Launch the application
python launch_portal.py
```

### 2. Database Management
```bash
# Interactive database management
python data/database_scripts/db_manager.py
```

### 3. Data Reset/Refresh
```bash
# Clear and reload data
python data/database_scripts/db_manager.py
# Choose option 6 to clear data, then run:
python data/database_scripts/import_skeleton_data.py
```

---

## 🔧 Configuration

### Environment Variables
Ensure these variables are set in your `.env` file:

```env
DATABASE_HOST=az-psdb-eastus.postgres.database.azure.com
DATABASE_PORT=5432
DATABASE_NAME=finance_insights_db
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_SSL=require
```

### Dependencies
These scripts require the following Python packages:
- `asyncpg` - PostgreSQL async driver
- `pandas` - Data manipulation and analysis
- `python-dotenv` - Environment variable management
- `tabulate` - Table formatting for console output
- `openpyxl` - Excel file reading

Install with:
```bash
pip install asyncpg pandas python-dotenv tabulate openpyxl
```

---

## 📊 Database Schema

### Tables
- **clients**: Client information (name, industry, location, contact)
- **projects**: Project details (name, type, dates, budget, costs)
- **revenue_data**: Revenue records (amounts, dates, margins, types)

### Views
- **client_revenue_summary**: Aggregated revenue data by client
- **project_performance**: Project profitability and performance metrics
- **monthly_revenue_trends**: Monthly revenue and profit trends

### Sample Data
- **10 clients** across different industries
- **25-50 projects** with realistic budgets and timelines
- **200-750 revenue records** spanning 18+ months
- **Comprehensive analytics** ready for dashboard consumption

---

## 🔍 Troubleshooting

### Common Issues

**Database Connection Errors**:
- Verify `.env` file configuration
- Check Azure PostgreSQL firewall settings
- Ensure network connectivity

**Import Data Issues**:
- Check if `Skeleton.xlsx` exists in project root
- Verify file permissions and format
- Review column names in Excel file

**Performance Issues**:
- Run `setup_database.py` to ensure indexes are created
- Consider data volume when generating large datasets

### Support Commands
```bash
# Test database connection
python data/database_scripts/setup_database.py

# View current data status
python data/database_scripts/db_manager.py
# Choose option 1 for table information

# Backup current data
python data/database_scripts/db_manager.py
# Choose option 5 for backup
```

---

## 📁 File Structure
```
data/
├── database_scripts/
│   ├── README.md              # This file
│   ├── setup_database.py      # Database schema setup
│   ├── import_skeleton_data.py # Data import and generation
│   └── db_manager.py          # Interactive management tool
└── backups/                   # Generated backup files (CSV exports)
```

---

## 🎯 Best Practices

1. **Always run setup_database.py first** for new environments
2. **Backup data before major changes** using db_manager.py
3. **Use db_manager.py for data exploration** instead of direct SQL access
4. **Import fresh data regularly** to keep analytics current
5. **Monitor database performance** through the analytics views

---

*These tools are designed to be standalone and can be run independently of the main application for database maintenance and development purposes.*
