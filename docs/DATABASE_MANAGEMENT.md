# 🗄️ Database Management Guide

## 📋 **Available Scripts**

### **1. 🏗️ Setup Database (`setup_database.py`)**
Creates database tables, indexes, and views from scratch.

```bash
python setup_database.py
```

**What it does:**
- ✅ Creates `clients`, `projects`, and `revenue_data` tables
- ✅ Sets up indexes for performance optimization
- ✅ Creates analytics views (`client_revenue_summary`, `project_performance`, `monthly_revenue_trends`)
- ✅ Tests database connectivity and table structure

### **2. 📊 Import Data (`import_skeleton_data.py`)**
Imports data from `Skeleton.xlsx` or generates sample data.

```bash
python import_skeleton_data.py
```

**What it does:**
- ✅ Loads data from `Skeleton.xlsx` (if available)
- ✅ Generates realistic sample data if Excel file is missing
- ✅ Imports clients, projects, and revenue data
- ✅ Verifies data integrity after import

### **3. 🔧 Database Manager (`db_manager.py`)**
Interactive database management tool.

```bash
python db_manager.py
```

**Interactive Menu Options:**
- 🔍 Check database status
- 🏗️ Setup database (create tables)
- 📊 Import sample data
- 🔄 Full setup (create + import)
- 🗑️ Clear all data (keep structure)
- 💥 Drop all tables
- ❌ Exit

## 🚀 **Quick Start Workflow**

### **For First-Time Setup:**
```bash
# Option 1: Individual steps
python setup_database.py
python import_skeleton_data.py

# Option 2: Interactive manager
python db_manager.py
# Choose option 4 (Full setup)
```

### **For Data Refresh:**
```bash
python db_manager.py
# Choose option 5 (Clear data) then option 3 (Import data)
```

### **For Complete Reset:**
```bash
python db_manager.py
# Choose option 6 (Drop tables) then option 4 (Full setup)
```

## 📊 **Database Schema**

### **Tables Created:**
- **`clients`**: Client information (name, industry, location, contact)
- **`projects`**: Project details (name, type, dates, budget, status)
- **`revenue_data`**: Revenue transactions (amounts, dates, margins)

### **Analytics Views:**
- **`client_revenue_summary`**: Aggregated client performance metrics
- **`project_performance`**: Project profitability and status
- **`monthly_revenue_trends`**: Time-series revenue analysis

## ⚙️ **Configuration**

All scripts use the same database configuration from `.env`:

```env
DATABASE_HOST=az-psdb-eastus.postgres.database.azure.com
DATABASE_PORT=5432
DATABASE_NAME=finance_insights_db
DATABASE_USER=neethu
DATABASE_PASSWORD=Vijaya@7722
DATABASE_SSL=require
```

## 🔍 **Verification**

After running any script, you can verify the setup:

```bash
python db_manager.py
# Choose option 1 (Check database status)
```

This will show:
- ✅ Table counts and structure
- ✅ Data record counts
- ✅ Analytics view status
- ✅ Sample data preview

## 📝 **Sample Data Generated**

If `Skeleton.xlsx` is not found, scripts generate realistic sample data:

- **8 sample clients** across different industries
- **2-4 projects per client** with realistic budgets and timelines
- **6-12 revenue entries per project** spanning the past year
- **Realistic financial metrics** (margins, costs, profits)

## 🎯 **Integration with Main Application**

After database setup, launch the main application:

```bash
python launch_portal.py
```

The portal will connect to your configured database and display real-time analytics based on the imported data.

---

**🏦 Database Management for NextGen Revenue Insights Assistant**
