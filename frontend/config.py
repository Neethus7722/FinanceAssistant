# Configuration loader for Streamlit frontend
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID", "your-azure-ad-client-id")
    TENANT_ID = os.getenv("AZURE_AD_TENANT_ID", "your-azure-ad-tenant-id")
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPE = ["User.Read"]
    RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8000/rag-advanced/")

settings = Settings()
