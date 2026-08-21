# Backlog V1

Этот документ фиксирует **порядок реализации первой рабочей версии Bakunity Infra** после завершения Phase 0.

Backlog строится не по принципу «сначала весь backend, потом весь frontend», а вертикальными возможностями: бизнес-правило → API/application layer → Telegram/Web → аудит → тесты.

# Цель V1

Сделать безопасное управление доменами и DNS с минимальным каталогом серверов через Web и Telegram.

Подробный стратегический вектор: [GOALS.md](GOALS.md).

# Принципы выполнения backlog

- Не начинать следующий крупный слой, если предыдущий не имеет минимальных тестов и понятного состояния ошибок.
- Бизнес-логика не дублируется в Web и Telegram.
- Любая infrastructure mutation проходит authorization и audit.
- Provider-specific код остаётся в adapter layer.
- Сначала делаем минимальный работающий vertical slice, затем расширяем типами записей и UX.
- Telegram может получить UI раньше Web, но use case и API-контракт не должны проектироваться только под Telegram.

# Epic 0 — Закрытие Phase 0

## BI-0001 — Финальная сверка документации

Проверить согласованность:

- Product;
- Goals;
- Architecture;
- Domain Model;
- Database Model;
- API Contract;
- Telegram UX;
- Web UX;
- Permissions;
- Security;
- Roadmap.

**Готово, когда:** нет известных противоречий по границе V1, сущностям, ролям и серверному каталогу.

## BI-0002 — Зафиксировать Web authentication decision

До реализации identity выбрать конкретный механизм Web-authentication и оформить отдельный ADR.

Требования:

- внутренняя сущность `User` не зависит от способа входа;
- Telegram identity и Web identity могут принадлежать одному User;
- session/token нельзя хранить как бизнес-идентичность;
- backend выполняет authorization самостоятельно.

## BI-0003 — Зафиксировать concurrency/idempotency decisions

Перед write endpoint выбрать:

- optimistic concurrency mechanism;
- способ хранения `Idempotency-Key`;
- поведение повторной provider operation.

# Epic 1 — Каркас модульного монолита

## BI-0101 — Создать repository scaffold

Целевая структура:

```text
apps/
modules/
infrastructure/
tests/
deploy/
```

Без преждевременного создания пустых абстракций для будущих модулей.

## BI-0102 — Конфигурация приложения

Определить:

- environment settings;
- secret references;
- logging;
- request/correlation ID;
- production/dev separation.

## BI-0103 — PostgreSQL и миграции

Подключить PostgreSQL и Alembic.

## BI-0104 — Базовые тестовые инструменты

Подготовить unit/integration testing и отдельную тестовую БД.

# Epic 2 — Identity, authorization и audit foundation

## BI-0201 — User и Identity

Реализовать внутреннего User и внешние identities.

## BI-0202 — RBAC permissions

Реализовать permission checks без `if role == ...` в UI handlers.

## BI-0203 — Ownership/scopes foundation

Поддержать ownership доменных ресурсов и основу scoped roles.

## BI-0204 — Audit Event

Любая значимая mutation должна иметь возможность создать audit event с actor, source client, resource, result и request ID.

## BI-0205 — GET /api/v1/me

Первый identity endpoint.

# Epic 3 — DNS Provider и зоны

## BI-0301 — DNS Provider port

Определить provider-neutral interface для операций DNS.

Минимальные операции:

- list/get zone metadata;
- create record;
- update record;
- delete record;
- read records при необходимости reconciliation.

## BI-0302 — Cloudflare adapter

Первая реализация DNS Provider port.

Секреты не хранятся в Git или открытых полях БД.

## BI-0303 — DNS Zone model

Сохранение управляемых зон и provider zone IDs.

## BI-0304 — Zone access policy

Определить доступ пользователя к конкретной зоне.

## BI-0305 — GET /zones

Список доступных зон через API/application use case.

# Epic 4 — Первый vertical slice: создать поддомен

Это первый главный пользовательский сценарий проекта.

## BI-0401 — Domain Resource model

Создание внутренней модели доменного ресурса.

## BI-0402 — Валидация label/FQDN

Проверить:

- формат;
- длину;
- reserved names;
- уникальность;
- доступ к зоне;
- пользовательские лимиты.

## BI-0403 — CreateDomain use case

Поддержать target:

- IPv4;
- CNAME;
- server — после готовности минимального server catalog.

Для первого vertical slice допускается начать с IPv4, затем подключить server target без изменения публичной модели use case.

## BI-0404 — Provider synchronization

Операция не должна становиться ложным `success`, если Cloudflare вернул ошибку.

## BI-0405 — POST /domains

API endpoint поверх того же use case.

## BI-0406 — Telegram flow: создание

Реализовать:

```text
Зона → имя → target → подтверждение → результат
```

## BI-0407 — Web flow: создание

Подключить форму к тому же backend use case.

## BI-0408 — Audit + tests

Проверить создание из API/Web/Telegram, права, provider error и повтор запроса.

# Epic 5 — Управление доменами

## BI-0501 — GET /domains

Список с ownership и фильтрами.

## BI-0502 — GET /domains/{id}

Карточка ресурса.

## BI-0503 — Telegram «Мои домены»

С пагинацией.

## BI-0504 — Web список и карточка

Таблица, фильтры и domain details.

## BI-0505 — DeleteDomain use case

Проверка зависимостей, provider operation, audit, soft delete/state handling.

## BI-0506 — Destructive confirmations

Web и Telegram требуют явного подтверждения.

# Epic 6 — DNS Records

## BI-0601 — DNS Record model и validation

## BI-0602 — A / AAAA

## BI-0603 — CNAME

## BI-0604 — TXT

## BI-0605 — MX + priority

## BI-0606 — NS

## BI-0607 — Record CRUD API

## BI-0608 — Telegram DNS UX

## BI-0609 — Web DNS table/editor

## BI-0610 — Provider error/retry state

Не скрывать `error/unknown` под статусом success.

# Epic 7 — Минимальный каталог серверов V1

V1 Server — каталог и DNS target, не SSH-management.

## BI-0701 — Server model

Поля:

- name;
- IPv4/IPv6;
- environment;
- provider/region;
- labels;
- registration status.

## BI-0702 — Server permissions

Разделить:

- read;
- use_as_target;
- manage_metadata.

## BI-0703 — Server CRUD API

## BI-0704 — Telegram server catalog

Без ложного `Online`, если мониторинг ещё не реализован.

## BI-0705 — Web server catalog

## BI-0706 — Domain Binding

Связь домен → сервер с `direct_dns`.

## BI-0707 — Server target в CreateDomain

При выборе сервера backend сам получает разрешённый IP и создаёт требуемый DNS target.

# Epic 8 — Roles, limits и admin UX

## BI-0801 — Системные роли V1

```text
superadmin
admin
operator
member
viewer
```

## BI-0802 — User limits

Минимум:

- количество доменных ресурсов;
- max records per domain/zone policy.

## BI-0803 — Admin API

Минимум для пользователей, зон и access policy.

## BI-0804 — Web admin UI

Основные административные действия удобнее сначала реализовать в Web.

## BI-0805 — Telegram admin minimum

Только короткие операционные сценарии, без попытки копировать всю Web Console.

# Epic 9 — Надёжность V1

## BI-0901 — Idempotency

Для критичных create mutation.

## BI-0902 — Optimistic concurrency

Защита от конфликтующих изменений Web/Telegram.

## BI-0903 — Нормализованные error codes

Provider details не протекают в клиенты.

## BI-0904 — Reconciliation/retry strategy

Определить, как пользователь повторяет или восстанавливает provider operation в состоянии `error`.

V1 не обязана иметь сложную distributed queue, если надёжность обеспечивается более простым механизмом.

## BI-0905 — Structured logging

Correlation между client → application → provider → audit.

## BI-0906 — Backup/restore procedure

До production использования.

# Epic 10 — Release readiness

## BI-1001 — Integration tests ключевых сценариев

Минимум:

- create domain;
- duplicate domain;
- permission denied;
- Cloudflare unavailable;
- record CRUD;
- domain delete;
- server binding;
- Web/Telegram consistency.

## BI-1002 — Security review

Проверить:

- secrets;
- authorization;
- audit;
- destructive actions;
- provider permissions;
- sensitive logs.

## BI-1003 — Документация соответствует реализации

Обновить API, DB model, permissions и UX после фактической реализации.

## BI-1004 — Staging

Перед production должен существовать отдельный staging path/environment.

## BI-1005 — V1 acceptance

V1 принимается только по критериям из [GOALS.md](GOALS.md), а не по факту наличия красивого интерфейса.

# Рекомендуемая последовательность первой разработки

```text
Scaffold
   ↓
Identity + Permissions + Audit
   ↓
Cloudflare + Zones
   ↓
Create Domain через IPv4
   ↓
Telegram create flow
   ↓
Web create flow
   ↓
Domain list/details/delete
   ↓
DNS Record CRUD
   ↓
Server catalog + bindings
   ↓
Roles / limits / admin
   ↓
Reliability + staging + V1 release
```

# Первый реальный milestone

Первый milestone разработки должен быть маленьким, но полностью вертикальным:

> Пользователь с разрешением выбирает `bakunity.online`, создаёт `test.bakunity.online` на заданный IPv4, Cloudflare получает запись, PostgreSQL хранит ресурс, audit фиксирует действие, а результат можно прочитать через API и увидеть в Telegram.

После этого тот же use case подключается к Web.

Это будет доказательством, что архитектура работает сквозным образом, а не только существует на бумаге.
