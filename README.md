# BankPulse Platform

SaaS d'analyse financière personnelle — FastAPI + SQLAlchemy 2.0 + PostgreSQL + Next.js 16.

## Stack

**Backend** : Python 3.12 · FastAPI · SQLAlchemy 2.0 · Alembic · PostgreSQL · JWT (stateless) · Docker Compose
**Frontend** : Next.js 16 · App Router · shadcn/ui v3 · Tailwind v4 · Bun

## Setup

### Backend
```bash
cp .env.example .env
docker compose up -d db db_test
uv run alembic upgrade head
uv run uvicorn main:app --reload   # http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
bun install
bun run dev   # http://localhost:3000
```

## Commandes utiles

```bash
uv run pytest                                      # tests (coverage ≥ 70%)
uv run ruff check . && uv run black --check .      # lint
```

## État — MVP Phase 1

| Étape | Statut |
|-------|--------|
| 1 Infra | ✅ |
| 2 Auth JWT | ✅ |
| 3 Import CSV Boursorama | ✅ |
| 4 Catégorisation | ✅ |
| 5 Dashboard | ✅ |
| 6 Transactions Power User | ✅ |
| 7 Budget Tracking | ✅ |
| 8 Frontend Next.js (8 phases) | ✅ |
| + Mot de passe oublié | ✅ |
| + Import multi-banque | ✅ |
| + Partage de comptes | ✅ |

## Déploiement

Railway : 2 services (backend FastAPI + frontend Next.js) + PostgreSQL plugin.
CI GitHub Actions : ruff/black/pytest + bun build.
