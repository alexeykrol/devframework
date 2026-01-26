# Пример задачи с автономным режимом

Это полный пример того, как должна выглядеть task definition для автономного выполнения Claude Code.

---

**Метаданные задачи**

```yaml
task_id: implement-user-profile
phase: main
execution_mode: autonomous
time_budget: 60
priority: high
dependencies: [db-schema]
```

---

## 🤖 AUTONOMOUS MODE PROTOCOL

You are Claude Code running in **AUTONOMOUS mode**. This fundamentally changes your behavior:

### CRITICAL RULES

1. **NO QUESTIONS TO USER**
   - NEVER use AskUserQuestion tool
   - NEVER stop and wait for clarifications
   - NEVER ask "Should I...?" or "Do you want me to...?"

2. **DECISION MAKING FRAMEWORK**
   When facing ambiguity, use this priority order:

   a) **Check existing patterns** in the codebase
      - Look at similar features (e.g., other profile pages)
      - Match naming conventions
      - Follow established architecture

   b) **Choose CONSERVATIVE approach**
      - Server-side rendering over client-side (safer)
      - SQL queries over ORM magic (more explicit)
      - Standard libraries over new dependencies

   c) **Document the decision**
      - Write in `framework/docs/handoff.md`
      - Format: "DECISION: [choice] | RATIONALE: [why] | ALTERNATIVES: [rejected]"

3. **ERROR HANDLING**
   - Errors are NON-FATAL
   - Try 3 different approaches
   - If still blocked: document + continue with next subtask
   - NEVER stop entire task due to one blocker

4. **TIME MANAGEMENT**
   - Target: 60 minutes
   - Check progress every 15 minutes
   - At 40 min (70%): if < 50% done, cut scope
   - At 55 min (90%): wrap up, document incomplete parts

5. **COMMUNICATION**
   - Output text is for logging, NOT questions
   - Use: "Implementing X", "Creating Y", "Testing Z"
   - Avoid: "Should I...?", "Would you like...?"

6. **HANDOFF DOCUMENTATION**
   Document everything in `framework/docs/handoff.md`:
   - Decisions made with rationale
   - Blockers encountered and workarounds
   - Scope adjustments
   - Known limitations

7. **SUCCESS CRITERIA**
   Task complete when:
   - Core functionality works
   - Tests pass
   - Code matches project style
   - All decisions documented

### DECISION DEFAULTS FOR THIS TASK

- **UI Framework**: Use existing framework (check `package.json`)
- **API Pattern**: Match existing endpoints (check `src/api/`)
- **Database queries**: Follow patterns in `db/queries/`
- **Testing**: Unit tests with same framework as other features
- **Styling**: Match CSS/Tailwind patterns in `src/styles/`

### FALLBACK STRATEGIES

**Scenario 1: API endpoint pattern unclear**
```
1. Check most recent endpoint implementations
2. Choose the most common pattern
3. Document: "Following pattern from [file:line]"
```

**Scenario 2: Database query fails**
```
1. Check SQL syntax (use Bash: psql --dry-run)
2. Try simpler query version
3. If still failing: use mock data + document blocker
```

**Scenario 3: UI component not rendering**
```
1. Check browser console for errors
2. Simplify component (remove advanced features)
3. Test with minimal version
4. Document what features deferred
```

---

## 📋 TASK OVERVIEW

**Goal**: Implement user profile page with edit functionality

**Success Criteria**:
- [ ] Profile page displays user info (name, email, avatar)
- [ ] Edit button opens edit form
- [ ] Save button persists changes to database
- [ ] Changes reflected immediately after save
- [ ] Unit tests cover main functionality
- [ ] No console errors

**Out of Scope**:
- Password change (separate feature)
- Profile picture upload (use URL input for now)
- Social media links
- Advanced settings

**Time Budget**: 60 minutes
- Backend API: 20 min
- Frontend UI: 25 min
- Testing: 10 min
- Integration: 5 min

---

## 📝 DETAILED REQUIREMENTS

### Must Have (within time budget)

1. **Backend: GET /api/user/profile**
   - Returns: `{ id, name, email, avatar_url, created_at }`
   - Auth: Requires valid JWT token
   - RLS: User can only see their own profile

2. **Backend: PUT /api/user/profile**
   - Accepts: `{ name, email, avatar_url }`
   - Validation: email must be valid format, name 2-50 chars
   - Returns: updated profile object
   - Auth: Requires valid JWT token

3. **Frontend: Profile Display Component**
   - Route: `/profile`
   - Shows user info from API
   - "Edit" button → edit mode
   - Loading state while fetching

4. **Frontend: Profile Edit Form**
   - Editable fields: name, email, avatar_url
   - "Save" and "Cancel" buttons
   - Form validation (match backend rules)
   - Success message on save

5. **Tests**
   - Backend: Test both endpoints with valid/invalid data
   - Frontend: Test profile display and edit flow
   - Integration: Test full save → refetch flow

### Should Have (if time permits)

- Avatar preview when URL changes
- Optimistic UI updates (show change before API confirms)
- Better error messages (field-specific)

### Nice to Have (bonus)

- Profile picture upload (not just URL)
- Undo changes functionality

---

## 🎯 DECISION FRAMEWORK

### Technology Choices

**Backend**:
- Check `src/api/` for existing endpoint structure
- Use same router/middleware pattern
- Match error handling style

**Frontend**:
- Check `src/pages/` for similar pages
- Use same state management (Context/Redux/etc)
- Match form patterns from other forms

**Database**:
- Check `db/schema.sql` for users table structure
- If fields missing: add migration
- Use same RLS policy pattern as other tables

### Code Style

**Naming conventions**:
- Check existing files for snake_case vs camelCase
- API endpoints: Follow REST conventions
- Components: Match existing naming (PascalCase, kebab-case?)

**File structure**:
```
src/
  api/
    user/
      profile.js     ← Backend endpoint
  pages/
    Profile.jsx      ← Frontend page
  components/
    ProfileForm.jsx  ← Form component
  __tests__/
    profile.test.js  ← Tests
```

---

## 🚧 FALLBACK STRATEGIES

### Blocker: Can't determine which framework (React/Vue/etc)

```
SOLUTION:
1. Read package.json → Check dependencies
2. Read src/ directory → Look for .jsx, .vue files
3. Document in handoff: "Detected [framework] from [evidence]"
```

### Blocker: Database users table doesn't have needed fields

```
SOLUTION:
1. Create migration: framework/migration/00X_add_avatar_url.sql
2. Add field: ALTER TABLE users ADD COLUMN avatar_url TEXT;
3. Document in handoff: "Added migration for avatar_url"
```

### Blocker: Tests not running (missing framework)

```
SOLUTION:
1. Check package.json for test script
2. If missing: npm install --save-dev jest (or similar)
3. If still fails: write test file but skip execution
4. Document in handoff: "Tests written but not executed due to [reason]"
```

### Blocker: Running out of time

```
AT 40 minutes (70% of budget):
IF less than 50% complete:
  → Focus ONLY on "Must Have"
  → Defer "Should Have" items
  → Document: "Deferred: avatar preview (should have)"

AT 55 minutes (90% of budget):
  → Finish current subtask
  → Commit what's done
  → Document incomplete items in handoff
```

---

## 📚 REFERENCE MATERIALS

**Similar features to study**:
- `src/pages/Settings.jsx` — another profile-like page
- `src/api/auth/me.js` — similar auth endpoint
- `db/queries/users.sql` — existing user queries

**Project conventions**:
- `docs/api-conventions.md` — API design rules
- `docs/testing-guide.md` — How to write tests
- `.eslintrc.js` — Code style rules

---

## ✅ DEFINITION OF DONE

Task complete when ALL are true:

- [ ] GET /api/user/profile works (test with curl)
- [ ] PUT /api/user/profile works (test with curl)
- [ ] Profile page loads and displays data
- [ ] Edit form saves changes successfully
- [ ] Tests written and passing (run `npm test`)
- [ ] No linter errors (run `npm run lint`)
- [ ] All decisions documented in `framework/docs/handoff.md`
- [ ] Git commit with clear message

---

## 🔍 SELF-CHECK BEFORE COMPLETING

1. **Did I ask questions?** → No AskUserQuestion in logs
2. **Tests pass?** → Run test command
3. **Linter happy?** → Run lint command
4. **Code matches style?** → Compare with reference files
5. **Time budget OK?** → Actual time ≤ 70 minutes
6. **Handoff complete?** → Check handoff.md has all sections

If ALL ✓ → Task complete!

---

## 📤 HANDOFF TEMPLATE

Write this to `framework/docs/handoff.md`:

```markdown
## Task: implement-user-profile — 2026-01-26 14:30

### What was delivered
- GET /api/user/profile endpoint (200ms avg response)
- PUT /api/user/profile endpoint with validation
- Profile page UI at /profile route
- Edit form with save/cancel functionality
- 8 unit tests, 2 integration tests

### Files changed
- `src/api/user/profile.js` — new endpoints (180 lines)
- `src/pages/Profile.jsx` — profile display (95 lines)
- `src/components/ProfileForm.jsx` — edit form (120 lines)
- `framework/migration/004_add_avatar_url.sql` — schema change
- `src/__tests__/profile.test.js` — tests (150 lines)

### Key decisions

1. DECISION: Used Context API for state | RATIONALE: Already used in Settings page | ALTERNATIVES: Redux (overkill for this), local state (too limited)

2. DECISION: Avatar as URL input, not upload | RATIONALE: File upload complex, out of time budget | ALTERNATIVES: Cloudinary integration (should have, deferred)

3. DECISION: Optimistic UI updates | RATIONALE: Better UX, rollback on error | ALTERNATIVES: Wait for API (slower UX)

### Testing
- Unit tests: 8 (6 backend, 2 frontend) in profile.test.js
- Integration test: Full save flow (edit → save → refetch)
- Manual testing: Verified in Chrome, Firefox

### Known limitations
- Avatar upload not implemented (URL input only)
- No field-specific error messages (generic error shown)
- No undo functionality

### Deferred items
- Avatar preview widget (should have) — defer to future task
- Social media links (nice to have) — not in scope
- Profile picture upload (nice to have) — complex, needs separate task

### Time spent
- Planning: 5 min
- Backend: 22 min
- Frontend: 28 min
- Testing: 8 min
- Total: 63 min (budget was 60 min, 5% over)

### Recommendations
- Add avatar preview in follow-up task (2-3 hours)
- Consider file upload library (e.g., Uppy) for future
- Add profile completeness indicator (nice UX touch)
```

---

## 🚀 START IMPLEMENTATION

[Actual detailed implementation steps would go here in a real task]

---

**Usage**: Copy this template, replace "user profile" with your actual feature, adjust time budgets and requirements.
