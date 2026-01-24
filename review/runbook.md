# Runbook: независимое ревью через worktree

## 1) Создать worktree
```bash
git worktree add ../project-review <COMMIT_HASH>
```

## 2) Прочитать bundle/brief/handoff
- `review/bundle.md`
- `review/review-brief.md`
- `review/handoff.md`

## 3) Запустить агента
```bash
cd ../project-review
# запуск вашего AI‑агента с prompt из review/review-brief.md
```

## 4) Выполнить тесты (если есть)
- Использовать команды из `review/handoff.md` или `review/review-brief.md`
- Сохранить результаты/логи в `review/test-results.md`

## 5) Итог
- Заполнить:
  - `review/test-plan.md`
  - `review/test-results.md`
  - `review/code-review-report.md`
  - `review/bug-report.md`
  - `review/qa-coverage.md`
- Передать результаты в основную ветку
