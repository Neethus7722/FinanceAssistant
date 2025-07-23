# 🔧 NextGen Revenue Insights - Backend Service

Enterprise-grade FastAPI backend with multi-agent AI system and separate environment configuration.

## 📁 **Structure**

```
backend/
├── 📱 main.py                   # Main FastAPI application with multi-agent integration
├── ⚙️  config.py               # Environment-based configuration management
├── 🔐 .env                     # Backend-specific environment variables
├── 📋 .env.example             # Environment configuration template
├── 📋 requirements.txt         # Python dependencies
├── 🐳 Dockerfile               # Container configuration
│
├── 🎯 core/                    # Core business logic
│   ├── 🗄️  database.py        # Async PostgreSQL connections
│   ├── 📊 models.py            # Pydantic data models
│   └── 📦 __init__.py
│
├── 🌐 api/                     # API endpoint definitions
│   └── 📦 __init__.py
│
├── 🤖 services/                # Business services
│   ├── 🧠 ai_agent_service.py  # Enhanced Multi-Agent AI System
│   └── 📦 __init__.py
│
└── 🧪 tests/                   # Backend tests
```

## 🚀 **Features**

### **Multi-Agent AI System**
- 🔍 Query Classification Agent
- 💰 Revenue Analysis Agent
- 🏢 Client Performance Agent
- 🎯 Project Analytics Agent
- 📊 Risk Assessment Agent
- 👔 CXO Executive Agent

### **Configuration Management**
- 🔐 Separate environment file (`backend/.env`)
- ⚙️  Type-safe configuration classes
- 🌐 Dynamic CORS and security settings
- 🗄️  Database connection management

### **API Endpoints**
- 💬 `/api/chat` - AI Assistant interface
- 📊 `/api/dashboard/comprehensive` - Executive dashboard data
- 📈 `/api/analytics/*` - Analytics endpoints
- 🔍 `/api/intelligence/query` - Multi-agent query processing

## 🛠️ **Setup**

### **1. Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Run Backend**
```bash
# Development mode
uvicorn main:app --reload --port 8001

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8001
```

## 🔐 **Environment Variables**

Key environment variables in `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Application
DEBUG=false
ENVIRONMENT=production
```

See `.env.example` for complete configuration options.
