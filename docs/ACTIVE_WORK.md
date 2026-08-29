# Активная работа

**Статус:** BI-0101 scaffold реализован в рабочей ветке; требуется PR и CI verification.  
**Обновлено:** 2026-08-29

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Активная задача

```text
BI-0101 — Repository scaffold
Issue: #5
Branch: bi-0101-repository-scaffold
PR: ещё не открыт
Base commit: 0095bb7c73027f6e619959d85c9c4472cd025d29
Runtime scope: repository/local/CI only
```

## Что уже реализовано в ветке

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
- [ ] PR открыт;
- [ ] `ruff check` PASS в CI;
- [ ] compile/import check PASS в CI;
- [ ] `pytest` PASS в CI;
- [ ] PCS structural validation PASS на финальном PR HEAD;
- [ ] PCS readiness validation PASS на финальном PR HEAD;
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

1. Открыть PR BI-0101.
2. Запустить Product CI и PCS Context Check.
3. Исправить только реальные проблемы scaffold/CI.
4. После зелёного финального HEAD — merge.
5. Post-merge PCS reconcile.
6. Следующая задача backlog: `BI-0102 — Конфигурация приложения`.
