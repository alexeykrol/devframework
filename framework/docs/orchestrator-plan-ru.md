# Оркестратор: общие контракты + карта параллельных задач + мини‑ТЗ

Документ для запуска параллельных подзадач разными агентами.

---

## 1) Общие контракты (единые для всех задач)

### 1.1 Глобальные правила
- Ничего не перезаписываем: только версии (`version`, `is_current`).
- Везде хранить `project_id` (multi‑tenant Supabase).
- Медицинские/юридические советы запрещены.
- Анонимизация данных перед LLM.
- Данные до авторизации сохраняем как анонимные сессии.

### 1.2 Схемы данных (входные файлы)
См. **`docs/data-templates-ru.md`**:
- `plans_2026.csv`
- `zip_rating_map_2026.csv`
- `fpl_2026.csv`
- `slcsp_2026.csv`

### 1.3 БД‑контракты (минимальный набор)
- `plans`
- `rating_area_map`
- `questionnaires` (versioned)
- `reports` (versioned)
- `chat_sessions`, `chat_messages` (versioned)
- `users` (link to Supabase auth)
- `subscriptions`, `token_balance`
- Все таблицы содержат `project_id`.

### 1.4 API/поведение (минимум)
- Wizard → данные анкеты → расчет → результаты.
- Results → Report → PDF.
- What‑If → расчёт в реальном времени.

### 1.5 Логирование
- Логи LLM и промптов сохраняем (анонимизированно).
- Сессии диалога сохраняем полностью.

---

## 2) Карта задач и параллельность

### Можно делать параллельно (без взаимных блокировок)
1) **Data Research** (таблицы A–D по шаблону)
2) **DB schema + migrations + RLS**
3) **Business Logic** (APTC, сценарии, скоринг)
4) **UI/UX** (подбор Tailwind UI компонентов + макеты)
5) **PDF генерация** (на синтетике)
6) **LLM prompts/policies**
7) **Unit + E2E tests (mock data)**
8) **DevOps (Vercel env, deploy pipelines)**
9) **Test Plan (independent)** (по ТЗ и DoD)
10) **Review Handoff Prep** (пакет для независимого ревью)

### Зависимости
- UI зависит от выбора Tailwind UI компонентов (по протоколу).
- Реальные расчёты субсидий точнее после реальных таблиц (A–D).
- Интеграции (Supabase/Auth, Stripe/PayPal, SES) — после базового каркаса.
- Независимый Review выполняется после ключевых dev‑задач + Test Plan.

---

## 3) Мини‑ТЗ и промпты по задачам

### 3.1 Data Research (A–D)
**Цель:** собрать официальные таблицы 2026 года.
- Использовать `docs/deep-research-prompt-ru.md`.
- Выход: 4 CSV + `sources.md` + `issues.md` + `summary.md`.

### 3.2 DB Schema + RLS
**Цель:** миграции Supabase для всех сущностей + RLS.
- Учитывать `project_id`.
- Применить AES‑256 шифрование в приложении перед записью.

### 3.3 Business Logic
**Цель:** реализовать расчет субсидий и сценариев.
- APTC формулы (FPL 2026, expected contribution до 8.5%).
- 4 сценария + cap `(premium*12 + MOOP)`.
- Return-subsidy сценарии (+50/100/200/300/500%).

### 3.4 UI/UX (Tailwind UI)
**Цель:** подобрать компоненты по списку экранов.
- Использовать `docs/screens-list-ru.md`.
- Сначала выбрать шаблоны в `Claude-Cowork/TAILWIND_UI_CATALOG.md`.

### 3.5 PDF‑генерация
**Цель:** PDF‑отчет в платном плане.
- Включить все секции (таблицы, сценарии, источники, дисклеймеры).

### 3.6 LLM Prompts/Policies
**Цель:** промпты для чата и финального анализа.
- Соблюдать запреты (no medical/legal advice).
- Сохранять reasoning/объяснение отдельно.

### 3.7 Tests
**Цель:** автоматизация (unit + Playwright).
- Unit: APTC, сценарии, скоринг.
- E2E: Anonymous → Wizard → Payment (mock) → PDF.

### 3.8 DevOps
**Цель:** deploy pipeline на Vercel.
- main → prod, develop → staging, feature → preview.
- ENV per environment.

### 3.9 Test Plan (Independent)
**Цель:** составить независимый план тестирования.
- Основание: ТЗ + DoD.
- Выход: `review/test-plan.md`.
- Без изменения кода.

### 3.10 Review Handoff Prep
**Цель:** подготовить пакет для независимого ревью.
- Вход: commit/branch, результаты тестов (если есть).
- Выход: `review/handoff.md`, `review/test-results.md` (опционально).
- Без изменения кода.

### 3.11 Independent Review
**Цель:** независимое код‑ревью и QA.
- Вход: `review/test-plan.md`, `review/review-brief.md`.
- Выход: `review/code-review-report.md`, `review/bug-report.md`, `review/qa-coverage.md`.
- Без изменения кода.

---

## 4) Общие входы (креды/данные)
См. `docs/inputs-required-ru.md`.

---

## 5) Ссылки
- `docs/tech-spec-ru.md`
- `docs/tech-addendum-1-ru.md`
- `docs/qa-ru.md`
