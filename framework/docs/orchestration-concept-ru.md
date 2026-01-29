# Концепция оркестрации параллельных задач (локально)

Цель: **полностью автоматизировать** запуск параллельных задач без участия человека после этапа проектирования.

---

## 1) Общая идея
Оркестратор — это локальная утилита, которая:
1) читает список задач и их параметры (из YAML),
2) создаёт отдельные git‑worktree/ветки для каждой задачи,
3) запускает агента в каждой worktree,
4) мониторит выполнение (по статусу процесса),
5) собирает итоги и сохраняет их в отчёт.

---

## 2) Почему Python (не bash)
Python удобнее для:
- управления зависимостями между задачами,
- логирования в файлы,
- мониторинга статусов,
- более сложной логики (retry, timeouts).

---

## 3) Как выглядит процесс
1) Подготовить **мини‑задачи** в `framework/tasks/*.md`.
2) Настроить список задач в `framework/orchestrator/orchestrator.json`.
3) Запустить:
   ```bash
   python3 framework/orchestrator/orchestrator.py --config framework/orchestrator/orchestrator.json
   ```
4) Оркестратор:
   - создаст worktree для каждой задачи (по умолчанию `_worktrees/{phase}/{task}`),
   - запустит команды,
   - запишет лог в `framework/logs/*.log`,
   - создаст отчет `framework/docs/orchestrator-run-summary.md`,
   - периодически печатает `[RUNNING] ...` для признака жизни (интервал задаётся `FRAMEWORK_PROGRESS_INTERVAL`).

**Ключевой user‑flow:**
- Empty проект → запуск интервью (phase `discovery`) → генерация ТЗ → подтверждение старта разработки → phase `main`.
- Legacy проект → анализ (phase `legacy`) → интервью (phase `discovery`) → подтверждение старта разработки → phase `main`.

**Мониторинг и устойчивость:**
- Протокол запускается через `framework/tools/run-protocol.py`.
- Наблюдатель (`framework/tools/protocol-watch.py`) следит за прогрессом, пишет алерты и останавливает протокол при длительном простое.
- Каждые 10 секунд печатается строка статуса `[STATUS]` (настройка: `FRAMEWORK_STATUS_INTERVAL`).
- Интервью discovery — интерактивное; для паузы используйте команду `/pause`.

---

## 4) Параллельность и зависимости
- Каждая задача может иметь `depends_on`.
- Оркестратор запускает задачу только после успешного завершения зависимостей.

---

## 5) Как агент запускается
В YAML‑конфиге для каждой задачи есть `command`, например:
```
command: "codex run --prompt framework/tasks/db-schema.md"
```
Команда может быть любой, главное — чтобы завершалась кодом 0 при успехе.

---

## 6) Выходные артефакты
- `framework/logs/<task>.log` — лог каждой задачи
- `framework/docs/orchestrator-run-summary.md` — итоговый статус

---

## 7) Ограничения
- Оркестратор локальный, без серверной автоматизации.
- Полная автономность зависит от корректных мини‑промптов.

---

## 8) Независимое ревью (две сессии)
Идея: dev‑агент завершает работу и готовит handoff, а второй агент в другом worktree
проводит ревью и тесты без контекста.

**Артефакты:**
- `framework/review/handoff.md` — контекст и команды запуска от dev‑агента.
- `framework/review/test-plan.md` — независимый план тестирования.
- `framework/review/code-review-report.md`, `framework/review/bug-report.md`, `framework/review/qa-coverage.md`.

---

## 9) Framework Review (третий поток, post‑run)
Идея: отдельный агент анализирует ошибки самого фреймворка между прогонами.

**Правило:** третий поток запускается только после завершения main‑прогона.

**Механика:**
- Во время main‑прогона создаётся `framework/logs/framework-run.lock`.
- После завершения lock удаляется и можно запускать post‑run задачи.
- Логи хранятся в `framework/logs/framework-run.jsonl`.

**Артефакты:**
- `framework/framework-review/framework-log-analysis.md`
- `framework/framework-review/framework-bug-report.md`
- `framework/framework-review/framework-fix-plan.md`

---

## 10) Legacy Migration (read-only контур)
Legacy‑миграция выполняется в отдельном контуре и не меняет код до approval.

**Артефакты:**
- `framework/migration/legacy-snapshot.md`
- `framework/migration/legacy-tech-spec.md`
- `framework/migration/legacy-gap-report.md`
- `framework/migration/legacy-risk-assessment.md`
- `framework/migration/legacy-migration-plan.md`
- `framework/migration/legacy-migration-proposal.md`
- `framework/migration/approval.md`
- `framework/migration/rollback-plan.md`
