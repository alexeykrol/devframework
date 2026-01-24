# Legacy Migration Runbook

## 0) Входные условия
- Главная ветка стабильна.
- Есть резервная точка (commit hash).
- Основные агенты не запущены.

## 1) Read‑only анализ (legacy phase)
- Запускать только анализ и генерацию документов.
- Не менять код.
```
python3 framework/orchestrator/orchestrator.py --phase legacy
```

## 2) Сформировать артефакты
- `migration/legacy-snapshot.md`
- `migration/legacy-tech-spec.md`
- `migration/legacy-gap-report.md`
- `migration/legacy-risk-assessment.md`
- `migration/legacy-migration-plan.md`
- `migration/legacy-migration-proposal.md`

## 3) Approval Gate
- Человек заполняет `migration/approval.md`.
- Без approval изменения запрещены.

## 4) Создать ветку миграции (изолированно)
Ветка создаётся автоматически оркестратором при запуске `legacy-apply` и включает `run_id`:
`legacy-migration-<run_id>`.

## 5) Применить изменения только в migration‑ветке
- Все правки в ветке `legacy-migration`.
- После изменений — тесты и review.
```
python3 framework/orchestrator/orchestrator.py --phase legacy --include-manual
```

## 6) Merge в main (manual)
- Только после тестов + review.
- Если что-то пошло не так — откат через reset/rollback в main.

## 7) Post‑merge контроль
- Обновить `migration/legacy-migration-plan.md` статусами.
- Сохранить итог в `migration/legacy-migration-proposal.md`.
