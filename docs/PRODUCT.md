# Product Definition

## What Bakunity Infra is

Bakunity Infra is an infrastructure control plane for managing domains, DNS, servers and, later, application delivery.

The system is designed around one application core with multiple clients:

- Web Console;
- Telegram Bot;
- REST API;
- possible CLI in the future.

The product goal is to turn routine infrastructure operations into clear, guided actions instead of requiring users to work directly with DNS provider dashboards, server configuration files and command-line tooling for every change.

## Primary use case

A user wants to create a new subdomain and point it to infrastructure.

Expected flow:

1. Choose a managed DNS zone.
2. Enter a subdomain name.
3. Choose a target server, IP address or CNAME.
4. Confirm the action.
5. Bakunity Infra creates and stores the requested configuration.
6. The result is visible from both Telegram and the Web Console.

## Product surfaces

### Telegram Bot

The fastest operational client. It should be optimized for short workflows such as:

- creating a subdomain;
- viewing owned domains;
- managing common DNS records;
- attaching a domain to a server;
- checking status;
- reviewing recent infrastructure actions.

### Web Console

The primary full-featured management interface. It should be better suited for:

- browsing many zones and domains;
- managing DNS records in detail;
- server inventory;
- deployments;
- monitoring;
- audit history;
- user and permission management;
- advanced settings.

### REST API

A stable interface for programmatic access and future integrations.

## First product boundary

The first usable release focuses on domain and DNS management plus a server catalog.

Included:

- multiple DNS zones;
- subdomain lifecycle;
- A, AAAA, CNAME, TXT, MX and NS records;
- DNS record editing and deletion;
- domain ownership and limits;
- server inventory;
- linking a domain/subdomain to a server;
- roles and access control;
- audit events;
- Telegram and Web clients using the same application logic.

Not included in the first release:

- arbitrary remote shell access;
- automatic server provisioning;
- automatic reverse proxy configuration;
- automatic TLS issuance;
- application deployment;
- full monitoring platform;
- multi-region orchestration.

These are planned later, after the DNS/domain foundation is stable.

## Product principles

- Simple for routine operations.
- Safe by default for infrastructure-changing actions.
- The same state is visible from every client.
- No provider-specific concepts should leak unnecessarily into the user experience.
- Every significant mutation should be auditable.
- Advanced capabilities should not make simple workflows harder.

## Naming

Repository: `bakunity/bakunity-infra`

Product name: **Bakunity Infra**

Long-form description: **Bakunity Infrastructure Control Plane**
