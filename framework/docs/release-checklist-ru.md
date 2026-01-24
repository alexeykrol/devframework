# Release Checklist

1) Все E2E тесты прошли.
2) Независимый review выполнен (см. `review/`).
3) Handoff для ревью подготовлен (`review/handoff.md`).
4) Framework review выполнен (см. `framework-review/`).
5) Проверен critical flow: Wizard → Results → Report → PDF.
6) Проверены auth и подписки (mock/real).
7) Проверены уведомления email/web‑push (mock/real).
8) Миграции БД применены.
9) Проверены RLS политики.
10) Обновлены legal‑страницы.
11) Проверена доступность (WCAG базовые требования).
12) Готов rollback план.
13) Для legacy‑проектов: изменения шли через `legacy-migration` ветку и approval.
