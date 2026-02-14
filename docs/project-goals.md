# Project Goals — fbrseo (SEO API + Dashboard)

This document is the **source of truth** for what this project is for.
Any change must be evaluated against these goals.

## 1) Mission
Provide a **multi-tenant SEO data platform** (API + dashboard) that combines **Semrush historical imports** with **free Google sources (GSC/GA)** to deliver actionable SEO insights with strong security, rate limiting, and auditability.

## 2) Core goals (must-have)
1. **Secure multi-tenant access via API keys**
   - Per-client keys, granular permissions.
   - Strong logging/auditing.

2. **Hybrid data model**
   - Import Semrush CSV exports (keywords, rankings, backlinks) for historical depth.
   - Enrich continuously with GSC/GA data for freshness.

3. **Operational reliability**
   - Redis cache.
   - Rate limiting per minute/day.
   - Clear health endpoints and diagnostics.

4. **Product surface**
   - REST API (FastAPI) with first-class docs.
   - React dashboard for admins/operators: clients, keys, domains, uploads, usage logs.

## 3) Quality bar
- Safe by default: permission checks everywhere.
- Predictable performance with caching and quotas.
- Easy onboarding: quick start + docker-compose.

## 4) Non-goals
- Being a full replacement for Semrush.
- Crawling the entire web; scope is domain/on-page analysis + integrated sources.

## 5) Decision rule (“Should we do this?”)
Approve changes if they:
- improve correctness of SEO datasets,
- improve security/tenancy isolation,
- reduce operational load (observability, retries, caching),
- increase usefulness of insights.

Reject/defer if they:
- add vendor lock-in without clear upside,
- weaken authentication/authorization boundaries.
