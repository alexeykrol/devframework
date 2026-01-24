# Release Checklist

1) Все E2E тесты прошли.
2) Независимый review выполнен (см. `review/`).
3) Проверен critical flow: Wizard → Results → Report → PDF.
4) Проверены auth и подписки (mock/real).
5) Проверены уведомления email/web‑push (mock/real).
6) Миграции БД применены.
7) Проверены RLS политики.
8) Обновлены legal‑страницы.
9) Проверена доступность (WCAG базовые требования).
10) Готов rollback план.
