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
1) Подготовить **мини‑задачи** в `docs/tasks/*.md`.
2) Настроить список задач в `framework/orchestrator/orchestrator.yaml`.
3) Запустить:
   ```bash
   python3 framework/orchestrator/orchestrator.py --config framework/orchestrator/orchestrator.yaml
   ```
4) Оркестратор:
   - создаст worktree для каждой задачи,
   - запустит команды,
   - запишет лог в `logs/*.log`,
   - создаст отчет `docs/orchestrator-run-summary.md`.

---

## 4) Параллельность и зависимости
- Каждая задача может иметь `depends_on`.
- Оркестратор запускает задачу только после успешного завершения зависимостей.

---

## 5) Как агент запускается
В YAML‑конфиге для каждой задачи есть `command`, например:
```
command: "codex run --prompt docs/tasks/db-schema.md"
```
Команда может быть любой, главное — чтобы завершалась кодом 0 при успехе.

---

## 6) Выходные артефакты
- `logs/<task>.log` — лог каждой задачи
- `docs/orchestrator-run-summary.md` — итоговый статус

---

## 7) Ограничения
- Оркестратор локальный, без серверной автоматизации.
- Полная автономность зависит от корректных мини‑промптов.

---

## 8) Независимое ревью (две сессии)
Идея: dev‑агент завершает работу и готовит handoff, а второй агент в другом worktree
проводит ревью и тесты без контекста.

**Артефакты:**
- `review/handoff.md` — контекст и команды запуска от dev‑агента.
- `review/test-plan.md` — независимый план тестирования.
- `review/code-review-report.md`, `review/bug-report.md`, `review/qa-coverage.md`.

---

## 9) Framework Review (третий поток, post‑run)
Идея: отдельный агент анализирует ошибки самого фреймворка между прогонами.

**Правило:** третий поток запускается только после завершения main‑прогона.

**Механика:**
- Во время main‑прогона создаётся `logs/framework-run.lock`.
- После завершения lock удаляется и можно запускать post‑run задачи.
- Логи хранятся в `logs/framework-run.jsonl`.

**Артефакты:**
- `framework-review/framework-log-analysis.md`
- `framework-review/framework-bug-report.md`
- `framework-review/framework-fix-plan.md`

---

## 10) Legacy Migration (read-only контур)
Legacy‑миграция выполняется в отдельном контуре и не меняет код до approval.

**Артефакты:**
- `migration/legacy-snapshot.md`
- `migration/legacy-tech-spec.md`
- `migration/legacy-gap-report.md`
- `migration/legacy-risk-assessment.md`
- `migration/legacy-migration-plan.md`
- `migration/legacy-migration-proposal.md`
- `migration/approval.md`
- `migration/rollback-plan.md`
