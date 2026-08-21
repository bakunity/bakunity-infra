# ADR-0004 — DNS-ядро не зависит от конкретного провайдера

**Status:** Accepted  
**Date:** 2026-08-21

## Context

Первым DNS backend выбран Cloudflare, но продукт не должен становиться оболочкой над Cloudflare API. В будущем возможны другие DNS providers.

## Decision

DNS business logic работает через provider-neutral port/interface.

Cloudflare реализуется как первый adapter. Provider IDs, ошибки и дополнительные возможности преобразуются на границе adapter layer.

## Consequences

- Domain/DNS use case не импортируют Cloudflare SDK/API напрямую.
- Web и Telegram не зависят от Cloudflare payload.
- Provider-specific возможности (например `proxied`) остаются опциональными расширениями и не определяют основную модель.
- Добавление второго provider не должно требовать переписывания клиентских flows.
