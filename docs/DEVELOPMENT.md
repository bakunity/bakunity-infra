# Локальная разработка

Этот документ описывает repository/local workflow. Staging/production deployment сюда не входит.

## Требования

- Python 3.13+
- Git

## Подготовка

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

`.env` не коммитится.

## Environment configuration

Все application settings читаются через `infrastructure.config.Settings` с prefix `BAKUNITY_`.

Поддерживаемые environment values:

```text
development
test
staging
production
```

Не использовать произвольные значения вроде `live`: typed configuration отклонит их при startup/config load.

Основные переменные BI-0102:

```text
BAKUNITY_APP_NAME
BAKUNITY_APP_ENV
BAKUNITY_LOG_LEVEL
BAKUNITY_REQUEST_ID_HEADER
BAKUNITY_TELEGRAM_BOT_TOKEN
```

`BAKUNITY_TELEGRAM_BOT_TOKEN` нужен только процессу Telegram client. Реальное значение не должно попадать в Git, Issues, PR, docs или logs.

Production secret storage backend остаётся отдельным decision gate до подключения реальных provider credentials.

## API

```bash
uvicorn apps.api.main:app --reload
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

Ожидаемый body:

```json
{
  "status": "ok",
  "service": "bakunity-infra"
}
```

Каждый HTTP response получает request/correlation header. По умолчанию:

```text
X-Request-ID: <opaque id>
```

Если клиент передал безопасный `X-Request-ID`, backend сохраняет его. Если header отсутствует или содержит неподходящее значение, backend генерирует новый opaque ID.

Пример:

```bash
curl -i -H 'X-Request-ID: local-check-1' http://127.0.0.1:8000/health
```

Request ID используется только для correlation/observability и **не является** identity, permission или authentication token.

## Structured logging

API и Telegram process используют общий logging foundation из `infrastructure/observability.py`.

Логи формируются как JSON и содержат безопасный operational context, например:

```json
{
  "level": "INFO",
  "service": "Bakunity Infra",
  "environment": "development",
  "message": "http_request_completed",
  "request_id": "local-check-1"
}
```

Фактическая запись также содержит timestamp/logger и при HTTP request — method/path/status/duration.

Нельзя передавать в logging context:

- Telegram bot token;
- Cloudflare/provider token;
- raw session token;
- WebAuthn challenge/private material;
- encryption/master keys.

`SecretStr` защищает случайное отображение secret setting в repr, но разработчик всё равно не должен явно вызывать `get_secret_value()` для логирования.

## Telegram client

Для локального запуска:

```text
BAKUNITY_TELEGRAM_BOT_TOKEN=...
```

Запуск:

```bash
python -m apps.telegram.main
```

Telegram entrypoint использует общий structured logging, но Domain/DNS/provider business logic в нём отсутствует и будет подключаться позже через общие application use cases.

## Проверки product-code

```bash
ruff check apps modules infrastructure tests
python -m compileall -q apps modules infrastructure tests
pytest -q
```

## Проверки PCS

```bash
python scripts/validate_context.py .
python scripts/validate_context.py . --ready
```

До merge product-code задачи обе группы проверок должны быть зелёными.

## Runtime boundary

Локальный development workflow не означает разрешение на:

- SSH к серверам;
- staging/production deploy;
- Cloudflare mutation;
- production database;
- production credentials.

Для live действий нужен отдельный task/live gate.
