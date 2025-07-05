import streamlit as st
import requests
import uuid
# from msal_streamlit_auth import msal_authentication
from config import settings

# --- Auth & Session ---
# result = msal_authentication(
#     client_id=settings.CLIENT_ID,
#     authority=settings.AUTHORITY,
#     scopes=settings.SCOPE,
#     redirect_uri=None,
# )
# if not result:
#     st.warning("Please sign in with your Azure AD account to use this application.")
#     st.stop()
# user_id = result.get('user', {}).get('oid', None) or result.get('id_token_claims', {}).get('oid', None)
# if not user_id:
#     st.error("Could not determine user identity from Azure AD login.")
#     st.stop()
user_id = "demo_user"  # Temporary for UI preview
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "user_id" not in st.session_state:
    st.session_state["user_id"] = user_id

# --- API Utilities ---
def fetch_all_sessions(user_id):
    api_url = f"{settings.RAG_API_URL.replace('/rag-advanced/', '/chat/sessions/')}"
    resp = requests.get(api_url, params={"user_id": user_id})
    if resp.status_code == 200:
        return resp.json().get("sessions", [])
    return []

def fetch_chat_history(session_id, user_id):
    api_url = f"{settings.RAG_API_URL.replace('/rag-advanced/', '/chat/history/')}"
    resp = requests.post(api_url, json={"session_id": session_id, "user_id": user_id})
    if resp.status_code == 200:
        return resp.json().get("history", [])
    return []

def send_rag_query(query, user_id, user_role):
    resp = requests.post(settings.RAG_API_URL, json={
        "query": query,
        "user_id": user_id,
        "user_role": user_role
    })
    return resp
