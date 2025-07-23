"""
Frontend configuration management for NextGen Revenue Insights Portal
Loads environment variables from .env file with Streamlit-specific settings
"""
import os
import streamlit as st
from typing import List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from frontend .env file
frontend_dir = Path(__file__).parent
env_path = frontend_dir / ".env"
load_dotenv(env_path)


class FrontendConfig:
    """Frontend configuration with environment variable support"""
    
    def __init__(self):
        self._load_env_vars()
    
    def _load_env_vars(self):
        """Load environment variables with defaults"""
        
        # ===========================================
        # STREAMLIT APPLICATION CONFIGURATION
        # ===========================================
        self.app_name = os.getenv("APP_NAME", "NextGen Revenue Insights Portal")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.app_host = os.getenv("APP_HOST", "0.0.0.0")
        self.app_port = int(os.getenv("APP_PORT", "8500"))
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        
        # ===========================================
        # BACKEND API CONFIGURATION
        # ===========================================
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8001")
        self.backend_api_prefix = os.getenv("BACKEND_API_PREFIX", "/api")
        self.backend_timeout = int(os.getenv("BACKEND_TIMEOUT", "30"))
        self.backend_retry_attempts = int(os.getenv("BACKEND_RETRY_ATTEMPTS", "3"))
        
        # ===========================================
        # STREAMLIT THEME CONFIGURATION
        # ===========================================
        self.theme_primary_color = os.getenv("STREAMLIT_THEME_PRIMARY_COLOR", "#1f77b4")
        self.theme_background_color = os.getenv("STREAMLIT_THEME_BACKGROUND_COLOR", "#ffffff")
        self.theme_secondary_background_color = os.getenv("STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR", "#f0f2f6")
        self.theme_text_color = os.getenv("STREAMLIT_THEME_TEXT_COLOR", "#262730")
        
        # ===========================================
        # AUTHENTICATION CONFIGURATION
        # ===========================================
        self.auth_enabled = os.getenv("AUTH_ENABLED", "False").lower() == "true"
        self.auth_secret_key = os.getenv("AUTH_SECRET_KEY", "your-frontend-auth-secret-key")
        self.auth_cookie_name = os.getenv("AUTH_COOKIE_NAME", "finance_assistant_auth")
        self.auth_cookie_expiry_days = int(os.getenv("AUTH_COOKIE_EXPIRY_DAYS", "7"))
        
        # ===========================================
        # CHART AND VISUALIZATION CONFIGURATION
        # ===========================================
        self.chart_height = int(os.getenv("CHART_HEIGHT", "400"))
        self.chart_width = int(os.getenv("CHART_WIDTH", "800"))
        self.chart_theme = os.getenv("CHART_THEME", "plotly_white")
        self.chart_color_palette = self._parse_list(
            os.getenv("CHART_COLOR_PALETTE", '["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd"]')
        )
        
        # ===========================================
        # CACHE CONFIGURATION
        # ===========================================
        self.cache_ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "300"))
        self.cache_max_entries = int(os.getenv("CACHE_MAX_ENTRIES", "100"))
        self.enable_data_caching = os.getenv("ENABLE_DATA_CACHING", "True").lower() == "true"
        
        # ===========================================
        # UI CONFIGURATION
        # ===========================================
        self.sidebar_default_state = os.getenv("SIDEBAR_DEFAULT_STATE", "expanded")
        self.page_layout = os.getenv("PAGE_LAYOUT", "wide")
        self.show_footer = os.getenv("SHOW_FOOTER", "True").lower() == "true"
        self.show_menu = os.getenv("SHOW_MENU", "True").lower() == "true"
        self.enable_dark_mode = os.getenv("ENABLE_DARK_MODE", "False").lower() == "true"
        
        # ===========================================
        # API CALL CONFIGURATION
        # ===========================================
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY", "1"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
        # ===========================================
        # LOGGING CONFIGURATION
        # ===========================================
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_to_console = os.getenv("LOG_TO_CONSOLE", "True").lower() == "true"
        self.log_file = os.getenv("LOG_FILE", "logs/frontend.log")
        
        # ===========================================
        # ENVIRONMENT SETTINGS
        # ===========================================
        self.environment = os.getenv("ENVIRONMENT", "development")
    
    def _parse_list(self, value: str) -> List[str]:
        """Parse list from string representation"""
        try:
            import ast
            return ast.literal_eval(value)
        except:
            return value.split(",") if value else []
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    @property
    def api_base_url(self) -> str:
        """Get complete API base URL"""
        return f"{self.backend_url}{self.backend_api_prefix}"
    
    def configure_streamlit_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=self.app_name,
            page_icon="📊",
            layout=self.page_layout,
            initial_sidebar_state=self.sidebar_default_state,
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': f"{self.app_name} v{self.app_version}"
            } if not self.show_menu else None
        )
    
    def get_chart_config(self) -> Dict[str, Any]:
        """Get chart configuration dictionary"""
        return {
            'height': self.chart_height,
            'width': self.chart_width,
            'theme': self.chart_theme,
            'color_palette': self.chart_color_palette
        }


# Global configuration instance
config = FrontendConfig()


def get_config() -> FrontendConfig:
    """Get frontend configuration instance"""
    return config
