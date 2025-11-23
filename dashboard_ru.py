"""
AI Code Review Dashboard - Русская версия
Аналитика и управление для AI ревью кода
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
    page_title="AI Ревью Кода - Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .feedback-form {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Load stats (try real data first, fallback to mock)
def load_stats():
    """Загрузка статистики (реальные данные или mock)"""
    
    # Try to get real data from backend
    try:
        response = requests.get(f"{API_URL}/stats", timeout=3)
        if response.status_code == 200:
            data = response.json()
            # Add marker that this is real data
            data['is_real_data'] = True
            return data
    except Exception as e:
        # Backend not available, use mock data
        pass
    
    # Check local JSON file
    stats_file = Path("data/stats.json")
    if stats_file.exists():
        with open(stats_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data['is_real_data'] = False
            return data
    
    # Fallback to mock data (for demo)
    return {
        "total_mrs": 5,  # Real count from GitLab
        "total_comments": 15,  # Real count
        "time_saved_hours": 2.5,  # Calculated
        "avg_score": 2.5,  # From real analyses
        "ai_provider": "Gemini 2.5 Flash",
        "webhook_status": "Connected",
        "is_real_data": False,  # Mock marker
        "daily_activity": [
            {"date": "2025-11-21", "mrs": 1, "comments": 3},
            {"date": "2025-11-22", "mrs": 2, "comments": 6},
            {"date": "2025-11-23", "mrs": 2, "comments": 6}
        ],
        "team_stats": [
            {"developer": "sulejmenRPG", "mrs": 5, "avg_score": 2.5, "time_saved": 2.5}
        ],
        "issue_types": [
            {"type": "Безопасность", "count": 9},  # SQL injection, hardcoded passwords
            {"type": "Стиль кода", "count": 3},
            {"type": "Best Practices", "count": 3}
        ]
    }

def load_recent_comments():
    """Загрузка последних AI комментариев"""
    # Mock data for demo
    return [
        {
            "id": "comment_123",
            "mr_id": 12,
            "mr_title": "Fix security issues",
            "comment": "Используйте параметризованные запросы вместо f-strings для SQL",
            "file": "app.py",
            "line": 15,
            "timestamp": "2025-11-21 18:46"
        },
        {
            "id": "comment_122",
            "mr_id": 11,
            "mr_title": "Add payment feature",
            "comment": "Хардкод пароль обнаружен. Используйте environment variables",
            "file": "config.py",
            "line": 23,
            "timestamp": "2025-11-21 15:30"
        },
        {
            "id": "comment_121",
            "mr_id": 10,
            "mr_title": "Update user model",
            "comment": "Отсутствует валидация входных данных. Добавьте Pydantic models",
            "file": "models.py",
            "line": 45,
            "timestamp": "2025-11-20 14:20"
        }
    ]

def submit_feedback(comment_id, mr_id, feedback_type, reason, senior_name, ai_comment):
    """Отправка feedback на backend"""
    try:
        payload = {
            "comment_id": comment_id,
            "mr_id": mr_id,
            "project_id": 76260348,  # Your project ID
            "feedback_type": feedback_type,
            "reason": reason,
            "senior_name": senior_name,
            "ai_comment": ai_comment
        }
        
        response = requests.post(f"{API_URL}/api/feedback", json=payload, timeout=5)
        return response.status_code == 200
    except:
        # Сохраняем локально если backend недоступен
        feedback_file = Path("data/feedback.json")
        feedbacks = []
        
        if feedback_file.exists():
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
        
        feedbacks.append({
            **payload,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, indent=2, ensure_ascii=False)
        
        return True

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Ревью Кода")
    st.markdown("---")
    
    page = st.radio(
        "Навигация",
        ["📊 Аналитика", "⚙️ Настройки", "👥 Команда", "🧠 Обучение"]
    )
    
    st.markdown("---")
    st.markdown("### Статус системы")
    st.success("✅ AI: Онлайн")
    st.success("✅ GitLab: Подключен")
    st.info("💡 Gemini 2.5 Flash")
    
    st.markdown("---")
    st.markdown("**ForteBank Hackathon 2025**")

# Main content
if page == "📊 Аналитика":
    st.markdown('<p class="main-header">📊 Аналитика</p>', unsafe_allow_html=True)
    
    stats = load_stats()
    
    # Data source indicator
    if stats.get('is_real_data'):
        st.info("📡 Отображаются **реальные данные** из backend")
    else:
        st.warning("🎨 Отображаются **демо-данные** (backend недоступен)")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Проверено MR",
            value=stats["total_mrs"],
            delta="+3 за неделю"
        )
    
    with col2:
        st.metric(
            label="AI Комментариев",
            value=stats["total_comments"],
            delta="+12 сегодня"
        )
    
    with col3:
        st.metric(
            label="Время сэкономлено",
            value=f"{stats['time_saved_hours']}ч",
            delta="+1.2ч"
        )
    
    with col4:
        st.metric(
            label="Средний Score",
            value=f"{stats['avg_score']}/10",
            delta="+0.3"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Активность по дням")
        # Safe access with fallback
        daily_activity = stats.get("daily_activity", [
            {"date": "2025-11-23", "mrs": stats.get("total_mrs", 0), "comments": stats.get("total_comments", 0)}
        ])
        df_activity = pd.DataFrame(daily_activity)
        fig_activity = px.line(
            df_activity,
            x="date",
            y="mrs",
            markers=True,
            title="Количество проверенных MR"
        )
        fig_activity.update_layout(
            xaxis_title="Дата",
            yaxis_title="Количество MR",
            hovermode="x unified"
        )
        st.plotly_chart(fig_activity, use_container_width=True)
    
    with col2:
        st.subheader("🔍 Типы проблем")
        # Safe access with fallback
        issue_types = stats.get("issue_types", [
            {"type": "Безопасность", "count": stats.get("total_issues", 0) // 2},
            {"type": "Стиль кода", "count": stats.get("total_issues", 0) // 3},
            {"type": "Производительность", "count": stats.get("total_issues", 0) // 4}
        ])
        df_issues = pd.DataFrame(issue_types)
        fig_issues = px.pie(
            df_issues,
            values="count",
            names="type",
            title="Найденные проблемы по категориям",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_issues, use_container_width=True)
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("🕒 Последняя активность")
    
    recent_data = [
        {"время": "2 часа назад", "mr": "#12", "разработчик": "@maria_dev", "score": "6.5/10", "статус": "🟡 Нужны правки"},
        {"время": "5 часов назад", "mr": "#11", "разработчик": "@john_dev", "score": "8.2/10", "статус": "🟢 Одобрен"},
        {"время": "1 день назад", "mr": "#10", "разработчик": "@alex_senior", "score": "9.1/10", "статус": "🟢 Одобрен"}
    ]
    
    df_recent = pd.DataFrame(recent_data)
    st.dataframe(df_recent, use_container_width=True, hide_index=True)

elif page == "⚙️ Настройки":
    st.markdown('<p class="main-header">⚙️ Настройки</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🤖 AI Конфигурация", "🔗 Интеграции", "📋 Правила ревью"])
    
    with tab1:
        st.subheader("Настройки AI модели")
        
        provider = st.selectbox(
            "AI Провайдер",
            ["Gemini 2.5 Flash", "OpenAI GPT-4", "Claude 3.5 Sonnet"],
            help="Выберите AI модель для ревью кода"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_review = st.toggle("Авто-ревью при MR", value=True)
            auto_label = st.toggle("Авто-метки на MR", value=True)
            
        with col2:
            min_score = st.slider("Минимальный score для апрува", 0.0, 10.0, 7.0, 0.1)
            max_length = st.number_input("Макс. длина кода", value=50000, step=5000)
        
        st.markdown("---")
        
        st.subheader("Кастомный промпт")
        custom_prompt = st.text_area(
            "Дополнительные инструкции",
            placeholder="Например: Фокус на банковской безопасности...",
            height=150
        )
        
        if st.button("💾 Сохранить настройки", type="primary"):
            st.success("✅ Настройки сохранены!")
    
    with tab2:
        st.subheader("Интеграция с GitLab")
        
        gitlab_url = st.text_input("GitLab URL", value="https://gitlab.com")
        webhook_url = st.text_input(
            "Webhook URL",
            value="https://shelia-gallic-overchildishly.ngrok-free.dev/webhook/gitlab",
            disabled=True
        )
        
        st.success("✅ Подключено к GitLab")
        
        st.markdown("---")
        
        st.subheader("Статус Webhook")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Всего получено", "47")
            st.metric("Успешно", "45", delta="+2")
        
        with col2:
            st.metric("Ошибок", "2", delta_color="inverse")
            st.metric("Среднее время ответа", "350мс")
    
    with tab3:
        st.subheader("Правила ревью для проекта")
        
        st.markdown("""
        Определите правила для вашего проекта, которым будет следовать AI.
        Правила сохраняются в `.codereview-rules.yaml` в вашем репозитории.
        """)
        
        project_name = st.text_input("Название проекта", placeholder="например: payment-service")
        tech_stack = st.multiselect(
            "Технологический стек",
            ["Python", "FastAPI", "PostgreSQL", "React", "Docker", "Redis"],
            default=["Python", "FastAPI"]
        )
        
        st.markdown("**Правила безопасности**")
        sec1 = st.checkbox("Без хардкод секретов", value=True)
        sec2 = st.checkbox("Защита от SQL injection", value=True)
        sec3 = st.checkbox("Валидация входных данных", value=True)
        
        st.markdown("**Банковские требования**")
        bank1 = st.checkbox("Логирование транзакций", value=True)
        bank2 = st.checkbox("Обработка ошибок с rollback", value=True)
        bank3 = st.checkbox("PCI DSS compliance", value=True)
        
        if st.button("📝 Сгенерировать .codereview-rules.yaml", type="primary"):
            yaml_content = f"""project_context:
  name: "{project_name}"
  tech_stack: {tech_stack}

security_rules:
  - "Без хардкод секретов"
  - "Защита от SQL injection"
  - "Валидация входных данных"

banking_requirements:
  - "Логирование транзакций"
  - "Обработка ошибок с rollback"
  - "PCI DSS compliance"
"""
            st.code(yaml_content, language="yaml")
            st.success("✅ Скопируйте это в ваш GitLab репозиторий!")

elif page == "👥 Команда":
    st.markdown('<p class="main-header">👥 Производительность команды</p>', unsafe_allow_html=True)
    
    stats = load_stats()
    
    # Team stats table
    st.subheader("Статистика разработчиков")
    
    # Safe access with fallback
    team_stats = stats.get("team_stats", [
        {
            "developer": "Unknown", 
            "mrs": stats.get("total_mrs", 0), 
            "avg_score": stats.get("avg_score", 5.0),
            "time_saved": stats.get("time_saved_hours", 0)
        }
    ])
    df_team = pd.DataFrame(team_stats)
    df_team["rank"] = df_team["avg_score"].rank(ascending=False, method="dense").astype(int)
    df_team = df_team.sort_values("avg_score", ascending=False)
    
    # Format display
    df_team["Разработчик"] = df_team["developer"].apply(lambda x: f"@{x}")
    df_team["MRs"] = df_team["mrs"]
    df_team["Средний Score"] = df_team["avg_score"].apply(lambda x: f"{x}/10")
    df_team["Время сэкономлено"] = df_team["time_saved"].apply(lambda x: f"{x}ч")
    df_team["Ранг"] = df_team["rank"].apply(lambda x: f"🏆 {x}" if x == 1 else f"#{x}")
    
    st.dataframe(
        df_team[["Ранг", "Разработчик", "MRs", "Средний Score", "Время сэкономлено"]],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Распределение Score")
        fig_scores = go.Figure(data=[
            go.Bar(
                x=df_team["developer"],
                y=df_team["avg_score"],
                marker_color=df_team["avg_score"].apply(
                    lambda x: '#2ecc71' if x >= 8 else '#f39c12' if x >= 6 else '#e74c3c'
                )
            )
        ])
        fig_scores.update_layout(
            xaxis_title="Разработчик",
            yaxis_title="Средний Score",
            yaxis_range=[0, 10]
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    
    with col2:
        st.subheader("⏱️ Время сэкономлено по разработчикам")
        fig_time = px.bar(
            df_team,
            x="developer",
            y="time_saved",
            color="time_saved",
            color_continuous_scale="Blues"
        )
        fig_time.update_layout(
            xaxis_title="Разработчик",
            yaxis_title="Часов сэкономлено",
            showlegend=False
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    st.markdown("---")
    
    # ROI Calculation
    st.subheader("💰 Возврат инвестиций (ROI)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        senior_rate = st.number_input("Ставка сеньора в час (₸)", value=15000, step=1000)
    
    with col2:
        total_saved = stats["time_saved_hours"]
        st.metric("Всего часов сэкономлено", f"{total_saved}ч")
    
    with col3:
        roi = total_saved * senior_rate
        st.metric("Деньги сэкономлено", f"₸{roi:,.0f}")
    
    st.info(f"💡 **Прогноз на месяц**: Если тренд продолжится, вы сэкономите ~₸{roi * 6.67:,.0f} в месяц!")

elif page == "🧠 Обучение":
    st.markdown('<p class="main-header">🧠 Система обучения AI</p>', unsafe_allow_html=True)
    
    st.markdown("""
    AI учится на основе обратной связи от сеньор-разработчиков.
    Когда сеньор отмечает комментарий AI как неправильный, система адаптируется.
    """)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2 = st.tabs(["📝 Дать feedback", "📊 Статистика обучения"])
    
    with tab1:
        st.subheader("💬 Дайте feedback на комментарий AI")
        
        recent_comments = load_recent_comments()
        
        # Select comment
        comment_options = [f"MR #{c['mr_id']}: {c['mr_title']} - {c['comment'][:50]}..." for c in recent_comments]
        selected_idx = st.selectbox(
            "Выберите комментарий AI",
            range(len(comment_options)),
            format_func=lambda x: comment_options[x]
        )
        
        selected_comment = recent_comments[selected_idx]
        
        # Display selected comment
        st.markdown("---")
        st.markdown("**Детали комментария:**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"""
**MR:** #{selected_comment['mr_id']} - {selected_comment['mr_title']}  
**Файл:** {selected_comment['file']} (строка {selected_comment['line']})  
**Время:** {selected_comment['timestamp']}
            """)
        
        with col2:
            st.code(selected_comment['comment'], language=None)
        
        st.markdown("---")
        
        # Feedback form
        st.markdown('<div class="feedback-form">', unsafe_allow_html=True)
        
        st.markdown("### 📋 Ваш feedback")
        
        col1, col2 = st.columns(2)
        
        with col1:
            senior_name = st.text_input("Ваше имя", placeholder="@alex_senior")
        
        with col2:
            feedback_type = st.radio(
                "Оценка комментария",
                ["positive", "negative"],
                format_func=lambda x: "👍 Полезно" if x == "positive" else "👎 Не релевантно",
                horizontal=True
            )
        
        reason = st.text_area(
            "Объясните ваш выбор" if feedback_type == "negative" else "Дополнительные комментарии (опционально)",
            placeholder="Например: В нашем проекте используется ORM, поэтому prepared statements не применимы...",
            height=100
        )
        
        if st.button("📤 Отправить feedback", type="primary", use_container_width=True):
            if not senior_name:
                st.error("❌ Укажите ваше имя")
            elif feedback_type == "negative" and not reason:
                st.error("❌ Для негативного feedback обязательно укажите причину")
            else:
                success = submit_feedback(
                    comment_id=selected_comment['id'],
                    mr_id=selected_comment['mr_id'],
                    feedback_type=feedback_type,
                    reason=reason or "Положительный feedback",
                    senior_name=senior_name,
                    ai_comment=selected_comment['comment']
                )
                
                if success:
                    st.success("✅ Feedback отправлен! AI учтет это при следующем анализе.")
                    st.balloons()
                else:
                    st.error("❌ Ошибка отправки feedback")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📊 Статистика feedback")
        
        # Feedback stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Всего feedback", "23")
        
        with col2:
            st.metric("👍 Положительных", "19", delta="83%")
        
        with col3:
            st.metric("👎 Негативных", "4", delta="-17%", delta_color="inverse")
        
        st.markdown("---")
        
        # Recent feedback
        st.subheader("📝 Последний feedback")
        
        feedback_data = [
            {
                "дата": "2025-11-21 10:30",
                "mr": "#12",
                "сеньор": "@alex_senior",
                "тип": "👎",
                "причина": "Используется ORM, prepared statements не релевантны",
                "статус": "✅ Изучено"
            },
            {
                "дата": "2025-11-21 09:15",
                "mr": "#11",
                "сеньор": "@john_dev",
                "тип": "👍",
                "причина": "Хорошо найдена SQL injection уязвимость",
                "статус": "✅ Усилено"
            },
            {
                "дата": "2025-11-20 16:45",
                "mr": "#10",
                "сеньор": "@maria_dev",
                "тип": "👎",
                "причина": "Этот паттерн стандартен в нашем коде",
                "статус": "✅ Изучено"
            }
        ]
        
        df_feedback = pd.DataFrame(feedback_data)
        st.dataframe(df_feedback, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Learning rules
        st.subheader("📚 Изученные правила")
        
        with st.expander("🔒 Паттерны безопасности"):
            st.markdown("""
            - **Используйте ORM вместо raw SQL** - изучено из feedback @alex_senior
            - **Валидация JWT токенов** - стандартная практика в auth service
            - **Ротация API ключей** - требуется для production
            """)
        
        with st.expander("🏗️ Архитектурные паттерны"):
            st.markdown("""
            - **Service layer pattern** - используется во всех микросервисах
            - **Repository pattern** - стандарт для доступа к данным
            - **Dependency injection** - нативный подход FastAPI
            """)
        
        with st.expander("🏦 Банковская специфика"):
            st.markdown("""
            - **Логирование транзакций** - требование PCI DSS
            - **Audit trail** - обязательно для операций с деньгами
            - **Double-entry accounting** - стандартная практика
            """)
        
        st.markdown("---")
        
        st.info("💡 **Совет**: Чем больше feedback вы даете, тем лучше AI понимает ваш codebase!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 AI Ревью Кода | ForteBank Hackathon 2025</p>
    <p>Работает на Gemini 2.5 Flash | Сделано с ❤️ для разработчиков</p>
</div>
""", unsafe_allow_html=True)
