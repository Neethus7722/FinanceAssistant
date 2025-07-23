"""
AI Assistant Components for the Unified Portal
Modular components for chat interface and evidence panels
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import configuration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import get_config
config = get_config()

def initialize_chat_session():
    """Initialize chat session state"""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def send_chat_message(query: str, backend_url: str = None) -> Dict[str, Any]:
    """Send message to the enhanced backend"""
    if backend_url is None:
        backend_url = config.api_base_url
    try:
        response = requests.post(
            f"{backend_url}/chat",
            json={
                "message": query,
                "session_id": st.session_state.session_id,
                "conversation_id": st.session_state.conversation_id
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Backend error: {response.text}"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def render_chat_interface():
    """Render the main chat interface"""
    st.markdown("### 🤖 AI Financial Assistant")
    
    # Initialize session
    initialize_chat_session()
    
    # Chat input
    with st.container():
        user_input = st.chat_input("Ask me anything about your financial data...")
        
        if user_input:
            # Add user message to chat
            st.session_state.chat_messages.append({
                "role": "user", 
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Show thinking spinner
            with st.spinner("🔍 AI agents are analyzing your request..."):
                # Send to backend
                response = send_chat_message(user_input)
                
                if "error" not in response:
                    # Add assistant response to chat
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": response.get("response", ""),
                        "timestamp": datetime.now().isoformat(),
                        "evidence_data": {
                            "workflow_evidence": response.get("workflow_evidence", []),
                            "sql_queries_used": response.get("sql_queries_used", {}),
                            "analysis_data": response.get("analysis_data", {}),
                            "agents_used": response.get("agents_used", []),
                            "recommendations": response.get("recommendations", []),
                            "execution_metrics": response.get("execution_metrics", {}),
                            "query_classifications": response.get("query_classifications", [])
                        }
                    })
                else:
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"❌ Error: {response['error']}",
                        "timestamp": datetime.now().isoformat(),
                        "evidence_data": None
                    })
    
    # Display chat messages
    render_chat_messages()

def render_chat_messages():
    """Render all chat messages with evidence panels"""
    if not st.session_state.chat_messages:
        st.info("👋 Welcome! Ask me anything about your financial data. For example:\n\n" +
                "• How many clients have more than 10 projects?\n" +
                "• Who are the top 5 clients by revenue?\n" +
                "• What's the total revenue this year?")
        return
    
    for i, message in enumerate(st.session_state.chat_messages):
        if message["role"] == "user":
            render_user_message(message)
        else:
            render_assistant_message(message, i)

def render_user_message(message: Dict[str, Any]):
    """Render user message"""
    with st.chat_message("user"):
        st.write(message["content"])

def render_assistant_message(message: Dict[str, Any], message_index: int):
    """Render assistant message with evidence panel"""
    with st.chat_message("assistant"):
        # Main response
        st.write(message["content"])
        
        # Evidence panel (if available)
        if message.get("evidence_data"):
            render_evidence_panel(message["evidence_data"], message_index)

def render_evidence_panel(evidence_data: Dict[str, Any], message_index: int):
    """Render evidence panel showing agents used, SQL queries, and data"""
    
    # Recommendations first (if available)
    if evidence_data.get("recommendations"):
        with st.expander("💡 Strategic Recommendations", expanded=False):
            for i, rec in enumerate(evidence_data["recommendations"], 1):
                st.markdown(f"{i}. {rec}")
    
    # Agent Workflow Evidence
    workflow_evidence = evidence_data.get("workflow_evidence", [])
    if workflow_evidence:
        with st.expander("🔍 Agent Workflow Evidence", expanded=False):
            render_workflow_evidence(workflow_evidence)
    
    # SQL Queries and Data
    sql_queries = evidence_data.get("sql_queries_used", {})
    analysis_data = evidence_data.get("analysis_data", {})
    if sql_queries or analysis_data:
        with st.expander("🗄️ SQL Queries & Data Retrieved", expanded=False):
            render_sql_and_data_panel(sql_queries, analysis_data)
    
    # Execution Metrics
    metrics = evidence_data.get("execution_metrics", {})
    if metrics:
        with st.expander("⚡ Performance Metrics", expanded=False):
            render_execution_metrics(metrics)

def render_workflow_evidence(workflow_evidence: List[Dict[str, Any]]):
    """Render workflow evidence in user-readable format"""
    st.markdown("**Agent Execution Timeline:**")
    
    # Group steps by agent type
    agent_steps = {}
    system_steps = []
    
    for step in workflow_evidence:
        step_name = step.get("step", "")
        if "agent" in step_name:
            agent_name = step_name.replace("_agent", "").replace("_", " ").title()
            if agent_name not in agent_steps:
                agent_steps[agent_name] = []
            agent_steps[agent_name].append(step)
        else:
            system_steps.append(step)
    
    # Display system initialization
    if system_steps:
        st.markdown("**🔧 System Process:**")
        for step in system_steps[:3]:  # Show first few system steps
            status_icon = get_status_icon(step.get("status"))
            st.markdown(f"{status_icon} **{format_step_name(step.get('step', ''))}**: {step.get('details', '')}")
    
    # Display agent executions
    if agent_steps:
        st.markdown("**🤖 AI Agents Executed:**")
        for agent_name, steps in agent_steps.items():
            completed_step = next((s for s in steps if s.get("status") == "completed"), None)
            if completed_step:
                results = completed_step.get("results", {})
                
                # Agent summary
                agent_icon = get_agent_icon(agent_name)
                st.markdown(f"{agent_icon} **{agent_name}**")
                st.markdown(f"   └─ {completed_step.get('details', '')}")
                
                # Show key results
                if results:
                    key_metrics = extract_key_metrics(agent_name, results)
                    if key_metrics:
                        st.markdown(f"   └─ **Key Results**: {key_metrics}")

def render_sql_and_data_panel(sql_queries: Dict[str, str], analysis_data: Dict[str, Any]):
    """Render SQL queries and fetched data"""
    
    # Show SQL queries
    if sql_queries:
        st.markdown("**SQL Queries Executed:**")
        for query_type, sql in sql_queries.items():
            if sql:
                query_name = query_type.replace("_sql", "").replace("_", " ").title()
                st.markdown(f"**{query_name} Query:**")
                st.code(sql, language="sql")
                st.markdown("---")
    
    # Show fetched data
    if analysis_data:
        st.markdown("**Data Retrieved:**")
        render_analysis_data_tables(analysis_data)

def render_analysis_data_tables(analysis_data: Dict[str, Any]):
    """Render analysis data as tables"""
    
    for analysis_type, data in analysis_data.items():
        if not data:
            continue
            
        analysis_name = analysis_type.replace("_", " ").title()
        st.markdown(f"**{analysis_name}:**")
        
        # Revenue Analysis
        if analysis_type == "revenue_analysis" and data.get("total_revenue") is not None:
            revenue_df = pd.DataFrame([{
                "Metric": "Total Revenue",
                "Value": f"${data['total_revenue']:,.2f}"
            }, {
                "Metric": "Unique Clients", 
                "Value": data.get('unique_clients', 0)
            }, {
                "Metric": "Total Transactions",
                "Value": data.get('total_transactions', 0)
            }, {
                "Metric": "Avg Transaction Value",
                "Value": f"${data.get('avg_transaction_value', 0):,.2f}"
            }])
            st.dataframe(revenue_df, hide_index=True, use_container_width=True)
        
        # Client Analysis  
        elif analysis_type == "client_analysis" and data.get("clients"):
            clients_data = []
            for client in data["clients"][:10]:  # Limit to top 10
                clients_data.append({
                    "Client": client.get("client_name", ""),
                    "Revenue": f"${client.get('total_revenue', 0):,.2f}",
                    "Transactions": client.get('transaction_count', 0),
                    "Projects": client.get('project_count', 0),
                    "Avg Transaction": f"${client.get('avg_transaction_value', 0):,.2f}",
                    "Margin %": f"{client.get('avg_margin_percent', 0):.1f}%",
                    "Tier": client.get('profitability_tier', 'N/A')
                })
            
            if clients_data:
                clients_df = pd.DataFrame(clients_data)
                st.dataframe(clients_df, hide_index=True, use_container_width=True)
        
        # Project Analysis
        elif analysis_type == "project_analysis" and data.get("clients_with_threshold"):
            projects_data = []
            for client in data["clients_with_threshold"]:
                projects_data.append({
                    "Client": client.get("client_name", ""),
                    "Project Count": client.get('project_count', 0),
                    "Total Revenue": f"${client.get('total_revenue', 0):,.2f}",
                    "Transactions": client.get('total_transactions', 0),
                    "Avg Transaction": f"${client.get('avg_transaction_value', 0):,.2f}"
                })
            
            if projects_data:
                projects_df = pd.DataFrame(projects_data)
                st.dataframe(projects_df, hide_index=True, use_container_width=True)
        
        # Time series data
        elif analysis_type == "revenue_analysis" and data.get("time_series_data"):
            time_series_data = []
            for item in data["time_series_data"]:
                time_series_data.append({
                    "Period": item.get("period", ""),
                    "Revenue": f"${item.get('revenue', 0):,.2f}",
                    "Transactions": item.get('transactions', 0),
                    "Unique Clients": item.get('unique_clients', 0)
                })
            
            if time_series_data:
                ts_df = pd.DataFrame(time_series_data)
                st.dataframe(ts_df, hide_index=True, use_container_width=True)

def render_execution_metrics(metrics: Dict[str, Any]):
    """Render execution metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Duration", f"{metrics.get('total_duration_seconds', 0):.2f}s")
    with col2:
        st.metric("Agents Used", metrics.get('agents_executed', 0))
    with col3:
        st.metric("SQL Queries", metrics.get('sql_queries_generated', 0))
    with col4:
        if metrics.get('start_time'):
            start_time = datetime.fromisoformat(metrics['start_time'].replace('Z', '+00:00'))
            st.metric("Started", start_time.strftime("%H:%M:%S"))

def get_status_icon(status: str) -> str:
    """Get status icon for workflow steps"""
    icons = {
        "completed": "✅",
        "running": "🔄", 
        "starting": "🟡",
        "error": "❌",
        "skipped": "⏸️"
    }
    return icons.get(status, "⚪")

def get_agent_icon(agent_name: str) -> str:
    """Get icon for different agent types"""
    icons = {
        "Revenue Analysis": "💰",
        "Client Analysis": "🏢", 
        "Project Analysis": "🎯",
        "Response Generation": "📝"
    }
    return icons.get(agent_name, "🤖")

def format_step_name(step_name: str) -> str:
    """Format step name for display"""
    return step_name.replace("_", " ").title()

def extract_key_metrics(agent_name: str, results: Dict[str, Any]) -> str:
    """Extract key metrics from agent results"""
    if agent_name == "Revenue Analysis":
        if results.get("total_revenue"):
            return f"Total Revenue: ${results['total_revenue']:,.2f}"
        elif results.get("data_points"):
            return f"Analyzed {results['data_points']} time periods"
    
    elif agent_name == "Client Analysis":
        if results.get("clients_analyzed"):
            return f"Analyzed {results['clients_analyzed']} clients"
        if results.get("top_client"):
            return f"Top client: {results['top_client']}"
    
    elif agent_name == "Project Analysis":
        if results.get("clients_matching"):
            threshold = results.get("project_threshold", 0)
            return f"Found {results['clients_matching']} clients with >{threshold} projects"
    
    elif agent_name == "Response Generation":
        if results.get("recommendations_count"):
            return f"Generated {results['recommendations_count']} recommendations"
    
    return ""

def clear_chat_history():
    """Clear chat history"""
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_messages = []
        st.rerun()

def render_session_info():
    """Render session information"""
    with st.expander("ℹ️ Session Info", expanded=False):
        st.write(f"**Session ID:** {st.session_state.get('session_id', 'Not set')}")
        st.write(f"**Conversation ID:** {st.session_state.get('conversation_id', 'Not set')}")
        st.write(f"**Messages:** {len(st.session_state.get('chat_messages', []))}")
        clear_chat_history()
