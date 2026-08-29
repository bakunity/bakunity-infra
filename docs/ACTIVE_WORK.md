# Активная работа

**Статус:** BI-0101 merged; post-merge PCS pointer reconciled; активная задача — BI-0102 configuration foundation.  
**Обновлено:** 2026-08-29

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Завершённая задача BI-0101

```text
Issue: #5
PR: #6
Merge commit: 91ae2239475a7c9560dfcff5a16424cb9cb3134c
Runtime scope: repository/local/CI only
```

BI-0101 создал первый product-code scaffold:

```text
apps/
├── api/
├── telegram/
└── web/README.md

modules/
infrastructure/
tests/
deploy/README.md
```

Подтверждено:

- FastAPI `/health`;
- Telegram bootstrap без provider/business logic;
- typed settings foundation;
- `.env.example` без secrets;
- Ruff/compile/pytest Product CI;
- local development docs.

PR final Product CI и PCS были PASS. После squash merge Product CI на `main` run `33261628217` также PASS.

Первый post-merge PCS run `33261628261` корректно обнаружил stale `state_based_on_commit`: он ссылался на pre-squash PR head. Это не product failure; pointer reconciled на merge commit `91ae2239...`.

## Активная задача

```text
BI-0102 — Конфигурация приложения, logging и correlation ID
Issue: #7
Branch: ещё не создана
PR: нет
Base commit: 91ae2239475a7c9560dfcff5a16424cb9cb3134c
Runtime scope: repository/local/CI only
```

## Цель BI-0102

Развить минимальный config scaffold до foundation для следующих PostgreSQL/Identity/provider задач:

- typed environment configuration;
- явные development/test/staging/production semantics;
- startup/config validation;
- structured logging;
- HTTP request/correlation ID middleware;
- application correlation context, пригодный позже для Telegram/provider/audit;
- защита sensitive values от логирования;
- tests и документация.

## Что BI-0102 не делает

- не выбирает и не подключает production secret storage backend;
- не добавляет реальные provider credentials;
- не подключается к Cloudflare;
- не создаёт PostgreSQL business schema;
- не реализует WebAuthn/RBAC;
- не делает staging/production deploy;
- не трогает серверы.

Production secret storage остаётся отдельным decision gate до реальных provider credentials.

## Definition of Done BI-0102

- [ ] ветка создана от актуального `main` после успешного PCS reconcile;
- [ ] config environment semantics реализованы и протестированы;
- [ ] structured logging foundation реализован;
- [ ] request/correlation ID проходит через HTTP request/response;
- [ ] sensitive settings не попадают в logs;
- [ ] `/health` не сломан;
- [ ] Ruff/compile/pytest PASS;
- [ ] PCS structural/readiness PASS;
- [ ] PR merged;
- [ ] runtime/server untouched.

## Runtime boundary

Текущая работа — **repository/local/CI only**.

Любые SSH, staging/production deploy, Cloudflare mutation, production DB и production Telegram запуск остаются за отдельным live gate.

## Следующий безопасный шаг

1. Получить PASS PCS structural/readiness после post-merge pointer reconciliation на `main`.
2. Создать `bi-0102-application-configuration` от актуального `main`.
3. Реализовать BI-0102 в bounded scope.
