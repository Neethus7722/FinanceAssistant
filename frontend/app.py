import streamlit as st
import requests
import uuid
import os
from msal_streamlit_auth import msal_authentication  # Re-enable Azure AD authentication
from dotenv import load_dotenv
from pathlib import Path

# Required Python packages for Azure AD authentication:
# - msal-streamlit-auth (pip install msal-streamlit-auth)
# - requests
# - streamlit
# - uuid
#
# To install, run:
# pip install msal-streamlit-auth requests streamlit uuid
#
# For backend (FastAPI + Cosmos DB):
# - fastapi
# - uvicorn
# - sqlalchemy
# - asyncpg
# - pandas
# - python-dotenv
# - azure-identity
# - azure-ai-ml
# - openai
# - python-jose[cryptography]
# - passlib[bcrypt]
# - psycopg2-binary
# - azure-cosmos
#
# To install backend requirements:
# pip install -r backend/requirements.txt
#
# For Azure AD integration, configure your Azure App Registration and set CLIENT_ID, TENANT_ID in the code or .env file.
#
# For Streamlit Azure AD login, see: https://github.com/streamlit/streamlit-authenticator or https://pypi.org/project/msal-streamlit-auth/

st.set_page_config(page_title="NextGen Revenue Insights Assistant", layout="wide")
st.title("💡 NextGen Revenue Insights Assistant")

st.markdown("""
A secure, LLM-powered conversational system for accurate financial intelligence.
""")

# Load environment variables from .env file in project root
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID", "your-azure-ad-client-id")
TENANT_ID = os.getenv("AZURE_AD_TENANT_ID", "your-azure-ad-tenant-id")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read"]

RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8000/rag-advanced/")

# Azure AD login
result = msal_authentication(
    client_id=CLIENT_ID,
    authority=AUTHORITY,
    scopes=SCOPE,
    redirect_uri=None,  # Use default Streamlit redirect
)
if not result:
    st.warning("Please sign in with your Azure AD account to use this application.")
    st.stop()
user_id = result.get('user', {}).get('oid', None) or result.get('id_token_claims', {}).get('oid', None)
if not user_id:
    st.error("Could not determine user identity from Azure AD login.")
    st.stop()

# To enable user-specific chat sessions, use Azure AD login info
user_id = "default_user_id"  # Placeholder for UI preview
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "user_id" not in st.session_state:
    st.session_state["user_id"] = user_id

# Fetch all session IDs for this user only
def fetch_all_sessions(user_id):
    api_url = "http://localhost:8000/chat/sessions/"
    resp = requests.get(api_url, params={"user_id": user_id})
    if resp.status_code == 200:
        return resp.json().get("sessions", [])
    return []

# Session selection and creation
sessions = fetch_all_sessions(st.session_state["user_id"])
session_options = [s for s in sessions]
selected_session = st.selectbox("Select a chat session", session_options + ["+ New Chat"], index=0 if session_options else None)

if selected_session == "+ New Chat" or not session_options:
    if st.button("Start New Chat Session"):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.cache_data.clear()
        st.experimental_rerun()
else:
    st.session_state["session_id"] = selected_session

# Fetch chat history from backend for this user/session
@st.cache_data(show_spinner=False)
def fetch_chat_history(session_id, user_id):
    api_url = "http://localhost:8000/chat/history/"
    resp = requests.post(api_url, json={"session_id": session_id, "user_id": user_id})
    if resp.status_code == 200:
        return resp.json().get("history", [])
    return []

# Display previous chat history (persistent)
chat_history = fetch_chat_history(st.session_state["session_id"], st.session_state["user_id"])
st.subheader("Chat History (This Session)")
for chat in chat_history:
    st.markdown(f"**You:** {chat['user']}")
    st.markdown(f"**Assistant:** {chat['assistant']}")
    st.markdown("---")

query = st.text_input("Ask a financial question (e.g., 'Show Q1 revenue by project'):")

if st.button("Submit") and query:
    try:
        response = requests.post(RAG_API_URL, json={
            "query": query,
            "user_id": st.session_state.get("user_id"),
            "user_role": "admin" if st.session_state.get("user_id") == "admin_id" else "user"
        })
        if response.status_code == 200:
            result = response.json().get("result", "No result returned.")
            st.session_state["chat_history"].append({"user": query, "assistant": result})
            st.success(result)
        else:
            error_msg = response.json().get("error", response.text)
            st.error(f"Error: {error_msg}")
    except Exception as e:
        st.error(f"Request failed: {str(e)}")

st.info("Role-based access and secure data handling enabled.")

# Entry point for Streamlit app
import main_app
main_app.run()
