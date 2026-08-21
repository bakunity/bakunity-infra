# Architecture Decision Records (ADR)

Этот каталог — authoritative источник ответа на вопрос **почему было принято архитектурное или процессное решение**.

Новые решения добавляются отдельным ADR и не должны тихо переписываться задним числом.

## Формат

```text
# ADR-NNNN — Название

Status: Proposed / Accepted / Superseded / Rejected
Date: YYYY-MM-DD

## Context
## Decision
## Consequences
## Alternatives considered
## References
```

Если решение заменено, старый ADR остаётся в истории со статусом `Superseded` и ссылкой на новый ADR.

## Реестр

- [ADR-0001 — Модульный монолит](0001-modular-monolith.md)
- [ADR-0002 — Web и Telegram являются клиентами одного ядра](0002-web-telegram-one-core.md)
- [ADR-0003 — REST API как first-class boundary](0003-rest-api-boundary.md)
- [ADR-0004 — Provider-neutral DNS core](0004-provider-neutral-dns.md)
- [ADR-0005 — PostgreSQL как внутренний source of truth](0005-postgresql-source-of-truth.md)
- [ADR-0006 — Infrastructure automation после security foundation](0006-security-before-automation.md)
- [ADR-0007 — Никаких преждевременных микросервисов](0007-no-premature-microservices.md)
- [ADR-0008 — Project Context System](0008-project-context-system.md)

`docs/DECISIONS.md` оставлен как совместимый индекс/историческая точка входа, но детали решений хранятся здесь.
