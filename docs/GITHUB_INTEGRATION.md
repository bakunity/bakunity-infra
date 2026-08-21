# GitHub Integration

Bakunity Infra использует PCS как Git-native слой постоянного контекста, а GitHub — как operational layer для единиц работы, review и автоматических проверок.

## Ownership

- `docs/PROJECT_STATE.md` — текущая project truth.
- `docs/ACTIVE_WORK.md` — текущая execution/workstream.
- `docs/ARCHITECTURE.md` + `docs/ADR/` — архитектура и rationale.
- `docs/ROADMAP.md` — стратегия.
- GitHub Issues — bounded units of work.
- GitHub Project — execution visibility.
- Pull Requests — implementation review.
- GitHub Actions — автоматическая verification.
- `docs/EVIDENCE.md` — принятая verification memory.

GitHub Issues/Projects/PR не заменяют authoritative repository truth.

## Runtime boundary

GitHub development flow сам по себе **не даёт runtime scope**.

По умолчанию работа ограничена repository/local/CI. Staging/server/live действия начинаются только по отдельной явно разрешённой задаче и после соответствующего live gate.

## Рекомендуемый flow

```text
Issue
  ↓
bounded branch/task
  ↓
implementation
  ↓
tests / CI
  ↓
PR / review
  ↓
merge
```

Если требуется runtime verification:

```text
repository implementation accepted
  ↓
explicit staging task
  ↓
deploy
  ↓
smoke/live evidence
  ↓
production approval, если требуется
```

## Issue Forms

PCS V1 forms:

- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/ISSUE_TEMPLATE/feature.yml`
- `.github/ISSUE_TEMPLATE/architecture.yml`
- `.github/ISSUE_TEMPLATE/incident.yml`
- `.github/ISSUE_TEMPLATE/context-drift.yml`

Blank issues отключены через `.github/ISSUE_TEMPLATE/config.yml`, чтобы bounded task context не терялся.

## CODEOWNERS

`.github/CODEOWNERS` защищает контекстно-критичные пути review ownership для `@bakunity`:

- `.project/`;
- `AGENTS.md`;
- `docs/ARCHITECTURE.md`;
- `docs/ADR/`;
- `.github/`.

Это repository policy file; фактическое требование review зависит от GitHub branch/ruleset configuration.

## GitHub manifests

- `.project/github/labels.json`
- `.project/github/project-model.json`
- `.project/github/ruleset-policy.json`

Эти файлы описывают рекомендуемую operational model и governance.

Они **не означают**, что ruleset или GitHub Project уже применены live.

## setup_github.py

```bash
python scripts/setup_github.py .
```

Без флагов скрипт ничего не мутирует.

После отдельного review можно применить только безопасный label manifest:

```bash
python scripts/setup_github.py . --repo bakunity/bakunity-infra --apply-labels
```

PCS V1 намеренно не применяет Project/Ruleset автоматически: governance может влиять на merge/access и требует отдельного approval.

## PCS Context Check

Consumer-repository workflow:

```text
.github/workflows/pcs-context-check.yml
```

В Bakunity Infra он адаптирован под профиль `standard-adapted` и запускает:

```bash
python scripts/validate_context.py .
python scripts/validate_context.py . --ready
```

Собственные installer-profile tests репозитория `Project-Context-System` сюда не переносятся, потому что они тестируют PCS distribution, а не consumer project.

## Что migration не делала

PCS V1 migration:

- не применяла GitHub labels через API/CLI;
- не создавала GitHub Project;
- не применяла branch/ruleset governance;
- не трогала server/runtime;
- не деплоила приложение;
- не меняла production credentials.

Эти действия остаются отдельными, явно подтверждаемыми задачами.
