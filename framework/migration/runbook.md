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
- `framework/migration/legacy-snapshot.md`
- `framework/migration/legacy-tech-spec.md`
- `framework/migration/legacy-gap-report.md`
- `framework/migration/legacy-risk-assessment.md`
- `framework/migration/legacy-migration-plan.md`
- `framework/migration/legacy-migration-proposal.md`

## 3) Approval Gate
- Человек заполняет `framework/migration/approval.md`.
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
- Обновить `framework/migration/legacy-migration-plan.md` статусами.
- Сохранить итог в `framework/migration/legacy-migration-proposal.md`.
