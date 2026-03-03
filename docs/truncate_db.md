# Effacer les données de la DB PostgreSQL

## Option 1 — Vider toutes les tables (garder la structure)

```bash
docker compose exec db psql -U bankpulse -d bankpulse -c "TRUNCATE TABLE transactions, bank_accounts, users, tags, categories, password_reset_tokens CASCADE;"
```

## Option 2 — Supprimer et recréer la DB complète (reset total)

```bash
docker compose down db
docker volume rm bankpulse-platform_postgres_data
docker compose up -d db
uv run alembic upgrade head
```

## Option 3 — Via psql interactif

```bash
docker compose exec db psql -U bankpulse -d bankpulse
```

Puis dans le shell psql :

```sql
TRUNCATE TABLE transactions, bank_accounts, users CASCADE;
```

---

**Recommandation** : l'option 2 (suppression du volume Docker) est la plus propre pour un reset complet — elle repart de zéro avec les migrations. Le `TRUNCATE ... CASCADE` (option 1) est plus rapide si tu veux juste vider les données sans toucher à la structure.
