# Текущее состояние проекта

**Статус знания:** CONFIRMED  
**Последняя сверка:** 2026-08-29  
**Фаза:** старт реализации V1; активная задача BI-0101 repository scaffold.

Этот документ отвечает только на вопрос: **что истинно о Bakunity Infra прямо сейчас**.

Подробные цели, архитектура и roadmap хранятся в профильных authoritative документах и здесь не дублируются.

## Что существует сейчас

- Репозиторий проекта оформлен и содержит архитектурную/продуктовую спецификацию.
- Архитектура зафиксирована как **modular monolith**.
- Клиенты: **Web Console**, **Telegram Bot**, **REST API**.
- Web и Telegram используют одно application core и одну модель прав.
- PostgreSQL выбран как внутренний source of truth для продуктового состояния.
- Cloudflare выбран первым DNS provider adapter.
- V1 зафиксирована как управление доменами/DNS с минимальным Server Catalog и Domain Binding.
- Phase 0 прошёл архитектурную ревизию со статусом PASS.
- Backlog V1 сформирован.
- Project Context System интегрирована и reconciled до **PCS V1**, baseline `06cd250d2847ee87f66f73930d471d7c1f60991d`, профиль `standard-adapted`.
- В репозитории есть canonical PCS validator с structural/readiness режимами и GitHub operational-layer manifests/workflow.
- `BI-0002` принят и merged: Web authentication V1 использует Passkeys/WebAuthn с server-side browser sessions (`ADR-0010`).
- `BI-0003` принят и merged: optimistic concurrency/idempotency используют integer resource version + ETag/If-Match и PostgreSQL-backed application operation state (`ADR-0011`).
- Default completed idempotency retention V1 — 24 часа; неопределённый provider outcome не допускает blind retry.
- Internal `User` остаётся независимым от Telegram/Web authentication mechanism; Telegram identity и WebAuthn credentials могут принадлежать одному User.
- Следующая активная задача — `BI-0101` (Issue #5), первый product-code scaffold.
- Server/runtime не менялись в рамках BI-0002/BI-0003.

## Чего сейчас нет

На момент этой сверки **product-code scaffold ещё не зафиксирован как завершённый**.

В репозитории пока нет подтверждённой реализации:

- рабочего FastAPI backend scaffold;
- PostgreSQL migrations;
- WebAuthn runtime;
- browser session persistence;
- optimistic concurrency runtime;
- idempotency runtime/storage migration;
- Cloudflare adapter;
- Telegram bot runtime;
- Next.js Web Console;
- server management;
- reverse proxy;
- TLS automation;
- deployments;
- monitoring.

Наличие этих элементов в architecture/API/DB/backlog означает зафиксированный план/contract, а не реализованную возможность.

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
- optimistic concurrency protection;
- idempotency protection для retry-sensitive infrastructure mutation;
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

### Optimistic concurrency + idempotency

**Accepted:** `ADR-0011`.

```text
Mutable resource
      ↓
version BIGINT
      ↓
ETag / If-Match / expected_version
      ↓
stale write → 409 resource_version_conflict
```

Retry-sensitive mutation:

```text
Idempotency-Key / operation_id
      ↓
PostgreSQL idempotency_operations
      ↓
request fingerprint
      ↓
one logical operation
      ↓
completed result reused without second side effect
```

Default completed idempotency retention V1 — 24 часа. `unknown` external outcome не маскируется под success/blind retry.

## Открытые stage-specific decision gates

1. Production secret storage — закрыть до реальных provider credentials.
2. Семантика zone-level/apex DNS operations — закрыть до административного apex write flow.
3. Provider reconciliation/retry strategy — закрыть до DNS provider write flow.

Дополнительно при Identity implementation нужно конкретизировать bootstrap/recovery UX для WebAuthn enrollment, не меняя выбранный authentication primitive.

Эти оставшиеся gate **не блокируют repository scaffold BI-0101**.

## Текущий инженерный рубеж

Активная задача:

```text
BI-0101 — Repository scaffold
Issue #5
```

Цель — создать минимальный рабочий каркас modular monolith, после которого можно последовательно реализовывать configuration, PostgreSQL/migrations и Identity foundation.

Первый продуктовый vertical milestone после foundation epics остаётся:

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

## Verification state

### BI-0002

Merge commit:

```text
c1e70d768255c86c089f6b06f070d2c710fa0bb6
```

Main PCS Context Check: workflow run `33260864549` → success.

### BI-0003

Merge commit:

```text
daea95ab7d042069c1cd962c038bb4fad8fd2d59
```

PR #4 final PCS checks → success.  
Main PCS Context Check: workflow run `33261170180` → success.

Runtime/server verification не выполнялась и не требовалась: обе задачи были repository/docs only.

## Authoritative ссылки

- Цели: `docs/GOALS.md`
- Product boundary: `docs/PRODUCT.md`
- Архитектура: `docs/ARCHITECTURE.md`
- Решения: `docs/ADR/`
- Web authentication: `docs/ADR/0010-web-auth-passkeys.md`
- Concurrency/idempotency: `docs/ADR/0011-concurrency-idempotency.md`
- Roadmap: `docs/ROADMAP.md`
- Backlog: `docs/BACKLOG_V1.md`
- Phase 0 review: `docs/PHASE0_REVIEW.md`
- Активная работа: `docs/ACTIVE_WORK.md`
- PCS integration: `docs/CONTEXT_SYSTEM.md`
- GitHub integration: `docs/GITHUB_INTEGRATION.md`
- Evidence: `docs/EVIDENCE.md`
