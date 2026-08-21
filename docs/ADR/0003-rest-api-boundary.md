# ADR-0003 — REST API является first-class boundary

**Status:** Accepted  
**Date:** 2026-08-21

## Context

Web Console, будущие интеграции и потенциальный CLI требуют стабильной внешней границы, которая не раскрывает внутреннее устройство модулей и provider-specific модели.

## Decision

Bakunity Infra предоставляет версионируемый REST API (`/api/v1`) как полноценную application boundary.

API является интерфейсом к application layer, а не местом хранения бизнес-правил.

Telegram может технически работать в том же deployable unit и вызывать application use case напрямую, но смысл операций должен совпадать с API.

## Consequences

- Web зависит от стабильного API contract, а не от внутренней структуры Python-модулей.
- Breaking changes требуют управляемой версии/миграции.
- Cloudflare-specific payload не становится публичной доменной моделью.
- Ошибки нормализуются стабильными error codes.
