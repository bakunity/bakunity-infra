# Активная работа

**Статус:** BI-0002 выполнен в рабочей ветке; ожидает PR/review. Product-code ещё не начат.  
**Обновлено:** 2026-08-29

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Активная задача

```text
BI-0002 — Web authentication decision
Issue: #1
Branch: bi-0002-web-auth
Base commit: d07f4c43be699d437db95c0183aae16492de4c9d
Runtime scope: repository/local/CI only
```

## Что принято в BI-0002

Web authentication V1 зафиксирован в `ADR-0010`:

- основной механизм — Passkeys/WebAuthn;
- internal `User` не зависит от способа входа;
- Telegram identity и WebAuthn credential могут принадлежать одному User;
- после WebAuthn verification создаётся server-side session;
- browser получает opaque `Secure` + `HttpOnly` cookie;
- backend повторно выполняет authorization по актуальному состоянию пользователя;
- публичная самостоятельная регистрация по умолчанию не входит в V1;
- Telegram не является обязательным Web IdP.

Связанные API/DB/Web UX/Security документы reconciled с решением.

## Definition of Done BI-0002

- [x] отдельный ADR принят;
- [x] API contract reconciled;
- [x] database model reconciled;
- [x] Web UX reconciled;
- [x] security model reconciled;
- [x] project context обновлён;
- [ ] PCS structural validation в PR CI;
- [ ] PCS readiness validation в PR CI;
- [ ] PR reviewed/merged.

## Следующий безопасный шаг

После принятия BI-0002:

1. `BI-0003` — зафиксировать optimistic concurrency + idempotency decisions.
2. Затем `BI-0101` — создать минимальный repository scaffold модульного монолита.
3. До реальных provider credentials — закрыть production secret storage decision.
4. До DNS write flows — закрыть provider reconciliation/retry semantics.

## Runtime boundary

Текущая работа — **repository/local/CI only**.

Не выполнялись и не разрешены этой задачей:

- подключение к серверам;
- staging/production deploy;
- Cloudflare credentials/configuration;
- Telegram runtime;
- production database;
- SSH automation.

## Правило обновления

После merge BI-0002:

- `PROJECT_STATE.md` фиксирует WebAuthn decision как текущую truth;
- `.project/state.json` удаляет `web_authentication` из open decision gates;
- `ACTIVE_WORK.md` переключается на BI-0003;
- evidence фиксирует CI/validation результат.
