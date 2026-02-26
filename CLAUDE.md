# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
schemas/auth.py           — Schémas Pydantic auth : RegisterRequest, LoginRequest, TokenResponse, UserResponse
schemas/accounts.py       — BankAccountCreate, BankAccountUpdate, BankAccountResponse
schemas/import_.py        — ImportResult, AccountImportSummary
api/router.py             — APIRouter racine, préfixe /api/v1
api/deps.py               — get_current_user (OAuth2PasswordBearer → decode JWT → User)
api/v1/health.py          — GET /api/v1/health/db (SELECT 1 pour vérifier la BDD)
api/v1/auth.py            — POST /auth/register|login|refresh|logout
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
main.py                   — App FastAPI + GET /health
alembic/env.py            — Lit DATABASE_URL depuis settings, target_metadata = Base.metadata
tests/conftest.py         — Fixtures : test_engine (session), db_session (function, rollback), client, seed_categories, seed_rules
```

### Frontend (`frontend/`)

Stack : Next.js 16.1.6, App Router, TypeScript strict, Tailwind v4, shadcn/ui v3 (new-york/neutral), Bun.

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── layout.tsx                    ← layout centré sans Sidebar (fond gray-50)
│   │   ├── login/page.tsx                ← page login — Zod + react-hook-form
│   │   └── register/page.tsx             ← page register — Zod + react-hook-form + auto-login
│   ├── (dashboard)/
│   │   ├── layout.tsx                    ← DashboardLayout (client, useState sidebarOpen)
│   │   └── dashboard/page.tsx            ← Server Component async, fetch 4 endpoints, empty state
│   ├── api/auth/
│   │   ├── login/route.ts               ← proxy → FastAPI + Set-Cookie access_token HttpOnly
│   │   ├── register/route.ts            ← proxy → FastAPI register + auto-login + Set-Cookie
│   │   └── logout/route.ts              ← Delete-Cookie + appel backend best-effort
│   ├── globals.css                       ← design tokens BankPulse + shadcn vars
│   ├── layout.tsx                        ← root layout (Inter + JetBrains Mono, lang="fr", suppressHydrationWarning)
│   └── page.tsx                          ← redirect /dashboard
├── components/
│   ├── layout/
│   │   ├── sidebar.tsx                   ← Sidebar (desktop fixed w-16 hover:w-60) + MobileSidebar
│   │   └── top-bar.tsx                   ← TopBar sticky + Breadcrumbs + UserMenu (logout branché)
│   └── ui/                              ← composants shadcn (17 installés)
├── components/shared/
│   ├── kpi-card.tsx                      ← KPICard (titre, valeur mono, delta coloré)
│   └── empty-state.tsx                   ← EmptyState (icône, texte, bouton Link)
├── components/dashboard/
│   └── category-chart.tsx               ← "use client" — Recharts PieChart donut + légende
├── hooks/
│   └── useAuth.ts                        ← useAuth() : logout() + isLoggingOut
├── lib/
│   ├── utils.ts                         ← cn() (shadcn)
│   └── format.ts                        ← formatAmount (EUR fr-FR), formatDate (fr-FR)
├── types/api.ts                         ← LoginRequest, RegisterRequest, TokenResponse, UserResponse, ApiError + types dashboard (DashboardSummary, CategoriesBreakdown, TopMerchants, RecurringSubscriptions)
├── proxy.ts                             ← protection routes (Next.js 16, anciennement middleware.ts)
├── .env.local                           ← NEXT_PUBLIC_API_URL=http://localhost:8000
└── next.config.ts                       ← proxy rewrites /api/v1/* → FastAPI :8000
```

**Décisions frontend** :
- **Proxy CORS** : `next.config.ts` rewrites `/api/v1/:path*` → `NEXT_PUBLIC_API_URL` — pas de config CORS côté backend
- **Design tokens** : bloc `@theme` dans `globals.css` — couleurs `primary-500/600/700`, `success-500`, `warning-500`, `danger-500`, `sidebar-bg/border`
- **Fonts** : Inter (`--font-inter`) + JetBrains Mono (`--font-jetbrains-mono`) via `next/font/google`
- **shadcn v3** : package `radix-ui` combiné + `@import "shadcn/tailwind.css"` dans globals.css
- **Tailwind v4** : configuration CSS-first via `@theme` — pas de `tailwind.config.ts` pour les couleurs
- **Sidebar collapse** : pattern `showLabel: boolean` — `false` → `opacity-0 group-hover:opacity-100`, `true` → toujours visible. Deux exports : `Sidebar` (desktop, `fixed w-16 hover:w-60 group`) + `MobileSidebar` (mobile dans Sheet, `w-60` expanded).
- **Couleurs sidebar** : utiliser les valeurs hex directes `bg-[#1f2937]` / `border-[#374151]` plutôt que les classes générées (`bg-sidebar-bg`) — plus fiable avec les blocs `@theme` imbriqués en Tailwind v4.
- **`suppressHydrationWarning`** : à mettre sur `<body>` dans `app/layout.tsx` pour éviter les fausses erreurs d'hydratation causées par des extensions browser (ex: `data-gptw=""`).
- **`SheetContent` sans titre visible** : Radix UI requiert un `DialogTitle` accessible → `<VisuallyHidden.Root><SheetTitle>Navigation</SheetTitle></VisuallyHidden.Root>` dans le SheetContent. `VisuallyHidden` de `radix-ui` est un namespace → utiliser `VisuallyHidden.Root`.
- **Cookies HttpOnly pour les tokens** : ne jamais stocker les JWT en `localStorage`. Les route handlers `/app/api/auth/*` font le proxy vers FastAPI et appellent `response.cookies.set("access_token", ..., { httpOnly: true, sameSite: "lax" })`. Le cookie est invisible au JS client.
- **Auth proxy pattern** : les route handlers Next.js (`/api/auth/login`, `/register`, `/logout`) servent d'intermédiaire entre le browser et FastAPI — ils reçoivent les credentials, appellent FastAPI, et gèrent les cookies. Le browser ne contacte jamais FastAPI directement pour l'auth.
- **`proxy.ts`** (pas `middleware.ts`) : Next.js 16 déprécie `middleware.ts` → utiliser `proxy.ts` avec la fonction exportée `proxy()` (même API, même `config` export).
- **Dashboard data fetching** : Server Component async + `cookies()` (next/headers) → fetch direct FastAPI avec `Authorization: Bearer`. `cache: "no-store"` obligatoire. `Promise.all` pour les fetches parallèles. Retourner `null` si fetch échoue → afficher empty state. Pas de route handler intermédiaire pour les reads (contrairement à l'auth).
- **Recharts** : toujours `"use client"`. PieChart donut = `<Pie innerRadius={65} outerRadius={95} strokeWidth={0}>`. Passer les données sérialisées du Server Component comme props — jamais d'ORM, que des objets JSON plats.
- **Zod v4 + react-hook-form** : ne pas utiliser `.default()` dans les schemas — crée un mismatch TypeScript entre input type (`boolean | undefined`) et output type (`boolean`) incompatible avec `zodResolver`. Mettre les valeurs par défaut uniquement dans `defaultValues` de `useForm`.

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
- `categories` — hiérarchie 2 niveaux (parent_id auto-référençant) ; seedées par la migration `c7d8e3f1a234`
- `category_rules` — règles RegExp merchant_pattern → category_id (priorité décroissante) ; seedées par la même migration
- `tags` + `transaction_tags` — table de jonction M-N
- `budgets` — budgets par catégorie (`period_type`: monthly/quarterly/yearly)
- `recurring_rules` — abonnements détectés par merchant (`frequency`: monthly/yearly)
- `audit_logs` — log de toutes les actions (LOGIN, CREATE, UPDATE, DELETE) avec JSONB `old_values`/`new_values`
- `organizations` — multi-tenant, hors scope Phase 1

**Conventions du schéma** :
- Toutes les PKs sont des UUID générés côté Python (`uuid4`)
- Soft delete universel via `deleted_at TIMESTAMP NULL` (sauf `transactions`)
- `NUMERIC(15, 2)` pour tous les montants financiers

### Roadmap d'implémentation (SPEC_BACKEND.md)

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
- **Refresh tokens stateless** : les refresh tokens sont des JWT signés (pas stockés en DB/Redis pour le MVP). La question ouverte du SPEC_BACKEND (DB vs Redis) est résolue en faveur du stateless jusqu'à besoin de révocation.
- **pydantic[email]** : requis pour `EmailStr` — toujours inclure dans les dépendances si on valide des emails.
- **Migrations seed** : utiliser des UUIDs fixes définis comme constantes au niveau module (ex: `CAT_ALIMENTATION = "a1000000-..."`) pour que le downgrade puisse les cibler sans raw SQL. Insérer via `op.bulk_insert()` + `sa.table()`, supprimer via `op.get_bind()` + `sa.delete()`. **ATTENTION** : les préfixes mnémotechniques des UUIDs fixes doivent rester dans l'alphabet hexadécimal [0-9a-f] — `r` (pour "rule") est invalide et PostgreSQL rejettera l'insertion. Utiliser `a` (alimentation), `c` (child), `d` (rule/règle), `e`, `f`, etc. Les IDs des category_rules dans ce projet utilisent `d1000000-0000-0000-0000-000000000XXX`.
- **Filtres numériques** : toujours `if value is not None:` (jamais `if value:`) pour les filtres `amount_min`, `amount_max` etc. — `0` est un filtre valide mais falsy.
- **Services d'agrégation retournent des `dict`** : les méthodes de `DashboardService` construisent et retournent des `list[dict]`, pas des instances ORM. Les schémas Pydantic correspondants n'ont donc pas besoin de `model_config = ConfigDict(from_attributes=True)`. Utiliser `from_attributes` uniquement quand un endpoint retourne directement un ORM object comme `response_model`.
- **`python-dateutil`** : requis pour `relativedelta` (calcul mois précédent, next_expected d'abonnements). `timedelta` ne gère pas les mois correctement (mois de longueurs différentes).
- **Pagination cursor-based** : encoder `(transaction_date, id)` en base64 JSON. Condition : `OR(date < cursor_date, (date == cursor_date AND id < cursor_id))`. Récupérer `limit+1` pour détecter `next_cursor` sans COUNT. Schéma de réponse : `CursorTransactionListResponse` avec `next_cursor: str | None`.
- **Tags globaux (sans user_id)** : le modèle `Tag` n'a pas de `user_id` — les tags sont partagés entre utilisateurs. La contrainte UNIQUE porte sur `name`. Le bulk-tag vérifie que les transactions appartiennent à l'utilisateur courant.
- **`Transaction.tags` — `lazy="selectin"`** : pour les relations M-N chargées dans une liste d'objets, `lazy="selectin"` émet 1 requête SELECT IN pour tous les objets (évite le N+1). À préférer à `lazy="joined"` pour les M-N.
- **Routes statiques avant routes dynamiques** : dans un router FastAPI, toujours déclarer les routes à segment fixe (`/progress`, `/export`, `/me`) **avant** les routes à paramètre (`/{id}`). Sinon FastAPI essaie de convertir le segment fixe en UUID → 422. Ex: `GET /budgets/progress` avant `GET /budgets/{budget_id}`.

### Definition of Done par étape

Chaque étape requiert : endpoints documentés (OpenAPI auto FastAPI), tests unitaires (≥ 70% coverage), tests d'intégration, migration Alembic versionnée et réversible.
