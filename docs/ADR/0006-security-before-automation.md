# ADR-0006 — Infrastructure automation только после security foundation

**Status:** Accepted  
**Date:** 2026-08-21

## Context

Будущие SSH, reverse proxy, TLS и deployment операции смогут менять production-инфраструктуру. Добавлять их до готовой identity/authorization/audit модели рискованно.

## Decision

Широкая remote automation откладывается до появления необходимых основ:

- identity;
- backend authorization;
- least privilege;
- audit;
- безопасного secret handling;
- idempotency/rollback принципов;
- контролируемого набора операций.

## Consequences

V1 ограничивает Server Catalog метаданными, IP и использованием сервера как DNS target.

Произвольный remote shell через Telegram/Web не является допустимым способом реализации server management.
