# Security Model

Bakunity Infra is intended to manage infrastructure-changing operations. Security is therefore a product requirement, not a later add-on.

## Security baseline

### Secrets never belong in Git

Do not commit:

- Telegram bot tokens;
- Cloudflare API tokens;
- database passwords;
- SSH private keys;
- application secret keys;
- encryption keys;
- production `.env` files;
- exported provider credentials;
- backup archives containing credentials.

Repository examples may contain variable names only, never real values.

## Least privilege

Provider credentials should receive only the permissions necessary for Bakunity Infra to perform its intended operations.

Examples:

- DNS tokens should be limited to required zones and DNS permissions;
- server credentials should not default to unrestricted root access;
- application database users should have only required database privileges.

## Identity and authorization

Authorization must be enforced in backend/application logic rather than relying on hidden buttons or frontend routes.

The identity model should support:

- users;
- roles;
- permissions;
- ownership of domains/resources;
- administrative overrides where explicitly allowed;
- source client information for important actions.

Telegram identity and Web identity should resolve to the same internal user model where appropriate.

## Audit trail

Meaningful infrastructure mutations should generate audit events.

Examples:

- domain created/deleted;
- DNS record created/changed/deleted;
- server added/changed/removed;
- resource ownership changed;
- role or permission changed;
- deployment started or rolled back;
- sensitive integration configuration changed.

An audit event should be able to answer, where applicable:

- who performed the action;
- which client was used;
- what resource changed;
- when it happened;
- whether it succeeded;
- enough metadata to investigate the action without logging secrets.

## External provider boundaries

Cloudflare and future providers must be accessed through controlled adapters.

Provider errors must not expose secrets in Telegram messages, web responses or logs.

## Server management

When remote server management is introduced, it must not begin as arbitrary remote shell execution from user input.

Preferred direction:

- explicit allowed operations;
- dedicated service account;
- key-based authentication;
- narrow privilege elevation where required;
- host identity verification;
- operation timeouts;
- audit events;
- idempotent operations where possible;
- rollback strategy for configuration changes.

## Destructive operations

High-impact operations should require explicit confirmation and should be designed to minimize accidental removal.

Examples include deleting a managed domain, removing DNS records used in production, deleting a server, or replacing routing configuration.

## Logging

Logs must avoid secret values and sensitive credential material.

Structured logs should include correlation/request identifiers where useful so that Web, Telegram, API and provider actions can be traced across a single operation.

## Backups

Before the system manages production infrastructure, backup and recovery procedures must exist for its own persistent state.

Backups must be protected at least as carefully as the primary database because they can contain infrastructure metadata and encrypted secrets.

## Security before automation

The first DNS/domain phase intentionally avoids broad SSH automation. Remote provisioning, proxy changes and deployment automation should be added only after authorization, auditing, credential storage and rollback foundations are established.
