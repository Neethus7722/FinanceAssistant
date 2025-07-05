# NextGen Revenue Insights Assistant

A secure, LLM-powered conversational system for accurate financial intelligence.

## Features
- Natural language financial queries (revenue, margin, cost, project performance)
- Secure, role-aware interface (Azure AD integration)
- Retrieval-Augmented Generation (RAG) with GPT-4o for summaries and charts
- PostgreSQL-backed structured store from Excel data
- Enterprise-ready UI (Streamlit)
- Modular, extensible, and Azure-ready

## Tech Stack
- Backend: Python (FastAPI), PostgreSQL, Azure OpenAI
- Frontend: Streamlit
- Auth: Azure Active Directory
- Deployment: Azure Cloud

## Getting Started
1. Backend: FastAPI app for API, data ingestion, RAG logic, and security
2. Frontend: Streamlit app for chat-style UX
3. Infrastructure: Azure deployment scripts

## Security
- Encryption, RBAC, audit logging
- Role-based data access and masking

---

This project is a solution accelerator for enterprise financial analytics and can be extended to other domains (Ops, HR, Delivery).

# Additional required extensions and installations for Azure AD, Cosmos DB, and Streamlit integration:

## Frontend (Streamlit):
- streamlit
- requests
- uuid
- msal-streamlit-auth  # For Azure AD authentication

## Backend (FastAPI):
- fastapi
- uvicorn
- sqlalchemy
- asyncpg
- pandas
- python-dotenv
- azure-identity
- azure-ai-ml
- openai
- python-jose[cryptography]
- passlib[bcrypt]
- psycopg2-binary
- azure-cosmos  # For Cosmos DB integration

## VS Code Extensions:
- ms-python.python  # Python support
- ms-python.vscode-python-envs  # Python environment management

## Azure Setup:
- Configure Azure AD App Registration for authentication
- Set up Azure Cosmos DB for chat history persistence

---

# Installation

## Frontend:
```powershell
pip install streamlit requests uuid msal-streamlit-auth
```

## Backend:
```powershell
pip install -r backend/requirements.txt
```

---

# Configuration
- Set Azure AD CLIENT_ID and TENANT_ID in your environment or code
- Set Cosmos DB connection details in backend .env

---
