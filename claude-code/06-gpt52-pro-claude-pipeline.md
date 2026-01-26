# GPT-5.2 Pro + Claude Code: Архитектор + Исполнитель

> **NOTE**: В этом документе используются примерные пути к файлам (formal-spec.md, architecture-decisions.md, review-report.md и др.). Эти файлы **будут генерироваться** агентами во время выполнения задач. Пути указаны для иллюстрации структуры.

## Концепция

**Ключевая идея**: Использовать сильные стороны обоих агентов в одном пайплайне.

```
GPT-5.2 Pro reasoning → Устраняет неоднозначности
         ↓
Claude Code → Может работать автономно
```

## Почему эта связка работает

### Проблема Claude Code
❌ Задаёт много вопросов из-за неоднозначностей в ТЗ
❌ Останавливается при неопределённости
❌ Требует постоянного участия пользователя

### Сила GPT-5.2 Pro reasoning
✅ Формализует требования до машиночитаемого уровня
✅ Выявляет противоречия и дырки
✅ Описывает инварианты, edge cases, критерии
✅ Создаёт детальную архитектуру

### Результат
✅ Claude Code получает настолько детальный спек, что **не нужно задавать вопросы**
✅ Автономная работа часами без прерываний
✅ Высокое качество кода (сильная сторона Claude)
✅ Security audit от GPT-5.2 Pro на финальной стадии

---

## Архитектура пайплайна

```
┌─────────────────────────────────────────────────────┐
│ USER INPUT                                          │
│ "Реализовать систему уведомлений с email и push"   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 1: FORMAL SPECIFICATION                       │
│ Agent: GPT-5.2 Pro reasoning                        │
│ Mode: Interactive (задаёт вопросы пользователю)     │
│ Duration: 45-90 min                                 │
│                                                     │
│ Процесс:                                            │
│ 1. Анализирует требования                          │
│ 2. Задаёт уточняющие вопросы                       │
│ 3. Формализует архитектуру                         │
│ 4. Описывает инварианты                            │
│ 5. Определяет acceptance criteria                  │
│ 6. Создаёт test matrix                             │
│                                                     │
│ Output:                                             │
│ - formal-spec.md (детальная спецификация)          │
│ - architecture-decisions.md (ADR)                  │
│ - test-plan.md (тест-план)                         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 2: IMPLEMENTATION                             │
│ Agent: Claude Code                                  │
│ Mode: AUTONOMOUS (без вопросов!)                    │
│ Duration: 2-6 hours                                 │
│                                                     │
│ Input:                                              │
│ - formal-spec.md                                    │
│ - architecture-decisions.md                         │
│ - autonomous-mode-protocol.md                       │
│                                                     │
│ Почему автономен:                                   │
│ ✓ Все архитектурные решения приняты               │
│ ✓ Технологии выбраны                               │
│ ✓ Edge cases описаны                               │
│ ✓ Критерии готовности явные                        │
│ ✓ Паттерны указаны                                 │
│                                                     │
│ Процесс:                                            │
│ 1. Читает formal-spec.md                           │
│ 2. Реализует по спецификации                       │
│ 3. Следует паттернам проекта                       │
│ 4. Пишет тесты согласно test-plan.md              │
│ 5. Документирует решения в handoff.md             │
│                                                     │
│ Output:                                             │
│ - Реализованная функциональность                   │
│ - Тесты (unit + integration)                       │
│ - handoff.md (документация решений)                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 3: CODE REVIEW & SECURITY AUDIT               │
│ Agent: GPT-5.2 Pro reasoning                        │
│ Mode: Analytical                                    │
│ Duration: 30-60 min                                 │
│                                                     │
│ Input:                                              │
│ - formal-spec.md (оригинальная спецификация)       │
│ - Код от Claude Code                               │
│ - handoff.md (решения Claude)                      │
│                                                     │
│ Процесс:                                            │
│ 1. Проверяет соответствие спецификации             │
│ 2. Ищет логические баги                            │
│ 3. Проверяет инварианты                            │
│ 4. Находит race conditions                         │
│ 5. Security audit                                  │
│ 6. Проверяет edge cases                            │
│                                                     │
│ Output:                                             │
│ - review-report.md                                  │
│   - Critical issues (блокируют мерж)               │
│   - Warnings (желательно исправить)                │
│   - Suggestions (опциональные улучшения)           │
└──────────────────┬──────────────────────────────────┘
                   │
              [Если найдены critical issues]
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 4: FIXES (опционально)                        │
│ Agent: Claude Code                                  │
│ Mode: Autonomous                                    │
│ Duration: 30-90 min                                 │
│                                                     │
│ Input: review-report.md (только critical issues)    │
│ Исправляет найденные критичные проблемы            │
│                                                     │
│ Output: Исправленный код                            │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
              [ГОТОВО]
```

---

## Шаблон Formal Specification от GPT-5.2 Pro

### Структура документа `formal-spec.md`

```markdown
# Formal Specification: [Feature Name]

**Created by**: GPT-5.2 Pro reasoning
**Date**: [YYYY-MM-DD]
**For**: Claude Code (autonomous implementation)

---

## 1. EXECUTIVE SUMMARY

**What**: [Краткое описание фичи в 2-3 предложениях]

**Why**: [Бизнес-обоснование, зачем это нужно]

**Success Criteria**: [Как измерить успех]
- Metric 1: [конкретная метрика]
- Metric 2: [конкретная метрика]

---

## 2. FUNCTIONAL REQUIREMENTS

### 2.1 Core Features (Must Have)

#### Feature 1: [Name]
**Description**: [Детальное описание]

**User Story**: As a [role], I want [action], so that [benefit]

**Acceptance Criteria**:
- [ ] Given [precondition], when [action], then [expected result]
- [ ] Given [precondition], when [action], then [expected result]

**Invariants** (условия, которые ВСЕГДА должны быть true):
- Invariant 1: [формальное описание]
- Invariant 2: [формальное описание]

**Edge Cases**:
- Case 1: [описание] → Expected behavior: [что должно произойти]
- Case 2: [описание] → Expected behavior: [что должно произойти]

---

### 2.2 Optional Features (Should Have)

[Аналогичная структура для опциональных фич]

---

### 2.3 Out of Scope

**Explicitly NOT included**:
- Item 1: [что не входит] — Reason: [почему]
- Item 2: [что не входит] — Reason: [почему]

---

## 3. TECHNICAL ARCHITECTURE

### 3.1 Technology Stack

**Confirmed Choices** (уже приняты, НЕ менять):

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Database | PostgreSQL 15 | Existing stack, JSONB support |
| Backend | Node.js + Express | Project standard |
| Frontend | React 18 + TypeScript | Project standard |
| Styling | Tailwind CSS | Project standard |
| Testing | Jest + React Testing Library | Project standard |

**New Dependencies** (нужно добавить):
- Package: `nodemailer` — Purpose: Email sending
- Package: `web-push` — Purpose: Push notifications

---

### 3.2 Database Schema

**New Tables**:

```sql
-- Table: notifications
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL CHECK (type IN ('email', 'push', 'in_app')),
  title TEXT NOT NULL CHECK (length(title) > 0 AND length(title) <= 200),
  body TEXT CHECK (length(body) <= 2000),
  data JSONB DEFAULT '{}',
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Constraints
  CONSTRAINT valid_data CHECK (jsonb_typeof(data) = 'object')
);

-- Indexes
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, created_at DESC)
  WHERE read_at IS NULL;
CREATE INDEX idx_notifications_user_all ON notifications(user_id, created_at DESC);

-- RLS Policies
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY notifications_select_own ON notifications
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY notifications_update_own ON notifications
  FOR UPDATE USING (user_id = auth.uid());
```

**Schema Invariants**:
1. `user_id` must always reference valid user
2. `type` must be one of allowed values
3. `title` cannot be empty
4. `read_at` can only be set, never unset (monotonic)
5. `created_at` is immutable

---

### 3.3 API Endpoints

#### GET /api/notifications

**Purpose**: Fetch user's notifications

**Auth**: Required (JWT token)

**Query Parameters**:
```typescript
{
  unread?: boolean;      // Filter by read status (optional)
  limit?: number;        // Default: 20, Max: 100
  offset?: number;       // Default: 0
  type?: 'email' | 'push' | 'in_app';  // Filter by type (optional)
}
```

**Response**:
```typescript
{
  data: Array<{
    id: string;
    type: 'email' | 'push' | 'in_app';
    title: string;
    body: string | null;
    data: object;
    read_at: string | null;
    created_at: string;
  }>;
  pagination: {
    total: number;
    limit: number;
    offset: number;
    has_more: boolean;
  };
}
```

**Error Responses**:
- 401: Unauthorized (no/invalid token)
- 400: Bad request (invalid query params)
- 500: Internal server error

**Validation Rules**:
- `limit`: Must be 1-100
- `offset`: Must be >= 0
- `type`: Must be one of allowed values

**Edge Cases**:
1. User has no notifications → Return empty array with total=0
2. Offset > total → Return empty array with has_more=false
3. Invalid type filter → 400 error with descriptive message

---

#### POST /api/notifications/:id/read

**Purpose**: Mark notification as read

**Auth**: Required (JWT token)

**Path Parameters**:
- `id`: UUID of notification

**Request Body**: None

**Response**:
```typescript
{
  data: {
    id: string;
    read_at: string;  // Timestamp when marked as read
  }
}
```

**Error Responses**:
- 401: Unauthorized
- 404: Notification not found or not owned by user
- 400: Notification already marked as read
- 500: Internal server error

**Invariants**:
- Cannot unmark as read (read_at is monotonic)
- Can only mark own notifications
- Idempotent: calling twice returns same result

---

### 3.4 File Structure

**New Files to Create**:

```
src/
├── api/
│   └── notifications/
│       ├── index.ts              # Router
│       ├── list.ts               # GET /api/notifications
│       ├── markRead.ts           # POST /api/notifications/:id/read
│       └── __tests__/
│           └── notifications.test.ts
│
├── services/
│   ├── notificationService.ts    # Business logic
│   └── emailService.ts           # Email sending
│
├── components/
│   ├── NotificationBell.tsx      # Bell icon with badge
│   ├── NotificationList.tsx      # Dropdown list
│   └── NotificationItem.tsx      # Single notification
│
├── hooks/
│   └── useNotifications.ts       # React hook for real-time
│
└── types/
    └── notification.ts           # TypeScript types

db/
└── migrations/
    └── 007_create_notifications.sql
```

---

### 3.5 Code Patterns to Follow

**Pattern Source**: Check these files for existing patterns

| Pattern | Reference File | What to Match |
|---------|---------------|---------------|
| API endpoint structure | `src/api/auth/me.ts` | Middleware, error handling, response format |
| Database queries | `src/db/queries/users.ts` | Prepared statements, error handling |
| React components | `src/components/UserMenu.tsx` | TypeScript typing, hooks usage |
| Testing | `src/api/__tests__/auth.test.ts` | Test structure, mocking |

**Naming Conventions**:
- API files: `camelCase.ts`
- Components: `PascalCase.tsx`
- Hooks: `useCamelCase.ts`
- Database tables: `snake_case`
- Database columns: `snake_case`
- TypeScript types: `PascalCase`

---

## 4. NON-FUNCTIONAL REQUIREMENTS

### 4.1 Performance

- GET /api/notifications: < 200ms p95
- POST /api/notifications/:id/read: < 100ms p95
- Notification list load: < 500ms perceived (with skeleton loader)

### 4.2 Security

**Threats to Mitigate**:
1. **IDOR**: User accessing other user's notifications
   - Mitigation: RLS policies + server-side user_id check
2. **XSS**: Malicious content in notification body
   - Mitigation: Sanitize HTML, use DOMPurify in frontend
3. **SQL Injection**: Malicious query params
   - Mitigation: Parameterized queries only
4. **DoS**: Excessive notifications
   - Mitigation: Rate limiting on notification creation

**Security Checklist**:
- [ ] All queries use parameterized statements
- [ ] RLS policies tested with different user contexts
- [ ] HTML content sanitized before rendering
- [ ] Rate limiting implemented (100 req/min per user)

### 4.3 Accessibility

- Bell icon has `aria-label="Notifications"`
- Notification count has `aria-live="polite"`
- Keyboard navigation (Tab, Enter, Escape)
- Screen reader friendly (ARIA labels on all interactive elements)

---

## 5. TEST PLAN

### 5.1 Unit Tests

**Backend** (`src/api/notifications/__tests__/notifications.test.ts`):

```typescript
describe('GET /api/notifications', () => {
  test('returns user notifications', async () => {
    // Setup: Create test notifications
    // Action: GET request with auth
    // Assert: Correct data, pagination
  });

  test('filters by unread status', async () => {
    // Test unread=true parameter
  });

  test('respects pagination limits', async () => {
    // Test limit, offset, has_more
  });

  test('returns 401 without auth', async () => {
    // Test unauthorized access
  });

  test('does not return other users notifications', async () => {
    // Security test: IDOR prevention
  });
});

describe('POST /api/notifications/:id/read', () => {
  test('marks notification as read', async () => {
    // Test happy path
  });

  test('is idempotent', async () => {
    // Test calling twice
  });

  test('returns 404 for other user notification', async () => {
    // Security test
  });
});
```

**Frontend** (`src/components/__tests__/NotificationBell.test.tsx`):

```typescript
describe('NotificationBell', () => {
  test('displays unread count', () => {
    // Test badge with count
  });

  test('opens dropdown on click', () => {
    // Test interaction
  });

  test('marks as read on click', () => {
    // Test marking read
  });

  test('is keyboard accessible', () => {
    // Test Tab, Enter, Escape
  });
});
```

### 5.2 Integration Tests

**Full Flow Test**:
1. Create notification in DB
2. GET /api/notifications → should appear
3. Click notification → mark as read
4. GET /api/notifications?unread=true → should not appear

### 5.3 Manual Testing Checklist

- [ ] Notification appears in real-time (without refresh)
- [ ] Badge count updates after marking as read
- [ ] Works in Chrome, Firefox, Safari
- [ ] Keyboard navigation works
- [ ] Screen reader announces notifications

---

## 6. ACCEPTANCE CRITERIA (Definition of Done)

Implementation is complete when ALL are true:

### Functional
- [ ] All "Must Have" features implemented and tested
- [ ] All API endpoints return correct responses
- [ ] Database migration runs successfully
- [ ] RLS policies prevent unauthorized access

### Quality
- [ ] All unit tests passing (coverage > 80%)
- [ ] Integration tests passing
- [ ] No TypeScript errors
- [ ] No ESLint warnings
- [ ] Code follows project patterns (verified by comparing to reference files)

### Documentation
- [ ] All decisions documented in `handoff.md`
- [ ] API endpoints documented in code comments
- [ ] Complex logic has explanatory comments
- [ ] README updated (if public API changes)

### Security
- [ ] Security checklist (section 4.2) completed
- [ ] No secrets in code
- [ ] Input validation on all endpoints
- [ ] XSS prevention tested

---

## 7. IMPLEMENTATION GUIDANCE FOR CLAUDE CODE

### 7.1 Decision Framework

**If you encounter ambiguity NOT covered in this spec:**

1. **Check reference files first** (section 3.5)
   - Follow existing patterns exactly

2. **Choose conservative approach**
   - Simpler > Complex
   - Explicit > Implicit
   - Standard library > New dependency

3. **Document your decision in handoff.md**
   ```markdown
   DECISION: [what you chose]
   RATIONALE: [why]
   ALTERNATIVES: [what else you considered]
   SPEC GAP: [what was missing from spec]
   ```

### 7.2 If You Get Blocked

**DO NOT stop the entire task.**

Instead:
1. Try 3 different approaches (document each)
2. If still blocked: implement minimal version that compiles
3. Document blocker in handoff.md:
   ```markdown
   BLOCKER: [description]
   ATTEMPTED: [what you tried]
   WORKAROUND: [what you did instead]
   NEEDS: [what's needed to unblock]
   ```
4. Continue with next subtask

### 7.3 Time Budget

**Total**: 240 minutes (4 hours)

- Database migration: 20 min
- API endpoints: 90 min (45 min each)
- Frontend components: 80 min
- Tests: 40 min
- Integration & polish: 10 min

**Progress Checkpoints**:
- 60 min (25%): Database + 1 endpoint done
- 120 min (50%): Both endpoints + basic UI done
- 180 min (75%): All features done, starting tests
- 240 min (100%): Tests done, ready for review

**If running behind at 50% mark**: Focus only on "Must Have", defer "Should Have"

---

## 8. KNOWN RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Push notifications require VAPID keys setup | High | Medium | Defer to Phase 2, implement email first |
| Real-time updates complex in Safari | Medium | High | Use polling fallback for Safari |
| Email rate limits hit during testing | Low | Medium | Mock email service in tests |
| Notification spam (user gets too many) | Medium | Low | Add rate limiting from start |

---

## 9. SUCCESS METRICS

**After implementation, measure**:

- Implementation time: Target < 5 hours
- Test coverage: Target > 80%
- API response times: p95 < 200ms
- Zero critical security issues in review
- Autonomous completion: No questions asked during implementation

---

## 10. APPENDIX

### 10.1 Example Notification Objects

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "email",
  "title": "Welcome to the platform!",
  "body": "Thanks for signing up. Get started by...",
  "data": {
    "action_url": "/onboarding",
    "action_label": "Get Started"
  },
  "read_at": null,
  "created_at": "2026-01-26T10:30:00Z"
}
```

### 10.2 Database Test Data

```sql
-- Use this for testing
INSERT INTO notifications (user_id, type, title, body) VALUES
  ('123e4567-e89b-12d3-a456-426614174000', 'in_app', 'Test notification 1', 'Body 1'),
  ('123e4567-e89b-12d3-a456-426614174000', 'email', 'Test notification 2', 'Body 2');
```

---

**This specification is complete and unambiguous. Claude Code should have ZERO questions during implementation.**
```

---

## Интеграция в orchestrator.json

```json
{
  "runners": {
    "gpt52-pro": {
      "type": "gpt52-pro-reasoning",
      "command": "gpt52-cli",
      "mode": "interactive",
      "note": "Used for architecture and review phases"
    },
    "claude-code": {
      "type": "claude-code",
      "command": "claude-code",
      "autonomous_mode": {
        "enabled": true,
        "protocol_file": "claude-code/01-autonomous-mode-protocol.md"
      }
    }
  },

  "workflows": {
    "gpt52-claude-pipeline": {
      "description": "GPT-5.2 Pro (architect) → Claude Code (executor)",
      "phases": [
        {
          "name": "formal-spec",
          "agent": "gpt52-pro",
          "mode": "interactive",
          "output": "framework/docs/formal-spec.md"
        },
        {
          "name": "implementation",
          "agent": "claude-code",
          "mode": "autonomous",
          "input": "framework/docs/formal-spec.md",
          "depends_on": ["formal-spec"]
        },
        {
          "name": "review",
          "agent": "gpt52-pro",
          "mode": "analytical",
          "input": [
            "framework/docs/formal-spec.md",
            "git diff main...feature-branch",
            "framework/docs/handoff.md"
          ],
          "output": "framework/review/review-report.md",
          "depends_on": ["implementation"]
        },
        {
          "name": "fixes",
          "agent": "claude-code",
          "mode": "autonomous",
          "input": "framework/review/review-report.md",
          "condition": "if critical issues found",
          "depends_on": ["review"]
        }
      ]
    }
  },

  "tasks": [
    {
      "id": "notifications-feature",
      "workflow": "gpt52-claude-pipeline",
      "phases": [
        {
          "phase": "formal-spec",
          "file": "prompts/notifications-initial-request.md",
          "time_budget": 90
        },
        {
          "phase": "implementation",
          "file": "framework/docs/formal-spec.md",
          "time_budget": 240,
          "watchdog": {
            "enabled": true,
            "check_interval_seconds": 120,
            "stuck_threshold_seconds": 600
          }
        },
        {
          "phase": "review",
          "time_budget": 60
        },
        {
          "phase": "fixes",
          "time_budget": 60,
          "optional": true
        }
      ]
    }
  ]
}
```

---

## Полный пример workflow

### Шаг 1: Пользователь даёт задачу GPT-5.2 Pro

**Input**: `prompts/notifications-initial-request.md`

```markdown
Нужно реализовать систему уведомлений для SaaS-приложения.

Требования:
- In-app уведомления (колокольчик в header)
- Email уведомления
- Push notifications (опционально)
- Пользователь может отмечать как прочитанное
- История уведомлений

Стек: Node.js, React, PostgreSQL
```

### Шаг 2: GPT-5.2 Pro задаёт вопросы

```
GPT-5.2: "Уточню несколько моментов для полной спецификации:

1. Email уведомления:
   - Использовать существующий email provider или нужен новый?
   - Какие триггеры для email? (сразу, дайджест раз в день, настраиваемо?)

2. In-app уведомления:
   - Real-time (WebSocket) или polling?
   - Нужна ли группировка похожих уведомлений?

3. Push notifications:
   - Web Push (Service Workers) или native apps тоже?
   - Defer в Phase 2 или реализовать сразу?

4. Архитектура:
   - Notifications как отдельный микросервис или часть монолита?
   - Нужна ли очередь (Redis/RabbitMQ) или синхронно?

5. Privacy & Security:
   - Могут ли уведомления содержать sensitive data?
   - Как долго хранить (retention policy)?
```

### Шаг 3: Пользователь отвечает

```
User: "
1. Email - использовать существующий SendGrid, триггер сразу
2. In-app - polling проще, real-time defer в Phase 2
3. Push - defer в Phase 2 совсем
4. Архитектура - часть монолита, синхронно
5. Privacy - нет sensitive data, хранить 90 дней
"
```

### Шаг 4: GPT-5.2 Pro создаёт formal-spec.md

(См. шаблон выше — полный документ на ~20KB с детализацией каждого аспекта)

### Шаг 5: Claude Code реализует автономно

**Запуск**:
```bash
python orchestrator.py --phase implementation --task notifications-feature
```

**Что происходит**:
1. Claude Code читает `formal-spec.md`
2. Видит что все решения приняты (email = SendGrid, polling, монолит, etc)
3. Читает паттерны из reference files
4. Реализует:
   - Database migration (20 мин)
   - API endpoints (90 мин)
   - React components (80 мин)
   - Tests (40 мин)
5. Документирует решения в `handoff.md`
6. **Ноль вопросов к пользователю** (всё было в спеке)

### Шаг 6: GPT-5.2 Pro делает review

**Input**:
- `formal-spec.md` (оригинальная спецификация)
- `git diff main...notifications-branch` (код от Claude)
- `handoff.md` (решения Claude)

**Process**:
```
GPT-5.2 Pro анализирует:

✓ Соответствие спецификации
✓ Инварианты соблюдены (read_at monotonic, user_id always valid)
✓ Security: RLS policies работают
✓ Edge cases обработаны
⚠ Найдено: Race condition в markAsRead (два параллельных запроса)
⚠ Найдено: Missing index на notifications.created_at
✓ Accessibility: ARIA labels присутствуют
```

**Output**: `review-report.md`

```markdown
# Code Review Report: Notifications Feature

## Summary
Implementation matches specification 95%.
Found 2 issues: 1 critical, 1 warning.

## Critical Issues (блокируют мерж)

### Issue 1: Race Condition in markAsRead
**File**: `src/api/notifications/markRead.ts:23`

**Problem**:
Two parallel requests can both see read_at=null and both try to update.
Not transactionally safe.

**Current Code**:
```typescript
const notification = await db.query('SELECT * FROM notifications WHERE id = $1', [id]);
if (notification.read_at !== null) {
  throw new Error('Already read');
}
await db.query('UPDATE notifications SET read_at = NOW() WHERE id = $1', [id]);
```

**Fix**:
Use atomic UPDATE with WHERE condition:
```typescript
const result = await db.query(
  'UPDATE notifications SET read_at = NOW() WHERE id = $1 AND read_at IS NULL RETURNING *',
  [id]
);
if (result.rows.length === 0) {
  // Already read or not found
}
```

**Severity**: Critical (data race)
**Must fix**: Yes

---

## Warnings (желательно исправить)

### Issue 2: Missing Index
**File**: `framework/migration/007_create_notifications.sql`

**Problem**:
Query `SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC`
will be slow without index on created_at.

**Fix**:
Add composite index:
```sql
CREATE INDEX idx_notifications_user_created ON notifications(user_id, created_at DESC);
```

**Severity**: Warning (performance issue at scale)
**Must fix**: No (but recommended)

---

## Suggestions (опциональные улучшения)

1. Consider adding `updated_at` trigger for audit
2. Notification `data` JSONB could use GIN index for filtering
3. Add Prometheus metrics for notification send rate

---

## Approval Status

❌ NOT APPROVED - Fix critical issue #1 first
```

### Шаг 7: Claude Code исправляет critical issues

**Input**: `review-report.md` (секция Critical Issues)

**Process**:
```
Claude Code:
1. Читает Issue #1
2. Применяет предложенный fix
3. Обновляет тесты (добавляет test for race condition)
4. Коммитит: "fix: atomic update in markAsRead to prevent race condition"
5. Документирует в handoff.md:
   "FIXED: Race condition in markAsRead (review issue #1)
    Changed to atomic UPDATE with WHERE clause"
```

**Duration**: 15 минут

### Шаг 8: Финальная проверка

GPT-5.2 Pro проверяет что fix применён:

```markdown
# Re-review: Critical Issues

## Issue #1: Race Condition
✅ FIXED - Atomic UPDATE implemented correctly
✅ Test added for concurrent requests
✅ Code matches recommended fix

## Approval Status
✅ APPROVED - Ready to merge
```

---

## Метрики эффективности

### Сравнение подходов

| Метрика | Claude Only | GPT-5.2 Pro Only | **Pipeline** |
|---------|-------------|------------------|--------------|
| **Время спецификации** | 30 мин (неполная) | 90 мин (полная) | **90 мин** |
| **Вопросов во время реализации** | 15-20 | 0 | **0** ✅ |
| **Время реализации** | 6-8 часов | 8-10 часов | **4 часа** ✅ |
| **Багов в review** | 3-5 | 1-2 | **2** |
| **Critical issues** | 2-3 | 0-1 | **1** |
| **Качество кода** | 8/10 | 7/10 | **9/10** ✅ |
| **Security audit качество** | 6/10 | 10/10 | **10/10** ✅ |
| **Общее время** | 7-9 часов | 9-11 часов | **6 часов** ✅ |
| **Привязка пользователя** | Высокая | Средняя | **Низкая** ✅ |

### Детализация по фазам

```
GPT-5.2 + Claude Pipeline:
├─ Phase 1 (Spec): 90 min [GPT-5.2 Pro, interactive]
├─ Phase 2 (Code): 240 min [Claude Code, AUTONOMOUS] ← Нет вопросов!
├─ Phase 3 (Review): 60 min [GPT-5.2 Pro, analytical]
└─ Phase 4 (Fixes): 30 min [Claude Code, autonomous]
─────────────────────────────────────────────────────
Total: 420 min (7 hours)

Из них user interaction:
- Phase 1: 90 min (отвечает на вопросы GPT-5.2 Pro)
- Phase 2: 0 min (автономная работа Claude) ✅
- Phase 3: 10 min (читает review report)
- Phase 4: 0 min (автономные фиксы)
─────────────────────────────────────────────────────
Total user time: ~100 min (1.7 hours)

Autonomy index: 76% (5.3 из 7 часов автономно)
```

### ROI анализ

**Стоимость**:
- ChatGPT Pro: $200/мес
- Claude Code: включен в Anthropic API (~$50/мес)
- **Total**: ~$250/мес

**Экономия времени** (на 1 фиче):
- Без пайплайна: 9 часов
- С пайплайном: 7 часов
- **Saved**: 2 часа чистой работы

**Экономия привязки**:
- Без пайплайна: 7 часов привязки к компьютеру
- С пайплайном: 1.7 часа привязки
- **Freedom**: 5.3 часа можешь делать другие дела

**Break-even** (при $100/час developer time):
- Savings: 2 часа × $100 = $200 за фичу
- Cost: $250/мес
- Break-even: **1.25 фичи в месяц**

---

## Практические рекомендации

### Когда использовать этот пайплайн

✅ **Используй когда:**
- Фича сложная (> 4 часов реализации)
- Важна надёжность (финансы, безопасность, данные)
- Нужна автономность (не хочешь быть привязанным)
- Есть бюджет на ChatGPT Pro
- Проект долгосрочный

❌ **Не используй когда:**
- Простые CRUD (< 2 часов реализации)
- Прототипы, эксперименты
- Нет бюджета на Pro
- Задача исследовательская (архитектура неясна)

### Оптимизация пайплайна

**Ускорить Phase 1 (Spec)**:
- Подготовь шаблон вопросов для GPT-5.2 Pro
- Дай ссылки на docs заранее
- Укажи reference files в initial request

**Ускорить Phase 2 (Code)**:
- Убедись что formal-spec.md действительно полный
- Добавь больше code examples в спек
- Укажи явно что defer в будущее

**Улучшить Phase 3 (Review)**:
- Дай GPT-5.2 Pro доступ к test results
- Включи security checklist в спек
- Попроси ranked list issues (critical → warning → suggestion)

---

## Альтернативные конфигурации

### Вариант 1: Бюджетная (без GPT-5.2 Pro)

```
Claude Code (spec, interactive)
       ↓
Codex (implementation, autonomous)
       ↓
Claude Code (review, interactive)
```

**Плюсы**: Дешевле (~$50/мес вместо $250)
**Минусы**: Claude будет задавать вопросы в Phase 1, менее строгий review

---

### Вариант 2: Максимальное качество

```
GPT-5.2 Pro (spec, interactive)
       ↓
Claude Code (architecture, interactive) ← Добавлен шаг
       ↓
Codex (implementation, autonomous)
       ↓
GPT-5.2 Pro (review, analytical)
       ↓
Claude Code (polish, autonomous)
```

**Плюсы**: Максимум качества, код следует паттернам
**Минусы**: Дольше (~8-9 часов вместо 7)

---

### Вариант 3: Ультра-автономный

```
GPT-5.2 Pro (spec, interactive) ← Только этот шаг с пользователем
       ↓
Codex (implementation, autonomous)
       ↓
GPT-5.2 Pro (review, autonomous) ← Тоже автономно!
       ↓
Codex (fixes, autonomous)
```

**Плюсы**: Максимальная автономность (пользователь только в начале)
**Минусы**: Нужна автономная версия GPT-5.2 Pro review

---

## Troubleshooting

### Проблема: Claude всё равно задаёт вопросы

**Причина**: formal-spec.md недостаточно детальный

**Решение**:
1. Проверь что спек содержит ВСЕ секции из шаблона
2. Добавь больше примеров кода
3. Укажи reference files явно
4. В следующий раз дай GPT-5.2 Pro больше времени на спек

---

### Проблема: GPT-5.2 Pro делает спек слишком долго

**Причина**: Overthinking, слишком детализирует

**Решение**:
1. Дай ограничение времени: "У тебя 60 минут на спек"
2. Попроси "production-ready spec, не academic paper"
3. Укажи что defer некритичные детали
4. Дай template и скажи "заполни этот шаблон"

---

### Проблема: Claude не находит reference files

**Причина**: Пути в спеке неточные или файлы не существуют

**Решение**:
1. Проверь что reference files действительно существуют
2. Используй relative paths от project root
3. Дай Claude список всех files: `find src -name "*.ts" > files.txt`
4. Включи `ls -la` output в спек

---

### Проблема: Review находит слишком много issues

**Причина**: GPT-5.2 Pro слишком строг, или Claude отклонился от спека

**Решение**:
1. Проверь что Claude читал formal-spec.md (в handoff должны быть ссылки)
2. Если issues legitimate: улучши спек для следующего раза
3. Если GPT-5.2 Pro nitpicky: попроси focus on critical/high severity only
4. Calibrate: дай примеры "что считать critical vs warning"

---

## Следующие шаги

1. ✅ Прочитали документ
2. → Решить: есть ли доступ к GPT-5.2 Pro? (ChatGPT Pro subscription)
3. → Попробовать на одной фиче:
   - Пусть GPT-5.2 Pro создаст formal-spec.md
   - Claude Code реализует по спеку (проверить: сколько вопросов?)
   - GPT-5.2 Pro сделает review
4. → Собрать метрики (время, вопросы, качество)
5. → Решить: оправдана ли стоимость Pro subscription?
6. → Если да: интегрировать в orchestrator.json
7. → Если нет: использовать бюджетный вариант (Claude-only)

---

**Статус**: ✅ Готов к использованию
**Требует**: ChatGPT Pro subscription ($200/мес) для GPT-5.2 Pro reasoning
**ROI**: Break-even при 1.25+ фичах в месяц
**Автономность**: 76% времени без участия пользователя
**Ключевая выгода**: Claude Code работает автономно благодаря детальному спеку от GPT-5.2 Pro

🚀 **Это финальный элемент вашей автономной архитектуры!**
