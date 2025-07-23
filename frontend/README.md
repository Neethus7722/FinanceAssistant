# 🎨 NextGen Revenue Insights - Frontend Portal

Enterprise Streamlit dashboard with AI assistant and comprehensive financial analytics.

## 📁 **Structure**

```
frontend/
├── 🏠 app.py                    # Main Streamlit application
├── ⚙️  config.py               # Frontend configuration management
├── 🔐 .env                     # Frontend-specific environment variables
├── 📋 .env.example             # Environment configuration template
├── 📋 requirements.txt         # Python dependencies
├── 🐳 Dockerfile               # Container configuration
│
├── 🧩 components/              # UI components
│   ├── 💬 chat_interface.py    # AI Assistant chat interface
│   └── 📦 __init__.py
│
├── 🔧 utils/                   # Frontend utilities
│   └── 📦 __init__.py
│
└── 🧪 tests/                   # Frontend tests
```

## 🚀 **Features**

### **📊 Analytics Dashboard Sections**
1. 🎯 **Executive Dashboard** - KPIs and strategic metrics
2. 💰 **Revenue Analytics** - Revenue trends and forecasting
3. 🏢 **Client Performance** - Client segmentation and tracking
4. 📈 **Profitability Analysis** - Margin analysis and ROI
5. 🔍 **Data Insights** - Deep-dive analytics
6. 🤖 **AI Assistant** - Multi-agent powered chat interface

### **🎨 UI Features**
- 🌓 Dynamic theming and customization
- 📱 Responsive design for all screen sizes
- 🔍 Interactive data visualizations
- 💬 Evidence-based AI responses
- 📊 Real-time data updates

### **⚙️ Configuration Management**
- 🔐 Separate environment file (`frontend/.env`)
- 🎨 Customizable themes and colors
- 🔗 Dynamic backend API configuration
- 📊 Chart and visualization settings

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

### **3. Run Frontend**
```bash
# Development mode
streamlit run app.py

# Production mode
streamlit run app.py --server.port 8500 --server.address 0.0.0.0
```

## 🔐 **Environment Variables**

Key environment variables in `frontend/.env`:

```env
# Backend API
BACKEND_URL=http://localhost:8001

# Streamlit Configuration
APP_PORT=8500
PAGE_LAYOUT=wide

# Theme Configuration
STREAMLIT_THEME_PRIMARY_COLOR=#1f77b4
CHART_THEME=plotly_white
```

See `.env.example` for complete configuration options.

## 🌐 **Access**

Once running, access the portal at:
- **Local Development**: http://localhost:8500
- **Production**: https://yourdomain.com

The frontend communicates with the backend API at the configured `BACKEND_URL`.
