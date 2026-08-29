# Активная работа

**Статус:** BI-0002 merged; BI-0003 оформлен в PR #4, ожидается финальный PCS CI. Product-code ещё не начат.  
**Обновлено:** 2026-08-29

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Активная задача

```text
BI-0003 — Optimistic concurrency + idempotency
Issue: #3
Branch: bi-0003-concurrency-idempotency
PR: #4
Base commit: c1e70d768255c86c089f6b06f070d2c710fa0bb6
Runtime scope: repository/local/CI only
```

## Что уже принято до BI-0003

`BI-0002` merged в `main` commit:

```text
c1e70d768255c86c089f6b06f070d2c710fa0bb6
```

Main PCS Context Check после merge: workflow run `33260864549` → success.

Web authentication V1 остаётся зафиксирован в `ADR-0010`: Passkeys/WebAuthn + server-side sessions.

## Что фиксирует BI-0003

`ADR-0011`:

- mutable resources получают integer `version`;
- Web/API используют `ETag` + `If-Match`;
- internal Telegram/application use case передаёт `expected_version`;
- stale write → `409 resource_version_conflict` без silent overwrite;
- retry-sensitive mutation использует application `operation_id`;
- Web/API передают `Idempotency-Key`;
- Telegram сохраняет и повторно использует operation id подтверждённого flow;
- idempotency state хранится в PostgreSQL;
- same key + same payload возвращает тот же logical result;
- same key + different payload → `409 idempotency_key_reused`;
- concurrent duplicate → `idempotency_in_progress` без второго side effect;
- неопределённый provider outcome → `unknown`, а не blind retry;
- default completed retention V1 — 24 часа.

Связанные API/DB/Security/PCS документы reconciled с решением.

## Definition of Done BI-0003

- [x] отдельный ADR принят;
- [x] API contract reconciled;
- [x] database model reconciled;
- [x] security model reconciled;
- [x] project state reconciled;
- [x] BI-0002 merge/main CI зафиксированы;
- [x] PR #4 открыт;
- [ ] PCS structural validation PASS на финальном PR HEAD;
- [ ] PCS readiness validation PASS на финальном PR HEAD;
- [ ] PR merged.

## Следующий безопасный шаг

После merge BI-0003:

```text
BI-0101 — repository scaffold
```

Это будет первый product-code этап.

Целевая минимальная структура из backlog:

```text
apps/
modules/
infrastructure/
tests/
deploy/
```

Без преждевременного создания пустых модулей для поздних Deployments/Proxy/Certificates/Monitoring.

Оставшиеся decision gates stage-specific:

1. Production secret storage — до реальных provider credentials.
2. Zone-level/apex semantics — до административного apex write flow.
3. Provider reconciliation/retry — до DNS provider write flow.

Они не блокируют scaffold.

## Runtime boundary

Текущая работа — **repository/local/CI only**.

Не выполнялись и не разрешены BI-0003:

- подключение к серверам;
- staging/production deploy;
- Cloudflare credentials/configuration;
- Telegram runtime;
- production database;
- SSH automation.

## После merge BI-0003

PCS должен быть переключён на `main`/следующий work item, evidence — дополнен финальным merge + CI result, а следующей активной задачей становится `BI-0101`.
