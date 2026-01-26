# Улучшения шаблонов задач для автономного режима

## Текущие проблемы с task definitions

Изучая существующие `framework/tasks/*.md`, я вижу:

### ✅ Что уже хорошо:
- Детальные описания функциональности
- Чёткие технические требования
- Ссылки на документацию
- Примеры кода

### ❌ Что вызывает вопросы у Claude Code:

1. **Неоднозначные формулировки**
   - "Реализуй аутентификацию" — какую? OAuth, JWT, сессии?
   - "Оптимизируй производительность" — какие метрики успеха?

2. **Отсутствие decision framework**
   - Нет приоритетов при выборе между подходами
   - Не указано, что делать если библиотека/API недоступна

3. **Нет явного time budget**
   - Неясно, это задача на 30 минут или 3 часа
   - Не определены обязательные vs опциональные части

4. **Отсутствие fallback strategies**
   - Что делать если тесты не проходят?
   - Как поступить если зависимость не устанавливается?

## Предлагаемая структура task definition

### Шаблон новой структуры

```markdown
---
# Метаданные задачи
task_id: db-schema
phase: main
execution_mode: autonomous
time_budget: 45
priority: high
dependencies: []
---

# [Task ID] Название задачи

## 🤖 AUTONOMOUS MODE PROTOCOL
[см. 01-autonomous-mode-protocol.md]

---

## 📋 TASK OVERVIEW

**Goal**: [Одно предложение — что нужно сделать]

**Success Criteria**: [Чёткие, измеримые критерии]
- [ ] Критерий 1
- [ ] Критерий 2
- [ ] Критерий 3

**Out of Scope**: [Что НЕ входит в эту задачу]
- Item 1
- Item 2

**Time Budget**: {TIME_BUDGET} minutes
- Core functionality: 60%
- Testing: 20%
- Documentation: 10%
- Buffer: 10%

---

## 🎯 DECISION FRAMEWORK

### Technology Choices

When choosing technologies, prioritize in this order:

1. **Already in project dependencies** (check package.json/requirements.txt)
2. **Explicitly mentioned in docs** (check framework/docs/)
3. **Industry standard for this stack** (e.g., PostgreSQL for relational DB)
4. **Conservative default** (e.g., REST over GraphQL if unclear)

### Architectural Decisions

**Pattern to follow**: [Explicit pattern]
- Check `[specific file path]` for existing implementation
- Match the style in `[reference file]`

**If uncertain between approaches**:
```
IF (approach A is safer but slower):
  → Choose A
  → Document trade-off in handoff.md

IF (approach B is innovative but risky):
  → Reject B in autonomous mode
  → Note B as future improvement in handoff.md
```

---

## 📝 DETAILED REQUIREMENTS

### Functional Requirements

[Детальное описание функциональности]

**Must Have** (обязательно в пределах time budget):
- Requirement 1
- Requirement 2

**Should Have** (если остаётся время):
- Requirement 3
- Requirement 4

**Nice to Have** (только если budget > 80% выполнено):
- Requirement 5

### Technical Requirements

**Stack constraints**:
- Language: [specific version]
- Framework: [specific version]
- Database: [specific type]

**Code style**:
- Follow existing patterns in `[file path]`
- Use same naming conventions as `[reference]`
- Match indentation style (tabs/spaces)

**Testing requirements**:
- Unit tests for all public functions
- Integration test for main flow
- Test coverage > 70% (measure with [tool])

---

## 🚧 FALLBACK STRATEGIES

### Scenario 1: Dependency installation fails

```
TRY:
  1. Check if alternative package available
  2. Check if functionality can be implemented without dependency
  3. Mock the dependency with stub implementation

DOCUMENT in handoff.md:
  - Which dependency failed
  - What was tried
  - What workaround used
```

### Scenario 2: Tests failing

```
TRY:
  1. Fix obvious issues (syntax, imports)
  2. Check if test assumptions match implementation
  3. Simplify implementation to pass tests

IF (still failing after 3 attempts):
  DOCUMENT: Test failure details + hypothesis why
  CONTINUE: Mark as known issue
```

### Scenario 3: Running out of time

```
AT 70% time budget:
  IF (< 50% requirements complete):
    → Focus only on "Must Have" items
    → Defer "Should Have" to future task
    → Document what was deferred

AT 90% time budget:
  → Finish current subtask
  → Write handoff with status
  → Commit what's done
```

### Scenario 4: Architectural blocker

```
IF (can't understand how existing code works):
  1. Spend max 15 min reading related files
  2. If still unclear: implement minimal version
  3. Document: "Assumed pattern [X], verify with team"

IF (conflicting patterns in codebase):
  → Choose pattern from most recent code
  → Document both patterns observed
```

---

## 📚 REFERENCE MATERIALS

**Existing code to study**:
- `[file path 1]` — example of similar feature
- `[file path 2]` — architectural pattern to follow

**Documentation**:
- `[doc path 1]` — technical spec
- `[doc path 2]` — API contracts

**External resources** (if needed):
- [Library official docs URL]
- [Framework guide URL]

---

## ✅ DEFINITION OF DONE

Task is complete when ALL of these are true:

- [ ] All "Must Have" requirements implemented
- [ ] Code follows existing patterns (verified by checking [reference file])
- [ ] Tests written and passing (run `[test command]`)
- [ ] No linter errors (run `[lint command]`)
- [ ] All decisions documented in `framework/docs/handoff.md`
- [ ] Commit message follows project convention
- [ ] Handoff document includes:
  - [ ] List of files changed
  - [ ] Key decisions made
  - [ ] Known issues/limitations
  - [ ] Deferred items (if any)

---

## 🔍 SELF-CHECK BEFORE COMPLETING

Run this mental checklist:

1. **Did I ask any questions?** → If yes, autonomous mode failed
2. **Are all decisions documented?** → Check handoff.md
3. **Do tests pass?** → Run test command
4. **Does code match existing style?** → Compare with reference file
5. **Is time budget respected?** → Check elapsed time
6. **Are blockers documented?** → List in handoff.md

If ALL checks pass → Task complete ✅

---

## 📤 HANDOFF TEMPLATE

When task is done, ensure `framework/docs/handoff.md` contains:

```markdown
## Task: [task_id] — [timestamp]

### What was delivered
- Feature 1: [brief description]
- Feature 2: [brief description]

### Files changed
- `path/to/file1.py` — [what changed]
- `path/to/file2.py` — [what changed]

### Key decisions
1. DECISION: [what] | RATIONALE: [why] | ALTERNATIVES: [rejected options]
2. DECISION: [what] | RATIONALE: [why] | ALTERNATIVES: [rejected options]

### Testing
- Unit tests: [number] added in [file]
- Integration tests: [number] added in [file]
- Manual testing steps: [if needed]

### Known issues / limitations
- [Issue 1]: [description] — [why not fixed]
- [Issue 2]: [description] — [why not fixed]

### Deferred items (if any)
- [Item 1]: [why deferred] — [recommendation]
- [Item 2]: [why deferred] — [recommendation]

### Time spent
- Planning: [X] min
- Implementation: [Y] min
- Testing: [Z] min
- Total: [T] min (budget was [B] min)

### Recommendations for next task
- [Recommendation 1]
- [Recommendation 2]
```

---

## 🚀 START IMPLEMENTATION

[Actual task details begin here...]
```

## Пример реального улучшения

Возьмём существующую задачу `framework/tasks/db-schema.md` и покажем как улучшить:

### ❌ БЫЛО (гипотетический пример проблемной задачи)

```markdown
# Database Schema

Create a database schema for the application.

Requirements:
- User table
- Authentication
- Data models
```

**Проблемы**:
- Неясно какая БД (PostgreSQL? MySQL? SQLite?)
- Какая аутентификация? (JWT? сессии?)
- Нет decision framework для выбора типов полей
- Нет fallback если БД недоступна

### ✅ СТАЛО

```markdown
---
task_id: db-schema
execution_mode: autonomous
time_budget: 45
---

# Database Schema Design

## 🤖 AUTONOMOUS MODE PROTOCOL
[full protocol here]

## 📋 TASK OVERVIEW

**Goal**: Create complete PostgreSQL database schema with RLS policies

**Success Criteria**:
- [ ] SQL migration file created in `framework/migration/001_initial_schema.sql`
- [ ] All tables have proper indexes
- [ ] RLS policies implemented for all tables
- [ ] Migration runs without errors on fresh DB
- [ ] Rollback script included

**Time Budget**: 45 minutes
- Schema design: 25 min
- RLS policies: 15 min
- Testing: 5 min

## 🎯 DECISION FRAMEWORK

### Database Choice
**Fixed**: PostgreSQL 15+ (already specified in project docs)

### Field Types
When choosing field type, use this priority:
1. Check existing tables for similar fields
2. Follow this mapping:
   - User IDs: `uuid` (not integer)
   - Timestamps: `timestamptz` (not timestamp)
   - Text: `text` (not varchar, unless length constraint needed)
   - Booleans: `boolean` (with DEFAULT)

### Naming Conventions
- Tables: plural snake_case (`users`, `auth_sessions`)
- Columns: singular snake_case (`user_id`, `created_at`)
- Indexes: `idx_{table}_{column(s)}`
- Foreign keys: `fk_{source_table}_{target_table}`

## 📝 DETAILED REQUIREMENTS

### Must Have Tables

1. **users**
   ```sql
   - id: uuid PRIMARY KEY DEFAULT gen_random_uuid()
   - email: text UNIQUE NOT NULL
   - created_at: timestamptz DEFAULT now()
   - updated_at: timestamptz DEFAULT now()
   ```

2. **auth_sessions**
   [similar detail...]

### RLS Policies
- Each table must have `ENABLE ROW LEVEL SECURITY`
- Policy names: `{table}_{action}_policy`
- Document policy logic in migration comments

## 🚧 FALLBACK STRATEGIES

### Scenario: Can't connect to PostgreSQL
```
DO NOT BLOCK on missing DB connection in autonomous mode.

INSTEAD:
1. Create migration file without running it
2. Add comment at top: "-- Run with: psql -f this_file.sql"
3. Document in handoff: "Migration not executed, DB unavailable"
4. Consider complete if file is syntactically valid
```

## 📚 REFERENCE MATERIALS

**Existing migrations**: Check `framework/migration/` for naming pattern
**RLS examples**: See `framework/docs/database-security.md`

## ✅ DEFINITION OF DONE

- [ ] Migration file at `framework/migration/001_initial_schema.sql`
- [ ] Rollback file at `framework/migration/001_rollback.sql`
- [ ] All decisions documented in handoff.md
- [ ] SQL syntax validated (try running in psql if available, else validate manually)
- [ ] Comments explain all non-obvious choices
```

## Преимущества новой структуры

1. **Нулевая неоднозначность** — все решения предопределены
2. **Чёткий time budget** — агент знает сколько времени тратить
3. **Fallback на каждый риск** — нет "застревания"
4. **Самопроверка** — checklist перед завершением
5. **Стандартизация** — все задачи в едином формате

## Как применить к существующим задачам

### Быстрый способ (без рефакторинга)

Добавить в начало каждого `framework/tasks/*.md`:

```markdown
[Prepend this to existing task content]

---
execution_mode: autonomous
time_budget: [estimate based on complexity]
---

## 🤖 AUTONOMOUS MODE PROTOCOL
[Include full protocol from 01-autonomous-mode-protocol.md]

## 🎯 DECISION DEFAULTS FOR THIS TASK

When uncertain, use these defaults:
- [Default 1 specific to this task]
- [Default 2 specific to this task]

[... existing task content below ...]
```

### Полный рефакторинг (рекомендуется)

1. Проанализировать каждую задачу на неоднозначности
2. Добавить decision framework для каждой развилки
3. Определить Must/Should/Nice-to-have приоритеты
4. Описать fallback для каждого блокера
5. Установить realistic time budget

## Метрики улучшения

Задача улучшена качественно, если:

- ✅ Можно дать 3 людям независимо — получат похожий результат
- ✅ Нет вопросов типа "а какую библиотеку использовать?"
- ✅ Есть fallback на каждый пункт "что если X не работает?"
- ✅ Время выполнения предсказуемо (± 20% от budget)

---

**Статус**: Готов к применению
**Следующий шаг**: Создать примеры (см. `examples/task-autonomous-example.md`)
