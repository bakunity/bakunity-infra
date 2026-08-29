# ADR-0010 — Web authentication через Passkeys/WebAuthn

Status: Accepted  
Date: 2026-08-29

## Context

Bakunity Infra — control plane для инфраструктурных mutation. Web Console должна аутентифицировать пользователя независимо от Telegram, но обе внешние identity должны разрешаться в одну внутреннюю сущность `User` и использовать одну authorization model.

До начала Identity implementation необходимо закрыть decision gate `BI-0002` и определить:

- первичный способ Web authentication;
- границу между identity и session;
- способ хранения browser session;
- требования к credential lifecycle;
- поведение для blocked/disabled users.

Решение не должно привязывать доменную модель к конкретному внешнему IdP и не должно делать browser token бизнес-идентичностью пользователя.

## Decision

Для V1 основной Web authentication mechanism — **Passkeys на базе WebAuthn**.

### Internal identity

Внутренняя сущность `User` остаётся независимой от способа входа.

```text
User
├── Telegram identity
└── WebAuthn credential(s)
```

WebAuthn credential является credential/identity binding пользователя, а не самим `User`.

### Registration

Самостоятельная публичная регистрация в V1 по умолчанию отсутствует.

Credential enrollment разрешается только:

- уже аутентифицированному пользователю, которому разрешено добавить credential;
- либо через контролируемый bootstrap/invite flow, определённый Identity module.

Администратор не должен иметь возможность получить или восстановить private key passkey: private key остаётся у authenticator пользователя.

### Authentication ceremony

Backend генерирует WebAuthn challenge, проверяет origin/RP ID, challenge, signature, credential state и user status.

После успешной проверки backend создаёт **server-side session**.

### Browser session

Browser получает только opaque session identifier в cookie:

```text
Secure
HttpOnly
SameSite=Lax (или более строгий режим, если UX позволяет)
Path=/
```

Session payload/roles/permissions не являются доверенным клиентским состоянием.

Server-side session хранит как минимум:

- session id/hash;
- `user_id`;
- created/last-used/expires timestamps;
- revoked state;
- безопасные metadata, необходимые для security/audit.

Для чувствительных mutation authorization вычисляется backend из актуального состояния пользователя/ролей, а не из данных, зафиксированных в cookie.

### CSRF

Cookie-authenticated write endpoints должны иметь CSRF protection. Конкретная техника может быть реализована через same-site policy + CSRF token/origin checks, но защита не может полагаться только на UI.

### Session lifecycle

Должны поддерживаться:

- explicit logout;
- expiration;
- server-side revocation;
- revocation всех сессий пользователя при необходимости;
- запрет новых session для `blocked`/`disabled` user;
- повторная проверка user status/authorization при запросах.

### Credential lifecycle

Пользователь может иметь несколько passkeys.

Credential metadata не должна содержать private key. В БД хранится только публичный verification material и технические идентификаторы, необходимые WebAuthn.

Удаление последнего credential должно быть защищено от случайной потери доступа и выполняться отдельным use case.

### Telegram linking

Telegram identity не является способом browser authentication по умолчанию. Связывание Telegram identity с Web user выполняется отдельным безопасным linking flow и не создаёт вторую систему ролей.

## Consequences

Плюсы:

- нет пользовательских паролей, которые Bakunity Infra должна хранить/сбрасывать;
- phishing-resistant authentication при корректной WebAuthn verification;
- продукт не зависит от Google/GitHub/Telegram как обязательного Web IdP;
- несколько passkeys можно связать с одним `User`;
- browser session полностью контролируется backend и может быть отозвана.

Стоимость:

- WebAuthn ceremony сложнее обычного password login;
- нужен корректный RP ID/origin configuration для dev/staging/production;
- требуется продуманный bootstrap/recovery flow;
- session storage становится частью persistence/security foundation.

## Alternatives considered

### Username/password

Отклонено как основной V1 механизм: добавляет хранение password verifier, password reset, anti-bruteforce и повышает phishing surface без явной продуктовой выгоды.

### Telegram Login как единственный Web-вход

Отклонено: делает Web Console зависимой от Telegram и смешивает transport/client identity с platform identity.

### Google/GitHub OIDC как обязательный вход

Отклонено как единственный V1 механизм: создаёт обязательную зависимость от стороннего IdP и ограничивает будущих пользователей. OIDC может быть добавлен позже как дополнительный identity provider без изменения `User`.

### JWT в localStorage

Отклонено: persistent bearer token в browser storage увеличивает последствия XSS и усложняет отзыв/актуализацию authorization state.

## Security invariants

1. Private key passkey никогда не попадает на backend.
2. Challenge одноразовый и ограничен по времени.
3. RP ID/origin проверяются backend.
4. Cookie содержит только opaque session identifier, а не permissions/roles.
5. Session можно отозвать server-side.
6. Authorization выполняется после authentication в application/backend layer.
7. `blocked`/`disabled` user не получает новую session и не может выполнять mutation.
8. Authentication/session events доступны для audit без записи чувствительного credential material.

## References

- Issue #1 — `BI-0002`
- `docs/ARCHITECTURE.md`
- `docs/API_CONTRACT.md`
- `docs/DATABASE_MODEL.md`
- `docs/PERMISSIONS.md`
- `docs/SECURITY.md`
- `docs/WEB_UX.md`
