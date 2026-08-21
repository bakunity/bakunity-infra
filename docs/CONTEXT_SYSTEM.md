# Project Context System в Bakunity Infra

Bakunity Infra использует адаптированную **Project Context System (PCS) V1** из репозитория `bakunity/Project-Context-System`.

Текущий reconciliation baseline: `06cd250d2847ee87f66f73930d471d7c1f60991d`.

Профиль проекта: **standard-adapted**.

Цель PCS — сделать состояние проекта переносимым между ChatGPT, Codex, другими AI agents и человеческими разработчиками без зависимости от памяти конкретного чата.

> **CHAT IS WORKSPACE. GIT IS MEMORY. DOCS ARE CURRENT KNOWLEDGE.**

## История integration

Ранняя интеграция Bakunity Infra была сделана по PCS commit `d6b8aaa4e1450841a601daa77d9da26aae101c88`.

После появления PCS V1 существующая integration была **migrated/reconciled**, а не установлена заново:

- `install_pcs.py --force` не использовался;
- существующий `AGENTS.md` не затирался шаблоном;
- `PROJECT_STATE.md` и `ACTIVE_WORK.md` сохранены и reconciled;
- GOALS / PRODUCT / ARCHITECTURE / ROADMAP / API / DB / UX / SECURITY docs сохранены;
- ADR-0001...ADR-0008 сохранены;
- не создано дублирующих authoritative docs.

## Почему профиль standard-adapted

Bakunity Infra уже имела подробную проектную документацию до PCS.

Поэтому PCS V1 используется как protocol/process layer поверх существующих authoritative документов, а не как причина создать вторые копии архитектуры, roadmap или product truth.

## Canonical machine state

`.project/state.json` использует canonical PCS V1 pointers:

```text
state_doc
active_work_doc
architecture_doc
roadmap_doc
adr_dir
incidents_dir
evidence_doc
state_based_on_commit
last_verified_commit
active_branch
active_pr
status
updated_at
```

Дополнительный project-specific machine context Bakunity Infra сохраняется:

```text
phase
implementation_status
open_decision_gates
authoritative
knowledge_status
pcs_source
```

PCS schema допускает project-specific дополнительные поля.

## Карта authoritative knowledge

```text
Текущий state          → docs/PROJECT_STATE.md
Активная работа        → docs/ACTIVE_WORK.md
Цели                   → docs/GOALS.md
Продукт                → docs/PRODUCT.md
Архитектура            → docs/ARCHITECTURE.md
Решения                → docs/ADR/
Roadmap                 → docs/ROADMAP.md
Backlog                 → docs/BACKLOG_V1.md
Domain model            → docs/DOMAIN_MODEL.md
Database model          → docs/DATABASE_MODEL.md
API                     → docs/API_CONTRACT.md
Telegram UX             → docs/TELEGRAM_UX.md
Web UX                  → docs/WEB_UX.md
Permissions             → docs/PERMISSIONS.md
Security                → docs/SECURITY.md
GitHub operational      → docs/GITHUB_INTEGRATION.md
Incidents/root cause    → docs/INCIDENTS/
Evidence                → docs/EVIDENCE.md
Freshness/bootstrap     → .project/state.json
История                 → Git
```

## Что нельзя делать

Нельзя создавать второй source of truth для уже существующего знания.

Например:

- не создавать вторую architecture document рядом с `docs/ARCHITECTURE.md`;
- не копировать roadmap в `PROJECT_STATE.md`;
- не превращать GitHub Issue или handoff в постоянную параллельную truth;
- не записывать runtime-факт только в чат;
- не использовать AI memory как единственное подтверждение project-specific состояния.

## Freshness / reconciliation

Если HEAD отличается от `state_based_on_commit`:

1. определить изменённые файлы;
2. понять, меняют ли они semantic project state;
3. при необходимости обновить `PROJECT_STATE`, `ACTIVE_WORK`, `EVIDENCE` и профильный authoritative документ;
4. только затем считать контекст reconciled.

Сам drift HEAD не всегда ошибка: context/tooling-only commit может не менять product truth. Но drift должен быть осознанным.

## GitHub operational layer

PCS V1 добавляет:

```text
.github/ISSUE_TEMPLATE/
.github/CODEOWNERS
.github/workflows/pcs-context-check.yml
.project/github/
scripts/setup_github.py
docs/GITHUB_INTEGRATION.md
```

GitHub Issues/Projects/PRs координируют execution и не заменяют repository truth.

## Runtime boundary

Default PCS agent scope: **repository/local/CI only**.

Server/staging/production действия требуют отдельного explicit task, environment, verification plan и evidence update.

## Validation

Structural:

```bash
python scripts/validate_context.py .
```

Readiness:

```bash
python scripts/validate_context.py . --ready
```

`PCS READY` допустимо сообщать только после PASS режима `--ready`.

Validator проверяет protocol structure/readiness, но не заменяет инженерную ревизию смысла project-specific документов.
