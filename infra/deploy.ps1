# Azure Infrastructure Deployment Script for NextGen Revenue Insights Assistant
# Enhanced version with CI/CD support and container deployment

# Prerequisites: Install Azure CLI and login
# az login
# az account set --subscription "your-subscription-id"

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory=$true)]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipInfrastructure,
    
    [Parameter(Mandatory=$false)]
    [switch]$DeployFromCI
)

Write-Host "🚀 Starting deployment for NextGen Revenue Insights Assistant" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Yellow
Write-Host "Location: $Location" -ForegroundColor Yellow

# Set subscription if provided
if ($SubscriptionId) {
    Write-Host "Setting Azure subscription: $SubscriptionId" -ForegroundColor Blue
    az account set --subscription $SubscriptionId
}

# Deploy GPT-4o model
Write-Host "🧠 Deploying GPT-4o model..." -ForegroundColor Cyan
az cognitiveservices account deployment create `
    --name $openaiName `
    --resource-group $resourceGroup `
    --deployment-name "gpt-4o" `
    --model-name "gpt-4o" `
    --model-version "2024-06-01" `
    --model-format OpenAI `
    --sku-capacity 10 `
    --sku-name "Standard"

# 2. Create PostgreSQL Database
Write-Host "🗄️ Creating PostgreSQL Database..." -ForegroundColor Cyan
$dbServerName = "$appName-postgres-$environment"
$dbAdminUser = "financeadmin"
$dbAdminPassword = "Finance123!@#"  # Change this in production
az postgres flexible-server create `
    --name $dbServerName `
    --resource-group $resourceGroup `
    --location $location `
    --admin-user $dbAdminUser `
    --admin-password $dbAdminPassword `
    --sku-name Standard_B2s `
    --tier Burstable `
    --version 14 `
    --storage-size 128 `
    --public-access 0.0.0.0

# Create database
az postgres flexible-server db create `
    --resource-group $resourceGroup `
    --server-name $dbServerName `
    --database-name "finance_insights_db"

# 3. Cosmos DB (NO LONGER USED - REPLACED BY POSTGRESQL)
# Write-Host "🌍 Creating Cosmos DB..." -ForegroundColor Cyan
# $cosmosName = "$appName-cosmos-$environment"
# All chat history and session data is now stored in PostgreSQL for better integration

# 4. Create Storage Account
Write-Host "📁 Creating Storage Account..." -ForegroundColor Cyan
$storageName = "$appName" + "storage" + $environment  # Remove dashes for storage name
az storage account create `
    --name $storageName `
    --resource-group $resourceGroup `
    --location $location `
    --sku Standard_LRS `
    --kind StorageV2

# Create blob container
az storage container create `
    --name "financial-data" `
    --account-name $storageName `
    --auth-mode login

# 5. Create App Service Plan
Write-Host "🏗️ Creating App Service Plan..." -ForegroundColor Cyan
$appServicePlan = "$appName-plan-$environment"
az appservice plan create `
    --name $appServicePlan `
    --resource-group $resourceGroup `
    --location $location `
    --sku S1 `
    --is-linux

# 6. Create Web App for Backend
Write-Host "🌐 Creating Backend Web App..." -ForegroundColor Cyan
$backendAppName = "$appName-backend-$environment"
az webapp create `
    --name $backendAppName `
    --resource-group $resourceGroup `
    --plan $appServicePlan `
    --runtime "PYTHON|3.11"

# 7. Create Redis Cache (Optional)
Write-Host "⚡ Creating Redis Cache..." -ForegroundColor Cyan
$redisName = "$appName-redis-$environment"
az redis create `
    --name $redisName `
    --resource-group $resourceGroup `
    --location $location `
    --sku Basic `
    --vm-size C1

# 8. Create Application Insights
Write-Host "📊 Creating Application Insights..." -ForegroundColor Cyan
$appInsightsName = "$appName-insights-$environment"
az monitor app-insights component create `
    --app $appInsightsName `
    --location $location `
    --resource-group $resourceGroup `
    --kind web

# 9. Create Key Vault
Write-Host "🔐 Creating Key Vault..." -ForegroundColor Cyan
$keyVaultName = "$appName-kv-$environment"
az keyvault create `
    --name $keyVaultName `
    --resource-group $resourceGroup `
    --location $location `
    --sku standard

Write-Host "✅ Infrastructure Creation Complete!" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Yellow

# Get connection strings and keys
Write-Host "📋 Retrieving Connection Information..." -ForegroundColor Cyan

# OpenAI
$openaiKey = az cognitiveservices account keys list --name $openaiName --resource-group $resourceGroup --query "key1" --output tsv
$openaiEndpoint = az cognitiveservices account show --name $openaiName --resource-group $resourceGroup --query "properties.endpoint" --output tsv

# Database
$dbConnectionString = "postgresql+asyncpg://$dbAdminUser`:$dbAdminPassword@$dbServerName.postgres.database.azure.com:5432/finance_insights_db"

# Storage
$storageConnectionString = az storage account show-connection-string --name $storageName --resource-group $resourceGroup --query "connectionString" --output tsv

# Redis
$redisKey = az redis list-keys --name $redisName --resource-group $resourceGroup --query "primaryKey" --output tsv
$redisHostname = az redis show --name $redisName --resource-group $resourceGroup --query "hostName" --output tsv

# Application Insights
$appInsightsKey = az monitor app-insights component show --app $appInsightsName --resource-group $resourceGroup --query "instrumentationKey" --output tsv

Write-Host "=========================================================" -ForegroundColor Yellow
Write-Host "🎉 DEPLOYMENT COMPLETE! Update your .env file with:" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Yellow

Write-Host "# Azure OpenAI" -ForegroundColor Cyan
Write-Host "OPENAI_API_KEY=$openaiKey"
Write-Host "OPENAI_API_BASE=$openaiEndpoint"

Write-Host "`n# Database (PostgreSQL)" -ForegroundColor Cyan
Write-Host "DATABASE_URL=$dbConnectionString"

Write-Host "`n# Storage" -ForegroundColor Cyan
Write-Host "AZURE_STORAGE_CONNECTION_STRING=$storageConnectionString"
Write-Host "AZURE_STORAGE_ACCOUNT_URL=https://$storageName.blob.core.windows.net/"

Write-Host "`n# Redis" -ForegroundColor Cyan
Write-Host "REDIS_URL=redis://:$redisKey@$redisHostname`:6380/0?ssl=True"

Write-Host "`n# Application Insights" -ForegroundColor Cyan
Write-Host "APPINSIGHTS_INSTRUMENTATIONKEY=$appInsightsKey"

Write-Host "`n# Backend URL" -ForegroundColor Cyan
Write-Host "BACKEND_URL=https://$backendAppName.azurewebsites.net"

Write-Host "=========================================================" -ForegroundColor Yellow
Write-Host "📝 NEXT STEPS:" -ForegroundColor Green
Write-Host "1. Update your .env file with the values above"
Write-Host "2. Set up Azure AD App Registration manually"
Write-Host "3. Configure Dynamics 365 (if using CRM features)"
Write-Host "4. Deploy your application code to the Web App"
Write-Host "5. Build and deploy frontend container"
Write-Host "6. Configure custom domain (optional)"
Write-Host "=========================================================" -ForegroundColor Yellow

Write-Host "💰 ESTIMATED MONTHLY COST: $400-700" -ForegroundColor Yellow
Write-Host "🔒 SECURITY: Remember to configure firewall rules and access policies!" -ForegroundColor Red
