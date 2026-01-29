# Task: Legacy Audit (read-only)

## Goal
Собрать объективную картину legacy‑проекта без изменения кода.

## Inputs
- Репозиторий (read-only)
- `framework/docs/definition-of-done-ru.md`

## Outputs
- `framework/migration/legacy-snapshot.md`

## Rules
- Никаких правок кода.
- Только анализ и фиксация фактов.
- Игнорировать служебные каталоги: `framework/`, `framework.backup.*`, `_worktrees/`, `.git`.

## Done When
- Snapshot заполнен.
