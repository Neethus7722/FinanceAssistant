# Finance Assistant - Azure Deployment Guide

## 🚀 Quick Azure Deployment

### Prerequisites
```bash
# Install Azure CLI
winget install Microsoft.AzureCLI

# Login to Azure
az login

# Set your subscription
az account set --subscription "your-subscription-id"
```

### 1. Environment Setup
```bash
# Set deployment variables
$resourceGroup = "rg-finance-assistant-prod"
$location = "East US"
$appName = "finance-assistant"

# Create resource group
az group create --name $resourceGroup --location $location
```

### 2. Deploy Infrastructure
```bash
# Navigate to infra folder
cd infra

# Deploy using PowerShell script
.\deploy.ps1 -ResourceGroupName $resourceGroup -Environment "prod" -Location $location
```

### 3. Configure Application
```bash
# Set environment variables in Azure App Service
az webapp config appsettings set --resource-group $resourceGroup --name "$appName-backend" --settings @backend-settings.json
```

### 4. Deploy Application Code
```bash
# Deploy backend
cd ../backend
az webapp up --name "$appName-backend" --resource-group $resourceGroup --runtime "PYTHON:3.10"

# Deploy frontend  
cd ../frontend
az webapp up --name "$appName-frontend" --resource-group $resourceGroup --runtime "PYTHON:3.10"
```

## 🐳 Docker Alternative

### Local Development
```bash
# Start all services locally
docker-compose up --build

# Access application
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

### Production Docker
```bash
# Build production images
docker build -t finance-backend:prod ./backend
docker build -t finance-frontend:prod ./frontend

# Push to registry
docker tag finance-backend:prod your-registry.azurecr.io/finance-backend:prod
docker push your-registry.azurecr.io/finance-backend:prod
```

## 🔧 Configuration Files Needed

Create these files for production deployment:

### backend-settings.json
```json
{
  "DATABASE_URL": "postgresql://user:pass@your-postgres-server.postgres.database.azure.com:5432/finance_db",
  "OPENAI_API_KEY": "@Microsoft.KeyVault(SecretUri=https://your-keyvault.vault.azure.net/secrets/openai-api-key/)",
  "OPENAI_API_BASE": "https://your-openai-resource.openai.azure.com/",
  "OPENAI_DEPLOYMENT": "gpt-4o",
  "SECRET_KEY": "@Microsoft.KeyVault(SecretUri=https://your-keyvault.vault.azure.net/secrets/secret-key/)"
}
```

### Production Environment Variables
```env
# Required for production
DATABASE_HOST=your-postgres-server.postgres.database.azure.com
DATABASE_NAME=finance_insights_db
DATABASE_USER=your-admin-user
DATABASE_PASSWORD=secure-password
OPENAI_API_KEY=your-openai-key
OPENAI_API_BASE=https://your-openai-resource.openai.azure.com/
OPENAI_DEPLOYMENT=gpt-4o
SECRET_KEY=your-secret-key
ENVIRONMENT=production
```

## 🔐 Security Considerations

1. **Use Azure Key Vault** for secrets
2. **Enable Azure AD authentication**
3. **Setup SSL certificates**
4. **Configure firewall rules**
5. **Enable Application Insights monitoring**

## 📊 Monitoring Setup

```bash
# Enable Application Insights
az monitor app-insights component create \
  --app finance-assistant-insights \
  --location $location \
  --resource-group $resourceGroup
```

## 🔄 CI/CD Pipeline

The project includes GitHub Actions workflows for automated deployment:
- `.github/workflows/azure-deploy.yml`
- Automatic deployment on push to main branch
- Built-in testing and security scans
