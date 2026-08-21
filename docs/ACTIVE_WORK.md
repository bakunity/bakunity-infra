# Активная работа

**Статус:** PCS V1 migration/reconciliation завершена; product-code не разрабатывается.  
**Обновлено:** 2026-08-21

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Сейчас

Существующая ранняя интеграция Project Context System reconciled до PCS V1 baseline `06cd250d2847ee87f66f73930d471d7c1f60991d` в профиле `standard-adapted`.

Migration была repository-only:

- server/runtime не трогался;
- product implementation не начиналась;
- project-specific truth сохранена;
- authoritative product/architecture/API/DB/UX/security документы не заменялись шаблонами PCS.

На момент этой записи активной задачи по реализации backend/Web/Telegram нет.

## Следующий безопасный шаг

Первый decision gate перед началом соответствующей реализации:

1. `BI-0002` — выбрать Web authentication mechanism и оформить ADR.
2. Затем `BI-0003` — concurrency/idempotency decisions.
3. До реальных provider credentials — production secret storage decision.
4. До write DNS flows — reconciliation/retry semantics.

## После явного старта разработки

Порядок берётся из `docs/BACKLOG_V1.md`:

```text
Scaffold
   ↓
Identity + Permissions + Audit
   ↓
Cloudflare + Zones
   ↓
Create Domain через IPv4
   ↓
Telegram create flow
   ↓
Web create flow
```

## Не считать активной работой

Пока нет явного решения начать реализацию, не создавать автоматически:

- backend scaffold;
- Next.js приложение;
- Telegram runtime;
- Docker/production deployment;
- Cloudflare production credentials;
- SSH automation.

## Runtime boundary

По умолчанию текущая работа — repository/local/CI only.

Подключение к серверам, staging/production deploy и любые runtime mutations требуют отдельной явной задачи и live gate.

## Правило обновления

Когда начинается новая задача, этот файл должен получить:

- ID задачи/epic;
- цель;
- base commit;
- linked Issue, если есть;
- allowed/forbidden scope;
- затрагиваемые authoritative документы;
- критерий завершения;
- tests/smoke plan;
- runtime scope;
- фактический результат после завершения.

После завершения evidence переносится в `docs/EVIDENCE.md`, а текущее состояние — в `docs/PROJECT_STATE.md` при необходимости.
