# Azure & External Services Deployment Guide
## NextGen Revenue Insights Assistant - Complete Infrastructure

This document outlines all Azure and external services required for your NextGen Revenue Insights Assistant to function in production with PostgreSQL-based session management and advanced forecasting capabilities.

## 🏗️ **REQUIRED AZURE SERVICES**

### 1. **Azure OpenAI Service** ⭐ CRITICAL
```
Purpose: Core AI/LLM capabilities for all agents
Service: Azure OpenAI
Model: GPT-4o
Estimated Cost: $50-200/month (depending on usage)
```

**Setup Steps:**
1. Create Azure OpenAI resource in Azure Portal
2. Deploy GPT-4o model
3. Get API key and endpoint
4. Update `.env` variables:
   ```
   OPENAI_API_KEY=your-azure-openai-api-key
   OPENAI_API_BASE=https://your-resource.openai.azure.com/
   OPENAI_API_DEPLOYMENT=gpt-4o
   ```

---

### 2. **Azure Active Directory (Microsoft Entra ID)** ⭐ CRITICAL
```
Purpose: User authentication and authorization
Service: Azure Active Directory
Features: SSO, RBAC, Multi-tenant support
Estimated Cost: Free tier available, Premium $6/user/month
```

**Setup Steps:**
1. Create App Registration in Azure AD
2. Configure authentication flows
3. Set redirect URIs for Streamlit
4. Update `.env` variables:
   ```
   AZURE_AD_CLIENT_ID=your-azure-ad-app-client-id
   AZURE_AD_TENANT_ID=your-azure-ad-tenant-id
   AZURE_AD_CLIENT_SECRET=your-azure-ad-client-secret
   ```

---

### 4. **Azure Database for PostgreSQL** ⭐ CRITICAL
```
Purpose: Complete database solution for session management, chat history, user preferences, financial data storage
Service: Azure Database for PostgreSQL Flexible Server
Configuration: Standard_B2s (2 vCores, 4GB RAM) minimum
Features: JSONB storage, full-text search, advanced analytics, session management
Estimated Cost: $50-150/month
```

**Setup Steps:**
1. Create PostgreSQL Flexible Server
2. Configure firewall rules for secure access
3. Create database: `finance_insights_db`
4. Enable required extensions: `pg_trgm` for search, `uuid-ossp` for UUIDs
5. Update `.env` variables:
   ```
   DATABASE_URL=postgresql+asyncpg://username:password@server.postgres.database.azure.com:5432/finance_insights_db
   ```

**Database Schema:**
- `chat_sessions`: Session management with JSONB metadata
- `chat_messages`: Message history with rich content support
- `user_session_preferences`: Personalization settings
- `session_analytics`: Performance and usage tracking
- Financial data tables for forecasting and analytics

**Benefits of PostgreSQL-Only Approach:**
- ✅ Unified data storage (no need for separate Cosmos DB)
- ✅ Better SQL support for complex queries
- ✅ JSONB for flexible document storage
- ✅ Superior performance for relational data
- ✅ Built-in full-text search capabilities
- ✅ Cost efficiency through consolidation
- ✅ Simplified architecture and maintenance

---

### 4. **Microsoft Dynamics 365** 🏢 ENTERPRISE
```
Purpose: CRM data integration, pipeline analysis
Service: Dynamics 365 Sales/Customer Service
API: Web API v9.2
Estimated Cost: $95-210/user/month
```

**Setup Steps:**
1. Set up Dynamics 365 instance
2. Create service principal for API access
3. Configure OAuth2 authentication
4. Update `.env` variables:
   ```
   DYNAMICS_CLIENT_ID=your-dynamics-client-id
   DYNAMICS_RESOURCE_URL=https://yourorg.crm.dynamics.com/
   ```

---

### 5. **Azure Blob Storage** 📁 RECOMMENDED
```
Purpose: File uploads, Excel data ingestion, backups
Service: Azure Storage Account (Blob Storage)
Tier: Hot tier for active data
Estimated Cost: $20-50/month
```

**Setup Steps:**
1. Create Storage Account
2. Create container: `financial-data`
3. Configure access policies
4. Update `.env` variables:
   ```
   AZURE_STORAGE_ACCOUNT_URL=https://yourstorageaccount.blob.core.windows.net/
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
   ```

---

### 6. **Azure App Service** 🌐 HOSTING
```
Purpose: Host FastAPI backend with advanced session management
Service: Azure App Service (Linux)
Plan: Standard S1 minimum (1.75 GB RAM)
Features: PostgreSQL integration, streaming endpoints, session analytics
Estimated Cost: $70-150/month
```

**Setup Steps:**
1. Create App Service plan
2. Create Web App with Python 3.10+ runtime
3. Configure environment variables (see updated checklist below)
4. Deploy FastAPI application with session management
5. Configure database connection pooling
6. Set up health checks and monitoring

**Required Dependencies:**
- FastAPI with streaming support
- SQLAlchemy with asyncpg driver
- Session management middleware
- Authentication and security modules

---

### 7. **Azure Container Instances/App Service** 🖥️ HOSTING
```
Purpose: Host Streamlit frontend with enhanced UI and session integration
Service: Azure Container Instances or App Service
Configuration: 1 vCPU, 1.5 GB memory
Features: Professional dark theme UI, real-time session management, responsive design
Estimated Cost: $30-70/month
```

**Setup Steps:**
1. Containerize Streamlit app with enhanced UI components
2. Push to Azure Container Registry
3. Deploy to Container Instances with session backend integration
4. Configure networking and DNS
5. Set up SSL termination and custom domain

**UI Features:**
- Professional dark sidebar design
- Real-time chat interface
- Session history and management
- Interactive financial dashboards
- Responsive design for all devices

---

## 🔧 **OPTIONAL AZURE SERVICES**

### 8. **Azure Cache for Redis** ⚡ PERFORMANCE
```
Purpose: Caching forecast results, session data, PostgreSQL query optimization
Service: Azure Cache for Redis
Tier: Basic C1 (1GB)
Integration: FastAPI session endpoints, PostgreSQL query caching
Estimated Cost: $16-50/month
```

### 9. **Azure Application Insights** 📊 MONITORING
```
Purpose: Application monitoring, session analytics, performance tracking
Service: Application Insights
Integration: Built-in with App Service, PostgreSQL metrics, session management analytics
Features: Custom dashboards for session metrics, error tracking, performance analysis
Estimated Cost: $10-30/month
```

### 10. **Azure Key Vault** 🔐 SECURITY
```
Purpose: Secure storage of secrets, API keys
Service: Azure Key Vault
Features: Secret management, certificate storage
Estimated Cost: $5-15/month
```

### 11. **Azure Logic Apps** 🔄 AUTOMATION
```
Purpose: Workflow automation, alerts, notifications
Service: Azure Logic Apps
Use Cases: Email alerts, data sync workflows
Estimated Cost: $10-30/month
```

### 12. **Azure DevOps / GitHub Actions** 🚀 CI/CD
```
Purpose: Continuous Integration and Continuous Deployment
Service: Azure DevOps Services or GitHub Actions
Features: Automated testing, building, deployment, infrastructure as code
Estimated Cost: Free for public repos, $6/user/month for private Azure DevOps
```

**CI/CD Pipeline Features:**
- Automated testing for both frontend and backend
- Docker containerization and deployment
- Infrastructure as Code with Bicep/ARM templates
- Multi-environment deployment (dev, staging, production)
- Security scanning and compliance checks
- Automated database migrations

### 13. **Azure Container Registry** 📦 CONTAINER MANAGEMENT
```
Purpose: Store and manage Docker container images
Service: Azure Container Registry
Tier: Basic (sufficient for most use cases)
Integration: CI/CD pipelines, Container Instances, App Service
Estimated Cost: $5-20/month
```

---

## 🌐 **EXTERNAL SERVICES**

### 14. **Email Service** 📧 NOTIFICATIONS
```
Options:
- SendGrid (Azure Marketplace): $15-100/month
- Office 365/Outlook: $4-22/user/month
- Gmail SMTP: Free tier available
```

### 15. **Domain & SSL** 🌍 PRODUCTION
```
Requirements:
- Custom domain name: $10-50/year
- SSL certificate: Free with Azure App Service
- DNS management: $5-20/month
```

---

## 💰 **COST ESTIMATION SUMMARY**

### **Minimum Production Setup:**
| Service | Monthly Cost | Notes |
|---------|-------------|--------|
| Azure OpenAI (GPT-4o) | $50-200 | Core AI functionality |
| Azure AD Premium | $6/user | Authentication & RBAC |
| PostgreSQL Flexible Server | $50-150 | Complete database solution |
| App Service (Backend) | $70-150 | FastAPI with session management |
| Container Instance (Frontend) | $30-70 | Enhanced Streamlit UI |
| Blob Storage | $20-50 | File uploads & backups |
| Azure Container Registry | $5-20 | Docker image storage |
| **TOTAL** | **$231-646/month** | *Simplified PostgreSQL-only* |

### **Enterprise Setup (with Dynamics 365):**
| Additional Services | Monthly Cost | Benefits |
|-------------------|-------------|----------|
| Dynamics 365 Sales | $95-210/user | CRM integration |
| Redis Cache | $16-50 | Performance optimization |
| Application Insights | $10-30 | Advanced monitoring |
| Key Vault | $5-15 | Security & secrets |
| Azure DevOps (Private) | $6/user | CI/CD pipelines |
| **TOTAL ENTERPRISE** | **$363-957/month** | *Full DevOps integration* |

---

## 🚀 **DEPLOYMENT SEQUENCE**

### **Phase 1: Core Infrastructure**
1. ✅ Azure OpenAI Service
2. ✅ Azure Active Directory setup
3. ✅ PostgreSQL Database (Complete solution for all data and sessions)

### **Phase 2: Application Hosting**
1. ✅ App Service for FastAPI backend with session management
2. ✅ Container service for enhanced Streamlit frontend
3. ✅ Blob Storage for file uploads and data ingestion

### **Phase 3: Enterprise Integration**
1. ✅ Dynamics 365 CRM setup
2. ✅ Redis caching for PostgreSQL optimization
3. ✅ Application monitoring with session analytics

### **Phase 4: CI/CD & DevOps**
1. ✅ Azure Container Registry setup
2. ✅ CI/CD pipeline configuration (GitHub Actions or Azure DevOps)
3. ✅ Automated testing and deployment
4. ✅ Infrastructure as Code (Bicep/ARM templates)

### **Phase 5: Production Hardening**
1. ✅ Key Vault for secrets
2. ✅ Custom domain and SSL
3. ✅ Backup and disaster recovery
4. ✅ Security scanning and compliance

---

## 🔒 **SECURITY CONSIDERATIONS**

### **Required Security Setup:**
- ✅ Azure AD integration for authentication
- ✅ Key Vault for secret management
- ✅ PostgreSQL encryption at rest and in transit
- ✅ Session-based security with RBAC
- ✅ Network security groups
- ✅ Application firewall rules
- ✅ HTTPS/SSL everywhere
- ✅ Role-based access control (RBAC)

### **Compliance Features:**
- ✅ Audit logging to Application Insights
- ✅ Data encryption for PostgreSQL and session data
- ✅ PII data masking for non-admin users
- ✅ Session management with automatic timeout
- ✅ GDPR-compliant data retention policies
- ✅ Secure session token management

---

## 📋 **ENVIRONMENT VARIABLES CHECKLIST**

Create these in your Azure App Service Configuration:

```bash
# Critical - Must have for basic functionality
SECRET_KEY=required

# OpenAI Configuration - Configurable Provider
USE_AZURE_OPENAI=true  # Set to false for Direct OpenAI
OPENAI_API_KEY=required
OPENAI_API_BASE=required
OPENAI_API_DEPLOYMENT=gpt-4o  # For Azure OpenAI
OPENAI_MODEL=gpt-4o  # For Direct OpenAI
OPENAI_ORGANIZATION=optional  # For Direct OpenAI

# Database Configuration (PostgreSQL for everything)
DATABASE_URL=required

# PostgreSQL Session Management - Required
SESSION_SECRET_KEY=your-session-encryption-key
SESSION_TIMEOUT_MINUTES=30

# CRM Configuration - Configurable Data Source
USE_REAL_CRM=false  # Set to true for actual Dynamics 365
DYNAMICS_CLIENT_ID=optional
DYNAMICS_CLIENT_SECRET=optional
DYNAMICS_TENANT_ID=optional
DYNAMICS_RESOURCE_URL=optional

# Authentication - Required for multi-user
AZURE_AD_CLIENT_ID=required
AZURE_AD_TENANT_ID=required
AZURE_AD_CLIENT_SECRET=required

# Storage - File upload feature
AZURE_STORAGE_ACCOUNT_URL=optional
AZURE_STORAGE_CONNECTION_STRING=optional

# Caching - Performance optimization
REDIS_URL=optional

# Email - Notifications
EMAIL_USERNAME=optional
EMAIL_PASSWORD=optional

# Feature Flags
ENABLE_CRM_INTEGRATION=true
ENABLE_ADVANCED_FORECASTING=true
ENABLE_REAL_TIME_ALERTS=true
ENABLE_AUDIT_LOGGING=true
ENABLE_CACHING=true

# All data storage now unified in PostgreSQL
# No external document databases required
```

### **Configuration Flexibility Benefits:**

#### **OpenAI Provider Options:**
- **Azure OpenAI**: Enterprise-grade with data residency and compliance
- **Direct OpenAI**: Latest models and features, cost-effective for development
- **Seamless Switching**: Change `USE_AZURE_OPENAI` flag without code changes

#### **CRM Data Options:**
- **Real Dynamics 365**: Production CRM integration with live data
- **Mock Data**: Development and testing with realistic sample data
- **Gradual Migration**: Start with mock data, switch to real CRM when ready

---

## 🎯 **QUICK START RECOMMENDATION**

### **For Development/MVP:**
Start with these 5 services (~$180-370/month):
1. Azure OpenAI Service
2. Azure AD (Free tier)
3. PostgreSQL Database (includes session management)
4. App Service hosting
5. Azure Container Registry

**Cost Savings:** $25-50/month by using unified PostgreSQL storage instead of multiple databases

### **For Production:**
Add these services (~$370-620/month):
1. Blob Storage for files
2. Redis for PostgreSQL caching
3. Application Insights for monitoring
4. Enhanced UI with session analytics
5. CI/CD pipeline setup

### **For Enterprise:**
Include Dynamics 365 integration (~$720-1020/month):
1. Dynamics 365 Sales
2. Key Vault for secrets
3. Logic Apps for automation
4. Custom domain and enhanced security
5. Azure DevOps (if private repos)

**Architecture Benefits:**
- ✅ Simplified single-database architecture (PostgreSQL only)
- ✅ Better SQL query performance for complex analytics
- ✅ JSONB support for flexible session and document data
- ✅ Built-in full-text search capabilities
- ✅ Significant cost optimization through consolidation
- ✅ Enhanced session management with enterprise features
- ✅ Automated CI/CD deployment pipeline
- ✅ Infrastructure as Code with Bicep templates
- ✅ Containerized deployment for scalability
- ✅ Reduced complexity and maintenance overhead

## 🚀 **CI/CD Pipeline Features**

### **Automated Testing**
- Unit tests for both frontend and backend
- Integration tests with PostgreSQL
- Security scanning with Bandit and Safety
- Code coverage reporting
- Performance testing

### **Containerized Deployment**
- Docker containers for both services
- Azure Container Registry for image storage
- Multi-environment deployment (dev, staging, prod)
- Blue-green deployment capabilities
- Automated rollback on failure

### **Infrastructure as Code**
- Bicep templates for all Azure resources
- Parameterized deployments for different environments
- Automated resource provisioning
- Version-controlled infrastructure changes

### **Security & Compliance**
- Automated security scanning in pipeline
- Secret management with Azure Key Vault
- Vulnerability assessment of container images
- Compliance checks and reporting

This gives you a complete, scalable, enterprise-ready financial insights assistant with optimized PostgreSQL-based session management and automated CI/CD deployment! 🚀
