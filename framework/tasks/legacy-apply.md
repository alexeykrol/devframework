# Task: Legacy Migration Apply (manual)

## Goal
Применить изменения в migration‑ветке после одобрения.

## Inputs
- `framework/migration/approval.md`
- `framework/migration/legacy-migration-plan.md`

## Outputs
- Изменения в ветке `legacy-migration`
- Обновлённый план миграции со статусом

## Rules
- Запускать только после одобрения.
- Работать только в migration‑ветке (`legacy-migration-<run_id>`).
- Main не менять напрямую.

## Done When
- Изменения внесены в ветку и протестированы.
