"""
Configuration management for the NextGen Revenue Insights Backend
Loads environment variables from .env file with comprehensive defaults
"""
import os
from typing import List, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from backend/.env file
backend_dir = Path(__file__).parent
env_path = backend_dir / ".env"
load_dotenv(env_path)


class Settings:
    """Application settings with environment variable support"""
    
    def __init__(self):
        self._load_env_vars()
    
    def _load_env_vars(self):
        """Load environment variables with defaults"""
        
        # ===========================================
        # DATABASE CONFIGURATION
        # ===========================================
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/finance_db")
        self.database_host = os.getenv("DATABASE_HOST", "localhost")
        self.database_port = int(os.getenv("DATABASE_PORT", "5432"))
        self.database_name = os.getenv("DATABASE_NAME", "finance_db")
        self.database_username = os.getenv("DATABASE_USERNAME", "postgres")
        self.database_password = os.getenv("DATABASE_PASSWORD", "password")
        self.database_pool_size = int(os.getenv("DATABASE_POOL_SIZE", "20"))
        self.database_max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
        self.database_echo = os.getenv("DATABASE_ECHO", "False").lower() == "true"
        
        # ===========================================
        # AZURE OPENAI CONFIGURATION
        # ===========================================
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        self.azure_openai_model_name = os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4o")
        self.azure_openai_max_tokens = int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "4000"))
        self.azure_openai_temperature = float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.7"))
        self.azure_openai_top_p = float(os.getenv("AZURE_OPENAI_TOP_P", "0.95"))
        
        # ===========================================
        # MIXTRAL MODEL CONFIGURATION
        # ===========================================
        self.mixtral_api_key = os.getenv("MIXTRAL_API_KEY", "")
        self.mixtral_api_base = os.getenv("MIXTRAL_API_BASE", "https://api.mistral.ai/v1")
        self.mixtral_model_name = os.getenv("MIXTRAL_MODEL_NAME", "mixtral-8x7b-instruct-v0.1")
        self.mixtral_max_tokens = int(os.getenv("MIXTRAL_MAX_TOKENS", "4000"))
        self.mixtral_temperature = float(os.getenv("MIXTRAL_TEMPERATURE", "0.7"))
        self.mixtral_top_p = float(os.getenv("MIXTRAL_TOP_P", "0.95"))
        
        # ===========================================
        # AI PROVIDER CONFIGURATION
        # ===========================================
        self.ai_provider = os.getenv("AI_PROVIDER", "azure_openai")
        self.fallback_provider = os.getenv("FALLBACK_PROVIDER", "mixtral")
        
        # ===========================================
        # OPENAI DIRECT CONFIGURATION
        # ===========================================
        self.openai_direct_api_key = os.getenv("OPENAI_DIRECT_API_KEY", "")
        self.openai_direct_model_name = os.getenv("OPENAI_DIRECT_MODEL_NAME", "gpt-4")
        self.openai_direct_max_tokens = int(os.getenv("OPENAI_DIRECT_MAX_TOKENS", "4000"))
        self.openai_direct_temperature = float(os.getenv("OPENAI_DIRECT_TEMPERATURE", "0.7"))
        
        # ===========================================
        # FASTAPI APPLICATION CONFIGURATION
        # ===========================================
        self.app_name = os.getenv("APP_NAME", "NextGen Revenue Insights Backend")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.app_host = os.getenv("APP_HOST", "0.0.0.0")
        self.app_port = int(os.getenv("APP_PORT", "8001"))
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.reload = os.getenv("RELOAD", "False").lower() == "true"
        
        # ===========================================
        # SECURITY CONFIGURATION
        # ===========================================
        self.secret_key = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.api_key = os.getenv("API_KEY", "your-api-key-for-internal-communication")
        
        # ===========================================
        # CORS CONFIGURATION
        # ===========================================
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:8500,http://localhost:3000")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        self.cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
        
        cors_methods_str = os.getenv("CORS_ALLOW_METHODS", "*")
        self.cors_allow_methods = [method.strip() for method in cors_methods_str.split(",")] if cors_methods_str != "*" else ["*"]
        
        cors_headers_str = os.getenv("CORS_ALLOW_HEADERS", "*")
        self.cors_allow_headers = [header.strip() for header in cors_headers_str.split(",")] if cors_headers_str != "*" else ["*"]
        
        # ===========================================
        # AZURE SERVICES CONFIGURATION
        # ===========================================
        self.azure_subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "")
        self.azure_resource_group = os.getenv("AZURE_RESOURCE_GROUP", "")
        self.azure_location = os.getenv("AZURE_LOCATION", "East US")
        self.azure_tenant_id = os.getenv("AZURE_TENANT_ID", "")
        self.azure_client_id = os.getenv("AZURE_CLIENT_ID", "")
        self.azure_client_secret = os.getenv("AZURE_CLIENT_SECRET", "")
        
        # ===========================================
        # LOGGING CONFIGURATION
        # ===========================================
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_to_console = os.getenv("LOG_TO_CONSOLE", "True").lower() == "true"
        self.log_file = os.getenv("LOG_FILE", "logs/backend.log")
        self.log_rotation = os.getenv("LOG_ROTATION", "daily")
        self.log_retention = int(os.getenv("LOG_RETENTION", "30"))
        
        # ===========================================
        # API CONFIGURATION
        # ===========================================
        self.api_prefix = os.getenv("API_PREFIX", "/api")
        self.api_rate_limit = int(os.getenv("API_RATE_LIMIT", "100"))
        self.api_rate_limit_period = os.getenv("API_RATE_LIMIT_PERIOD", "minute")
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
        # ===========================================
        # ENVIRONMENT SETTINGS
        # ===========================================
        self.environment = os.getenv("ENVIRONMENT", "development")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    @property
    def use_azure_openai(self) -> bool:
        """Check if Azure OpenAI should be used"""
        return self.ai_provider.lower() == "azure_openai"
    
    @property
    def use_mixtral(self) -> bool:
        """Check if Mixtral should be used"""
        return self.ai_provider.lower() == "mixtral"
    
    @property
    def use_openai_direct(self) -> bool:
        """Check if direct OpenAI should be used"""
        return self.ai_provider.lower() == "openai_direct"
    
    def get_ai_config(self) -> dict:
        """Get AI configuration based on selected provider"""
        if self.use_azure_openai:
            return {
                "provider": "azure_openai",
                "api_key": self.azure_openai_api_key,
                "endpoint": self.azure_openai_endpoint,
                "api_version": self.azure_openai_api_version,
                "deployment_name": self.azure_openai_deployment_name,
                "model_name": self.azure_openai_model_name,
                "max_tokens": self.azure_openai_max_tokens,
                "temperature": self.azure_openai_temperature,
                "top_p": self.azure_openai_top_p
            }
        elif self.use_mixtral:
            return {
                "provider": "mixtral",
                "api_key": self.mixtral_api_key,
                "api_base": self.mixtral_api_base,
                "model_name": self.mixtral_model_name,
                "max_tokens": self.mixtral_max_tokens,
                "temperature": self.mixtral_temperature,
                "top_p": self.mixtral_top_p
            }
        elif self.use_openai_direct:
            return {
                "provider": "openai_direct",
                "api_key": self.openai_direct_api_key,
                "model_name": self.openai_direct_model_name,
                "max_tokens": self.openai_direct_max_tokens,
                "temperature": self.openai_direct_temperature
            }
        else:
            raise ValueError(f"Unknown AI provider: {self.ai_provider}")
    
    def get_fallback_ai_config(self) -> dict:
        """Get fallback AI configuration"""
        original_provider = self.ai_provider
        self.ai_provider = self.fallback_provider
        try:
            return self.get_ai_config()
        finally:
            self.ai_provider = original_provider


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings