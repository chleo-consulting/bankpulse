# BankPulse Platform

SaaS d'analyse financière personnelle — FastAPI + SQLAlchemy 2.0 + PostgreSQL + Next.js 16.

## Stack

**Backend** : Python 3.12 · FastAPI · SQLAlchemy 2.0 · Alembic · PostgreSQL · JWT (stateless) · Docker Compose
**Frontend** : Next.js 16 · shadcn/ui v3 · Tailwind v4 · Bun

## Setup

```bash
cp .env.example .env
docker compose up -d db db_test
uv run alembic upgrade head
uv run uvicorn main:app --reload   # http://localhost:8000/docs
```

## Tests

```bash
uv run pytest                          # coverage ≥ 70% requis
uv run ruff check . && uv run black --check .
```

## État — MVP Phase 1

| Étape | Statut |
|-------|--------|
| 1 Infra | ✅ |
| 2 Auth JWT | ✅ |
| 3 Import CSV | ✅ |
| 4 Catégorisation | ✅ |
| 5 Dashboard | ✅ |
| 6 Transactions Power User | ✅ |
| 7 Budget Tracking | ✅ |
| 8 Frontend Next.js | 🚧 en cours |
