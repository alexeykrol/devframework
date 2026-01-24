# Runbook: независимое ревью через worktree

## 1) Создать worktree
```bash
git worktree add ../project-review <COMMIT_HASH>
```

## 2) Заполнить review‑brief
- Открыть `review/review-brief.md`
- Указать commit/branch, контекст, команды тестов

## 3) Запустить агента
```bash
cd ../project-review
# запуск вашего AI‑агента с prompt из review/review-brief.md
```

## 4) Выполнить тесты (если есть)
- Использовать команды из `review/review-brief.md`
- Сохранить результаты/логи

## 5) Итог
- Заполнить:
  - `review/test-plan.md`
  - `review/code-review-report.md`
  - `review/bug-report.md`
  - `review/qa-coverage.md`
- Передать результаты в основную ветку
