import streamlit as st
from core import fetch_all_sessions, fetch_chat_history, send_rag_query
import uuid

st.set_page_config(page_title="NextGen Revenue Insights Assistant", layout="wide")

# --- Sidebar: Session Management ---
st.sidebar.title("💼 Sessions")
sessions = fetch_all_sessions(st.session_state["user_id"])
session_options = [s for s in sessions]
selected_session = st.sidebar.selectbox("Select a chat session", session_options + ["+ New Chat"], index=0 if session_options else None)
if selected_session == "+ New Chat" or not session_options:
    if st.sidebar.button("Start New Chat Session"):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.cache_data.clear()
        st.experimental_rerun()
else:
    st.session_state["session_id"] = selected_session

# --- Main Chat UI ---
st.markdown("""
<style>
.chat-container {background-color: #f6f8fa; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;}
.user-msg {color: #1a73e8; font-weight: 600; margin-bottom: 0.2rem;}
.assistant-msg {color: #222; background: #e8eaf6; border-radius: 8px; padding: 0.7rem; margin-bottom: 1.2rem;}
</style>
""", unsafe_allow_html=True)

st.title("💡 NextGen Revenue Insights Assistant")
st.caption("A secure, LLM-powered conversational system for accurate financial intelligence.")

chat_history = fetch_chat_history(st.session_state["session_id"], st.session_state["user_id"])
st.subheader("Chat History")
for chat in chat_history:
    st.markdown(f'<div class="chat-container"><div class="user-msg">You:</div><div>{chat["user"]}</div><div class="assistant-msg">{chat["assistant"]}</div></div>', unsafe_allow_html=True)

# --- Chat Input ---
with st.form(key="chat_form", clear_on_submit=True):
    query = st.text_input("Type your question...", key="user_query")
    submit = st.form_submit_button("Send")

if submit and query:
    with st.spinner("Thinking..."):
        response = send_rag_query(query, st.session_state["user_id"], "admin" if st.session_state["user_id"] == "admin_id" else "user")
        if response.status_code == 200:
            result = response.json().get("result", "No result returned.")
            st.session_state.setdefault("chat_history", []).append({"user": query, "assistant": result})
            st.success(result)
        else:
            error_msg = response.json().get("error", response.text)
            st.error(f"Error: {error_msg}")

st.info("Role-based access and secure data handling enabled.")
