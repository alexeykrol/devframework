# Пример гибридного workflow: Claude Code + Codex

Этот пример показывает как комбинировать сильные стороны обоих агентов в одном проекте.

## Сценарий

**Задача**: Реализовать систему уведомлений для SaaS-приложения

**Сложность**: Высокая (архитектурные решения + большой объём кода)

**Требования**:
- In-app уведомления (колокольчик в header)
- Email уведомления
- Push уведомления (опционально)
- Настройки уведомлений для пользователя
- История уведомлений
- Отметка как прочитанное

---

## Workflow Strategy: Sequential (Plan → Build → Review)

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: ARCHITECTURE & PLANNING                        │
│ Agent: Claude Code (Interactive)                        │
│ Duration: 30-45 minutes                                 │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 2: IMPLEMENTATION                                 │
│ Agent: Codex (Autonomous)                               │
│ Duration: 2-3 hours                                     │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 3: CODE REVIEW & POLISH                           │
│ Agent: Claude Code (Interactive)                        │
│ Duration: 45-60 minutes                                 │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1: Architecture & Planning (Claude Code)

### Task Definition: `notifications-architecture.md`

```markdown
# Notification System Architecture

**Execution Mode**: Interactive (Claude can ask questions)

**Goal**: Design comprehensive notification system architecture

**Deliverables**:
1. Architecture document with diagrams
2. Database schema design
3. API endpoint specifications
4. Technology choices with rationale
5. Implementation task breakdown

**Process**:
- Analyze existing codebase patterns
- Research notification best practices
- Present options for key decisions (ask user to choose)
- Document all architectural decisions
- Create detailed implementation plan for next phase

**Output Files**:
- `framework/docs/notifications-architecture.md`
- `framework/docs/notifications-decisions.md`
- `framework/tasks/notifications-implement.md` (detailed spec for Codex)
```

### Claude's Interactive Questions

During this phase, Claude can ask questions like:

1. "I see the app uses PostgreSQL. For real-time notifications, should we:
   - Option A: Use PostgreSQL LISTEN/NOTIFY (simpler, existing stack)
   - Option B: Add Redis pub/sub (better performance, new dependency)
   - Option C: WebSocket server (full real-time, complex)"

2. "For email delivery, I found these patterns:
   - Existing auth emails use SendGrid
   - Should we use same provider for consistency?"

3. "Push notifications require:
   - Service worker registration
   - VAPID keys setup
   - Should we implement in Phase 2 or defer to Phase 3?"

### Expected Output: Architecture Document

```markdown
# Notification System Architecture

## Overview
[High-level description]

## Technology Stack
- **Database**: PostgreSQL (existing)
- **Real-time**: PostgreSQL LISTEN/NOTIFY (rationale: no new deps)
- **Email**: SendGrid (rationale: already integrated)
- **Push**: Deferred to Phase 3 (rationale: optional feature)

## Database Schema

### Table: notifications
```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  type VARCHAR(50) NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  data JSONB,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read_at) WHERE read_at IS NULL;
```

## API Endpoints

### GET /api/notifications
- Returns: List of user's notifications (paginated)
- Query params: ?unread=true, ?limit=20, ?offset=0

### POST /api/notifications/:id/read
- Marks notification as read
- Returns: Updated notification

### GET /api/notifications/preferences
- Returns: User's notification preferences

### PUT /api/notifications/preferences
- Updates: User's notification preferences

## Implementation Tasks for Phase 2

1. Task: notifications-db-migration (30 min)
2. Task: notifications-api-endpoints (90 min)
3. Task: notifications-email-service (45 min)
4. Task: notifications-ui-components (60 min)
5. Task: notifications-real-time (45 min)

Total estimated: 4.5 hours
```

---

## Phase 2: Implementation (Codex)

### Task Definition: `notifications-implement.md`

This file is generated by Claude in Phase 1, optimized for autonomous execution.

```markdown
---
execution_mode: autonomous
time_budget: 270 (4.5 hours)
---

# Notification System Implementation

## 🤖 AUTONOMOUS MODE PROTOCOL
[Standard protocol here]

## 📋 IMPLEMENTATION SPEC

You are implementing the notification system according to the architecture document created in Phase 1.

**CRITICAL**: Follow the architecture EXACTLY. All decisions are already made.

### Architecture Reference
Read these files FIRST before starting:
- `framework/docs/notifications-architecture.md` — Full architecture
- `framework/docs/notifications-decisions.md` — Decision rationale

### Subtask 1: Database Migration (30 min budget)

**Goal**: Create and run migration for notifications table

**Files to create**:
- `framework/migration/005_create_notifications.sql`

**SQL to implement** (copy from architecture doc):
```sql
[Exact SQL from architecture doc]
```

**Testing**:
- Run migration: `psql -f framework/migration/005_create_notifications.sql`
- Verify: `psql -c "\d notifications"`

**Success criteria**:
- Migration file created
- Migration runs without errors
- All indexes created

---

### Subtask 2: API Endpoints (90 min budget)

**Goal**: Implement 4 notification endpoints

**Files to create**:
- `src/api/notifications/index.js` — Main router
- `src/api/notifications/list.js` — GET /api/notifications
- `src/api/notifications/markRead.js` — POST /api/notifications/:id/read
- `src/api/notifications/preferences.js` — GET/PUT preferences

**Pattern to follow**:
- Look at `src/api/auth/` for existing API patterns
- Use same middleware (auth, error handling)
- Match response format

**Endpoint specifications** (from architecture):
[Detailed specs for each endpoint]

**Testing**:
- Create `src/api/notifications/__tests__/notifications.test.js`
- Test each endpoint with valid/invalid inputs
- Run: `npm test notifications`

---

### Subtask 3: Email Service (45 min budget)

**Goal**: Create service for sending notification emails

**Files to create**:
- `src/services/notificationEmail.js`

**Pattern to follow**:
- Check `src/services/authEmail.js` for SendGrid usage
- Use same template pattern
- Match error handling

**Email templates to create**:
- `templates/notification.html` — Generic notification email

**Testing**:
- Mock SendGrid in tests
- Test template rendering
- Run: `npm test notificationEmail`

---

### Subtask 4: UI Components (60 min budget)

**Goal**: Create notification bell UI

**Files to create**:
- `src/components/NotificationBell.jsx` — Bell icon with badge
- `src/components/NotificationList.jsx` — Dropdown list
- `src/components/NotificationItem.jsx` — Single notification

**Pattern to follow**:
- Check `src/components/Header.jsx` for header integration
- Use same styling approach (Tailwind/CSS modules/etc)
- Match icon library (check package.json)

**Features**:
- Bell icon with unread count badge
- Click opens dropdown with recent notifications
- "Mark as read" action
- "View all" link to full page

**Testing**:
- Create `src/components/__tests__/NotificationBell.test.jsx`
- Test rendering, interaction
- Run: `npm test NotificationBell`

---

### Subtask 5: Real-time Updates (45 min budget)

**Goal**: Implement real-time notification delivery

**Files to create**:
- `src/lib/notificationListener.js` — PostgreSQL LISTEN client
- `src/hooks/useNotifications.js` — React hook for real-time

**Pattern to follow**:
- Check if WebSocket already used (search for "ws" or "socket")
- If not: Use PostgreSQL LISTEN/NOTIFY as specified

**Implementation**:
- Server: NOTIFY on new notification insert
- Client: LISTEN and update state
- React hook: Subscribe/unsubscribe

**Testing**:
- Integration test: Create notification → UI updates
- Run: `npm test notifications.integration`

---

## 📤 HANDOFF REQUIREMENTS

At completion, ensure these files exist:

1. **Code files**: All files listed in subtasks
2. **Tests**: All test files with passing tests
3. **Handoff doc**: `framework/docs/handoff.md` with:
   - What was implemented
   - Files created/modified
   - Any deviations from architecture (with reason)
   - Known issues/limitations
   - Testing results

## 🚨 FALLBACK STRATEGIES

**If stuck for > 5 minutes on any subtask**:
1. Document the blocker in handoff.md
2. Implement minimal version that compiles
3. Move to next subtask
4. Mark subtask as "partially complete"

**If running out of time**:
- Prioritize: Database → API → UI → Email → Real-time
- At 80% time: Wrap up current subtask, document rest as TODO
```

### Orchestrator Config for Phase 2

```json
{
  "tasks": [
    {
      "id": "notifications-implement",
      "file": "framework/tasks/notifications-implement.md",
      "runner": "codex",
      "execution_mode": "autonomous",
      "time_budget": 270,
      "watchdog": {
        "enabled": true,
        "check_interval_seconds": 300,
        "stuck_threshold_seconds": 900,
        "escalation": {
          "strategy": "notify"
        }
      }
    }
  ]
}
```

### Expected Codex Behavior

Codex will:
- Read architecture docs
- Implement all 5 subtasks sequentially
- Write tests for each
- Complete in ~4 hours
- Return with implemented feature

---

## Phase 3: Code Review & Polish (Claude Code)

### Task Definition: `notifications-review.md`

```markdown
# Notification System Code Review

**Execution Mode**: Interactive

**Goal**: Review Codex's implementation, find issues, polish code

**Process**:

1. **Read handoff document**
   - `framework/docs/handoff.md`
   - Understand what Codex implemented

2. **Compare to architecture**
   - `framework/docs/notifications-architecture.md`
   - Check if implementation matches design

3. **Code review**
   - Check code quality
   - Verify tests pass
   - Look for bugs, security issues
   - Check style consistency

4. **Interactive fixes**
   - Ask user about any significant issues found
   - Propose improvements
   - Fix critical bugs
   - Polish UI/UX

5. **Final validation**
   - Run full test suite
   - Manual testing in dev environment
   - Update documentation if needed

**Deliverables**:
- `framework/review/notifications-review-report.md`
- Code improvements (as needed)
- Updated tests (if gaps found)
```

### Claude's Review Process

```
1. Read Codex's handoff:
   "Codex implemented all 5 subtasks.
    Known issue: Real-time updates not working in Safari."

2. Review code:
   ✓ Database migration looks good
   ✓ API endpoints follow patterns
   ⚠ Email service missing error handling for rate limits
   ✗ UI component not accessible (no ARIA labels)
   ⚠ Real-time: Safari issue confirmed

3. Report to user:
   "Found 3 issues:
    - CRITICAL: UI not accessible (violates WCAG)
    - WARNING: Email service needs rate limit handling
    - INFO: Safari real-time issue (Codex documented it)

    Should I fix the critical issue now?
    The warning can be follow-up task."

4. Fix critical issues interactively

5. Generate report:
   "Review complete. Fixed accessibility.
    Deferred: email rate limits (low priority).
    Safari issue: requires separate investigation."
```

### Review Report Output

```markdown
# Notification System Code Review Report

## Summary
Codex successfully implemented notification system in 4.2 hours.
Core functionality works. Found and fixed 1 critical issue.

## What Codex Delivered
- ✅ Database migration (works perfectly)
- ✅ 4 API endpoints (tested, working)
- ✅ Email service (functional, has minor issue)
- ✅ UI components (nice design, had accessibility issue - FIXED)
- ⚠️ Real-time updates (works in Chrome/Firefox, broken in Safari)

## Issues Found

### CRITICAL (fixed during review)
1. **Accessibility Issue** (NotificationBell.jsx:23)
   - Problem: No ARIA labels on interactive elements
   - Impact: Screen readers can't navigate notifications
   - Fix: Added aria-label, aria-live regions
   - Status: ✅ FIXED

### WARNING (deferred to follow-up)
2. **Email Rate Limiting** (notificationEmail.js:45)
   - Problem: No handling for SendGrid rate limits
   - Impact: Could fail silently during high volume
   - Recommendation: Add retry logic with exponential backoff
   - Status: ⏸️ DEFERRED (low priority)

### INFO (known limitations)
3. **Safari Real-time Issue** (notificationListener.js:67)
   - Problem: EventSource not working in Safari
   - Root cause: Safari's stricter CORS policy
   - Workaround: Polling fallback for Safari
   - Status: 📋 TODO (separate task recommended)

## Code Quality Assessment

**Positive**:
- Follows existing code patterns ✅
- Good test coverage (82%) ✅
- Clean, readable code ✅
- Proper error handling (mostly) ✅

**Areas for Improvement**:
- Some files lack JSDoc comments
- Email service could use more robust error handling
- Consider extracting notification logic to custom hook

## Testing Results

**Unit Tests**: 28/28 passing ✅
**Integration Tests**: 3/3 passing ✅
**Manual Testing**:
- ✅ Create notification → appears in UI
- ✅ Mark as read → badge updates
- ✅ Email sent successfully
- ⚠️ Real-time in Safari (known issue)

## Recommendations

**Immediate** (before merging):
- None (critical issue fixed)

**Short-term** (next sprint):
1. Implement Safari real-time fallback (4 hours)
2. Add email rate limit handling (2 hours)
3. Add JSDoc comments (1 hour)

**Long-term** (future):
- Consider push notifications (Phase 4)
- Add notification analytics
- Notification grouping/threading

## Conclusion

✅ **Ready to merge**

Codex delivered a solid implementation. The one critical accessibility issue was found and fixed during review. Remaining items are enhancements, not blockers.

Estimated total time: 4.2h (Codex) + 0.8h (Claude review) = 5 hours
vs. estimated 6-8 hours for single agent → 20% faster! 🎉
```

---

## Metrics Comparison

| Metric | Claude Only | Codex Only | Hybrid (C+C) |
|--------|-------------|------------|--------------|
| **Planning** | 1h | 0.5h | 0.75h |
| **Implementation** | 8h | 4h | 4.2h |
| **Review/Polish** | Built-in | 2h | 1h |
| **Total Time** | 9h | 6.5h | **6h** ✅ |
| **Code Quality** | 9/10 | 7/10 | **8.5/10** ✅ |
| **Autonomy** | 3/10 | 9/10 | **8/10** ✅ |

---

## Lessons Learned

### ✅ What Worked Well

1. **Clear architecture phase** — Codex had zero questions during implementation
2. **Detailed task breakdown** — Each subtask had clear success criteria
3. **Reference to existing patterns** — Codex followed project conventions
4. **Time budgets** — Helped Codex prioritize (finished real-time with 15 min remaining)
5. **Claude's review** — Caught accessibility issue Codex missed

### ⚠️ What Could Improve

1. **More specific fallback strategies** — Codex struggled with Safari issue for 20 min
2. **Pre-validation** — Could have caught accessibility requirements in Phase 1
3. **Intermediate checkpoints** — Maybe check after Subtask 2 before continuing?

### 🚀 Next Iteration

For next feature, try:
- Add explicit accessibility requirements in architecture phase
- Include browser compatibility matrix in spec
- Set up intermediate validation (after each subtask?)

---

**Conclusion**: Hybrid approach leverages best of both agents. 20% faster than single agent while maintaining high quality.
