# ADR-0002 — Web и Telegram являются клиентами одного ядра

**Status:** Accepted  
**Date:** 2026-08-21

## Context

Bakunity Infra должна иметь два пользовательских клиента: Web Console и Telegram Bot. Если каждый клиент реализует собственные DNS-правила, permissions и lifecycle ресурсов, они быстро начнут расходиться.

## Decision

Web и Telegram используют одно application core и одну модель состояния.

Бизнес-правила, authorization и use case реализуются один раз. Клиенты отличаются UX, но не смыслом операций.

Telegram может получить UI раньше, потому что быстрее разрабатывается, однако не является архитектурным центром системы.

## Consequences

- Один mutation должен давать одинаковый результат независимо от клиента.
- Telegram handlers и Web components не содержат provider/business logic.
- Audit должен фиксировать `source_client`, не создавая отдельные модели данных для каждого клиента.
- Новые клиенты (CLI/external API) могут подключаться без копирования бизнес-правил.
