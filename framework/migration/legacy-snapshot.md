# Legacy Snapshot

## Кратко о проекте
- Devframework v2026.01.24.2: локальный скелет для оркестрации параллельных задач через git worktree, генерации логов/отчётов и публикации бандлов; в текущем worktree отсутствует код продуктового приложения (только сам framework).
- Целевой домен из документации: расчёт субсидий/планов (FPL/SLCSP/ZIP 2026), мастер-анкета → расчёт → результаты → PDF, multi-tenant Supabase с шифрованием перед записью.

## Архитектура / Модули
- Оркестратор (`framework/orchestrator/orchestrator.py`) читает конфиг (`orchestrator.json|yaml`), создаёт worktree/ветки per task, логирует события в `framework/logs/framework-run.jsonl`, ставит lock для main‑фазы, формирует `docs/orchestrator-run-summary.md`, опционально публикует отчёт через `tools/publish-report.py`.
- Задачи описаны в `framework/tasks/*.md`, фазы main/post/legacy, runner’ы зовут внешние CLI (`codex`, `claude`, `aider`); пути worktree заранее заданы в конфиге.
- Папки: `framework/migration` (шаблоны snapshot/tech-spec/gap/risk/plan/approval/rollback + runbook), `framework/review` (независимое ревью и тест‑план), `framework/framework-review` (post‑run QA самого фреймворка), `framework/tools` (export/publish отчётов), `install-fr.sh` (установка/обновление и автозапуск оркестратора).

## Данные / БД
- Документация требует шаблонов `plans_2026.csv`, `zip_rating_map_2026.csv`, `fpl_2026.csv`, `slcsp_2026.csv` (см. orchestrator-plan), но файлов нет.
- Описан минимальный контракт таблиц: `plans`, `rating_area_map`, `questionnaires`, `reports`, `chat_sessions`/`chat_messages`, `users`, `subscriptions`, `token_balance`, везде `project_id`, версионирование (`version`, `is_current`); готовых миграций/RLS нет.
- Реальных данных/фикстур и SQL-схем в репозитории нет.

## Критические флоу
- Пользовательский: Wizard → анкета → расчёт субсидий → Results → Report → PDF; What‑If пересчёты; логирование сессий/LLM.
- Релизный чек: Wizard → Results → Report → PDF, auth + подписки, уведомления email/web-push, миграции БД и RLS.
- Legacy‑контур: read‑only аудит → reverse tech spec → gap + risk → migration plan → human approval → применение только в ветке `legacy-migration-<run_id>` → review/tests.

## Тесты / CI
- Автотестов и CI-конфигураций нет (.github/ и аналогов отсутствуют); есть только шаблоны (`framework/review/test-plan.md`, задачи с упоминанием unit/E2E).
- Логи/отчёты тестов отсутствуют; оркестратор не вызывает тест-раннеры.

## Известные проблемы
- В worktree нет исходного кода продукта, миграций и данных — аудит фактической логики/схем невозможен.
- Ссылочные артефакты из документации отсутствуют (`docs/tech-spec-ru.md`, `docs/tech-addendum-1-ru.md`, `docs/data-templates-ru.md`, `docs/inputs-required-ru.md`), поэтому задачи db-schema/business-logic/UI лишены исходного контекста.
- Оркестратор зависит от внешних CLI runner’ов и PyYAML; при их отсутствии задачи не стартуют, валидации нет.
- `export-report.py` редактирует только простые токены/ключи (несколько regex), другие секреты в логах могут остаться.
- `install-fr.sh`/оркестратор требуют git и свободных worktree путей; запуск вне git или при существующих конфликтующих путях приводит к ошибке и не устраняет коллизии автоматически.
