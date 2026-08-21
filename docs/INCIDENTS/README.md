# Инциденты и root cause

Этот каталог хранит подтверждённые инженерные инциденты Bakunity Infra.

Инцидент создаётся, когда есть реальная проблема в runtime, deployment, provider integration, данных или security-sensitive поведении, которую важно не потерять между сессиями.

## Именование

```text
YYYY-MM-DD-short-title.md
```

Пример:

```text
2026-09-03-cloudflare-sync-timeout.md
```

## Минимальная структура

```text
# Название

Status: investigating / mitigated / resolved
Severity: ...
Detected: ...
Resolved: ...

## Симптом
## Impact
## Evidence
## Root cause
## Что исключили
## Исправление
## Проверка после исправления
## Prevention / follow-up
## Связанные commits / requests / issues
```

## Правила

- Не фиксировать предположение как root cause без evidence.
- Отделять симптом от причины.
- Записывать исключённые гипотезы, если это поможет не повторять расследование.
- Не помещать в incident секреты, токены, пароли или приватные ключи.
- После подтверждённого исправления добавить соответствующее evidence в `docs/EVIDENCE.md`.
- Если инцидент меняет архитектурное решение, создать отдельный ADR.

Сейчас подтверждённых runtime-инцидентов нет, поскольку product implementation ещё не начат.
