# Активная работа

**Статус:** BI-0101 product scaffold проверен; финальный context-only PCS check перед merge.  
**Обновлено:** 2026-08-29

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Активная задача

```text
BI-0101 — Repository scaffold
Issue: #5
Branch: bi-0101-repository-scaffold
PR: #6
Base commit: 0095bb7c73027f6e619959d85c9c4472cd025d29
Validated product-code head: 93ce9415af1e4f793b0bae69607e3e2a8ebca7ae
Runtime scope: repository/local/CI only
```

## Что реализовано

Минимальный scaffold создан без фиктивной реализации будущих модулей:

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

Добавлено:

- `pyproject.toml` с Python 3.13 и package/dependency metadata;
- FastAPI application factory/entrypoint;
- `GET /health`;
- отдельный Telegram entrypoint и bootstrap router без provider/business logic;
- `infrastructure/config.py` на `pydantic-settings`;
- `.env.example` без реальных secrets;
- `.gitignore` для env/venv/cache/frontend artifacts;
- pytest health test;
- pytest Telegram bootstrap/import test;
- Ruff/compile/test foundation;
- `.github/workflows/product-ci.yml`;
- `docs/DEVELOPMENT.md` с local-only workflow;
- Web и deploy boundaries без ложного утверждения о готовом frontend/runtime.

## Verification

Product CI run `33261488967` на product-code head `93ce9415...`:

```text
Install project → PASS
Ruff            → PASS
Compile         → PASS
Tests           → PASS
```

PCS Context Check run `33261488963` на том же head:

```text
Structural validation → PASS
Readiness validation  → PASS
```

После этого обновлены только PCS/context/evidence документы; product-code не менялся. Требуется последний PCS run на финальном context head перед merge.

## Что намеренно НЕ реализовано

BI-0101 не содержит:

- Cloudflare adapter;
- PostgreSQL business schema или Alembic migrations;
- WebAuthn runtime;
- browser session persistence;
- concurrency/idempotency runtime;
- полноценный Next.js Web Console;
- SSH/server management;
- deployment runtime;
- reverse proxy/TLS/monitoring.

## Definition of Done BI-0101

- [x] рабочая ветка создана от актуального `main`;
- [x] минимальный scaffold создан;
- [x] FastAPI `/health` имеет test;
- [x] Telegram entrypoint не содержит инфраструктурной бизнес-логики;
- [x] config foundation создан без committed secrets;
- [x] product-code CI workflow добавлен;
- [x] local development guide добавлен;
- [x] PR #6 открыт;
- [x] `ruff check` PASS в CI;
- [x] compile/import check PASS в CI;
- [x] `pytest` PASS в CI;
- [x] PCS structural validation PASS на verified product-code head;
- [x] PCS readiness validation PASS на verified product-code head;
- [ ] final context-only PCS validation PASS;
- [ ] PR merged;
- [x] runtime/server untouched.

## Runtime boundary

Текущая задача — **repository/local/CI only**.

Не выполнялись и не разрешены:

- server SSH;
- staging/production deploy;
- Cloudflare token/configuration;
- production database;
- production Telegram bot token/run;
- любые live infrastructure mutations.

## Следующий безопасный шаг

1. Дождаться финального PCS Context Check после context/evidence reconciliation.
2. При PASS — merge PR #6 без дополнительных product-code изменений.
3. Проверить Product CI + PCS на merge commit `main`.
4. Выполнить post-merge PCS reconcile.
5. Перейти к `BI-0102 — Конфигурация приложения`.
