# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BankPulse est un SaaS d'analyse financière personnelle (MVP Phase 1). Le backend est en FastAPI + SQLAlchemy 2.0 + PostgreSQL, le frontend (pas encore démarré) sera en Next.js + shadcn/ui + TailwindCSS.

**Étape 1 complétée** : infrastructure en place (FastAPI, Alembic, Docker Compose, ruff/black, tests).
**Étape 2 complétée** : Auth JWT — register, login, refresh, logout (stateless). Coverage 93%.
**Étape 3 complétée** : CRUD /accounts + POST /accounts/{id}/import + parser Boursorama. Coverage 96.65%.

Les specifications détaillées du produit sont dans `SPEC.md`. Les étapes de développement sont décrites dans `SPEC_MVP.md`.

## Commands

Ce projet utilise `uv` comme gestionnaire de packages (Python 3.12).

```bash
# Installer les dépendances
uv sync

# Lancer l'API FastAPI (dev, hot-reload)
uv run uvicorn main:app --reload

# Tests (coverage ≥ 70% requis)
uv run pytest
uv run pytest --tb=short -v  # verbose

# Linter / formatter
uv run ruff check .
uv run ruff check --fix .    # auto-fix
uv run black --check .
uv run black .               # appliquer le formatage

# Migrations Alembic
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic current

# Infrastructure Docker
docker compose up -d db db_test        # démarrer les 2 BDD
docker compose up -d db api            # démarrer BDD + API
docker compose --profile migrate up migrate  # appliquer les migrations via Docker
docker compose down
```

### Premier lancement (setup)
```bash
cp .env.example .env
docker compose up -d db db_test
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

## Architecture

### Structure des modules

```
core/config.py            — Settings pydantic-settings (DATABASE_URL, SECRET_KEY, JWT_ALGORITHM, …)
core/database.py          — engine SQLAlchemy + get_db() générateur (injection FastAPI)
core/security.py          — hash_password/verify_password (bcrypt direct), create_access/refresh_token, decode_token
schemas/auth.py           — Schémas Pydantic auth : RegisterRequest, LoginRequest, TokenResponse, UserResponse
schemas/accounts.py       — BankAccountCreate, BankAccountUpdate, BankAccountResponse
schemas/import_.py        — ImportResult, AccountImportSummary
api/router.py             — APIRouter racine, préfixe /api/v1
api/deps.py               — get_current_user (OAuth2PasswordBearer → decode JWT → User)
api/v1/health.py          — GET /api/v1/health/db (SELECT 1 pour vérifier la BDD)
api/v1/auth.py            — POST /auth/register|login|refresh|logout
api/v1/accounts_router.py — GET|POST /accounts, GET|PATCH|DELETE|import /accounts/{id}
api/v1/import_router.py   — POST /import/boursorama (import global multi-comptes)
parsers/base.py           — AbstractCsvParser (ABC), ParsedData, ParsedAccount, ParsedTransaction
parsers/boursorama.py     — BoursoramaCsvParser — encodage auto, 12 colonnes, import_hash SHA-256
services/import_service.py — ImportService : import_boursorama() + import_to_account()
main.py                   — App FastAPI + GET /health
alembic/env.py            — Lit DATABASE_URL depuis settings, target_metadata = Base.metadata
tests/conftest.py         — Fixtures : test_engine (session), db_session (function, rollback), client
```

**Conventions de code** :
- Annotations Python 3.10+ : `X | None` et `list[X]` (pas `Optional`, pas `List`)
- Imports triés par ruff (I001) : stdlib → third-party → local
- `line-length = 100` (ruff + black)
- `asyncio_mode = "auto"` pour pytest-asyncio

### Schéma de données (v2 — référence)

Le schéma actif est **v2** (`design/entities/v2/ddl_entities.sql`). Le v1 (`design/entities/v1/`) est obsolète (il incluait Open Banking et multi-devises, abandonnés pour le MVP).

Les modèles SQLAlchemy 2.0 sont dans `model/models.py` et correspondent exactement au DDL v2.

**Tables principales** :
- `users` — compte utilisateur (soft delete via `deleted_at`)
- `bank_accounts` — comptes bancaires EUR d'un utilisateur (soft delete)
- `transactions` — transactions importées via CSV (**pas de soft delete**)
- `merchants` — marchands normalisés extraits des descriptions CSV
- `categories` — hiérarchie 2 niveaux (parent_id auto-référençant)
- `tags` + `transaction_tags` — table de jonction M-N
- `budgets` — budgets par catégorie (`period_type`: monthly/quarterly/yearly)
- `recurring_rules` — abonnements détectés par merchant (`frequency`: monthly/yearly)
- `audit_logs` — log de toutes les actions (LOGIN, CREATE, UPDATE, DELETE) avec JSONB `old_values`/`new_values`
- `organizations` — multi-tenant, hors scope Phase 1

**Conventions du schéma** :
- Toutes les PKs sont des UUID générés côté Python (`uuid4`)
- Soft delete universel via `deleted_at TIMESTAMP NULL` (sauf `transactions`)
- `NUMERIC(15, 2)` pour tous les montants financiers

### Roadmap d'implémentation (SPEC_MVP.md)

8 étapes ordonnées avec dépendances :
1. **Infra** — Docker Compose, Alembic migrations, ruff/black
2. **Auth** — JWT + bcrypt, `/auth/register|login|refresh`
3. **Comptes & Import CSV** — CRUD accounts, parser CSV (Boursorama, CA, BNP), déduplication par hash
4. **Catégorisation** — seed catégories, moteur RegExp merchant→category, re-catégorisation manuelle
5. **Dashboard** — endpoints agrégation (`/dashboard/summary|categories-breakdown|top-merchants|recurring`)
6. **Transactions (Power User)** — pagination cursor-based, filtres multicritères, bulk-tag, export CSV
7. **Budget Tracking** — CRUD budgets, progression temps réel, alertes over/near limit
8. **Frontend Next.js** — assemblage des composants UI

### Décisions architecturales

- **bcrypt direct** (sans passlib) : `passlib` est incompatible avec bcrypt ≥ 4.x. Utiliser `bcrypt` directement.
- **Refresh tokens stateless** : les refresh tokens sont des JWT signés (pas stockés en DB/Redis pour le MVP). La question ouverte du SPEC_MVP (DB vs Redis) est résolue en faveur du stateless jusqu'à besoin de révocation.
- **pydantic[email]** : requis pour `EmailStr` — toujours inclure dans les dépendances si on valide des emails.

### Definition of Done par étape

Chaque étape requiert : endpoints documentés (OpenAPI auto FastAPI), tests unitaires (≥ 70% coverage), tests d'intégration, migration Alembic versionnée et réversible.
