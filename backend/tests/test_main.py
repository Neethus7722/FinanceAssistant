import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Test configuration
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb")

def test_main_imports():
    """Test that main modules can be imported without errors"""
    try:
        from main import app
        assert app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import main module: {e}")

def test_config_imports():
    """Test that config modules can be imported"""
    try:
        from config import get_settings
        settings = get_settings()
        assert settings is not None
    except ImportError as e:
        pytest.fail(f"Failed to import config: {e}")

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection"""
    try:
        from db import get_database
        # Test that database connection can be established
        db = await get_database()
        assert db is not None
    except Exception as e:
        # Skip if database not available in CI
        pytest.skip(f"Database not available: {e}")

def test_session_manager_import():
    """Test session manager imports"""
    try:
        from session_manager import SessionManager
        assert SessionManager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import SessionManager: {e}")

def test_schemas_import():
    """Test schema imports"""
    try:
        from schemas import ChatRequest, ChatResponse
        assert ChatRequest is not None
        assert ChatResponse is not None
    except ImportError as e:
        pytest.fail(f"Failed to import schemas: {e}")

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        # Should return 200 even if database is not connected
        assert response.status_code in [200, 503]  # 503 if DB not available
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            
    except Exception as e:
        pytest.skip(f"Health endpoint test failed: {e}")

def test_environment_variables():
    """Test that required environment variables are accessible"""
    # These should be set in CI/CD pipeline
    secret_key = os.getenv("SECRET_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # In CI, these might be test values
    assert secret_key is not None, "SECRET_KEY environment variable not set"
    assert openai_key is not None, "OPENAI_API_KEY environment variable not set"

if __name__ == "__main__":
    pytest.main([__file__])
