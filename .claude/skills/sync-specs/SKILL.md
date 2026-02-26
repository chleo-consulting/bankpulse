---
name: sync-specs
description: "Met à jour les PRD et specifications SPEC.md, SPEC_BACKEND.md et SPEC_UI.md en les synchronisant avec le codebase existant : marque les étapes livrées, répond aux questions ouvertes, et aligne l'architecture documentée avec le code réel. À utiliser après chaque étape de développement complétée."
user-invocable: true
---

# Sync Specs — Mise à jour des specifications depuis le codebase

## Objectif

Synchroniser `SPEC.md`, `SPEC_BACKEND.md` et `SPEC_UI.md` avec l'état réel du codebase :
- Marquer les étapes livrées (✅)
- Répondre aux questions ouvertes à partir du code/config
- Aligner la section architecture avec les dépendances et conventions réelles
- Mettre à jour la date et le statut global

## Workflow

### Étape 1 — Lire le contexte actuel des specs

Lire les deux fichiers de spec en entier :
- `SPEC.md`
- `SPEC_BACKEND.md`

Identifier :
- Le statut global (ligne `**Statut**`)
- Quelles étapes sont déjà marquées ✅ LIVRÉE
- Quelles questions ouvertes subsistent

### Étape 2 — Scanner le codebase

Exécuter les analyses suivantes **en parallèle** pour extraire les faits réels :

#### 2a. Infrastructure & configuration
```bash
# Version PostgreSQL utilisée
grep -r "postgres:" docker-compose.yml

# Gestionnaire de packages + version Python
cat pyproject.toml

# Dépendances installées (liste complète)
uv pip list 2>/dev/null || grep -A 999 '\[project\]' pyproject.toml | grep dependencies -A 999
```

#### 2b. Endpoints API implémentés
```bash
# Lister les fichiers de routes
find api/ -name "*.py" | sort

# Extraire les decorateurs de routes (@router.get, @router.post, etc.)
grep -rn "@router\.\(get\|post\|put\|patch\|delete\)" api/ --include="*.py"
```

#### 2c. Modèles de données
```bash
# Lister les modèles SQLAlchemy définis
grep -n "^class " model/models.py
```

#### 2d. Migrations Alembic
```bash
# Lister les migrations versionnées
ls -la alembic/versions/
```

#### 2e. Tests et couverture
```bash
# Lancer les tests avec coverage pour obtenir le taux réel
uv run pytest --tb=no -q --co 2>/dev/null | tail -5
uv run pytest --tb=no -q 2>&1 | tail -10
```

#### 2f. Linting configuré
```bash
# Vérifier la config ruff + black
grep -A5 "\[tool.ruff\]" pyproject.toml
grep -A5 "\[tool.black\]" pyproject.toml
```

### Étape 3 — Déterminer le statut de chaque étape

Pour chaque étape du SPEC_BACKEND.md, vérifier si elle est **livrée** selon ces critères (Definition of Done) :

| Étape | Critères de vérification |
|-------|--------------------------|
| **Étape 1** | `docker-compose.yml` présent, migration Alembic `head` existante, ruff + black configurés, `/health` endpoint actif |
| **Étape 2** | Fichiers `api/v1/auth.py` (ou équivalent), routes `/auth/register`, `/auth/login`, `/auth/refresh`, modèle `User`, bcrypt dans les deps |
| **Étape 3** | Routes `/accounts` (CRUD), route `/accounts/{id}/import`, parser CSV présent |
| **Étape 4** | Route `/categories`, seed categories, moteur RegExp, route `PATCH /transactions/{id}/category` |
| **Étape 5** | Routes `/dashboard/summary`, `/dashboard/categories-breakdown`, `/dashboard/top-merchants`, `/dashboard/recurring` |
| **Étape 6** | Route `GET /transactions` avec pagination cursor, route `GET /transactions/export`, routes tags |
| **Étape 7** | Routes `/budgets` (CRUD), route `/budgets/progress` |
| **Étape 8** | Répertoire `frontend/` ou `app/` présent avec pages Next.js |

Une étape est **LIVRÉE** si tous ses critères P0 sont satisfaits.
Une étape est **EN COURS** si elle a des fichiers/routes partiels.

### Étape 4 — Mettre à jour SPEC_BACKEND.md

Modifications à appliquer dans l'ordre :

#### 4a. Ligne de statut global
```
**Statut** : En cours (Étape N livrée) | **Date** : <date du jour> | **Stack** : ...
```
- Mettre à jour la date avec la date du jour
- Indiquer quelle est la dernière étape livrée

#### 4b. Titres des étapes livrées
Remplacer :
```
### Étape N — Nom de l'étape
```
Par :
```
### Étape N — Nom de l'étape ✅ LIVRÉE
```

Pour les étapes en cours :
```
### Étape N — Nom de l'étape 🚧 EN COURS
```

#### 4c. Répondre aux questions ouvertes
Pour chaque `#### Questions ouvertes` dont les réponses sont maintenant connues grâce au code :
- Barrer la question avec `~~question~~`
- Ajouter la réponse concrète : `→ **Réponse** (source : fichier ou commande)`

Exemple :
```markdown
- ~~[Engineering] Utiliser Alembic ou un outil de migration alternatif ?~~ → **Alembic** retenu (migration `8ffc6c2b8a87_initial_schema` en place, réversible).
```

#### 4d. Couverture de tests
Si la couverture a été mesurée, ajouter un badge après le titre de l'étape :
```
### Étape 1 — Fondations & Infrastructure ✅ LIVRÉE
> Coverage : 97% | Migration : `8ffc6c2b8a87_initial_schema`
```

### Étape 5 — Mettre à jour SPEC.md

Vérifier et corriger la section `## Architecture` pour qu'elle corresponde exactement aux faits :
- Version Python réelle (ex: 3.12 si c'est ce qui est dans pyproject.toml)
- Gestionnaire de packages réel (uv, pip, poetry…)
- Stack frontend si démarrée
- Enlever les mentions de technologies non encore utilisées

### Étape 6 — Rapport de synchronisation

À la fin, afficher un résumé des modifications effectuées :

```
## Résumé sync-specs

### Modifications SPEC_BACKEND.md
- [✅] Étape 1 marquée LIVRÉE
- [✅] Question "PostgreSQL 15 ou 16 ?" → PostgreSQL 16 (docker-compose.yml)
- [✅] Date mise à jour : 2026-02-25

### Modifications SPEC.md
- (aucune si à jour)

### Étapes non encore livrées
- Étape 2 (Auth) — aucun fichier api/v1/auth.py trouvé
- Étape 3–8 — non démarrées

### Prochaine étape recommandée
Étape 2 : Auth JWT + bcrypt
```

## Validation obligatoire avant toute écriture

Avant d'appliquer toute modification sur `SPEC.md` ou `SPEC_BACKEND.md`, **présenter à l'utilisateur le résumé des changements prévus** et attendre sa confirmation explicite.

Format de la demande de validation :

```
## Modifications prévues — validation requise

### SPEC_BACKEND.md
1. Ligne statut : "Draft" → "En cours (Étape 1 livrée)"
2. Titre Étape 1 : ajout "✅ LIVRÉE"
3. Question PostgreSQL : barrée + réponse "PostgreSQL 16 (docker-compose.yml)"

### SPEC.md
(aucune modification prévue)

Confirmes-tu ces modifications ?
```

Ne procéder aux éditions qu'après accord explicite de l'utilisateur.

## Règles

- **Ne jamais supprimer de contenu existant** sans raison explicite — enrichir, pas remplacer
- **Ne pas inventer** des réponses aux questions ouvertes : uniquement répondre si la réponse est vérifiable dans le codebase
- **Préserver la structure** Markdown (tableaux, listes, niveaux de titres)
- **Toujours lire les fichiers avant de les modifier** pour ne pas écraser des modifications manuelles
- Si une question ouverte ne peut pas être résolue depuis le code, la **laisser telle quelle**
