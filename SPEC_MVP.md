# PRD — BankPulse Phase 1 MVP : Étapes de développement

**Statut** : En cours (Étape 2 livrée) | **Date** : 25 février 2026 | **Stack** : FastAPI · SQLAlchemy 2.0 · PostgreSQL 16 · Next.js · shadcn/ui · TailwindCSS

---

## 1. Problème à résoudre

Les utilisateurs (Young Professionals, Power Users, Freelances) n'ont aucun moyen simple d'avoir une lecture instantanée et consolidée de leur situation financière à partir de leurs relevés bancaires. Ils perdent du temps à analyser manuellement des exports CSV, sans catégorisation, sans suivi de budget, sans vue comparative.

---

## 2. Objectifs du MVP

| # | Objectif | Indicateur de succès |
|---|----------|----------------------|
| U1 | L'utilisateur comprend sa situation en < 30s après connexion | Dashboard chargé en < 300ms, solde visible immédiatement |
| U2 | 80% des transactions sont catégorisées automatiquement | Taux de catégorisation auto mesuré après import |
| U3 | L'utilisateur peut corriger une catégorie en 1 clic | Taux de re-catégorisation manuelle > 0% (feedback loop actif) |
| B1 | Livraison itérative, chaque étape est démontrable indépendamment | Chaque step produit une API ou UI fonctionnelle testable |

---

## 3. Non-objectifs Phase 1

- Connexion bancaire temps-réel (Open Banking / PSD2) — Phase 3
- Insights IA / détection d'anomalies — Phase 2
- Mode multi-tenant / organisation — Phase 2
- Application mobile native — hors scope
- Prévision cashflow (Freelance) — Phase 2

---

## 4. Décomposition en étapes de développement

---

### Étape 1 — Fondations & Infrastructure ✅ LIVRÉE

> Coverage : 97% | Migration : `8ffc6c2b8a87_initial_schema`

**Objectif** : Avoir un environnement de développement reproductible et une base de données opérationnelle.

#### User Stories

- En tant que développeur, je veux un environnement Docker (API + DB) opérationnel en une commande pour ne pas perdre de temps en setup.
- En tant que développeur, je veux que les migrations de schéma soient versionnées pour pouvoir reproduire l'environnement en CI.

#### Requirements P0

| Req | Description | Critères d'acceptation |
|-----|-------------|------------------------|
| R1.1 | Structure projet FastAPI avec routing modulaire | `uvicorn main:app` démarre, `/health` renvoie 200 |
| R1.2 | Docker Compose : API + PostgreSQL | `docker compose up` → API joignable sur localhost:8000 |
| R1.3 | SQLAlchemy 2.0 + Alembic : migrations des entités v2 | `alembic upgrade head` crée toutes les tables du DDL v2 |
| R1.4 | Configuration via `.env` (DB URL, secret key) | Aucune valeur hardcodée dans le code |
| R1.5 | Linting + formatter configurés (ruff, black) | CI bloque si lint échoue |

#### Tables créées

`users`, `organizations`, `bank_accounts`, `merchants`, `categories`, `transactions`, `tags`, `transaction_tags`, `budgets`, `recurring_rules`, `audit_logs`

#### Questions ouvertes

- ~~[Engineering] Utiliser Alembic ou un outil de migration alternatif ?~~ → **Alembic** retenu (migration initiale `8ffc6c2b8a87_initial_schema` en place, réversible).
- ~~[Engineering] PostgreSQL 15 ou 16 ?~~ → **PostgreSQL 16** (image `postgres:16-alpine` dans Docker Compose).

---

### Étape 2 — Authentification (Auth API) ✅ LIVRÉE

> Coverage : 93% | Endpoints : `/auth/register` · `/auth/login` · `/auth/refresh` · `/auth/logout`

**Objectif** : Un utilisateur peut s'inscrire, se connecter, et ses requêtes sont sécurisées par JWT.

#### User Stories

- En tant que nouvel utilisateur, je veux créer un compte avec email + mot de passe pour accéder à l'application.
- En tant qu'utilisateur existant, je veux me connecter et recevoir un token JWT pour ne pas ressaisir mes credentials à chaque requête.
- En tant qu'utilisateur connecté, je veux que toutes les routes soient protégées pour que mes données restent privées.

#### Requirements P0

| Req | Description | Critères d'acceptation |
|-----|-------------|------------------------|
| R2.1 | `POST /auth/register` — création compte | Renvoie 201 + user_id ; email unique vérifié |
| R2.2 | `POST /auth/login` — authentification | Renvoie access_token (JWT, exp 24h) + refresh_token |
| R2.3 | Middleware JWT sur toutes les routes `/api/*` | 401 si token absent ou expiré |
| R2.4 | Mot de passe hashé avec bcrypt | Aucun mot de passe en clair en base |
| R2.5 | `POST /auth/refresh` — renouvellement token | Nouveau access_token sans re-login |
| R2.6 | Toutes les actions utilisateur loguées dans `audit_logs` | LOGIN enregistré avec ip_address et user_agent |

#### Requirements P1

- `POST /auth/logout` — invalidation du refresh token
- Rate limiting sur `/auth/login` (5 tentatives / minute)

#### Questions ouvertes

- ~~[Engineering] Stocker les refresh tokens en DB ou Redis ?~~ → **Stateless JWT** (refresh tokens signés, pas de stockage en MVP — révocation à implémenter en Phase 2 si besoin).

---

### Étape 3 — Gestion des Comptes Bancaires & Import CSV

**Objectif** : L'utilisateur peut déclarer ses comptes et importer ses transactions depuis un export CSV bancaire.

#### User Stories

- En tant qu'utilisateur, je veux ajouter un compte bancaire (nom, IBAN, type) pour organiser mes transactions par compte.
- En tant qu'utilisateur, je veux importer un fichier CSV d'export bancaire pour ne pas saisir mes transactions manuellement.
- En tant qu'utilisateur, je veux voir la liste de mes transactions après import pour vérifier que l'import s'est bien passé.
- En tant qu'utilisateur, je veux importer un fichier CSV d'export bancaire au format Boursorama et le convertir selon le modèle de l'application, sans avoir à déclarer mes comptes manuellement au préalable.

#### Requirements P0

| Req | Description | Critères d'acceptation |
|-----|-------------|------------------------|
| R3.1 | `GET/POST/PATCH/DELETE /accounts` — CRUD comptes | Soft delete ; comptes filtrés par user_id |
| R3.2 | `POST /accounts/{id}/import` — upload CSV | Accepte fichiers CSV jusqu'à 10 Mo |
| R3.3 | Parser CSV flexible (date, montant, description, IBAN) | Support formats : Boursorama (livré), Crédit Agricole, BNP (Phase suivante). Format Boursorama : parser dédié `parsers/boursorama.py` |
| R3.4 | Déduplication à l'import | Transaction déjà importée ignorée via `import_hash` (SHA-256 : `dateOp\|accountNum\|amount\|label`) stocké dans `transactions.import_hash` |
| R3.5 | Normalisation marchands | `supplierFound` → `merchant.normalized_name` via upsert |
| R3.6 | Mise à jour solde du compte après import | `bank_accounts.balance` = dernière valeur non-vide de `accountbalance` dans le CSV |
| R3.7 | `POST /api/v1/import/boursorama` — upload CSV global multi-comptes | Accepte multipart/form-data ; détecte N comptes automatiquement ; crée les comptes manquants |
| R3.8 | Module de transformation `parsers/boursorama.py` | Mappe les 12 colonnes CSV → BankAccount + Transaction + Merchant ; testé unitairement (sans DB) |
| R3.9 | Déduplication par `import_hash` (colonne `transactions.import_hash`) | SHA-256(dateOp + accountNum + amount + label) ; migration Alembic `b3e9f1a2c456` |

#### Requirements P1

- Rapport d'import : nb lignes traitées, erreurs, doublons ignorés *(inclus dans `ImportResult` — livré)*
- Support format OFX / QIF

#### Schéma de données impliqué

`bank_accounts`, `transactions`, `merchants`, `audit_logs`

#### Migration

`b3e9f1a2c456_add_import_hash_to_transactions` — ajout de `transactions.import_hash VARCHAR(64) UNIQUE NULL`

#### Questions ouvertes

- ~~[Product] Quels formats CSV bancaires prioriser pour la v1 ?~~ → **Boursorama** (format réel analysé, parser livré). Crédit Agricole et BNP en Phase suivante via l'ABC `AbstractCsvParser`.
- ~~[Engineering] Upload direct S3 ou stockage temporaire serveur ?~~ → **Pas de stockage** : le fichier est parsé en mémoire, seul le résultat est persisté en base.

---

### Étape 4 — Catégorisation des Transactions

**Objectif** : Chaque transaction est automatiquement catégorisée, et l'utilisateur peut corriger la catégorie.

#### User Stories

- En tant qu'utilisateur, je veux que mes transactions soient catégorisées automatiquement après import pour ne pas le faire manuellement.
- En tant qu'utilisateur, je veux corriger la catégorie d'une transaction en un clic pour améliorer la précision.
- En tant qu'utilisateur Power User, je veux voir la liste des catégories disponibles avec leur hiérarchie pour comprendre la taxonomie.

#### Requirements P0

| Req | Description | Critères d'acceptation |
|-----|-------------|------------------------|
| R4.1 | Seed des catégories par défaut (hiérarchie 2 niveaux) | Alimentation > Supermarché, Transport > Essence, etc. |
| R4.2 | `GET /categories` — liste catégories avec parent | Retourne arbre hiérarchique |
| R4.3 | Moteur RegExp : merchant → category | Rules configurées en base, appliquées à l'import |
| R4.4 | `PATCH /transactions/{id}/category` — re-catégorisation manuelle | Mise à jour `category_id` + log dans `audit_logs` |
| R4.5 | `GET /transactions` — liste paginée avec filtres | Filtres : compte, catégorie, date de début/fin, montant min/max |

#### Requirements P1

- `POST /transactions/bulk-categorize` — re-catégorisation en masse
- Apprentissage des corrections : si l'utilisateur re-catégorise un merchant X → catégorie Y, appliquer aux futures transactions du même merchant
- `GET /transactions/search?q=` — recherche full-text sur description

#### Schéma de données impliqué

`categories`, `transactions`, `merchants`, `audit_logs`

---

### Étape 5 — Dashboard Principal

**Objectif** : L'utilisateur dispose d'une vue synthétique de sa situation financière en moins de 30 secondes.

#### User Stories

- En tant qu'utilisateur, je veux voir mon solde global consolidé sur tous mes comptes dès l'ouverture de l'app.
- En tant qu'utilisateur, je veux comparer mes dépenses du mois en cours vs le mois précédent pour savoir si je dépense plus.
- En tant qu'utilisateur, je veux voir la répartition de mes dépenses par catégorie (donut) pour identifier où va mon argent.
- En tant qu'utilisateur, je veux voir le top 5 de mes marchands du mois pour savoir chez qui je dépense le plus.
- En tant qu'utilisateur, je veux voir les abonnements récurrents détectés pour ne pas les oublier.

#### Endpoints API

| Endpoint | Description |
|----------|-------------|
| `GET /dashboard/summary` | Solde global, dépenses M vs M-1, delta % |
| `GET /dashboard/categories-breakdown?month=` | Répartition par catégorie (données donut) |
| `GET /dashboard/top-merchants?month=` | Top 5 marchands par montant |
| `GET /dashboard/recurring` | Abonnements détectés via `recurring_rules` |

#### Requirements P0

| Req | Description | Critères d'acceptation |
|-----|-------------|------------------------|
| R5.1 | Solde consolidé multi-comptes | Somme de tous `bank_accounts.balance` de l'utilisateur |
| R5.2 | Dépenses M vs M-1 avec delta | `{"current": 1842, "previous": 2100, "delta_pct": -12.3}` |
| R5.3 | Breakdown catégories | Top catégories triées par montant décroissant |
| R5.4 | Top 5 marchands | Agrégation sur `transactions.merchant_id` du mois courant |
| R5.5 | Détection abonnements | Transactions récurrentes détectées via `recurring_rules` |
| R5.6 | Temps de réponse < 300ms | Mesuré avec p95 via traces FastAPI |

#### Requirements P1

- Cache Redis sur les endpoints dashboard (TTL 5 min)
- Filtrage par compte individuel

---

### Étape 6 — Vue Transactions (Power User)

**Objectif** : L'utilisateur Power User peut explorer, filtrer, tagger et exporter ses transactions.

#### User Stories

- En tant que Power User, je veux filtrer mes transactions par date, catégorie, montant et marchand simultanément pour des analyses précises.
- En tant que Power User, je veux rechercher une transaction par texte libre pour la retrouver rapidement.
- En tant que Power User, je veux tagger plusieurs transactions en une fois pour les grouper selon mes propres critères.
- En tant que Power User, je veux exporter mes transactions en CSV pour les utiliser dans Excel ou un autre outil.
- En tant qu'utilisateur, je veux catégoriser une transaction directement depuis la liste sans ouvrir de page de détail.

#### Requirements P0

| Req | Description | Critères d'acceptation |
|-----|-------------|------------------------|
| R6.1 | `GET /transactions` avec pagination (cursor-based) | page_size par défaut : 50 |
| R6.2 | Filtres multicritères | date_from, date_to, category_id, merchant_id, amount_min, amount_max, tag_id |
| R6.3 | `GET /transactions/search?q=` | Full-text sur `description` et `merchants.name` |
| R6.4 | `POST /tags`, `GET /tags` — CRUD tags | Tags globaux par utilisateur |
| R6.5 | `POST /transactions/bulk-tag` — tag en masse | `{ "transaction_ids": [...], "tag_ids": [...] }` |
| R6.6 | `GET /transactions/export?format=csv` | CSV UTF-8 avec colonnes : date, description, montant, catégorie, tags |
| R6.7 | `PATCH /transactions/{id}/category` | Inline sans rechargement de page (déjà en Étape 4) |

#### Requirements P1

- Tri multi-colonnes (date, montant, marchand)
- Vue "transactions en attente" (`is_pending=true`)

---

### Étape 7 — Budget Tracking

**Objectif** : L'utilisateur peut définir des budgets par catégorie et suivre sa progression avec alertes.

#### User Stories

- En tant qu'utilisateur, je veux définir un budget mensuel par catégorie pour ne pas dépasser mes limites.
- En tant qu'utilisateur, je veux voir ma progression budgétaire sous forme de barre de progression pour savoir où j'en suis en cours de mois.
- En tant qu'utilisateur, je veux recevoir une alerte quand j'approche ou dépasse un budget pour réagir à temps.

#### Requirements P0

| Req | Description | Critères d'acceptation |
|-----|-------------|------------------------|
| R7.1 | `POST/GET/PATCH/DELETE /budgets` — CRUD budgets | Period type : monthly / quarterly / yearly |
| R7.2 | `GET /budgets/progress?month=` — progression temps réel | `{"category": "Alimentation", "limit": 500, "spent": 320, "pct": 64}` |
| R7.3 | Calcul automatique du dépensé par catégorie | Agrégation sur `transactions` du mois en cours |
| R7.4 | Alerte dépassement : flag dans l'API | `"alert": "over_budget"` quand `spent > limit` |
| R7.5 | Alerte approche : flag dans l'API | `"alert": "near_limit"` quand `spent > 80% * limit` |

#### Requirements P1

- Notification email lors du dépassement
- Budget reporté sur plusieurs mois (rollover)

---

### Étape 8 — Frontend Next.js (Assemblage final)

**Objectif** : Interface utilisateur complète connectée à l'API, utilisable par un beta-testeur.

#### Composants à livrer (par étape API associée)

| Étape API | Composants UI |
|-----------|---------------|
| Étape 2 | Pages Login / Register avec validation form |
| Étape 3 | Page "Mes comptes" + modal import CSV + progress bar upload |
| Étape 4 | Page Transactions — inline category selector |
| Étape 5 | Dashboard : KPI cards, Donut chart (Recharts), Top merchants, Recurring subscriptions |
| Étape 6 | Page Transactions avancée : filtres, recherche, bulk actions, export |
| Étape 7 | Page Budgets : Progress bars par catégorie, badges d'alerte |

#### Requirements P0

| Req | Description |
|-----|-------------|
| R8.1 | Routing Next.js avec layout authentifié (redirect si non connecté) |
| R8.2 | Gestion du JWT en cookie HttpOnly |
| R8.3 | Composants shadcn/ui : Table, Card, Badge, Progress, Dialog |
| R8.4 | Recharts : DonutChart, BarChart, LineChart (préparation Phase 2) |
| R8.5 | États vides (empty states) sur chaque vue : "Aucune transaction", "Aucun budget" |
| R8.6 | Responsive : desktop first, lisible sur tablette |

---

## 5. Ordre de livraison recommandé & dépendances

```
Étape 1 (Infra)
    └── Étape 2 (Auth)
            ├── Étape 3 (Comptes & Import CSV)
            │       └── Étape 4 (Catégorisation)
            │               ├── Étape 5 (Dashboard)
            │               ├── Étape 6 (Transactions)
            │               └── Étape 7 (Budgets)
            │
            └── Étape 8 (Frontend)
                (peut démarrer en parallèle dès Étape 2)
```

---

## 6. Métriques de succès Phase 1

| Métrique | Cible à 30 jours post-lancement |
|----------|----------------------------------|
| Taux de catégorisation automatique | ≥ 80% des transactions importées |
| Temps de chargement dashboard | P95 < 300ms |
| Taux de complétion de l'onboarding (import 1er fichier CSV) | ≥ 60% des inscrits |
| Utilisateurs ayant créé ≥ 1 budget | ≥ 30% des utilisateurs actifs |
| Retention J7 | ≥ 40% |

---

## 7. Questions ouvertes bloquantes

| # | Question | Propriétaire | Étape impactée |
|---|----------|-------------|----------------|
| Q1 | Quels formats CSV bancaires prioriser ? (Boursorama, CA, BNP, LCL…) | Product | Étape 3 |
| Q2 | Taxonomie initiale des catégories (nombres, noms, icônes) | Product / UX | Étape 4 |
| Q3 | Où stocker les fichiers CSV uploadés : S3 ou temporaire serveur ? | Engineering | Étape 3 |
| Q4 | Notifications budget : email ou in-app uniquement en MVP ? | Product | Étape 7 |

---

## 8. Definition of Done par étape

Chaque étape est considérée **livrée** quand :

- [ ] Endpoints API documentés (OpenAPI / Swagger auto-généré par FastAPI)
- [ ] Tests unitaires sur la logique métier (coverage ≥ 70%)
- [ ] Tests d'intégration sur les endpoints principaux
- [ ] Migration Alembic versionnée et réversible
- [ ] Déployable en un `docker compose up`
