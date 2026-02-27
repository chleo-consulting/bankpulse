# Architecture Backend

## Schéma de données (v2 — référence)

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

## Roadmap d'implémentation (SPEC_BACKEND.md)

8 étapes ordonnées avec dépendances :
1. **Infra** — Docker Compose, Alembic migrations, ruff/black
2. **Auth** — JWT + bcrypt, `/auth/register|login|refresh`
3. **Comptes & Import CSV** — CRUD accounts, parser CSV (Boursorama, CA, BNP), déduplication par hash
4. **Catégorisation** — seed catégories, moteur RegExp merchant→category, re-catégorisation manuelle
5. **Dashboard** — endpoints agrégation (`/dashboard/summary|categories-breakdown|top-merchants|recurring`)
6. **Transactions (Power User)** — pagination cursor-based, filtres multicritères, bulk-tag, export CSV
7. **Budget Tracking** — CRUD budgets, progression temps réel, alertes over/near limit
8. **Frontend Next.js** — assemblage des composants UI

## Décisions architecturales

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

## Definition of Done par étape

Chaque étape requiert : endpoints documentés (OpenAPI auto FastAPI), tests unitaires (≥ 70% coverage), tests d'intégration, migration Alembic versionnée et réversible.
