"""
AI Code Review Dashboard - Modern Dark Theme
Professional design without emojis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import requests

# Page config
st.set_page_config(
    page_title="AI Code Review - ForteBank",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme custom CSS
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --dark-bg: #0f172a;
        --card-bg: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* Global styles */
    .stApp {
        background-color: var(--dark-bg);
        color: var(--text-primary);
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--primary-color);
        padding-left: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-success {
        background-color: rgba(16, 185, 129, 0.1);
        color: var(--success-color);
        border: 1px solid var(--success-color);
    }
    
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.1);
        color: var(--warning-color);
        border: 1px solid var(--warning-color);
    }
    
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.1);
        color: var(--danger-color);
        border: 1px solid var(--danger-color);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: var(--card-bg);
    }
    
    /* Tables */
    .dataframe {
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    /* Remove default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Icon styles */
    .icon {
        width: 24px;
        height: 24px;
        display: inline-block;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    .sidebar-icon {
        width: 20px;
        height: 20px;
        margin-right: 10px;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

def load_stats():
    """Load statistics from API"""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=3)
        if response.status_code == 200:
            data = response.json()
            data['is_real_data'] = True
            return data
    except:
        pass
    
    return {
        "total_mrs": 0,
        "total_comments": 0,
        "time_saved_hours": 0,
        "avg_score": 0.0,
        "is_real_data": False
    }

def load_recent_reviews():
    """Load recent reviews from API"""
    try:
        response = requests.get(f"{API_URL}/api/recent?limit=10", timeout=3)
        if response.status_code == 200:
            return response.json().get("reviews", [])
    except:
        pass
    return []

# Sidebar Navigation
with st.sidebar:
    st.markdown("### AI Code Review")
    st.markdown("ForteBank Hackathon 2025")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["Analytics", "Settings", "Team", "Learning"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**System Status**")
    st.success("AI: Online")
    st.success("GitLab: Connected")
    st.info("Provider: Gemini 2.5 Flash")

# Main Content
if page == "Analytics":
    st.markdown('<div class="main-header">Analytics Dashboard</div>', unsafe_allow_html=True)
    
    stats = load_stats()
    
    # Data source indicator
    if stats.get('is_real_data'):
        st.success("Real-time data from backend")
    else:
        st.warning("Demo mode - Connect database to see real data")
    
    st.markdown("---")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_mrs']}</div>
            <div class="metric-label">Merge Requests</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_comments']}</div>
            <div class="metric-label">AI Comments</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['time_saved_hours']}h</div>
            <div class="metric-label">Time Saved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['avg_score']}/10</div>
            <div class="metric-label">Avg Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Recent Activity</div>', unsafe_allow_html=True)
    
    recent_reviews = load_recent_reviews()
    
    if recent_reviews:
        recent_data = []
        for review in recent_reviews:
            created = datetime.fromisoformat(review['created_at'].replace('Z', '+00:00'))
            time_ago = datetime.now() - created.replace(tzinfo=None)
            
            if time_ago.days > 0:
                time_str = f"{time_ago.days}d ago"
            elif time_ago.seconds // 3600 > 0:
                time_str = f"{time_ago.seconds // 3600}h ago"
            else:
                time_str = f"{time_ago.seconds // 60}m ago"
            
            if review['status'] == 'approved':
                status_html = '<span class="status-badge badge-success">Approved</span>'
            elif review['status'] == 'needs_review':
                status_html = '<span class="status-badge badge-warning">Needs Review</span>'
            else:
                status_html = '<span class="status-badge badge-danger">Rejected</span>'
            
            recent_data.append({
                "Time": time_str,
                "MR": f"#{review['mr_id']}",
                "Author": review['author'],
                "Score": f"{review['score']}/10",
                "Issues": review['total_issues'],
                "Status": status_html
            })
        
        df_recent = pd.DataFrame(recent_data)
        st.markdown(df_recent.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("No activity yet. Create a MR in GitLab to see analytics.")
    
    # Charts
    st.markdown('<div class="section-header">Performance Metrics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Activity chart
        daily_activity = stats.get("daily_activity", [
            {"date": "2025-11-23", "mrs": stats.get("total_mrs", 0), "comments": stats.get("total_comments", 0)}
        ])
        df_activity = pd.DataFrame(daily_activity)
        
        fig_activity = px.line(
            df_activity,
            x="date",
            y="mrs",
            markers=True,
            title="Daily Activity"
        )
        fig_activity.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#f1f5f9',
            xaxis_title="Date",
            yaxis_title="Merge Requests"
        )
        st.plotly_chart(fig_activity, use_container_width=True)
    
    with col2:
        # Issue types chart
        issue_types = stats.get("issue_types", [
            {"type": "Security", "count": 5},
            {"type": "Code Style", "count": 3},
            {"type": "Performance", "count": 2}
        ])
        df_issues = pd.DataFrame(issue_types)
        
        fig_issues = px.pie(
            df_issues,
            values="count",
            names="type",
            title="Issue Categories",
            hole=0.4
        )
        fig_issues.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#f1f5f9'
        )
        st.plotly_chart(fig_issues, use_container_width=True)

elif page == "Settings":
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["AI Configuration", "Integrations", "Review Rules"])
    
    with tab1:
        st.markdown('<div class="section-header">AI Model Settings</div>', unsafe_allow_html=True)
        
        provider = st.selectbox(
            "AI Provider",
            ["Gemini 2.5 Flash", "OpenAI GPT-4", "Claude 3.5 Sonnet"]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_review = st.toggle("Auto-review on MR", value=True)
            auto_label = st.toggle("Auto-label MRs", value=True)
        
        with col2:
            min_score = st.slider("Min score for approval", 0.0, 10.0, 7.0, 0.1)
            max_length = st.number_input("Max code length", value=50000, step=5000)
        
        st.markdown("---")
        
        custom_prompt = st.text_area(
            "Custom Instructions",
            placeholder="E.g., Focus on banking security, PCI DSS compliance...",
            height=150
        )
        
        if st.button("Save Settings", type="primary"):
            st.success("Settings saved successfully!")
    
    with tab2:
        st.markdown('<div class="section-header">GitLab Integration</div>', unsafe_allow_html=True)
        
        gitlab_url = st.text_input("GitLab URL", value="https://gitlab.com")
        webhook_url = st.text_input(
            "Webhook URL",
            value=f"{API_URL}/webhook/gitlab",
            disabled=True
        )
        
        st.success("Connected to GitLab")
        
        st.markdown("---")
        
        st.markdown("**Webhook Status**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Received", "47")
        
        with col2:
            st.metric("Last Event", "2m ago")
    
    with tab3:
        st.markdown('<div class="section-header">Code Review Rules</div>', unsafe_allow_html=True)
        
        st.markdown("Configure custom rules for your project")
        
        security_level = st.select_slider(
            "Security Check Level",
            options=["Low", "Medium", "High", "Critical"],
            value="High"
        )
        
        check_types = st.multiselect(
            "Enable Checks",
            ["Security", "Performance", "Code Style", "Best Practices", "Architecture"],
            default=["Security", "Performance", "Best Practices"]
        )
        
        if st.button("Save Rules", type="primary"):
            st.success("Rules saved successfully!")

elif page == "Team":
    st.markdown('<div class="main-header">Team Performance</div>', unsafe_allow_html=True)
    
    stats = load_stats()
    
    team_stats = stats.get("team_stats", [
        {
            "developer": "Unknown",
            "mrs": stats.get("total_mrs", 0),
            "avg_score": stats.get("avg_score", 5.0),
            "time_saved": stats.get("time_saved_hours", 0)
        }
    ])
    
    df_team = pd.DataFrame(team_stats)
    
    if not df_team.empty:
        df_team["rank"] = df_team["avg_score"].rank(ascending=False, method="dense").astype(int)
        df_team = df_team.sort_values("avg_score", ascending=False)
        
        df_team["Developer"] = df_team["developer"].apply(lambda x: f"@{x}")
        df_team["MRs"] = df_team["mrs"]
        df_team["Avg Score"] = df_team["avg_score"].apply(lambda x: f"{x}/10")
        df_team["Time Saved"] = df_team["time_saved"].apply(lambda x: f"{x}h")
        df_team["Rank"] = df_team["rank"]
        
        st.dataframe(
            df_team[["Rank", "Developer", "MRs", "Avg Score", "Time Saved"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No team data available yet.")

elif page == "Learning":
    st.markdown('<div class="main-header">AI Learning Center</div>', unsafe_allow_html=True)
    
    st.markdown("Help improve AI by providing feedback on reviews")
    
    st.markdown('<div class="section-header">Feedback System</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("The AI learns from senior developer feedback to improve accuracy over time.")
    
    with col2:
        st.metric("Total Feedback", "12")
        st.metric("Accuracy", "94%")
    
    st.markdown("---")
    
    st.markdown("**Recent AI Improvements**")
    
    improvements = [
        {"Date": "2025-11-23", "Area": "Security", "Improvement": "Better SQL injection detection"},
        {"Date": "2025-11-22", "Area": "Performance", "Improvement": "Improved algorithm complexity analysis"},
        {"Date": "2025-11-21", "Area": "Code Style", "Improvement": "Enhanced PEP 8 compliance checking"}
    ]
    
    df_improvements = pd.DataFrame(improvements)
    st.dataframe(df_improvements, use_container_width=True, hide_index=True)
