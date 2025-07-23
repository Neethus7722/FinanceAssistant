# 🏗️ Infrastructure & Azure Deployment

This folder contains Infrastructure-as-Code (IaC) templates and deployment scripts for deploying the NextGen Revenue Insights Assistant to Azure with **separate frontend and backend services**.

## 📁 **Files Overview**

### **🏗️ Infrastructure Templates**
- **`azure-resources.bicep`** - Main Bicep template defining all Azure resources
- **`parameters.json`** - Configuration parameters for different environments

### **🚀 Deployment Scripts**
- **`deploy.ps1`** - Main deployment script using Azure App Services
- **`deploy-container-apps.ps1`** - Alternative deployment using Azure Container Apps (Recommended)

## 🎯 **Deployment Architecture**

### **Separate Services Deployment:**
```
Azure Cloud
├── 🔧 Backend Service (FastAPI)
│   ├── Azure Container App / App Service
│   ├── Port: 8000
│   └── Connects to: PostgreSQL, Key Vault, Redis
│
├── 🎨 Frontend Service (Streamlit)
│   ├── Azure Container App / App Service  
│   ├── Port: 8501
│   └── Connects to: Backend API
│
└── 🗄️ Shared Resources
    ├── PostgreSQL Flexible Server
    ├── Azure Key Vault (secrets)
    ├── Redis Cache (session storage)
    ├── Container Registry (images)
    └── Application Insights (monitoring)
```

## 🚀 **Quick Deployment**

### **Prerequisites**
```powershell
# Install Azure CLI
az login
az account set --subscription "your-subscription-id"
```

### **Option 1: Container Apps (Recommended)**
```powershell
# Navigate to infra folder
cd infra

# Deploy with Container Apps
.\deploy-container-apps.ps1
```

### **Option 2: App Services**
```powershell
# Navigate to infra folder
cd infra

# Deploy with App Services
.\deploy.ps1 -ResourceGroupName "rg-finance-assistant" -Location "East US" -Environment "prod"
```

## ⚙️ **Configuration Parameters**

Edit `parameters.json` for your environment:

```json
{
  "environment": "prod",
  "appNamePrefix": "financeassistant",
  "location": "East US",
  "postgresAdminLogin": "your-admin",
  "postgresAdminPassword": "secure-password",
  "openaiApiKey": "your-openai-key"
}
```

## 🔐 **Security Features**

- **Azure Key Vault** - Stores all secrets and API keys
- **Managed Identity** - Secure access to Azure resources
- **HTTPS Only** - All communication encrypted
- **Network Security** - Proper firewall and access controls
- **Environment Isolation** - Separate resources per environment

## 💰 **Cost Optimization**

- **PostgreSQL Flexible Server** - Burstable tier for development
- **Container Apps** - Pay-per-use scaling
- **Redis Cache** - Basic tier for session storage
- **Unified Database** - No Cosmos DB (PostgreSQL only)

## 📊 **Monitoring & Logs**

- **Application Insights** - Performance monitoring
- **Azure Monitor** - Infrastructure monitoring  
- **Log Analytics** - Centralized logging
- **Health Checks** - Automated health monitoring

## 🔄 **CI/CD Ready**

The templates support:
- **GitHub Actions** deployment
- **Azure DevOps** pipelines  
- **Environment-specific** configurations
- **Automated scaling** and updates

## 🆘 **Support**

For deployment issues:
1. Check Azure CLI version: `az --version`
2. Verify subscription access: `az account show`
3. Review deployment logs in Azure Portal
4. Check resource group permissions
