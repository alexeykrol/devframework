# Быстрый старт: Автономный режим Claude Code

## 3 способа использования (от простого к сложному)

### 🟢 Уровень 1: Метапромпт в задаче (5 минут)

**Что**: Добавить autonomous protocol прямо в task definition

**Как**:
1. Открыть любую задачу, например `framework/tasks/db-schema.md`
2. Добавить в начало файла:

```markdown
---
execution_mode: autonomous
time_budget: 45
---

## 🤖 AUTONOMOUS MODE PROTOCOL

[Скопировать полный протокол из 01-autonomous-mode-protocol.md]

---

[... остальное содержание задачи ...]
```

3. Запустить через orchestrator:
```bash
python framework/orchestrator/orchestrator.py --config framework/orchestrator/orchestrator.json
```

**Плюсы**: Работает немедленно, без изменений в коде
**Минусы**: Дублирование протокола в каждой задаче

---

### 🟡 Уровень 2: Конфигурация в orchestrator.json (30 минут)

**Что**: Добавить поддержку autonomous mode в orchestrator

**Как**:

1. **Обновить `orchestrator.json`**:
```json
{
  "runners": {
    "claude-code": {
      "type": "claude-code",
      "command": "claude-code",
      "autonomous_mode": {
        "enabled": true,
        "protocol_file": "claude-code/01-autonomous-mode-protocol.md"
      }
    }
  },
  "tasks": [
    {
      "id": "db-schema",
      "file": "framework/tasks/db-schema.md",
      "runner": "claude-code",
      "execution_mode": "autonomous",
      "time_budget": 45
    }
  ]
}
```

2. **Модифицировать `orchestrator.py`** (добавить ~30 строк кода):

```python
def build_command(self, task, runner):
    """Build command with optional autonomous mode injection"""
    base_cmd = runner["command"]
    task_file = task["file"]

    # Check if autonomous mode enabled
    if task.get("execution_mode") == "autonomous":
        autonomous_config = runner.get("autonomous_mode", {})

        if autonomous_config.get("enabled"):
            # Inject protocol
            protocol_file = autonomous_config["protocol_file"]
            temp_task_file = self._inject_protocol(
                protocol_file,
                task_file,
                task.get("time_budget", 60)
            )
            task_file = temp_task_file

    return f"{base_cmd} --task {task_file}"

def _inject_protocol(self, protocol_path, task_path, time_budget):
    """Prepend protocol to task"""
    protocol = Path(protocol_path).read_text()
    task_content = Path(task_path).read_text()

    # Replace placeholders
    protocol = protocol.replace("{TIME_BUDGET}", str(time_budget))

    # Create temp file
    temp_path = Path(f"/tmp/autonomous_task_{uuid.uuid4().hex}.md")
    temp_path.write_text(f"{protocol}\n\n{task_content}")

    return str(temp_path)
```

**Плюсы**: Централизованный протокол, легко обновлять
**Минусы**: Требует модификации orchestrator.py

---

### 🔴 Уровень 3: Полная интеграция с watchdog (2-3 часа)

**Что**: Добавить мониторинг прогресса и автоэскалацию

**Как**: Следовать инструкциям в `03-orchestrator-modifications.md` и `05-watchdog-escalation.md`

**Основные компоненты**:
1. ProgressWatchdog class
2. Escalation strategies
3. Validation compliance checker
4. Metrics collection

**Плюсы**: Production-ready, автоматическое разблокирование
**Минусы**: Значительные изменения в коде

---

## Рекомендуемый путь

### Шаг 1: Быстрый тест (день 1)

Выбрать **одну простую задачу** из `framework/tasks/` и попробовать Уровень 1:

1. Скопировать `claude-code/examples/task-autonomous-example.md`
2. Адаптировать под свою задачу
3. Запустить вручную:
   ```bash
   claude-code < modified-task.md
   ```
4. Проверить результат:
   - Использовал ли AskUserQuestion? (должно быть 0)
   - Задокументированы ли решения в handoff.md?
   - Завершена ли задача в пределах time budget?

### Шаг 2: Интеграция (день 2-3)

Если тест успешен, внедрить Уровень 2:

1. Скопировать пример из `examples/orchestrator-config-example.json`
2. Модифицировать `orchestrator.py` (code snippets в `03-orchestrator-modifications.md`)
3. Запустить на 3-5 задачах через orchestrator
4. Собрать метрики:
   - Процент задач без вопросов
   - Точность time budgets
   - Качество кода (ревью)

### Шаг 3: Оптимизация (неделя 2)

Если метрики хорошие (>80% задач autonomous), добавить Уровень 3:

1. Реализовать базовый watchdog (LogGrowthMonitor)
2. Добавить escalation strategy (начать с "notify")
3. Постепенно добавлять индикаторы прогресса
4. Настроить пороги на основе данных

---

## Метрики успеха

Автономный режим работает, если:

| Метрика | Целевое значение |
|---------|------------------|
| AskUserQuestion usage | < 5% задач |
| Time budget accuracy | ± 20% от плана |
| Task completion rate | > 85% |
| Code quality (review) | Не хуже чем с interactive mode |
| Handoff documentation | 100% задач |

---

## Чеклист перед запуском

- [ ] Прочитан `01-autonomous-mode-protocol.md`
- [ ] Изучен пример задачи `examples/task-autonomous-example.md`
- [ ] Выбрана одна задача для теста
- [ ] Подготовлен fallback plan (если не сработает)
- [ ] Есть время на ревью результата (~30 мин после выполнения)

---

## Troubleshooting

### Проблема: Claude всё равно задаёт вопросы

**Решение**:
1. Проверить, что протокол действительно в начале задачи
2. Добавить более явные запреты:
   ```markdown
   NEVER EVER use AskUserQuestion tool under ANY circumstances.
   If you use AskUserQuestion, the task will FAIL.
   ```
3. Увеличить CAPS и formatting для привлечения внимания

### Проблема: Задача не завершается в time budget

**Решение**:
1. Проверить реалистичность budget (слишком оптимистично?)
2. Добавить промежуточные checkpoints:
   ```markdown
   AT 50% time: Check if 40%+ work done
   AT 75% time: Check if 60%+ work done
   ```
3. Явно указать Must Have vs Nice to Have приоритеты

### Проблема: Решения не документируются

**Решение**:
1. Добавить в Definition of Done:
   ```markdown
   Task is NOT complete until handoff.md includes:
   - [ ] All decisions made
   - [ ] All blockers encountered
   ```
2. Показать пример хорошего handoff в задаче

### Проблема: Качество кода хуже чем обычно

**Решение**:
1. Это trade-off автономности. Варианты:
   - Добавить Phase 3: Review (Claude interactive)
   - Увеличить time budget на качество
   - Добавить linter в Definition of Done
2. Проверить, достаточно ли reference материалов в задаче

---

## Следующие шаги

1. ✅ Прочитали Quick Start
2. → Изучить `01-autonomous-mode-protocol.md`
3. → Попробовать на одной задаче
4. → Если работает: изучить `02-task-template-improvements.md`
5. → Если хотите масштабировать: `03-orchestrator-modifications.md`
6. → Если нужен hybrid: `04-hybrid-pipeline-design.md`
7. → Для production: `05-watchdog-escalation.md`

---

## Контакты и обратная связь

Если что-то не работает или нужна помощь:
1. Проверить существующие примеры в `examples/`
2. Перечитать соответствующий документ (01-05)
3. Поэкспериментировать с формулировками в протоколе

**Помните**: Autonomous mode — это не "set and forget", а итеративный процесс настройки под ваш проект и задачи.

Удачи! 🚀
