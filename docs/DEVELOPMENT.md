# Локальная разработка

Этот документ описывает только repository/local workflow. Staging/production deployment сюда не входит.

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

## API

```bash
uvicorn apps.api.main:app --reload
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "service": "bakunity-infra"
}
```

## Telegram client

Для локального запуска нужен Telegram bot token в локальном environment:

```text
BAKUNITY_TELEGRAM_BOT_TOKEN=...
```

Не передавать реальный token в Issues, PR, docs или Git.

Запуск:

```bash
python -m apps.telegram.main
```

BI-0101 содержит только bootstrap interface. Domain/DNS/provider business logic в Telegram entrypoint отсутствует и добавляется позже через общие application use cases.

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
