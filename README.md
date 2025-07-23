# 🏦 NeFi```
FinanceAssistant/
├── 🚀 launch_portal.py              # Main application launcher
├── 🐳 docker-compose.yml            # Container orchestration
│ssistant/
├── 🚀 launch_portal.py              # Main application launcher
├── 🐳 docker-compose.yml            # Container orchestration
│ Revenue Insights Assistant

Enterprise-grade Financial Analytics Platform with Multi-Agent AI System and Separate Environment Configuration

## 🏗️ **Project Architecture**

```
FinanceAssistant/
├── 🚀 launch_portal.py              # Main application launcher
├── 🐳 docker-compose.yml            # Container orchestration
├── � env_loader.py                 # Environment configuration loader
│
├── 🔧 backend/                      # FastAPI Backend Service
│   ├── 📱 main.py                   # Main FastAPI application
│   ├── ⚙️  config.py               # Backend configuration management
│   ├── � .env                     # Backend environment variables
│   ├── �📋 .env.example             # Backend environment template
│   ├── 📋 requirements.txt         # Python dependencies
│   ├── 🐳 Dockerfile               # Backend containerization
│   │
│   ├── 🎯 core/                    # Core business logic
│   │   ├── 🗄️  database.py        # Database connections & models
│   │   ├── 📊 models.py            # Pydantic data models
│   │   └── 📦 __init__.py
│   │
│   ├── 🌐 api/                     # API endpoint definitions
│   │   └── 📦 __init__.py
│   │
│   ├── 🤖 services/                # Business services
│   │   ├── 🧠 ai_agent_service.py  # Multi-Agent AI System
│   │   └── 📦 __init__.py
│   │
│   └── 🧪 tests/                   # Backend tests
│
├── 🎨 frontend/                     # Streamlit Frontend Service
│   ├── 🏠 app.py                    # Main Streamlit application
│   ├── ⚙️  config.py               # Frontend configuration management
│   ├── � .env                     # Frontend environment variables
│   ├── �📋 .env.example             # Frontend environment template
│   ├── 📋 requirements.txt         # Python dependencies
│   ├── 🐳 Dockerfile               # Frontend containerization
│   │
│   ├── 🧩 components/              # UI components
│   │   ├── 💬 chat_interface.py    # AI Assistant Chat UI
│   │   └── 📦 __init__.py
│   │
│   ├── 🔧 utils/                   # Frontend utilities
│   │   └── 📦 __init__.py
│   │
│   └── 🧪 tests/                   # Frontend tests
│
├── 💾 data/                        # Data & Database Management
│   ├── 📊 Skeleton.xlsx            # Sample financial data
│   ├── 📋 README.md                # Data documentation
│   │
│   └── �️  database_scripts/       # Database management tools
│       ├── 🔧 setup_database.py    # Database schema setup
│       ├── 📥 import_skeleton_data.py # Data import utility
│       ├── 🛠️  db_manager.py       # Database management CLI
│       ├── 📋 requirements.txt     # Database tools dependencies
│       └── 📋 README.md            # Database scripts documentation
│
├── ☁️  infra/                      # Infrastructure as Code
│   ├── 🏗️  azure-resources.bicep   # Azure resource definitions
│   ├── 🚀 deploy.ps1               # Deployment script
│   ├── 📋 parameters.json          # Deployment parameters
│   └── � README.md                # Infrastructure documentation
│
└── 📚 Documentation/               # Project documentation
    ├── 📄 ENVIRONMENT_CONFIG.md    # Environment configuration guide
    ├── 📄 docs/MULTI_AGENT_ARCHITECTURE.md # AI system architecture
    ├── 📄 DOCKER_CONFIGURATION.md  # Docker setup guide
    ├── 📄 DEPLOYMENT_GUIDE.md      # Deployment instructions
    ├── 📄 DATABASE_MANAGEMENT.md   # Database management guide
    ├── 📄 AZURE_SERVICES_GUIDE.md  # Azure integration guide
    └── 📄 CI_CD_DOCUMENTATION.md   # CI/CD pipeline guide
```
│   ├── 🗄️  database_scripts/       # Database management tools
│   │   ├── ⚙️  setup_database.py   # Database schema setup
│   │   ├── 📊 import_skeleton_data.py # Data import & generation
│   │   ├── 🔧 db_manager.py         # Interactive DB management
│   │   └── 📋 README.md             # Database tools documentation
│   └── 📄 Skeleton.xlsx            # Sample data source
│
├── 🏗️  infra/                      # Infrastructure as Code
└── 📚 Documentation/                # Project documentation files
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.10+
- Azure PostgreSQL Database
- Azure OpenAI Service

### **Environment Setup**

#### **1. Backend Configuration**
```bash
# Copy backend environment template
cp backend/.env.example backend/.env

# Edit backend/.env with your values:
# - DATABASE_URL (PostgreSQL connection)
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
```

#### **2. Frontend Configuration**
```bash
# Copy frontend environment template
cp frontend/.env.example frontend/.env

# Edit frontend/.env with your values:
# - BACKEND_URL (usually http://localhost:8001)
# - UI and theme preferences
```

#### **3. Install Dependencies**
```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Frontend dependencies
pip install -r frontend/requirements.txt

# Database tools dependencies (optional)
pip install -r data/database_scripts/requirements.txt
```

### **Database Setup**
```bash
# Option 1: Interactive database manager
python data/database_scripts/db_manager.py

# Option 2: Individual setup steps
python data/database_scripts/setup_database.py          # Create tables and schema
python data/database_scripts/import_skeleton_data.py     # Import sample data
```

### **Launch Application**
```bash
# Single command to start both backend and frontend
python launch_portal.py
```

The portal will be available at:
- 🏦 **Frontend Dashboard**: http://localhost:8500
- 🔧 **Backend API**: http://localhost:8001

## 🏛️ **Architecture Components**

### **🔐 Environment Configuration**
- **`backend/config.py`**: Backend configuration management with environment isolation
- **`frontend/config.py`**: Frontend configuration with Streamlit integration
- **Separate `.env` files**: Isolated configuration for backend and frontend

### **🎯 Backend Core (`backend/core/`)**
- **`database.py`**: Async PostgreSQL connections, query execution
- **`models.py`**: Pydantic data models for API validation

### **🤖 AI Services (`backend/services/`)**
- **`ai_agent_service.py`**: Enhanced Multi-Agent System
  - 🔍 Query Classification Agent
  - 💰 Revenue Analysis Agent  
  - 🏢 Client Performance Agent
  - 🎯 Project Analytics Agent
  - 📊 Risk Assessment Agent
  - 👔 CXO Executive Agent

### **🎨 Frontend Components (`frontend/components/`)**
- **`chat_interface.py`**: AI Assistant Chat Interface
- **Evidence Panels**: Query analysis and data insights
- **Interactive Dashboards**: 6 comprehensive analytics sections
- **Dynamic Configuration**: Environment-based UI customization

### **💾 Data Management (`data/database_scripts/`)**
- **`setup_database.py`**: Automated database schema creation
- **`import_skeleton_data.py`**: Sample data import and generation
- **`db_manager.py`**: Interactive database management CLI
- **Standalone deployment**: Independent from main application

## 📊 **Features**

### **🎯 Executive Dashboard**
- 📈 Real-time KPIs and metrics
- 💼 Business performance overview
- 🎯 Strategic insights

### **💰 Revenue Analytics**
- 📊 Revenue trends and forecasting
- 🔍 Deep-dive analysis
- 📈 Growth trajectory insights

### **🏢 Client Performance**
- 👥 Client segmentation
- 💼 Relationship management
- 📊 Performance tracking

### **📈 Profitability Analysis**
- 💰 Margin analysis
- 🎯 Cost optimization
- 📊 ROI calculations

### **🤖 AI-Powered Assistant**
- 🧠 Multi-agent query processing
- 📊 Evidence-based responses
- 🔍 Natural language to SQL
- 📈 Automated insights generation

### **🎯 Business Insights**
- 📊 Predictive analytics
- 🔍 Trend identification
- 💡 Actionable recommendations

## 🛠️ **Technology Stack**

### **Backend**
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: Advanced ORM with async support
- **AsyncPG**: PostgreSQL async driver
- **Azure OpenAI**: Enterprise AI services
- **LangChain**: AI agent orchestration
- **Pydantic**: Data validation and settings

### **Frontend**
- **Streamlit**: Interactive web applications
- **Plotly**: Advanced data visualization
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing

### **Infrastructure**
- **Azure PostgreSQL**: Managed database service
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## 🔧 **Development**

### **Database Management**
- **`setup_database.py`**: Create database tables and schema
- **`import_skeleton_data.py`**: Import data from Skeleton.xlsx or generate sample data
- **`db_manager.py`**: Interactive database management tool

See [DATABASE_MANAGEMENT.md](DATABASE_MANAGEMENT.md) for detailed instructions.

### **Project Structure Benefits**
- ✅ **Modular Architecture**: Clear separation of concerns
- ✅ **Scalable Design**: Easy to extend and maintain
- ✅ **Enterprise Ready**: Production-grade organization
- ✅ **Clean Code**: Pythonic structure and conventions

### **Running Tests**
```bash
# Backend tests
cd backend && python -m pytest tests/

# Frontend tests  
cd frontend && python -m pytest tests/
```

### **Docker Development**
```bash
# Build and run all services
docker-compose up --build

# Run specific service
docker-compose up backend
docker-compose up frontend
```

## 📚 **API Documentation**

Access interactive API docs at: http://localhost:8001/docs

### **Key Endpoints**
- `GET /health` - Service health check
- `GET /api/dashboard/comprehensive` - Executive dashboard data
- `GET /api/analytics/time-series` - Revenue analytics
- `POST /api/chat` - AI Assistant queries

## 🔐 **Security & Configuration**

### **Environment Variables**
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://...

# Azure OpenAI
OPENAI_API_KEY=your_azure_openai_key
OPENAI_API_BASE=https://your-resource.openai.azure.com/
OPENAI_DEPLOYMENT=gpt-4o
OPENAI_API_VERSION=2024-02-15-preview
```

## � **Documentation**

For detailed information, see:

- **📄 [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation guide
- **📄 [ENVIRONMENT_CONFIG.md](ENVIRONMENT_CONFIG.md)** - Environment setup and configuration
- **📄 [MULTI_AGENT_ARCHITECTURE.md](docs/MULTI_AGENT_ARCHITECTURE.md)** - AI system architecture
- **📄 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment
- **📄 [DOCKER_CONFIGURATION.md](DOCKER_CONFIGURATION.md)** - Container setup
- **📄 [DATABASE_MANAGEMENT.md](DATABASE_MANAGEMENT.md)** - Database administration
- **📄 [AZURE_SERVICES_GUIDE.md](AZURE_SERVICES_GUIDE.md)** - Azure cloud services

## 🤝 **Contributing**

1. Follow the modular architecture patterns
2. Update documentation for any changes
3. Ensure environment configuration works for both development and production
4. Test both backend and frontend components

## � **Support**

- Check component-specific README files for detailed setup
- Review troubleshooting sections in documentation
- Ensure environment variables are properly configured
- Verify database connectivity and Azure service access

---

**Built with ❤️ for Enterprise Financial Analytics**
- 📊 Monitoring and logging
- 🔒 Security best practices

## 📈 **Performance Features**

- ⚡ Async/await throughout the stack
- 🗄️ Connection pooling for database
- 🧠 Intelligent query optimization
- 📊 Efficient data visualization
- 🔄 Auto-reloading in development

## 🤝 **Contributing**

This is a structured, enterprise-grade financial analytics platform built with modern Python best practices and cloud-native architecture.

---

**🏦 NextGen Revenue Insights Assistant v2.1.0**  
*Enterprise Financial Analytics with Multi-Agent AI*
- python-jose[cryptography]
- passlib[bcrypt]
- psycopg2-binary

## VS Code Extensions:
- ms-python.python  # Python support
- ms-python.vscode-python-envs  # Python environment management

## Azure Setup:
- Configure Azure AD App Registration for authentication
- Set up Azure PostgreSQL for data persistence

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
- Set PostgreSQL database connection details in backend .env

---
