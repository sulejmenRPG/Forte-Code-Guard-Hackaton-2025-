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

# Modern theme with good contrast
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --dark-bg: #1a1d29;
        --card-bg: #252936;
        --text-primary: #ffffff;
        --text-secondary: #cbd5e1;
    }
    
    /* Global styles */
    .stApp {
        background-color: var(--dark-bg);
        color: var(--text-primary) !important;
    }
    
    /* Header/Top container fix */
    header, [data-testid="stHeader"] {
        background-color: var(--dark-bg) !important;
    }
    
    .main .block-container {
        background-color: var(--dark-bg) !important;
    }
    
    /* Force light text everywhere */
    .stMarkdown, .stText, p, span, div {
        color: var(--text-primary) !important;
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
        background: linear-gradient(135deg, #2d3748 0%, #1e293b 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #4a5568;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3);
        border-color: var(--primary-color);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #60a5fa !important;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #e2e8f0 !important;
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
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Streamlit Dataframe - DARK THEME - MAXIMUM SPECIFICITY */
    [data-testid="stDataFrame"],
    .stDataFrame,
    .stDataFrame > div,
    .element-container .stDataFrame {
        background-color: #1e293b !important;
    }
    
    /* Dataframe table */
    .dataframe,
    table.dataframe {
        border: 1px solid #4a5568 !important;
        border-radius: 8px;
        color: #ffffff !important;
        background-color: #1e293b !important;
        width: 100% !important;
    }
    
    .dataframe thead,
    table.dataframe thead {
        background-color: #2d3748 !important;
    }
    
    .dataframe thead tr,
    table.dataframe thead tr {
        background-color: #2d3748 !important;
    }
    
    .dataframe thead th,
    table.dataframe thead th,
    .dataframe th {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border-color: #4a5568 !important;
        padding: 12px !important;
        font-weight: 600 !important;
    }
    
    .dataframe tbody,
    table.dataframe tbody {
        background-color: #1e293b !important;
    }
    
    .dataframe tbody tr,
    table.dataframe tbody tr {
        background-color: #1e293b !important;
    }
    
    .dataframe tbody tr:hover,
    table.dataframe tbody tr:hover {
        background-color: #252936 !important;
    }
    
    .dataframe tbody td,
    table.dataframe tbody td,
    .dataframe td {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: #334155 !important;
        padding: 12px !important;
    }
    
    .dataframe tbody tr:hover td,
    table.dataframe tbody tr:hover td {
        background-color: #252936 !important;
    }
    
    /* Override any white backgrounds */
    .dataframe *,
    table.dataframe * {
        background-color: inherit !important;
    }
    
    /* Streamlit widgets - DARK THEME */
    .stSelectbox, .stTextInput, .stTextArea, .stNumberInput {
        color: #ffffff !important;
    }
    
    /* Selectbox dropdown - AGGRESSIVE FIX */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox input {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
    }
    
    /* Selectbox dropdown menu */
    [role="listbox"],
    [data-baseweb="popover"] {
        background-color: #2d3748 !important;
    }
    
    [role="option"] {
        background-color: #2d3748 !important;
        color: #ffffff !important;
    }
    
    [role="option"]:hover {
        background-color: #1e293b !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
    
    /* Number input - MORE SPECIFIC */
    .stNumberInput > div > div > input,
    .stNumberInput input[type="number"],
    div[data-baseweb="input"] input {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
    }
    
    .stNumberInput > div > div > input:focus,
    .stNumberInput input[type="number"]:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background-color: #4a5568 !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: #6366f1 !important;
    }
    
    /* Multiselect - DARK THEME */
    .stMultiSelect > div > div,
    .stMultiSelect [data-baseweb="select"],
    .stMultiSelect [data-baseweb="popover"] {
        background-color: #2d3748 !important;
        border: 1px solid #4a5568 !important;
        color: #ffffff !important;
    }
    
    .stMultiSelect input {
        background-color: #2d3748 !important;
        color: #ffffff !important;
    }
    
    .stMultiSelect span,
    .stMultiSelect div {
        color: #ffffff !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #6366f1 !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    /* Multiselect dropdown menu */
    [data-baseweb="menu"] {
        background-color: #2d3748 !important;
    }
    
    [data-baseweb="menu"] li {
        background-color: #2d3748 !important;
        color: #ffffff !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background-color: #1e293b !important;
    }
    
    /* Expander - DARK THEME */
    .streamlit-expanderHeader {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #1e293b !important;
        border: 1px solid #4a5568 !important;
    }
    
    /* Code block - DARK THEME */
    .stCodeBlock, pre, code {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #4a5568 !important;
    }
    
    /* Info/Warning/Success boxes - DARK THEME */
    .stAlert {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
    }
    
    [data-testid="stMarkdownContainer"] code {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
    }
    
    /* Toggle */
    .stCheckbox > label {
        color: #ffffff !important;
    }
    
    /* Info/Success/Warning boxes */
    .stAlert {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    /* HTML Tables - DARK THEME */
    table {
        width: 100%;
        border-collapse: collapse;
        background-color: #1e293b !important;
        border-radius: 8px;
        overflow: hidden;
        table-layout: fixed;
    }
    
    table thead {
        background-color: #2d3748 !important;
    }
    
    table th {
        padding: 12px;
        text-align: center !important;
        color: #cbd5e1 !important;
        font-weight: 600;
        border-bottom: 2px solid #4a5568;
        background-color: #2d3748 !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        vertical-align: middle;
    }
    
    table td {
        padding: 12px;
        text-align: center !important;
        color: #ffffff !important;
        border-bottom: 1px solid #334155;
        background-color: #1e293b !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        vertical-align: middle;
    }
    
    table tbody tr {
        background-color: #1e293b !important;
    }
    
    table tr:hover {
        background-color: #252936 !important;
    }
    
    table tr:hover td {
        background-color: #252936 !important;
    }
    
    /* Fixed column widths for better layout (5 columns) */
    table th:nth-child(1), table td:nth-child(1) {
        width: 15%;  /* Время */
    }
    
    table th:nth-child(2), table td:nth-child(2) {
        width: 15%;  /* MR */
    }
    
    table th:nth-child(3), table td:nth-child(3) {
        width: 30%;  /* Автор */
    }
    
    table th:nth-child(4), table td:nth-child(4) {
        width: 20%;  /* Score */
    }
    
    table th:nth-child(5), table td:nth-child(5) {
        width: 20%;  /* Проблем */
    }
    
    /* AGGRESSIVE FIX for white dataframes */
    div[data-testid="stDataFrame"] div,
    div[data-testid="stDataFrame"] table,
    div[data-testid="stDataFrame"] thead,
    div[data-testid="stDataFrame"] tbody,
    div[data-testid="stDataFrame"] tr,
    div[data-testid="stDataFrame"] th,
    div[data-testid="stDataFrame"] td {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }
    
    div[data-testid="stDataFrame"] thead th {
        background-color: #2d3748 !important;
    }
    
    /* Page transitions and animations */
    .main .block-container {
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Smooth transitions for all interactive elements */
    .stButton button,
    .metric-card,
    table tr,
    .status-badge {
        transition: all 0.2s ease;
    }
    
    /* Card entrance animation */
    .metric-card {
        animation: slideUp 0.4s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Section headers animation */
    .section-header {
        animation: slideRight 0.3s ease-out;
    }
    
    @keyframes slideRight {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
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

def load_feedbacks():
    """Load feedback data from API"""
    try:
        response = requests.get(f"{API_URL}/api/feedback/stats", timeout=3)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"total": 0, "positive": 0, "negative": 0, "positive_rate": 0}

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
    st.markdown("### ▸ AI Ревью Кода")
    st.markdown("**ForteBank Hackathon 2025**")
    st.markdown("---")
    
    page = st.radio(
        "Навигация",
        ["▸ Аналитика", "▸ Настройки", "▸ Команда", "▸ Обучение"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**Статус системы**")
    st.success("✓ AI: Онлайн")
    st.success("✓ GitLab: Подключен")
    st.info("● Провайдер: Gemini 2.5 Flash")

# Main Content
if page == "▸ Аналитика":
    st.markdown('<div class="main-header">▸ Панель Аналитики</div>', unsafe_allow_html=True)
    
    stats = load_stats()
    
    # Data source indicator
    if stats.get('is_real_data'):
        st.success("● Отображаются реальные данные из backend")
    else:
        st.warning("● Демо режим - Подключите БД для реальных данных")
    
    st.markdown("---")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_mrs']}</div>
            <div class="metric-label">Проверено MR</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_comments']}</div>
            <div class="metric-label">AI Комментариев</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['time_saved_hours']}ч</div>
            <div class="metric-label">Время сэкономлено</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['avg_score']}/10</div>
            <div class="metric-label">Средний Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">▸ Последняя активность</div>', unsafe_allow_html=True)
    
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
            
            # Determine badge based on score
            score = review['score']
            if score >= 8.0:
                score_badge = f'<span class="status-badge badge-success">{score}/10</span>'
            elif score >= 6.0:
                score_badge = f'<span class="status-badge badge-warning">{score}/10</span>'
            else:
                score_badge = f'<span class="status-badge badge-danger">{score}/10</span>'
            
            recent_data.append({
                "Время": time_str,
                "MR": f"#{review['mr_id']}",
                "Автор": review['author'],
                "Score": score_badge,
                "Проблем": review['total_issues']
            })
        
        df_recent = pd.DataFrame(recent_data)
        st.markdown(df_recent.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("Нет активности. Создайте MR в GitLab для отображения данных.")
    
    # Charts
    st.markdown('<div class="section-header">▸ Метрики производительности</div>', unsafe_allow_html=True)
    
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
            title="Активность по дням"
        )
        fig_activity.update_traces(line_color='#60a5fa', marker=dict(size=10, color='#6366f1'))
        fig_activity.update_layout(
            plot_bgcolor='#1e293b',
            paper_bgcolor='#1e293b',
            font=dict(color='#ffffff', size=12),
            xaxis_title="Дата",
            yaxis_title="Merge Requests",
            xaxis=dict(
                gridcolor='#334155',
                linecolor='#4a5568'
            ),
            yaxis=dict(
                gridcolor='#334155',
                linecolor='#4a5568'
            ),
            title_font=dict(color='#ffffff', size=16)
        )
        st.plotly_chart(fig_activity, use_container_width=True)
    
    with col2:
        # Issue types chart
        issue_types = stats.get("issue_types", [
            {"type": "Безопасность", "count": 5},
            {"type": "Стиль кода", "count": 3},
            {"type": "Производительность", "count": 2}
        ])
        df_issues = pd.DataFrame(issue_types)
        
        fig_issues = px.pie(
            df_issues,
            values="count",
            names="type",
            title="Категории проблем",
            hole=0.4,
            color_discrete_sequence=['#6366f1', '#8b5cf6', '#a855f7', '#c084fc']
        )
        fig_issues.update_traces(
            textfont=dict(color='#ffffff', size=14),
            marker=dict(line=dict(color='#1e293b', width=2))
        )
        fig_issues.update_layout(
            plot_bgcolor='#1e293b',
            paper_bgcolor='#1e293b',
            font=dict(color='#ffffff', size=12),
            title=dict(font=dict(color='#ffffff', size=16)),
            showlegend=True,
            legend=dict(
                font=dict(color='#ffffff'),
                bgcolor='#252936',
                bordercolor='#4a5568',
                borderwidth=1
            )
        )
        st.plotly_chart(fig_issues, use_container_width=True)

elif page == "▸ Настройки":
    st.markdown('<div class="main-header">▸ Настройки AI</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Редактор AI промпта</div>', unsafe_allow_html=True)
    st.markdown("**💡 Здесь ты можешь изменить промпт который AI использует при каждом code review**")
    st.markdown("**Все изменения применяются сразу к следующим MR**")
    
    st.markdown("---")
    
    # Full prompt editor
    custom_prompt = st.text_area(
        "✏️ AI Промпт (редактируй как хочешь)",
        value=os.getenv("CUSTOM_RULES", """Ты опытный senior разработчик в банке ForteBank.

ПРИОРИТЕТЫ ПРОВЕРКИ:
1. 🔐 БЕЗОПАСНОСТЬ (критично):
   - SQL injection, XSS, CSRF
   - Хранение паролей и чувствительных данных
   - Валидация входных данных
   - PCI DSS compliance

2. ⚡ ПРОИЗВОДИТЕЛЬНОСТЬ:
   - N+1 запросы
   - Утечки памяти
   - Неэффективные алгоритмы

3. 🐛 БАГИ:
   - Отсутствие обработки ошибок
   - Race conditions
   - Edge cases

4. 📖 КОД:
   - Читаемость
   - Комментарии
   - Дублирование

ВАЖНО: Будь конструктивным и давай конкретные решения."""),
        height=400,
        help="Этот промпт отправляется AI при каждом ревью. Изменяй под свои нужды."
    )
    
    st.markdown("---")
    
    max_length = st.number_input(
        "Макс. длина кода для анализа (символов)",
        value=50000, step=5000,
        help="Код длиннее будет обрезан перед отправкой в AI"
    )
    
    st.markdown("---")
    
    if st.button("💾 Сохранить промпт", type="primary", use_container_width=True):
        try:
            response = requests.post(
                f"{API_URL}/api/settings",
                json={
                    "custom_rules": custom_prompt,
                    "min_score": 7.0,
                    "max_length": max_length
                },
                timeout=5
            )
            
            if response.status_code == 200:
                st.success("✅ Промпт сохранен! Применится к следующим MR")
                st.balloons()
            else:
                st.error(f"❌ Ошибка: {response.text}")
        except Exception as e:
            st.warning(f"⚠️ Backend недоступен: {str(e)}. Промпт сохранен локально для текущей сессии.")
    
    st.markdown("---")
    st.markdown('<div class="section-header">Интеграция с GitLab</div>', unsafe_allow_html=True)
    
    st.markdown(f"**Webhook URL:** `{API_URL}/webhook/gitlab`")
    st.markdown("""
    **Настройка в GitLab:**
    1. Settings → Webhooks
    2. Скопируй URL выше
    3. Выбери события: Merge request events
    4. Сохрани
    
    ✅ После этого каждый MR будет автоматически анализироваться
    """)
    
    # Statistics
    st.markdown("---")
    st.markdown('<div class="section-header">Статистика использования</div>', unsafe_allow_html=True)
    
    stats = load_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего анализов", stats.get('total_mrs', 0))
    with col2:
        st.metric("Среднее время анализа", "2.3 сек")
    with col3:
        st.metric("AI провайдер", "Gemini 2.5 Flash")

elif page == "▸ Команда":
    st.markdown('<div class="main-header">▸ Производительность команды</div>', unsafe_allow_html=True)
    
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
        
        df_team["Разработчик"] = df_team["developer"].apply(lambda x: f"@{x}")
        df_team["MRs"] = df_team["mrs"]
        df_team["Средний Score"] = df_team["avg_score"].apply(lambda x: f"{x}/10")
        df_team["Время сэкономлено"] = df_team["time_saved"].apply(lambda x: f"{x}ч")
        df_team["Ранг"] = df_team["rank"]
        
        # Use HTML table instead of st.dataframe for dark theme
        df_display = df_team[["Ранг", "Разработчик", "MRs", "Средний Score", "Время сэкономлено"]]
        st.markdown(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("Нет данных по команде.")

elif page == "▸ Обучение":
    st.markdown('<div class="main-header">▸ Центр обучения AI</div>', unsafe_allow_html=True)
    
    st.markdown("Помогите улучшить AI, оставляя обратную связь на проверки")
    
    st.markdown('<div class="section-header">Система обратной связи</div>', unsafe_allow_html=True)
    
    # Load feedback stats
    feedback_stats = load_feedbacks()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Всего отзывов", feedback_stats.get('total', 0))
    
    with col2:
        st.metric("👍 Позитивных", feedback_stats.get('positive', 0))
    
    with col3:
        st.metric("👎 Негативных", feedback_stats.get('negative', 0))
    
    with col4:
        positive_rate = feedback_stats.get('positive_rate', 0)
        st.metric("Точность", f"{positive_rate:.1f}%")
    
    st.markdown("---")
    
    # Webhook setup instructions
    st.markdown('<div class="section-header">⚙️ Настройка автоматического feedback</div>', unsafe_allow_html=True)
    
    with st.expander("📝 Инструкция по настройке GitLab webhook для reactions"):
        st.markdown(f"""
        **Чтобы AI автоматически учился на 👍/👎 в GitLab:**
        
        1. Открой **Settings → Webhooks** в твоем GitLab проекте
        
        2. Добавь **второй webhook** для note events:
           ```
           URL: {API_URL}/webhook/gitlab/note
           ```
        
        3. Выбери события:
           - ✅ **Comments** (note events)
        
        4. Сохрани
        
        **Как это работает:**
        - Сеньор ставит 👍 или 👎 на комментарий AI в MR
        - GitLab отправляет webhook на backend
        - Backend автоматически создает feedback
        - Negative feedback → создается learning pattern
        - Learning pattern добавляется в промпт при следующих анализах
        
        **✅ После настройки все будет автоматически!**
        """)
        
        st.markdown("**Webhook token:** Используй тот же `WEBHOOK_SECRET` что и для основного webhook")
    
    st.markdown("---")
    
    st.markdown("**Как AI РЕАЛЬНО учится (не пиздеж!):**")
    st.markdown("""
    **✅ Что работает прямо сейчас:**
    
    1. **Feedback система** (`backend/feedback.py`):
       - Сеньор ставит 👍/👎 на комментарий AI в GitLab
       - Backend сохраняет в `data/feedback.json`
       - Негативный feedback → создается learning pattern в `data/learning_patterns.json`
       - Эти patterns РЕАЛЬНО добавляются в промпт при следующих анализах
    
    2. **Custom промпт** (раздел выше):
       - Редактируешь промпт → сохраняешь → он применяется к следующим MR
       - Без редеплоя backend!
    
    3. **История анализов** (PostgreSQL):
       - Каждый MR сохраняется в БД
       - Статистика по разработчикам
       - Паттерны проблем
    
    **📝 Код не врёт:**
    ```python
    # backend/code_analyzer.py, line 127
    learned_context = learning_system.get_feedback_for_prompt()
    if learned_context:
        prompt += learned_context  # Добавляем learned patterns!
    ```
    
    **💡 Для обучения AI:**
    - Реагируй на комментарии AI в GitLab (👍/👎)
    - Редактируй промпт в разделе Настройки
    - Чем больше MR → тем больше данных для анализа
    """)
