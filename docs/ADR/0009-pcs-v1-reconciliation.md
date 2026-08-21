# ADR-0009 — Reconciliation существующей PCS-интеграции с PCS V1

Status: Accepted  
Date: 2026-08-21

## Context

Bakunity Infra уже использовала раннюю адаптированную интеграцию Project Context System.

Позже `bakunity/Project-Context-System` получил полноценный PCS V1 baseline `06cd250d2847ee87f66f73930d471d7c1f60991d` с canonical machine state, readiness validation и GitHub operational layer.

Повторная установка с `--force` создала бы риск затереть project-specific правила и authoritative документы Bakunity Infra.

## Decision

Выполнить migration/reconciliation поверх существующей integration.

Принципы migration:

- не использовать `install_pcs.py --force`;
- сохранить и reconcile существующий `AGENTS.md`;
- сохранить `PROJECT_STATE.md` и `ACTIVE_WORK.md`;
- сохранить project-specific GOALS / PRODUCT / ARCHITECTURE / ROADMAP / API / DB / UX / SECURITY;
- сохранить ADR-0001...ADR-0008;
- не создавать дублирующие authoritative документы;
- добавить отсутствующие части standard PCS V1;
- мигрировать `.project/state.json` на canonical PCS V1 pointers, сохранив дополнительные Bakunity Infra fields;
- использовать профиль `standard-adapted`;
- default runtime scope остаётся repository/local/CI only.

## Consequences

Положительные:

- новая AI-сессия следует актуальному PCS V1 bootstrap;
- доступны structural и readiness validation;
- GitHub Issues/Project/PR/Actions имеют описанную роль, не заменяя repository truth;
- context drift можно фиксировать отдельным Issue Form;
- project-specific знания Bakunity Infra не потеряны.

Ограничения:

- GitHub labels/ruleset/project manifests не применяются автоматически;
- runtime/server verification не является частью этой migration;
- `state_based_on_commit` может отставать от HEAD на context/tooling-only commits и требует осознанной reconciliation.

## Alternatives considered

### Переустановить PCS с `--force`

Отклонено: риск затереть существующую project truth и правила.

### Оставить раннюю integration без migration

Отклонено: отсутствовали canonical V1 readiness/GitHub integration capabilities.

### Скопировать новые PCS docs как второй набор документации

Отклонено: нарушает правило одного authoritative источника на тип знания.

## References

- PCS source: `bakunity/Project-Context-System`
- PCS V1 baseline: `06cd250d2847ee87f66f73930d471d7c1f60991d`
- `docs/CONTEXT_SYSTEM.md`
- `docs/GITHUB_INTEGRATION.md`
