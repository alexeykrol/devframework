# Runbook: независимое ревью через worktree

## 1) Создать worktree
```bash
git worktree add ../project-review <COMMIT_HASH>
```

## 2) Прочитать bundle/brief/handoff
- `framework/review/bundle.md`
- `framework/review/review-brief.md`
- `framework/review/handoff.md`

## 3) Запустить агента
```bash
cd ../project-review
# запуск вашего AI‑агента с prompt из framework/review/review-brief.md
```

## 4) Выполнить тесты (если есть)
- Использовать команды из `framework/review/handoff.md` или `framework/review/review-brief.md`
- Сохранить результаты/логи в `framework/review/test-results.md`

## 5) Итог
- Заполнить:
  - `framework/review/test-plan.md`
  - `framework/review/test-results.md`
  - `framework/review/code-review-report.md`
  - `framework/review/bug-report.md`
  - `framework/review/qa-coverage.md`
- Передать результаты в основную ветку
