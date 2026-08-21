# ADR-0005 — PostgreSQL как внутренний source of truth

**Status:** Accepted  
**Date:** 2026-08-21

## Context

Bakunity Infra должна знать владельцев, роли, зоны, доменные ресурсы, связи с серверами, audit и состояния синхронизации. DNS provider не хранит эту продуктовую модель.

## Decision

PostgreSQL используется как основное постоянное хранилище внутреннего состояния Bakunity Infra.

Внешний provider является исполнителем и источником внешнего состояния, но не заменяет product database.

## Consequences

- Provider error не может автоматически означать success внутреннего ресурса.
- Нужны явные sync/error states и reconciliation strategy.
- Web и Telegram читают общую внутреннюю модель.
- Секреты provider не хранятся открытым текстом в обычных product tables.
