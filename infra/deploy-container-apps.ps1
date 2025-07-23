# Azure Container Apps Deployment Script
# Separate containers with proper networking

# Set variables
$RESOURCE_GROUP = "rg-finance-assistant"
$LOCATION = "East US"
$CONTAINER_APP_ENV = "finance-app-env"
$BACKEND_APP = "finance-backend"
$FRONTEND_APP = "finance-frontend"

# Create Container Apps Environment
az containerapp env create `
  --name $CONTAINER_APP_ENV `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION

# Deploy Backend Container App
az containerapp create `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --environment $CONTAINER_APP_ENV `
  --image "your-registry.azurecr.io/finance-backend:latest" `
  --target-port 8000 `
  --ingress external `
  --min-replicas 1 `
  --max-replicas 5 `
  --cpu 1.0 `
  --memory 2.0Gi `
  --env-vars `
    DATABASE_URL=secretref:database-url `
    OPENAI_API_KEY=secretref:openai-key

# Deploy Frontend Container App  
az containerapp create `
  --name $FRONTEND_APP `
  --resource-group $RESOURCE_GROUP `
  --environment $CONTAINER_APP_ENV `
  --image "your-registry.azurecr.io/finance-frontend:latest" `
  --target-port 8501 `
  --ingress external `
  --min-replicas 1 `
  --max-replicas 3 `
  --cpu 0.5 `
  --memory 1.0Gi `
  --env-vars `
    BACKEND_URL="https://$BACKEND_APP.your-domain.azurecontainerapps.io"

Write-Host "🎉 Deployment Complete!"
Write-Host "📊 Backend API: https://$BACKEND_APP.your-domain.azurecontainerapps.io"
Write-Host "🏦 Frontend Portal: https://$FRONTEND_APP.your-domain.azurecontainerapps.io"
