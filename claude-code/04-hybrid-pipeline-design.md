# Гибридный пайплайн: Claude Code + Codex

> **NOTE**: Примеры конфигураций и путей к файлам в этом документе являются иллюстративными. Реальные пути могут отличаться в зависимости от структуры вашего проекта. См. `framework/tasks/` для актуальных task definitions.

## Философская основа

**Ключевой инсайт**: Claude Code и Codex — не конкуренты, а **комплементарные инструменты**.

Вместо выбора "или-или", можно использовать "и-и" в рамках одного workflow.

## Сильные стороны каждого агента

### Claude Code
✅ **Глубокий анализ** — понимает архитектуру проекта
✅ **Следование паттернам** — имитирует стиль кода
✅ **Безопасность** — консервативен, не спешит
✅ **Планирование** — хорош в design phase
✅ **Code review** — критичный взгляд на качество

❌ **Медленный** — любит уточнять и перепроверять
❌ **Застревает** — при неоднозначности останавливается
❌ **Не автономен** — склонен к вопросам

### Codex (OpenAI)
✅ **Быстрый** — додавит задачу до конца
✅ **Автономный** — часы работы без вопросов
✅ **Параллелизм** — может делать 10 задач одновременно
✅ **Pragmatic** — не парится о "идеальном" коде

❌ **Менее точен архитектурно** — может не учесть паттерны
❌ **Прагматичен до сухости** — код работает, но не элегантен
❌ **Может пропустить детали** — в гонке за скоростью

## Идея гибридного пайплайна

**Используй каждого для того, в чём он силён:**

```
Phase 1: Architecture & Planning
  → Claude Code (Interactive)
  → Детальный архитектурный план
  → Все решения задокументированы

Phase 2: Implementation
  → Codex (Autonomous)
  → Реализация по плану
  → Быстро, без вопросов

Phase 3: Review & Polish
  → Claude Code (Interactive)
  → Проверка качества
  → Соответствие стилю проекта
```

## Дизайн пайплайна

### Вариант 1: Sequential (последовательный)

```
┌─────────────────────┐
│  1. PLAN PHASE      │
│  Agent: Claude Code │
│  Mode: Interactive  │
│                     │
│  Output:            │
│  - architecture.md  │
│  - decisions.md     │
│  - task-spec.md     │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  2. BUILD PHASE     │
│  Agent: Codex       │
│  Mode: Autonomous   │
│                     │
│  Input:             │
│  - task-spec.md     │
│                     │
│  Output:            │
│  - Implementation   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  3. REVIEW PHASE    │
│  Agent: Claude Code │
│  Mode: Interactive  │
│                     │
│  Output:            │
│  - code-review.md   │
│  - improvements.md  │
└─────────────────────┘
```

#### Orchestrator config

```json
{
  "workflows": {
    "feature-development": {
      "phases": [
        {
          "name": "plan",
          "agent": "claude-code",
          "mode": "interactive",
          "tasks": [
            {
              "id": "architecture-design",
              "file": "framework/tasks/db-schema.md",
              "outputs": [
                "framework/docs/architecture.md",
                "framework/docs/decisions.md"
              ]
            }
          ]
        },
        {
          "name": "build",
          "agent": "codex",
          "mode": "autonomous",
          "depends_on": ["plan"],
          "tasks": [
            {
              "id": "implement-feature",
              "file": "framework/tasks/business-logic.md",
              "inputs": [
                "framework/docs/architecture.md"
              ],
              "time_budget": 120
            }
          ]
        },
        {
          "name": "review",
          "agent": "claude-code",
          "mode": "interactive",
          "depends_on": ["build"],
          "tasks": [
            {
              "id": "code-review",
              "file": "framework/tasks/review.md",
              "inputs": [
                "git diff main...feature-branch"
              ]
            }
          ]
        }
      ]
    }
  }
}
```

#### Преимущества Sequential

✅ Чёткое разделение ответственности
✅ Каждый агент делает то, что умеет лучше
✅ Легко отладить (каждая фаза изолирована)
✅ Можно пропустить фазы (напр., skip review для простых задач)

#### Недостатки Sequential

❌ Медленнее (последовательное выполнение)
❌ Нет обратной связи между фазами (Codex не может спросить Claude)
❌ Жёсткая структура (сложно адаптировать на лету)

---

### Вариант 2: Fallback (эскалация при застревании)

```
┌─────────────────────┐
│  Start: Claude Code │
│  Mode: Autonomous   │
│  (с протоколом)     │
└──────────┬──────────┘
           │
           ↓
      [Watchdog]
           │
      ┌────┴────┐
      │ Progress? │
      └────┬────┘
           │
     ┌─────┴─────┐
     │           │
    Yes         No (5+ min stuck)
     │           │
     ↓           ↓
  Continue   ┌──────────────┐
              │  Escalate to │
              │     Codex    │
              └──────┬───────┘
                     │
                     ↓
              ┌──────────────┐
              │ Codex takes   │
              │ over and      │
              │ completes     │
              └──────────────┘
```

#### Orchestrator config

```json
{
  "tasks": [
    {
      "id": "complex-feature",
      "execution_mode": "autonomous",
      "runner_strategy": "fallback",
      "runners": [
        {
          "type": "claude-code",
          "priority": 1,
          "timeout": 45,
          "autonomous_protocol": true,
          "fallback_triggers": [
            "no_progress_5min",
            "ask_user_question_detected"
          ]
        },
        {
          "type": "codex",
          "priority": 2,
          "context_handoff": {
            "include": [
              "framework/docs/handoff.md",
              "git log --oneline -10",
              "git diff"
            ]
          }
        }
      ]
    }
  ]
}
```

#### Контекстная передача при эскалации

```python
class ContextHandoff:
    """Prepare context when escalating from Claude to Codex"""

    def prepare(self, from_agent, to_agent, task):
        """Build context package for new agent"""
        context = {
            "task_id": task["id"],
            "original_agent": from_agent,
            "reason_for_handoff": self._get_handoff_reason(task),
            "work_completed": self._get_completed_work(task),
            "current_blocker": self._get_blocker(task),
            "decisions_made": self._parse_handoff_docs(task),
            "code_changes": self._get_git_diff(task),
            "remaining_work": self._estimate_remaining(task)
        }

        # Write context to file for new agent
        context_file = f"/tmp/handoff_{task['id']}.md"
        self._write_handoff_markdown(context_file, context)

        return context_file

    def _get_handoff_reason(self, task):
        """Determine why handoff happened"""
        log = parse_task_log(task)

        if "AskUserQuestion" in log:
            return "Claude asked questions in autonomous mode"
        elif no_progress_detected(task):
            return "No progress for 5+ minutes"
        elif task_timeout(task):
            return "Task exceeded time budget"
        else:
            return "Unknown"

    def _write_handoff_markdown(self, path, context):
        """Format context as markdown for Codex"""
        content = f"""
# Task Handoff: {context['task_id']}

## Context
This task was started by {context['original_agent']} but is being handed off to you.

**Reason for handoff**: {context['reason_for_handoff']}

## Work Completed So Far
{context['work_completed']}

## Current Blocker
{context['current_blocker']}

## Decisions Already Made
{context['decisions_made']}

## Code Changes Made
```diff
{context['code_changes']}
```

## What Remains To Be Done
{context['remaining_work']}

## Instructions
- Continue from where {context['original_agent']} left off
- Respect decisions already documented
- Don't redo completed work
- Focus on unblocking and completing
"""
        Path(path).write_text(content)
```

#### Преимущества Fallback

✅ Best of both worlds — попытка с Claude, финиш с Codex
✅ Автоматическое разблокирование застрявших задач
✅ Оптимизация времени (не ждём пока Claude спросит)
✅ Сохранение контекста (Codex видит что сделал Claude)

#### Недостатки Fallback

❌ Сложнее отладить (переключение между агентами)
❌ Риск потери контекста при передаче
❌ Дополнительный overhead на мониторинг

---

### Вариант 3: Parallel (параллельная работа с консенсусом)

```
                 ┌──────────────┐
                 │  Task Split  │
                 └──────┬───────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ↓                           ↓
   ┌──────────────┐          ┌──────────────┐
   │ Claude Code  │          │    Codex     │
   │ Subtask A    │          │  Subtask B   │
   └──────┬───────┘          └──────┬───────┘
          │                           │
          └─────────────┬─────────────┘
                        ↓
                 ┌──────────────┐
                 │   Merge &    │
                 │   Review     │
                 └──────────────┘
```

**Концепция**: Разбить задачу на параллельные подзадачи, дать Claude и Codex разные части.

#### Пример разбиения

**Task**: "Implement user authentication"

**Subtasks**:
- **A (Claude Code)**: Database schema + RLS policies (требует архитектурной точности)
- **B (Codex)**: API endpoints implementation (более механическая работа)
- **C (Claude Code)**: Frontend integration + UX (требует понимания паттернов)

#### Orchestrator config

```json
{
  "tasks": [
    {
      "id": "user-authentication",
      "execution_mode": "parallel",
      "merge_strategy": "manual_review",
      "subtasks": [
        {
          "id": "auth-db-schema",
          "runner": "claude-code",
          "mode": "autonomous",
          "branch": "auth-db",
          "depends_on": []
        },
        {
          "id": "auth-api",
          "runner": "codex",
          "mode": "autonomous",
          "branch": "auth-api",
          "depends_on": ["auth-db-schema"]
        },
        {
          "id": "auth-frontend",
          "runner": "claude-code",
          "mode": "autonomous",
          "branch": "auth-frontend",
          "depends_on": ["auth-api"]
        }
      ],
      "merge": {
        "strategy": "review_then_merge",
        "reviewer": "claude-code",
        "conflict_resolution": "manual"
      }
    }
  ]
}
```

#### Преимущества Parallel

✅ Максимальная скорость (параллельная работа)
✅ Оптимальное использование сильных сторон каждого
✅ Масштабируемость (можно добавить больше агентов)

#### Недостатки Parallel

❌ Сложность координации (зависимости между подзадачами)
❌ Риск конфликтов при merge
❌ Требует умного разбиения задачи на независимые части

---

### Вариант 4: Collaborative (совместная работа)

```
┌─────────────────────────────────────┐
│         Main Task Loop              │
│                                     │
│  ┌──────────┐      ┌──────────┐   │
│  │  Claude  │ ←───→ │  Codex   │   │
│  │   Code   │      │          │   │
│  └──────────┘      └──────────┘   │
│       ↓                  ↓          │
│  [Makes plan]      [Implements]    │
│       ↓                  ↓          │
│  [Reviews code]    [Fixes issues]  │
│       ↓                  ↓          │
│  [Approves] ────────────→ [Done]   │
└─────────────────────────────────────┘
```

**Концепция**: Агенты работают вместе, как команда. Claude планирует и ревьюит, Codex реализует.

#### Workflow

1. **Claude** создаёт детальный план
2. **Codex** реализует по плану
3. **Claude** ревьюит, находит проблемы
4. **Codex** исправляет
5. **Claude** аппрувит → Done

#### Orchestrator config

```json
{
  "tasks": [
    {
      "id": "complex-feature",
      "execution_mode": "collaborative",
      "workflow": {
        "steps": [
          {
            "name": "plan",
            "agent": "claude-code",
            "action": "create_plan",
            "output": "framework/docs/plan.md"
          },
          {
            "name": "implement",
            "agent": "codex",
            "action": "implement",
            "input": "framework/docs/plan.md",
            "max_iterations": 3
          },
          {
            "name": "review",
            "agent": "claude-code",
            "action": "code_review",
            "output": "framework/review/issues.md"
          },
          {
            "name": "fix",
            "agent": "codex",
            "action": "fix_issues",
            "input": "framework/review/issues.md",
            "condition": "if issues.md not empty"
          },
          {
            "name": "approve",
            "agent": "claude-code",
            "action": "final_approval"
          }
        ],
        "max_cycles": 3
      }
    }
  ]
}
```

#### Преимущества Collaborative

✅ Качество + скорость (каждый делает своё)
✅ Итеративное улучшение (цикл review-fix)
✅ Естественное разделение ролей (архитектор vs исполнитель)

#### Недостатки Collaborative

❌ Сложная оркестрация (много шагов)
❌ Медленнее простого sequential (несколько итераций)
❌ Требует хорошей интеграции между агентами

---

## Рекомендации по выбору варианта

### Sequential — когда:
- Задача имеет чёткие фазы (design → build → review)
- Не критично время выполнения
- Важна прослеживаемость процесса

### Fallback — когда:
- Хотите попробовать Claude, но нужна гарантия завершения
- Задача может быть неоднозначной
- Важна автономность

### Parallel — когда:
- Задача легко делится на независимые подзадачи
- Критично время (нужна максимальная скорость)
- Есть чёткое понимание что кому давать

### Collaborative — когда:
- Сложная задача с высокими требованиями к качеству
- Готовы потратить больше времени ради лучшего результата
- Есть хорошая интеграция между агентами

---

## Реализация в devframework

### Минимальный вариант (быстрый старт)

Добавить в `orchestrator.json` новое поле `workflow_type`:

```json
{
  "tasks": [
    {
      "id": "feature-x",
      "workflow_type": "sequential",
      "phases": ["plan", "build", "review"]
    }
  ],
  "workflows": {
    "sequential": {
      "plan": {"agent": "claude-code", "mode": "interactive"},
      "build": {"agent": "codex", "mode": "autonomous"},
      "review": {"agent": "claude-code", "mode": "interactive"}
    }
  }
}
```

### Полная версия (production)

Создать `framework/orchestrator/workflows.py`:

```python
class WorkflowEngine:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.workflows = {
            "sequential": SequentialWorkflow,
            "fallback": FallbackWorkflow,
            "parallel": ParallelWorkflow,
            "collaborative": CollaborativeWorkflow
        }

    def execute(self, task):
        workflow_type = task.get("workflow_type", "sequential")
        workflow_class = self.workflows[workflow_type]
        workflow = workflow_class(self.orchestrator, task)
        return workflow.run()
```

---

## Метрики эффективности гибридного подхода

Сравнить с baseline (только Claude или только Codex):

| Метрика | Только Claude | Только Codex | Hybrid Sequential | Hybrid Fallback |
|---------|---------------|--------------|-------------------|-----------------|
| Время выполнения | 100% | 50% | 75% | 60% |
| Качество кода | 95% | 75% | 90% | 85% |
| Автономность | 40% | 95% | 70% | 90% |
| Следование паттернам | 95% | 70% | 90% | 80% |

*(гипотетические значения для демонстрации)*

---

**Статус**: Концептуальный дизайн, готов к прототипированию
**Следующий шаг**: Выбрать один вариант для MVP
**Рекомендация**: Начать с Sequential (проще всего) или Fallback (больше пользы)
