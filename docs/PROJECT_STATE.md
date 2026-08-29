# Текущее состояние проекта

**Статус знания:** CONFIRMED  
**Последняя сверка:** 2026-08-29  
**Фаза:** Phase 0 decision gates; реализация V1 ещё не начата.

Этот документ отвечает только на вопрос: **что истинно о Bakunity Infra прямо сейчас**.

Подробные цели, архитектура и roadmap хранятся в профильных authoritative документах и здесь не дублируются.

## Что существует сейчас

- Репозиторий проекта оформлен и содержит архитектурную/продуктовую спецификацию.
- Архитектура зафиксирована как **modular monolith**.
- Клиенты: **Web Console**, **Telegram Bot**, **REST API**.
- Web и Telegram должны использовать одно application core и одну модель прав.
- PostgreSQL выбран как внутренний source of truth для продуктового состояния.
- Cloudflare выбран первым DNS provider adapter.
- V1 зафиксирована как управление доменами/DNS с минимальным Server Catalog и Domain Binding.
- Phase 0 прошёл архитектурную ревизию со статусом PASS.
- Backlog V1 сформирован.
- Project Context System интегрирована и reconciled до **PCS V1**, baseline `06cd250d2847ee87f66f73930d471d7c1f60991d`, профиль `standard-adapted`.
- В репозитории есть canonical PCS validator с structural/readiness режимами и GitHub operational-layer manifests/workflow.
- Web authentication decision закрыт в `ADR-0010`: V1 использует Passkeys/WebAuthn с server-side browser sessions.
- Internal `User` остаётся независимым от Telegram/Web authentication mechanism; Telegram identity и WebAuthn credentials могут принадлежать одному User.
- PCS V1 migration и BI-0002 не меняли сервер/runtime.

## Чего сейчас нет

**Product implementation ещё не начат.**

В репозитории пока нет подтверждённой реализации:

- FastAPI backend;
- PostgreSQL migrations;
- WebAuthn runtime;
- browser session persistence;
- Cloudflare adapter;
- Telegram bot runtime;
- Next.js Web Console;
- server management;
- reverse proxy;
- TLS automation;
- deployments;
- monitoring.

Наличие этих элементов в архитектуре/roadmap означает план, а не реализованную возможность.

## Зафиксированная граница V1

V1 включает:

- Identity/Authorization foundation;
- Passkeys/WebAuthn для Web authentication;
- server-side Web sessions с revocation/expiration;
- несколько DNS-зон;
- Cloudflare DNS adapter;
- Domain Resource lifecycle;
- A/AAAA/CNAME/TXT/MX/NS records;
- минимальный Server Catalog;
- Domain Binding `direct_dns`;
- ownership, roles, permissions и limits;
- audit log;
- Telegram operational UX;
- Web Console UX;
- REST API;
- provider sync/error states;
- idempotency/concurrency protection для критичных mutation;
- staging/release hardening.

V1 не включает SSH automation, reverse proxy, TLS issuance, deployments, server agent, полноценный monitoring, Kubernetes, собственный authoritative DNS или преждевременные микросервисы.

## Закрытые decision gates

### Web authentication

**Accepted:** `ADR-0010`.

```text
Passkeys / WebAuthn
      ↓
backend verification
      ↓
server-side session
      ↓
Secure + HttpOnly opaque cookie
      ↓
GET /api/v1/me + backend authorization
```

Telegram не является обязательным Web IdP, а browser session не является business identity.

## Открытые decision gates до соответствующей реализации

Нужно отдельно зафиксировать решения по:

1. Optimistic concurrency mechanism.
2. `Idempotency-Key` storage/TTL.
3. Production secret storage.
4. Семантике zone-level/apex DNS operations.
5. Provider reconciliation/retry strategy.

Дополнительно при Identity implementation нужно конкретизировать bootstrap/recovery UX для WebAuthn enrollment, не меняя выбранный authentication primitive.

## Следующий инженерный рубеж

После закрытия оставшихся обязательных decision gates первый реальный vertical milestone:

```text
Пользователь с permission
      ↓
выбирает bakunity.online
      ↓
создаёт test.bakunity.online на IPv4
      ↓
Cloudflare получает DNS record
      ↓
PostgreSQL хранит Domain Resource
      ↓
Audit фиксирует mutation
      ↓
результат читается через API
      ↓
виден в Telegram
      ↓
тот же use case подключается к Web
```

До реализации product-code этот milestone остаётся планом.

## Authoritative ссылки

- Цели: `docs/GOALS.md`
- Product boundary: `docs/PRODUCT.md`
- Архитектура: `docs/ARCHITECTURE.md`
- Решения: `docs/ADR/`
- Web authentication: `docs/ADR/0010-web-auth-passkeys.md`
- Roadmap: `docs/ROADMAP.md`
- Backlog: `docs/BACKLOG_V1.md`
- Phase 0 review: `docs/PHASE0_REVIEW.md`
- Активная работа: `docs/ACTIVE_WORK.md`
- PCS integration: `docs/CONTEXT_SYSTEM.md`
- GitHub integration: `docs/GITHUB_INTEGRATION.md`
- Evidence: `docs/EVIDENCE.md`
