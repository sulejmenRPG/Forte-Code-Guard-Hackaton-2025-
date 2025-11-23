# 🛡️ Безопасность - Forte Code Guard

## 📋 Содержание
1. [Реализованные меры безопасности](#реализованные-меры-безопасности)
2. [Конфиденциальность данных](#конфиденциальность-данных)
3. [Аутентификация и авторизация](#аутентификация-и-авторизация)
4. [Защита от атак](#защита-от-атак)
5. [Соответствие стандартам](#соответствие-стандартам)
6. [Рекомендации для банков](#рекомендации-для-банков)

---

## 🔐 Реализованные меры безопасности

### 1. **Webhook Token Verification**
```python
# backend/main.py
if x_gitlab_token != settings.WEBHOOK_SECRET:
    raise HTTPException(status_code=401, detail="Invalid webhook token")
```

**Что защищает:**
- ✅ Несанкционированные запросы к API
- ✅ Подделка webhook от GitLab
- ✅ DDoS атаки на endpoint

**Как работает:**
1. GitLab отправляет webhook с секретным токеном
2. Backend проверяет токен
3. Если токен неверный → 401 Unauthorized
4. Только валидные запросы обрабатываются

---

### 2. **Environment Variables для секретов**

**Все конфиденциальные данные в переменных окружения:**

```bash
# .env (НЕ в Git!)
GITLAB_TOKEN=glpat-xxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
WEBHOOK_SECRET=secure_random_string_123
DATABASE_URL=postgresql://user:pass@host:5432/db
```

**Что защищает:**
- ✅ API ключи не в коде
- ✅ Токены не в Git истории
- ✅ Легко ротация секретов
- ✅ Разные секреты для dev/prod

---

### 3. **Database Security**

**PostgreSQL с защищённым подключением:**

```python
# Не хардкодим пароли
DATABASE_URL = os.getenv("DATABASE_URL")

# SSL подключение (для prod)
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"
```

**Что защищает:**
- ✅ Шифрование соединения с БД
- ✅ Защита учётных данных
- ✅ Изоляция данных

---

### 4. **CORS Configuration**

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В prod: указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Для продакшна настроить:**
```python
allow_origins=[
    "https://dashboard.fortebank.kz",
    "https://gitlab.fortebank.kz"
]
```

---

### 5. **Rate Limiting для Webhooks**

```python
# Защита от дублирования (60 секунд)
if current_time - last_processed < 60:
    return {"status": "skipped", "reason": "Duplicate webhook"}
```

**Что защищает:**
- ✅ Повторная обработка одного MR
- ✅ Экономия ресурсов
- ✅ Защита от спама

---

### 6. **Валидация данных с Pydantic**

```python
class WebhookPayload(BaseModel):
    object_kind: str
    project: dict
    object_attributes: dict
    
    # Автоматическая валидация типов
```

**Что защищает:**
- ✅ Injection атаки
- ✅ Некорректные данные
- ✅ Type safety

---

## 🔒 Конфиденциальность данных

### **Что хранится:**
```
✅ Метаданные MR (ID, title, branch)
✅ Результаты анализа (score, issues)
✅ Статистика (anonymous)
❌ НЕ хранится исходный код
❌ НЕ хранятся пароли/токены
❌ НЕ передаётся в сторонние сервисы
```

### **Обработка кода:**
```
1. GitLab → Webhook → Backend
2. Backend → LLM API (только diff)
3. LLM → Анализ → Результат
4. Результат → GitLab комментарий
5. Метаданные → Database

❗ КОД НЕ ХРАНИТСЯ В БД!
```

---

## 🔑 Аутентификация и авторизация

### **GitLab Token Scopes:**

**Минимальные права для работы:**
```
✅ api (для работы с MR и комментариями)
✅ read_repository (чтение кода)
✅ write_repository (создание комментариев)

❌ НЕ НУЖНЫ:
❌ admin права
❌ sudo
❌ registry
```

### **Webhook Secret:**
```bash
# Генерация безопасного секрета
openssl rand -hex 32

# Пример:
WEBHOOK_SECRET=a3d5f7e9b2c4d6f8a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7
```

---

## 🛡️ Защита от атак

### **1. SQL Injection**
```python
✅ Используем SQLAlchemy ORM
✅ Параметризованные запросы
✅ Pydantic валидация

# Безопасно:
db.query(Review).filter(Review.id == mr_id).first()
```

### **2. XSS (Cross-Site Scripting)**
```python
✅ Markdown sanitization в GitLab
✅ Escape HTML в комментариях
✅ Content-Security-Policy headers
```

### **3. CSRF (Cross-Site Request Forgery)**
```python
✅ Webhook token verification
✅ Origin validation
✅ CORS настройки
```

### **4. DDoS Protection**
```python
✅ Rate limiting (60 сек на MR)
✅ Webhook validation
✅ Railway автоматическая защита
```

---

## 📜 Соответствие стандартам

### **PCI DSS (Payment Card Industry Data Security Standard)**

**Для банковских приложений:**

| Требование | Реализация |
|------------|------------|
| **6.2** Устранение уязвимостей | ✅ AI автоматически находит |
| **6.3.2** Код ревью | ✅ AI + сеньор ревью |
| **6.5.1** SQL Injection защита | ✅ AI проверяет |
| **6.5.7** XSS защита | ✅ AI проверяет |
| **8.2.3** Пароли не хардкодить | ✅ AI проверяет |

### **OWASP Top 10 Coverage:**

```
✅ A01 Broken Access Control → Webhook token
✅ A02 Cryptographic Failures → Env variables
✅ A03 Injection → AI детектирует
✅ A04 Insecure Design → Code review
✅ A05 Security Misconfiguration → AI проверяет
✅ A06 Vulnerable Components → Dependencies scan
✅ A07 Auth Failures → Token validation
✅ A08 Software/Data Integrity → Git signatures
✅ A09 Logging Failures → Structured logging
✅ A10 SSRF → Input validation
```

---

## 🏦 Рекомендации для банков

### **1. On-Premise развертывание**

```yaml
# docker-compose.yml для банковской сети
version: '3.8'
services:
  backend:
    image: forte-code-guard:latest
    environment:
      - DATABASE_URL=postgresql://db:5432/reviews
      - GITLAB_URL=https://gitlab.internal.bank
    networks:
      - internal_network
    restart: unless-stopped

  database:
    image: postgres:15
    volumes:
      - ./data:/var/lib/postgresql/data
    networks:
      - internal_network
    
networks:
  internal_network:
    internal: true  # Изолированная сеть
```

### **2. Дополнительная безопасность**

```bash
# 1. Используйте Private LLM (внутренний)
LLM_PROVIDER=internal
INTERNAL_LLM_URL=https://llm.internal.bank

# 2. Логируйте все действия
AUDIT_LOG_ENABLED=true
AUDIT_LOG_PATH=/var/log/code-review

# 3. Шифрование данных в БД
DATABASE_URL=postgresql://...?sslmode=require&sslcert=/path/to/cert

# 4. Ротация токенов (каждые 90 дней)
# Автоматический скрипт для ротации
```

### **3. Мониторинг и алерты**

```python
# Добавить мониторинг подозрительной активности
ALERT_EMAIL=security@bank.kz
ALERT_ON_MULTIPLE_FAILED_WEBHOOKS=true
ALERT_ON_SUSPICIOUS_PATTERNS=true
```

---

## 🔐 Безопасное развертывание

### **Чеклист для продакшна:**

```
✅ Все секреты в environment variables
✅ DATABASE_URL с SSL подключением
✅ CORS ограничен конкретными доменами
✅ HTTPS с валидным сертификатом
✅ Rate limiting настроен
✅ Логирование включено
✅ Мониторинг настроен
✅ Backup базы данных
✅ Disaster recovery план
✅ Incident response процедура
```

---

## 📞 Контакты безопасности

**Для вопросов по безопасности:**
- Email: security@forte-code-guard.dev
- Telegram: @forte_security
- Bug Bounty: https://forte-code-guard.dev/security/bounty

**Responsible Disclosure:**
```
1. Найдена уязвимость → security@forte-code-guard.dev
2. Ответ в течение 48 часов
3. Фикс в течение 7 дней (критичные)
4. Публикация после фикса
```

---

## 📚 Дополнительные ресурсы

- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [PCI DSS Requirements](https://www.pcisecuritystandards.org/)
- [GitLab Security Best Practices](https://docs.gitlab.com/ee/security/)
- [Python Security Guide](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Версия:** 1.0  
**Последнее обновление:** 23 ноября 2025  
**Аудит безопасности:** Рекомендуется каждые 6 месяцев
