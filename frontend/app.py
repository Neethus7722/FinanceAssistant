"""
Unified Finance Analytics Portal - Complete Finance Assistant Dashboard
All analytics features in one comprehensive application
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json

# Import configuration
from config import get_config
config = get_config()

# Page configuration
config.configure_streamlit_page()

# Custom CSS for unified styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .section-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1e3c72;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 3px solid #2a5298;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .insight-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .kpi-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #2a5298;
        margin: 1rem 0;
    }
    .nav-button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        border: none;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .nav-button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .success-metric {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 0.5rem 0;
    }
    .warning-metric {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 0.5rem 0;
    }
    .danger-metric {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 0.5rem 0;
    }
    .chat-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = config.api_base_url

# Initialize session state
if 'current_section' not in st.session_state:
    st.session_state.current_section = 'Executive Dashboard'

def fetch_comprehensive_data():
    """Fetch comprehensive dashboard data from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/dashboard/comprehensive")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching dashboard data: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def fetch_time_series_data():
    """Fetch time-series data from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/time-series")
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

def fetch_client_segments():
    """Fetch client segmentation data from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/client-segments")
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

def fetch_revenue_distribution():
    """Fetch revenue distribution data"""
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/revenue-distribution")
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

def fetch_margin_analysis():
    """Fetch margin analysis data"""
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/margin-analysis")
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

def create_executive_kpis(data):
    """Create executive-level KPI dashboard"""
    if not data or 'overview_metrics' not in data:
        return
    
    metrics = data['overview_metrics']
    clients_data = data.get('top_clients', [])
    
    # Calculate KPIs
    total_revenue = metrics.get('total_revenue', 0)
    total_cost = metrics.get('total_cost', 0)
    total_margin = metrics.get('total_margin', 0)
    client_count = metrics.get('unique_clients', 1)
    
    # Advanced KPIs
    revenue_per_client = total_revenue / client_count if client_count > 0 else 0
    profit_margin = (total_margin / total_revenue * 100) if total_revenue > 0 else 0
    roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
    
    # Client concentration
    top_3_revenue = sum(c.get('revenue', 0) for c in clients_data[:3])
    concentration_ratio = (top_3_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 Total Revenue", f"${total_revenue:,.0f}", 
                 delta=f"{profit_margin:.1f}% Margin")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        roi_delta = "Strong" if roi > 30 else "Moderate" if roi > 15 else "Needs Attention"
        st.metric("📈 ROI", f"{roi:.1f}%", delta=roi_delta)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("👥 Revenue/Client", f"${revenue_per_client:,.0f}",
                 delta=f"{client_count} Total Clients")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        concentration_status = "🔴 High Risk" if concentration_ratio > 60 else "🟡 Medium Risk" if concentration_ratio > 40 else "🟢 Low Risk"
        st.metric("🎯 Client Concentration", f"{concentration_ratio:.1f}%", 
                 delta=concentration_status)
        st.markdown('</div>', unsafe_allow_html=True)

def create_revenue_charts(data):
    """Create comprehensive revenue visualizations using real database data"""
    if not data:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue waterfall chart
        if 'overview_metrics' in data:
            metrics = data['overview_metrics']
            
            categories = ['Total Revenue', 'Total Costs', 'Net Profit']
            values = [
                metrics.get('total_revenue', 0),
                -metrics.get('total_cost', 0),
                metrics.get('total_margin', 0)
            ]
            
            try:
                fig = go.Figure(go.Waterfall(
                    name="Revenue Analysis",
                    orientation="v",
                    measure=["absolute", "relative", "total"],
                    x=categories,
                    textposition="outside",
                    text=[f"${v:,.0f}" for v in [metrics.get('total_revenue', 0), 
                                                metrics.get('total_cost', 0), 
                                                metrics.get('total_margin', 0)]],
                    y=values,
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                ))
                
                fig.update_layout(
                    title="Revenue Waterfall Analysis",
                    title_x=0.5,
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                # Fallback to simple metrics display if plotly fails
                st.subheader("Revenue Analysis")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Revenue", f"${metrics.get('total_revenue', 0):,.0f}")
                with col_b:
                    st.metric("Total Cost", f"${metrics.get('total_cost', 0):,.0f}")
                with col_c:
                    st.metric("Net Profit", f"${metrics.get('total_margin', 0):,.0f}")
    
    with col2:
        # Revenue trends from actual database time-series
        time_series_data = fetch_time_series_data()
        if time_series_data and 'time_series' in time_series_data:
            try:
                trends_df = pd.DataFrame(time_series_data['time_series'])
                fig = px.line(trends_df, x='period_label', y='revenue',
                             title="Revenue Trend Analysis (Database-Driven)",
                             markers=True,
                             line_shape='spline')
                fig.update_layout(height=400, template="plotly_white")
                fig.update_xaxes(title="Time Period")
                fig.update_yaxes(title="Revenue ($)")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                # Fallback to simple table if plotly fails
                st.subheader("Revenue Trend Analysis")
                trends_df = pd.DataFrame(time_series_data['time_series'])
                st.dataframe(trends_df[['period_label', 'revenue']], use_container_width=True)
        elif 'revenue_trends' in data:
            # Fallback to overview trends if time-series not available
            try:
                trends_df = pd.DataFrame(data['revenue_trends'])
                fig = px.line(trends_df, x='period', y='revenue',
                             title="Revenue Overview",
                             markers=True,
                             line_shape='spline')
                fig.update_layout(height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                # Fallback to simple table
                st.subheader("Revenue Overview")
                trends_df = pd.DataFrame(data['revenue_trends'])
                st.dataframe(trends_df, use_container_width=True)

def create_client_analysis_section(data):
    """Create comprehensive client analysis"""
    if not data or 'top_clients' not in data:
        return
    
    clients = data['top_clients']
    df = pd.DataFrame(clients)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Client revenue sunburst
        ids = ["Total"] + [f"Client-{i}" for i in range(len(clients[:10]))]
        labels = ["Total Revenue"] + [client['client'] for client in clients[:10]]
        parents = [""] + ["Total"] * len(clients[:10])
        values = [sum(client['revenue'] for client in clients[:10])] + [client['revenue'] for client in clients[:10]]
        
        fig = go.Figure(go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Percentage: %{percentParent}<extra></extra>',
        ))
        
        fig.update_layout(
            title="Client Revenue Distribution",
            title_x=0.5,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Client profitability matrix
        fig = px.scatter(
            df[:15], x='revenue', y='avg_margin_percent',
            size='transactions', 
            color='profitability_tier',
            hover_data=['client', 'unique_projects'],
            title="Client Profitability Matrix",
            labels={
                'revenue': 'Revenue ($)',
                'avg_margin_percent': 'Average Margin (%)',
                'transactions': 'Number of Transactions'
            },
            color_discrete_map={
                'High Profit': '#28a745',
                'Medium Profit': '#ffc107', 
                'Low Profit': '#dc3545'
            }
        )
        
        # Add quadrant lines
        median_revenue = df['revenue'].median()
        median_margin = df['avg_margin_percent'].median()
        
        fig.add_hline(y=median_margin, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=median_revenue, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(height=500, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

def create_profitability_analysis(data):
    """Create profitability analysis section"""
    if not data:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Margin distribution
        if 'profitability_metrics' in data:
            metrics = data['profitability_metrics']
            
            labels = ['High Margin (>40%)', 'Medium Margin (20-40%)', 'Low Margin (<20%)']
            values = [
                metrics.get('high_margin_transactions', 0),
                metrics.get('medium_margin_transactions', 0),
                metrics.get('low_margin_transactions', 0)
            ]
            
            fig = px.pie(values=values, names=labels, 
                        title="Transaction Margin Distribution",
                        color_discrete_sequence=['#28a745', '#ffc107', '#dc3545'])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Profit vs Revenue scatter
        if 'top_clients' in data:
            clients_df = pd.DataFrame(data['top_clients'][:10])
            fig = px.scatter(clients_df, x='total_margin', y='revenue',
                           size='transactions',
                           color='avg_margin_percent',
                           title="Profit vs Revenue Analysis",
                           color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Top profitable clients
        if 'top_clients' in data:
            clients = data['top_clients'][:8]
            profit_df = pd.DataFrame([{
                'client': c['client'][:15] + '...' if len(c['client']) > 15 else c['client'],
                'margin': c['total_margin']
            } for c in clients])
            
            fig = px.bar(profit_df, x='margin', y='client',
                        orientation='h',
                        title="Top Clients by Profit Margin",
                        color='margin',
                        color_continuous_scale='Blues')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def create_ai_chat_interface():
    """Enhanced AI chat interface with evidence panels and session management"""
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    
    from components.chat_interface import render_chat_interface, render_session_info
    
    st.markdown('<div class="section-header">🤖 AI Financial Assistant</div>', unsafe_allow_html=True)
    
    # Session info in sidebar
    with st.sidebar:
        render_session_info()
    
    # Main chat interface with evidence panels
    render_chat_interface()

def create_business_insights(data):
    """Generate comprehensive business insights from actual database data"""
    if not data:
        return []
    
    insights = []
    metrics = data.get('overview_metrics', {})
    clients = data.get('top_clients', [])
    risk_analysis = data.get('risk_analysis', {})
    benchmark = data.get('benchmark_analysis', {})
    
    total_revenue = metrics.get('total_revenue', 0)
    avg_margin = metrics.get('avg_margin_percent', 0)
    client_count = metrics.get('unique_clients', 0)
    total_records = metrics.get('total_records', 0)
    
    # Database-driven revenue insights
    revenue_per_client = total_revenue / client_count if client_count > 0 else 0
    if total_revenue > 10000000:
        insights.append(f"🚀 **Enterprise Scale**: Your ${total_revenue:,.0f} revenue from {total_records:,} transactions across {client_count} clients puts you in the enterprise category.")
    elif total_revenue > 5000000:
        insights.append(f"🏆 **Market Leader**: Strong ${total_revenue:,.0f} revenue with {client_count} clients shows market leadership position.")
    elif total_revenue > 1000000:
        insights.append(f"📈 **Growth Stage**: ${total_revenue:,.0f} revenue from {client_count} clients shows strong market traction.")
    else:
        insights.append(f"🌱 **Building Foundation**: ${total_revenue:,.0f} revenue across {total_records:,} transactions - focus on scaling proven models.")
    
    # Database-driven profitability insights
    if clients:
        high_margin_clients = len([c for c in clients if c.get('avg_margin_percent', 0) > 40])
        low_margin_clients = len([c for c in clients if c.get('avg_margin_percent', 0) < 20])
        
        if avg_margin > 50:
            insights.append(f"💎 **Premium Positioning**: {avg_margin:.1f}% average margin with {high_margin_clients} high-margin clients indicates exceptional pricing power.")
        elif avg_margin > 30:
            insights.append(f"💪 **Healthy Margins**: {avg_margin:.1f}% average margin across {client_count} clients shows strong profitability.")
        elif avg_margin > 15:
            insights.append(f"⚖️ **Moderate Profitability**: {avg_margin:.1f}% margin with {low_margin_clients} low-margin clients needs optimization focus.")
        else:
            insights.append(f"🔍 **Margin Challenge**: {avg_margin:.1f}% margin across {client_count} clients requires immediate pricing review.")
    
    # Database-driven client insights
    if clients:
        top_client_revenue = clients[0].get('revenue', 0)
        top_client_name = clients[0].get('client', 'Unknown')
        client_concentration = (top_client_revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        high_value_clients = len([c for c in clients if c.get('revenue', 0) > revenue_per_client])
        insights.append(f"🏢 **Client Portfolio**: Top client '{top_client_name}' represents {client_concentration:.1f}% of revenue. {high_value_clients} clients above average performance.")
    
    # Database-driven benchmark insights  
    if benchmark:
        margin_diff = benchmark.get('margin_vs_benchmark', 0)
        revenue_diff = benchmark.get('revenue_per_client_vs_benchmark', 0)
        
        if margin_diff > 0:
            insights.append(f"📊 **Above Benchmark**: Your {avg_margin:.1f}% margin is {margin_diff:+.1f}% above your portfolio average.")
        else:
            insights.append(f"📊 **Below Benchmark**: Your {avg_margin:.1f}% margin is {margin_diff:.1f}% below your portfolio average - opportunity for improvement.")
    
    # Database-driven risk insights
    concentration_risk = risk_analysis.get('client_concentration_top5', 0)
    if concentration_risk > 70:
        insights.append(f"⚠️ **Critical Risk**: Top 5 clients represent {concentration_risk:.1f}% of ${total_revenue:,.0f} revenue - urgent diversification needed.")
    elif concentration_risk > 50:
        insights.append(f"📊 **Moderate Risk**: {concentration_risk:.1f}% concentration in top clients from ${total_revenue:,.0f} total revenue.")
    else:
        insights.append(f"✅ **Well-Diversified**: {concentration_risk:.1f}% concentration shows balanced client portfolio risk.")
    
    return insights

def main():
    # Main header
    st.markdown('<div class="main-header">🏦 NextGen Revenue Insights Assistant</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Complete Financial Intelligence & Analytics Platform</p>', unsafe_allow_html=True)
    
    # Navigation sidebar
    st.sidebar.title("📊 Navigation Menu")
    
    sections = {
        "📈 Executive Dashboard": "executive",
        "💰 Revenue Analytics": "revenue", 
        "🏢 Client Performance": "clients",
        "📊 Profitability Analysis": "profitability",
        "🤖 AI Assistant": "ai_chat",
        "🎯 Business Insights": "insights"
    }
    
    selected_section = st.sidebar.selectbox(
        "Choose Analysis Section",
        list(sections.keys()),
        index=0
    )
    
    # Load data once
    with st.spinner("Loading comprehensive financial data..."):
        dashboard_data = fetch_comprehensive_data()
    
    if not dashboard_data:
        st.error("⚠️ Unable to fetch financial data. Please ensure the backend is running on port 8001.")
        st.info("💡 Try restarting the backend server: `uvicorn backend.main:app --reload --port 8001`")
        return
    
    # Content based on selection
    if selected_section == "📈 Executive Dashboard":
        st.markdown('<div class="section-header">📈 Executive Dashboard</div>', unsafe_allow_html=True)
        
        # Executive KPIs
        create_executive_kpis(dashboard_data)
        
        # Revenue charts
        create_revenue_charts(dashboard_data)
        
        # Quick insights
        st.markdown('<div class="section-header">🎯 Key Business Insights</div>', unsafe_allow_html=True)
        insights = create_business_insights(dashboard_data)
        for insight in insights[:3]:  # Show top 3 insights
            st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
    
    elif selected_section == "💰 Revenue Analytics":
        st.markdown('<div class="section-header">💰 Revenue Analytics</div>', unsafe_allow_html=True)
        
        # Revenue metrics overview
        if 'overview_metrics' in dashboard_data:
            metrics = dashboard_data['overview_metrics']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Revenue", f"${metrics.get('total_revenue', 0):,.0f}")
            with col2:
                st.metric("Unique Clients", f"{metrics.get('unique_clients', 0):,}")
            with col3:
                st.metric("Total Projects", f"{metrics.get('unique_projects', 0):,}")
            with col4:
                st.metric("Avg Margin", f"{metrics.get('avg_margin_percent', 0):.1f}%")
        
        # Revenue distribution analysis - using real database segmentation
        segments_data = fetch_client_segments()
        if segments_data and 'client_segments' in segments_data:
            st.subheader("📊 Client Segmentation Analysis (Database-Driven)")
            
            segments_df = pd.DataFrame(segments_data['client_segments'])
            
            col1, col2 = st.columns(2)
            with col1:
                # Revenue segment pie chart
                revenue_segments = segments_df.groupby('revenue_segment').agg({
                    'client_count': 'sum',
                    'segment_revenue': 'sum'
                }).reset_index()
                
                fig = px.pie(revenue_segments, values='client_count', names='revenue_segment', 
                           title="Client Count by Revenue Segment")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Revenue by segment
                fig = px.bar(revenue_segments, x='revenue_segment', y='segment_revenue',
                           title="Revenue by Segment", color='segment_revenue')
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed segmentation table
            st.subheader("� Detailed Segmentation Analysis")
            display_segments = segments_df.copy()
            display_segments['segment_revenue'] = display_segments['segment_revenue'].apply(lambda x: f"${x:,.0f}")
            display_segments['avg_revenue_per_client'] = display_segments['avg_revenue_per_client'].apply(lambda x: f"${x:,.0f}")
            display_segments['avg_segment_margin'] = display_segments['avg_segment_margin'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_segments, use_container_width=True)
        
        else:
            # Fallback to distribution data if segments not available
            distribution_data = fetch_revenue_distribution()
            if distribution_data and 'revenue_distribution' in distribution_data:
                dist_df = pd.DataFrame(distribution_data['revenue_distribution'])
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.pie(dist_df, values='client_count', names='segment', 
                               title="Client Count by Revenue Segment")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(dist_df, x='segment', y='total_revenue',
                               title="Revenue by Segment", color='total_revenue')
                    st.plotly_chart(fig, use_container_width=True)
        
        # Revenue trends and analysis - enhanced with database time-series
        create_revenue_charts(dashboard_data)
        
        # Time-series analysis from database
        time_series_data = fetch_time_series_data()
        if time_series_data and 'time_series' in time_series_data:
            st.subheader("📈 Advanced Time-Series Analysis")
            
            ts_df = pd.DataFrame(time_series_data['time_series'])
            
            col1, col2 = st.columns(2)
            with col1:
                # Revenue and margin trends
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig.add_trace(
                    go.Scatter(x=ts_df['period_label'], y=ts_df['revenue'], 
                              name="Revenue", line=dict(color='blue')),
                    secondary_y=False,
                )
                
                fig.add_trace(
                    go.Scatter(x=ts_df['period_label'], y=ts_df['total_margin'], 
                              name="Margin", line=dict(color='green')),
                    secondary_y=True,
                )
                
                fig.update_layout(title="Revenue & Margin Trends")
                fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
                fig.update_yaxes(title_text="Margin ($)", secondary_y=True)
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Transactions and clients over time
                fig = px.bar(ts_df, x='period_label', y='transactions',
                           title="Transaction Volume by Period",
                           color='unique_clients',
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
    
    elif selected_section == "🏢 Client Performance":
        st.markdown('<div class="section-header">🏢 Client Performance Analysis</div>', unsafe_allow_html=True)
        
        # Client analysis section with real database segmentation
        create_client_analysis_section(dashboard_data)
        
        # Enhanced client segmentation from database
        segments_data = fetch_client_segments()
        if segments_data and 'segments' in segments_data:
            st.subheader("🎯 Advanced Client Segmentation")
            
            segments_df = pd.DataFrame(segments_data['segments'])
            
            col1, col2 = st.columns(2)
            with col1:
                # Revenue distribution by segment
                fig = px.pie(segments_df, values='total_revenue', names='segment_label',
                           title="Revenue Distribution by Client Segment",
                           color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Margin analysis by segment
                fig = px.scatter(segments_df, x='total_revenue', y='avg_margin_percent',
                               size='client_count', hover_name='segment_label',
                               title="Revenue vs Margin by Segment",
                               labels={'total_revenue': 'Total Revenue ($)', 
                                      'avg_margin_percent': 'Average Margin %'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Segment performance table
            st.subheader("Client Segment Performance")
            display_df = segments_df.copy()
            display_df['total_revenue'] = display_df['total_revenue'].apply(lambda x: f"${x:,.0f}")
            display_df['avg_margin_percent'] = display_df['avg_margin_percent'].apply(lambda x: f"{x:.1f}%")
            display_df.columns = ['Segment', 'Clients', 'Revenue', 'Avg Margin %', 'Avg Billing']
            st.dataframe(display_df, use_container_width=True)
        
        # Client performance table
        if 'top_clients' in dashboard_data:
            st.subheader("📊 Detailed Client Performance Metrics")
            clients_df = pd.DataFrame(dashboard_data['top_clients'][:20])
            
            # Format for display
            display_df = clients_df[['client', 'revenue', 'transactions', 'avg_margin_percent', 
                                   'profitability_tier', 'volume_tier', 'revenue_percentage']].copy()
            display_df['revenue'] = display_df['revenue'].apply(lambda x: f"${x:,.0f}")
            display_df['avg_margin_percent'] = display_df['avg_margin_percent'].apply(lambda x: f"{x:.1f}%")
            display_df['revenue_percentage'] = display_df['revenue_percentage'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(display_df, use_container_width=True)
    
    elif selected_section == "📊 Profitability Analysis":
        st.markdown('<div class="section-header">📊 Profitability Analysis</div>', unsafe_allow_html=True)
        
        # Profitability overview
        create_profitability_analysis(dashboard_data)
        
        # Margin analysis
        margin_data = fetch_margin_analysis()
        if margin_data and 'margin_analysis' in margin_data:
            st.subheader("📈 Margin Volatility Analysis")
            
            margins = margin_data['margin_analysis']
            df = pd.DataFrame(margins[:15])  # Top 15
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['client'],
                y=df['avg_margin'],
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=df['max_margin'] - df['avg_margin'],
                    arrayminus=df['avg_margin'] - df['min_margin']
                ),
                mode='markers',
                marker=dict(
                    size=df['transactions'] * 2,
                    color=df['margin_volatility'],
                    colorscale='RdYlBu_r',
                    showscale=True
                ),
                name='Margin Range'
            ))
            
            fig.update_layout(
                title="Client Margin Volatility Analysis",
                xaxis_title="Client",
                yaxis_title="Average Margin (%)",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    elif selected_section == "🤖 AI Assistant":
        create_ai_chat_interface()
    
    elif selected_section == "🎯 Business Insights":
        st.markdown('<div class="section-header">🎯 AI-Powered Business Insights</div>', unsafe_allow_html=True)
        
        # Comprehensive insights
        insights = create_business_insights(dashboard_data)
        
        st.subheader("🚀 Strategic Recommendations")
        for i, insight in enumerate(insights, 1):
            st.markdown(f'<div class="insight-box">{i}. {insight}</div>', unsafe_allow_html=True)
        
        # Benchmark comparison
        if 'benchmark_analysis' in dashboard_data:
            benchmark = dashboard_data['benchmark_analysis']
            
            st.subheader("📊 Industry Benchmark Comparison")
            col1, col2 = st.columns(2)
            
            with col1:
                margin_diff = benchmark.get('margin_vs_benchmark', 0)
                if margin_diff > 0:
                    st.markdown(f'<div class="success-metric">✅ Margin Performance: <strong>+{margin_diff:.1f}%</strong> above industry average</div>', unsafe_allow_html=True)
                elif margin_diff < 0:
                    st.markdown(f'<div class="warning-metric">⚠️ Margin Performance: <strong>{margin_diff:.1f}%</strong> below industry average</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="metric-container">📊 Margin Performance: <strong>At industry average</strong></div>', unsafe_allow_html=True)
            
            with col2:
                revenue_diff = benchmark.get('revenue_per_client_vs_benchmark', 0)
                if revenue_diff > 0:
                    st.markdown(f'<div class="success-metric">✅ Revenue/Client: <strong>${revenue_diff:+,.0f}</strong> above industry average</div>', unsafe_allow_html=True)
                elif revenue_diff < 0:
                    st.markdown(f'<div class="warning-metric">⚠️ Revenue/Client: <strong>${revenue_diff:+,.0f}</strong> below industry average</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="metric-container">📊 Revenue/Client: <strong>At industry average</strong></div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🏦 <strong>NextGen Revenue Insights Assistant</strong> | Powered by AI & Advanced Analytics</p>
        <p>Real-time financial insights • Multi-agent analysis • Strategic recommendations</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
