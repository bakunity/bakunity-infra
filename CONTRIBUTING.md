# Contributing to Bakunity Infra

Bakunity Infra is currently in the planning and architecture phase. Contributions should preserve the product boundaries defined in the repository documentation.

## Before implementation

Before adding a major capability, confirm:

1. Which business module owns it.
2. Whether it belongs in the current roadmap phase.
3. Whether both Web and Telegram can reuse the same application behavior.
4. Which external adapters are required.
5. What authorization rules apply.
6. What audit event should be produced by infrastructure-changing actions.
7. Whether the change introduces new secrets or privileged credentials.

## Architecture rules

- Keep the project a modular monolith unless there is a documented reason to extract a service.
- Do not place business logic in Telegram handlers or web components.
- Do not call infrastructure providers directly from UI/client layers.
- Keep external providers behind adapters/interfaces.
- Keep module boundaries explicit.
- Avoid generic shared code unless it is genuinely shared and stable.
- Prefer clear use cases over hidden cross-module side effects.

## Web and Telegram

Web Console and Telegram Bot are clients of the same system.

A feature should not have two independent implementations of the same business rule.

Example:

```text
Web ───────┐
           ├── CreateSubdomain use case ──> Domains/DNS modules
Telegram ──┘
```

## Security rules

Never commit real credentials, tokens, private keys or production environment files.

If a change requires a new secret, document only the expected variable/configuration name and purpose.

Infrastructure-changing operations should include authorization and auditing from the beginning.

## Change scope

Prefer small, understandable changes.

A pull request should ideally focus on one architectural or product concern rather than combining unrelated refactors, infrastructure changes and features.

## Documentation

When a change affects system boundaries or product behavior, update the relevant documentation:

- `docs/PRODUCT.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/SECURITY.md`

## Current status

Implementation has not started yet. During the current phase, documentation and architecture decisions take priority over scaffolding code that may need to be replaced later.
