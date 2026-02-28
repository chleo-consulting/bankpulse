# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Whenever working with any third-party library or something similar, you MUST look up the official documentation to ensure that you're working with up-to-date information.
Use the docs-explorer subagent for efficient documentation lookup.

## Project Overview

BankPulse est un SaaS d'analyse financière personnelle (MVP Phase 1). Le backend est en FastAPI + SQLAlchemy 2.0 + PostgreSQL, le frontend (`frontend/`) est en Next.js 16 + shadcn/ui + Tailwind v4.

**Étape 1 complétée** : infrastructure en place (FastAPI, Alembic, Docker Compose, ruff/black, tests).
**Étape 2 complétée** : Auth JWT — register, login, refresh, logout (stateless). Coverage 93%.
**Étape 3 complétée** : CRUD /accounts + POST /accounts/{id}/import + parser Boursorama. Coverage 96.65%.
**Étape 4 complétée** : Catégorisation — seed 28 catégories + 7 rules RegExp, CategorizationService, GET /transactions, PATCH /transactions/{id}/category. Coverage 97.34%.
**Étape 5 complétée** : Dashboard — DashboardService + 4 endpoints agrégation (/dashboard/summary|categories-breakdown|top-merchants|recurring). Coverage 97.88%.
**Étape 6 complétée** : Transactions Power User — pagination cursor-based, filtres merchant_id+tag_id, GET /transactions/search, POST /bulk-tag, GET /export. Coverage 97.84%.
**Étape 7 complétée** : Budget Tracking — CRUD /budgets, GET /budgets/progress (alertes over/near_limit), BudgetService, calcul période monthly/quarterly/yearly. Coverage 98.05%.
**Étape 8 Phase 1 complétée** : Frontend Next.js 16 — squelette, design tokens BankPulse, shadcn/ui v3, fonts Inter + JetBrains Mono, proxy rewrites → FastAPI.
**Étape 8 Phase 2 complétée** : Layout commun — Sidebar collapse/expand, TopBar breadcrumbs, DashboardLayout (desktop + mobile Sheet).
**Étape 8 Phase 3 complétée** : Auth — Login/Register (Zod + react-hook-form), cookies HttpOnly, proxy.ts, hook useAuth, logout TopBar.
**Étape 8 Phase 4 complétée** : Dashboard — KPI Cards, Donut Chart (Recharts), Top marchands, Abonnements récurrents, Empty states. Server Component + fetch JWT via cookies().
**Étape 8 Phase 5 complétée** : Mes Comptes — liste AccountCard, solde consolidé, modal Ajouter compte, modal Importer CSV (dropzone + progress + résultat), route handlers API `/api/accounts/*`.
**Étape 8 Phase 6 complétée** : Transactions — filtres 8 critères, table checkbox, category inline, bulk-tag, export CSV, pagination cursor prev/next, route handlers `/api/transactions/*`.
**Étape 8 Phase 7 complétée** : Budgets — KPI cards, BudgetProgressCard (progress bar tricolore, alertes), navigation mensuelle URL, modal create/edit (2 schemas Zod distincts), route handlers `/api/budgets/*`.
**Étape 8 Phase 8 complétée** : Polish — loading skeletons (4 × `loading.tsx` App Router auto-Suspense), page `/settings` (SettingsTabs 3 onglets : profil/sécurité/à propos, UI only). Frontend MVP complet.
**Feature Mot de passe oublié complétée** : POST /auth/forgot-password + reset-password (backend), pages `/forgot-password` + `/reset-password` (frontend), service Resend, table `password_reset_tokens`, 13 tests. Coverage 97.80% (199 tests).
**Feature Import multi-banque complétée** : page `/import` (wizard 3 étapes : sélection banque → upload CSV → résultats), route handler dynamique `/api/import/[format]` → `POST /api/v1/import/{format}`, config statique `IMPORT_FORMATS` avec flag `available` pour activation progressive. Boursorama actif, BNP/CA/LCL/SG en "Bientôt disponible".

Les specifications détaillées du produit sont dans `SPEC.md`. Les étapes de développement backend sont décrites dans `SPEC_BACKEND.md`. Le design de l'UI et des layout sont décrites dans `SPEC_UI.md`, et le detail des pages dans `SPEC_UI_PAGES.md`

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

### Frontend (Bun + Next.js)
```bash
cd frontend

# Développement
bun run dev        # http://localhost:3000 (Turbopack)

# Build de vérification
bun run build      # doit passer sans erreur TypeScript

# Ajouter un composant shadcn
bun x shadcn@latest add <component>
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
schemas/auth.py           — Schémas Pydantic auth : RegisterRequest, LoginRequest, TokenResponse, UserResponse, ForgotPasswordRequest, ResetPasswordRequest, MessageResponse
schemas/accounts.py       — BankAccountCreate, BankAccountUpdate, BankAccountResponse
schemas/import_.py        — ImportResult, AccountImportSummary
api/router.py             — APIRouter racine, préfixe /api/v1
api/deps.py               — get_current_user (OAuth2PasswordBearer → decode JWT → User)
api/v1/health.py          — GET /api/v1/health/db (SELECT 1 pour vérifier la BDD)
api/v1/auth.py            — POST /auth/register|login|refresh|logout|forgot-password|reset-password
api/v1/accounts_router.py — GET|POST /accounts, GET|PATCH|DELETE|import /accounts/{id}
api/v1/import_router.py   — POST /import/boursorama (import global multi-comptes)
api/v1/categories_router.py — GET /categories (liste hiérarchique parents+enfants)
api/v1/tags_router.py     — GET /tags, POST /tags (CRUD tags globaux)
api/v1/transactions_router.py — GET /transactions (cursor-based, 7 filtres), GET /search, POST /bulk-tag, GET /export, PATCH /{id}/category
api/v1/dashboard_router.py — GET /dashboard/summary|categories-breakdown|top-merchants|recurring
api/v1/budgets_router.py  — POST|GET /budgets, GET /budgets/progress, GET|PATCH|DELETE /budgets/{id}
schemas/tags.py           — TagCreate, TagResponse
schemas/budgets.py        — BudgetCreate, BudgetUpdate, BudgetResponse, BudgetProgressItem, BudgetsProgress
services/budget_service.py — BudgetService : create/list/get_by_id/update/delete + get_progress()
schemas/dashboard.py      — MonthlySummary, DashboardSummary, CategoryBreakdownItem, CategoriesBreakdown, TopMerchantItem, TopMerchants, RecurringSubscription, RecurringSubscriptions
services/dashboard_service.py — DashboardService : 6 méthodes agrégation (balance, dépenses, comparaison, catégories, marchands, récurrents)
parsers/base.py           — AbstractCsvParser (ABC), ParsedData, ParsedAccount, ParsedTransaction
parsers/boursorama.py     — BoursoramaCsvParser — encodage auto, 12 colonnes, import_hash SHA-256
services/import_service.py — ImportService : import_boursorama() + import_to_account() + auto-catégorisation
services/categorization_service.py — CategorizationService : RegExp matching rules par priorité décroissante
schemas/categories.py     — CategoryResponse, CategoryWithChildrenResponse
schemas/transactions.py   — TransactionResponse (avec tags), TransactionCategoryUpdate, CursorTransactionListResponse, BulkTagRequest (TransactionListResponse = alias compat)
services/email_service.py — EmailService.send_password_reset() via SDK Resend (from: contact@contact.chleo-consulting.fr)
main.py                   — App FastAPI + GET /health
alembic/env.py            — Lit DATABASE_URL depuis settings, target_metadata = Base.metadata
alembic/versions/11ad90472e66_add_password_reset_tokens.py — table password_reset_tokens
tests/conftest.py         — Fixtures : test_engine (session), db_session (function, rollback), client, seed_categories, seed_rules
```

#### Frontend — modules import

```
frontend/app/(dashboard)/import/page.tsx          — Server Component statique (pas de fetch)
frontend/app/(dashboard)/import/loading.tsx       — Skeleton App Router auto-Suspense
frontend/app/api/import/[format]/route.ts         — Route handler proxy → POST /api/v1/import/{format}
frontend/components/import/import-wizard.tsx      — Wizard orchestrateur ("use client"), WizardStep + UploadState discriminated unions, IMPORT_FORMATS config
frontend/components/import/format-selector.tsx    — Étape 1 : grille banques (available / aria-disabled)
frontend/components/import/file-upload-step.tsx   — Étape 2 : dropzone drag-and-drop + fileInputRef reset
frontend/components/import/import-result-view.tsx — Étape 3 : tableau résultats par compte + totaux
```

### Frontend (`frontend/`)

Stack : Next.js 16.1.6, App Router, TypeScript strict, Tailwind v4, shadcn/ui v3 (new-york/neutral), Bun.

**Arborescence complète + décisions techniques → [`ARCHITECTURE_FRONTEND.md`](ARCHITECTURE_FRONTEND.md)**

**Conventions de code** :
- Annotations Python 3.10+ : `X | None` et `list[X]` (pas `Optional`, pas `List`)
- Imports triés par ruff (I001) : stdlib → third-party → local
- `line-length = 100` (ruff + black)
- `asyncio_mode = "auto"` pour pytest-asyncio

**Schéma de données, roadmap, décisions architecturales backend → [`ARCHITECTURE_BACKEND.md`](ARCHITECTURE_BACKEND.md)**
