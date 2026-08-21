# ADR-0008 — Project Context System

**Status:** Accepted  
**Date:** 2026-08-21

## Context

Проект проектируется и будет развиваться с активным участием ChatGPT, Codex и других AI agents. Контекст чата не является надёжным долгосрочным хранилищем: сессии заканчиваются, память может быть неполной, а новый agent может не знать причин старых решений.

Отдельный репозиторий `bakunity/Project-Context-System` задаёт подход, при котором Git хранит переносимое текущее знание проекта.

## Decision

Встроить Project Context System (PCS) в Bakunity Infra.

Основные элементы:

- `AGENTS.md` — правила bootstrap и работы AI;
- `.project/state.json` — машинный state/freshness;
- `docs/PROJECT_STATE.md` — что истинно сейчас;
- `docs/ACTIVE_WORK.md` — что делается сейчас;
- `docs/ADR/` — причины решений;
- `docs/INCIDENTS/` — подтверждённые incident/root cause;
- `docs/EVIDENCE.md` — подтверждённые проверки;
- Git — история.

Существующие `ARCHITECTURE`, `ROADMAP`, `PRODUCT`, `GOALS`, API/DB/UX документы сохраняются authoritative для своих типов знания и не копируются в параллельные context-файлы.

## Consequences

- Новая AI-сессия обязана восстанавливать состояние из repository context до планирования работы.
- Repository evidence имеет приоритет над chat memory.
- Semantic state transition требует обновления контекста вместе с кодом/документацией.
- `Done` без evidence не считается подтверждённым завершением.
- Handoff остаётся производным артефактом, а не вторым source of truth.
- Возникает небольшая дисциплина обновления context, но уменьшается риск потери решений и повторного расследования уже решённых вопросов.

## Source

PCS source inspected at:

```text
bakunity/Project-Context-System
d6b8aaa4e1450841a601daa77d9da26aae101c88
```

На момент интеграции source repository содержит specification README, но не готовые installer/validator scripts. Поэтому интеграция адаптирована вручную под существующую структуру Bakunity Infra.
