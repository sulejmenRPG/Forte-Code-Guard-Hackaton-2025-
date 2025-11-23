# 🎯 Автоматизация Feedback для AI Learning

## ✅ ЧТО ДОБАВЛЕНО:

### 1. **Методы в GitLabClient** (`backend/gitlab_client.py`)

```python
def get_note_reactions(self, project_id: int, mr_iid: int, note_id: int) -> List[str]:
    """Получить reactions (emojis) на комментарий"""
    # Возвращает список: ['thumbsup', 'thumbsdown', 'heart', ...]

def get_note_content(self, project_id: int, mr_iid: int, note_id: int) -> Optional[str]:
    """Получить содержимое комментария"""
    # Возвращает текст комментария
```

---

### 2. **Webhook Handler для Note Events** (`backend/main.py`)

```python
@app.post("/webhook/gitlab/note")
async def gitlab_note_webhook(request: Request):
    """
    Обрабатывает GitLab note events
    Автоматически создает feedback при 👍/👎 reactions
    """
```

**Что делает:**
1. Получает webhook от GitLab когда кто-то комментирует или ставит reaction
2. Проверяет что это комментарий на MR
3. Получает reactions на этом комментарии
4. Проверяет что комментарий от AI бота (по маркеру "🤖" или "AI Review")
5. Создает feedback:
   - 👎 `thumbsdown` → negative feedback
   - 👍 `thumbsup` → positive feedback
6. Сохраняет в `data/feedback.json`
7. Для negative feedback → создает learning pattern в `data/learning_patterns.json`

---

### 3. **UI в Dashboard** (`dashboard_ru.py`)

**Добавлено:**
- Реальная статистика feedbacks (загрузка через API)
- Метрики: Всего / Позитивных / Негативных / Точность
- Инструкция по настройке webhook для note events в expander
- Объяснение как работает автоматизация

---

## 🚀 КАК НАСТРОИТЬ:

### Шаг 1: Настроить webhook в GitLab

1. Открой **Settings → Webhooks** в GitLab проекте

2. **Создай ВТОРОЙ webhook** (первый уже есть для MR events):
   ```
   URL: http://your-backend-url/webhook/gitlab/note
   Secret Token: <тот же WEBHOOK_SECRET>
   ```

3. Выбери события:
   - ✅ **Comments**

4. Сохрани

---

### Шаг 2: Проверить что работает

1. **Создай MR** в GitLab

2. **AI оставит комментарии** автоматически

3. **Сеньор ставит 👍 или 👎** на комментарий AI

4. **Backend получает webhook** и создает feedback:
   ```
   💬 Received GitLab note event
   💬 Processing note 12345 on MR #67
   📊 Note 12345 has reactions: ['thumbsdown']
   👍👎 Reactions on AI comment: ['thumbsdown']
   ❌ Negative feedback recorded from John Senior
   ```

5. **Проверь файлы:**
   ```bash
   cat data/feedback.json
   cat data/learning_patterns.json
   ```

6. **Проверь dashboard:**
   - Раздел "Обучение"
   - Метрики должны обновиться
   - Всего отзывов +1

---

## 📊 ЧТО ПРОИСХОДИТ ПОД КАПОТОМ:

### 1. Сеньор ставит 👎 на комментарий AI

```
GitLab → webhook → POST /webhook/gitlab/note
```

### 2. Backend обрабатывает

```python
# main.py, line 245
reactions = gitlab_client.get_note_reactions(project_id, mr_iid, note_id)
# reactions = ['thumbsdown']

if 'thumbsdown' in reactions:
    feedback = Feedback(
        comment_id=str(note_id),
        mr_id=mr_iid,
        feedback_type='negative',
        reason="Senior marked AI comment as incorrect",
        senior_name=author_name,
        ai_comment=note_body
    )
    
    learning_system.add_feedback(feedback)
```

### 3. Learning system сохраняет

```python
# feedback.py, line 44
def add_feedback(self, feedback: Feedback):
    # Сохранить в data/feedback.json
    feedbacks.append(feedback.dict())
    self._save_feedback(feedbacks)
    
    # Создать learning pattern
    self._update_learning_patterns(feedback)
```

### 4. Learning pattern добавляется в промпт

```python
# code_analyzer.py, line 127
learned_context = learning_system.get_feedback_for_prompt()
if learned_context:
    prompt += learned_context
    # Промпт теперь содержит: "LEARNED PATTERNS: - <reason from feedback>"
```

### 5. AI использует при следующем анализе

```
AI получает промпт:
---
Базовый промпт
+ Custom rules
+ LEARNED PATTERNS:
  - Senior marked this as incorrect: <previous mistake>
---
```

---

## 🎯 ПРОВЕРКА РАБОТОСПОСОБНОСТИ:

### Тест 1: Webhook доставляется

```bash
# Проверь логи backend
docker logs backend-container
# Должно быть:
# 💬 Received GitLab note event
# 📊 Note 12345 has reactions: [...]
```

### Тест 2: Feedback сохраняется

```bash
cat data/feedback.json
```

**Ожидается:**
```json
[
  {
    "comment_id": "12345",
    "mr_id": 67,
    "project_id": 789,
    "feedback_type": "negative",
    "reason": "Senior marked AI comment as incorrect",
    "senior_name": "John Senior",
    "ai_comment": "...",
    "timestamp": "2025-11-24T01:30:00"
  }
]
```

### Тест 3: Learning pattern создается

```bash
cat data/learning_patterns.json
```

**Ожидается:**
```json
[
  {
    "rule": "Senior marked AI comment as incorrect",
    "context": "...",
    "added_by": "John Senior",
    "date": "2025-11-24T01:30:00",
    "mr_id": 67
  }
]
```

### Тест 4: Pattern добавляется в промпт

```bash
# Создай новый MR
# Проверь логи:
# 📚 Added learned patterns to prompt
```

---

## 💡 TROUBLESHOOTING:

### Проблема: Webhook не доставляется

**Решение:**
1. Проверь что webhook URL правильный
2. Проверь что Secret Token совпадает
3. Проверь что выбрано "Comments" event
4. Тест webhook в GitLab: Settings → Webhooks → Test → Comments

### Проблема: Feedback не создается

**Причины:**
1. Комментарий не от AI бота (нет маркера "🤖" или "AI Review")
2. Нет reactions на комментарии
3. Reaction не thumbsup/thumbsdown

**Решение:**
- Проверь логи backend
- Убедись что AI комментарий содержит "🤖"

### Проблема: Learning patterns не добавляются в промпт

**Решение:**
1. Проверь что файл `data/learning_patterns.json` существует
2. Проверь что он содержит patterns
3. Перезапусти backend
4. Создай новый MR и проверь логи: `📚 Added learned patterns to prompt`

---

## 📝 ИТОГОВАЯ СХЕМА:

```
┌──────────────┐
│  GitLab MR   │
│  AI Comment  │
└──────┬───────┘
       │
       │ Сеньор ставит 👍 или 👎
       │
       ▼
┌──────────────────────┐
│  GitLab Webhook      │
│  POST /webhook/note  │
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Backend Handler            │
│  1. Get reactions           │
│  2. Check if AI comment     │
│  3. Create feedback         │
│  4. Save to files           │
└──────┬──────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  data/feedback.json          │
│  data/learning_patterns.json │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Следующий MR               │
│  1. Load learned patterns   │
│  2. Add to prompt           │
│  3. AI использует опыт!     │
└─────────────────────────────┘
```

---

## ✅ ГОТОВО!

**Теперь AI учится автоматически на каждом 👍/👎 от сеньоров!**

**Для хакатона:**
- Настрой webhook
- Покажи жюри: ставишь 👎 → AI учится
- Dashboard показывает статистику
- Код не врёт - всё работает реально!

🚀 **PROFIT!**
