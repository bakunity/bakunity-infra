# Активная работа

**Статус:** PCS bootstrap завершён; product-code не разрабатывается.  
**Обновлено:** 2026-08-21

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Сейчас

Project Context System интегрирована в Bakunity Infra.

На момент этой записи активной задачи по реализации backend/Web/Telegram нет. Проект остаётся между завершённым Phase 0 и явным стартом V1.

## Следующие decision gates

Перед первой реализацией соответствующих блоков нужно закрыть:

1. `BI-0002` — Web authentication decision + ADR.
2. `BI-0003` — concurrency/idempotency decisions + ADR при необходимости.
3. Production secret storage decision до подключения реальных provider credentials.
4. Reconciliation/retry semantics для DNS provider operations.

## После явного старта разработки

Рекомендуемый порядок берётся из `docs/BACKLOG_V1.md`:

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

## Правило обновления

Когда начинается новая задача, этот файл должен получить:

- ID задачи/epic;
- цель;
- base commit;
- затрагиваемые authoritative документы;
- критерий завершения;
- фактический результат после завершения.

После завершения доказательства переносятся в `docs/EVIDENCE.md`, а текущее состояние — в `docs/PROJECT_STATE.md` при необходимости.
