# 📤 Instructions d'upload des fichiers de planification Étape 5

## ⚠️ Situation actuelle

Le token GitHub utilisé dans le sandbox a des permissions en **lecture seule**. Il n'est pas possible de pusher directement depuis cet environnement.

## ✅ Fichiers prêts à uploader

Les 3 fichiers de documentation sont disponibles dans `/home/user/webapp/` :

| Fichier | Taille | Description |
|---------|--------|-------------|
| `PLAN_ETAPE_5.md` | 23 KB | Plan d'implémentation détaillé avec 11 tâches |
| `ETAPE_5_API_EXAMPLES.md` | 12 KB | Exemples d'API et scénarios de test |
| `ETAPE_5_TECHNICAL_NOTES.md` | 14 KB | Notes techniques et bonnes pratiques |

## 🚀 Méthode recommandée : GitHub Web UI

### Étape 1 : Créer la branche

1. Allez sur https://github.com/chleo-consulting/bankpulse
2. Cliquez sur le dropdown "master" (en haut à gauche)
3. Tapez : `docs/etape-5-planning`
4. Cliquez sur "Create branch: docs/etape-5-planning from master"

### Étape 2 : Uploader les fichiers

1. Assurez-vous d'être sur la branche `docs/etape-5-planning`
2. Cliquez sur "Add file" → "Upload files"
3. Glissez-déposez les 3 fichiers `.md` depuis votre ordinateur
4. Commit message : 
   ```
   docs: Add comprehensive planning documentation for Step 5 (Dashboard)
   ```
5. Extended description :
   ```
   - PLAN_ETAPE_5.md: Detailed implementation plan with tasks breakdown
   - ETAPE_5_API_EXAMPLES.md: API endpoint examples and test scenarios
   - ETAPE_5_TECHNICAL_NOTES.md: Technical considerations and best practices
   
   Step 5 will implement:
   - GET /dashboard/summary (consolidated balance + M/M-1 comparison)
   - GET /dashboard/categories-breakdown (spending by category)
   - GET /dashboard/top-merchants (top 5 merchants)
   - GET /dashboard/recurring (recurring subscriptions)
   
   Estimated timeline: 14 hours
   Target performance: p95 < 300ms
   Test coverage target: ≥ 70%
   ```
6. Cliquez sur "Commit changes"

### Étape 3 : Créer la Pull Request

1. GitHub affichera automatiquement un bandeau "Compare & pull request"
2. Cliquez dessus
3. Titre : `📋 Documentation: Step 5 Planning (Dashboard API)`
4. Description : (voir modèle complet ci-dessous)
5. Assignez-vous la PR si nécessaire
6. Labels suggérés : `documentation`, `planning`, `step-5`
7. Cliquez sur "Create pull request"

## 📝 Modèle de description de Pull Request

```markdown
## 📊 Planification complète de l'Étape 5 : Dashboard Principal

Cette PR ajoute la documentation de planification détaillée pour l'implémentation de l'étape 5 du MVP BankPulse.

### 📋 Documents ajoutés

#### PLAN_ETAPE_5.md (23 KB)
- Décomposition en 11 tâches avec priorités (P0/P1)
- Architecture technique détaillée (API, Service, Models)
- Timeline estimée : 14 heures
- Checklist Definition of Done
- Dépendances et packages requis
- Matrice de risques et mitigation

#### ETAPE_5_API_EXAMPLES.md (12 KB)
- Exemples de requêtes/réponses JSON pour chaque endpoint
- Cas limites et edge cases documentés
- 3 scénarios de test end-to-end
- Gestion des erreurs (401, 422)
- Commandes curl pour tests manuels rapides

#### ETAPE_5_TECHNICAL_NOTES.md (14 KB)
- Gestion critique des décimaux (Decimal → string)
- Formule de calcul du delta pourcentage avec tests
- Optimisation SQL (agrégations natives, index, N+1 queries)
- Calcul de `next_expected` pour abonnements récurrents
- Tests de performance et benchmarks
- Checklist pre-commit et commandes utiles

### 🎯 Objectif de l'étape 5

Fournir une **vue synthétique de la situation financière en < 30 secondes** via 4 endpoints REST :

1. **GET /api/v1/dashboard/summary**
   - Solde consolidé multi-comptes
   - Comparaison dépenses M vs M-1 avec delta %

2. **GET /api/v1/dashboard/categories-breakdown?month=YYYY-MM**
   - Répartition des dépenses par catégorie
   - Données pour donut chart frontend

3. **GET /api/v1/dashboard/top-merchants?month=YYYY-MM&limit=5**
   - Top 5 marchands par montant dépensé
   - Filtrable par mois et limite configurable

4. **GET /api/v1/dashboard/recurring**
   - Abonnements récurrents détectés
   - Calcul automatique de la prochaine échéance

### 📁 Fichiers à créer (implémentation)

```
schemas/dashboard.py              # Schémas Pydantic (5 modèles)
services/dashboard_service.py     # Logique métier (6 fonctions)
api/v1/dashboard_router.py        # Endpoints REST (4 routes)
tests/test_dashboard_service.py   # Tests unitaires
tests/test_dashboard_api.py       # Tests d'intégration
```

### ⚡ Objectifs de performance

- **p95 < 300ms** sur `/dashboard/summary`
- Agrégations SQL optimisées (pas de boucles Python)
- **Coverage ≥ 70%** sur le service layer

### 🔑 Points techniques critiques

1. **Décimaux** : Utiliser `Decimal` backend → `string` JSON
2. **Division par zéro** : Gérer le cas `previous = 0` (delta = 0)
3. **Filtrage temporel** : `start_date` inclusif, `end_date` exclusif
4. **SQL natif** : Agrégations avec `func.sum()`, `GROUP BY`
5. **Performance** : Éviter les N+1 queries avec jointures

### 📦 Type de changement

- [x] Documentation
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change

### ✅ Checklist

- [x] Documentation technique complète et détaillée
- [x] Exemples d'API documentés avec cas limites
- [x] Notes d'implémentation rédigées
- [x] Timeline estimée avec décomposition des tâches
- [x] Definition of Done définie
- [x] Risques identifiés et mitigés
- [x] Structure de réponse API cohérente
- [x] Tests de performance définis

### 🔗 Références

- SPEC_MVP.md — Étape 5 (lignes 185-222)
- Étapes précédentes : Infrastructure (1), Auth (2), Import CSV (3), Catégorisation (4)

### 👥 Reviewers

- [ ] @technical-lead — Review architecture et performance
- [ ] @backend-dev — Review implémentation SQL
- [ ] @product-owner — Review user stories

---

**Note** : Cette PR contient uniquement la documentation de planification. L'implémentation suivra dans des PRs séparées selon le plan.
```

## 🔄 Méthode alternative : Git local

Si vous avez un accès local au repository :

```bash
# 1. Cloner (si pas déjà fait)
git clone https://github.com/chleo-consulting/bankpulse.git
cd bankpulse

# 2. Créer la branche
git checkout -b docs/etape-5-planning

# 3. Télécharger les fichiers depuis le sandbox
# (utiliser scp, rsync, ou copier manuellement)

# 4. Commit et push
git add PLAN_ETAPE_5.md ETAPE_5_API_EXAMPLES.md ETAPE_5_TECHNICAL_NOTES.md
git commit -m "docs: Add comprehensive planning documentation for Step 5 (Dashboard)"
git push origin docs/etape-5-planning

# 5. Créer la PR sur GitHub
```

## 📦 Fichier patch disponible

Un fichier patch Git a été créé pour faciliter l'application des changements :

**Localisation** : `/tmp/etape5-planning.patch` (52 KB)

**Utilisation** :
```bash
cd /path/to/bankpulse
git am < /tmp/etape5-planning.patch
```

## ✅ Validation post-upload

Après avoir uploadé les fichiers, vérifiez que :

- [ ] Les 3 fichiers `.md` sont présents dans la branche `docs/etape-5-planning`
- [ ] La PR est créée avec le bon titre et la bonne description
- [ ] Les labels sont appliqués (`documentation`, `planning`)
- [ ] Les reviewers sont assignés si nécessaire
- [ ] Les fichiers s'affichent correctement dans le preview GitHub

## 🎯 Prochaines étapes

Une fois la PR mergée :

1. L'équipe peut commencer l'implémentation selon le plan
2. Créer des issues/tickets pour chacune des 11 tâches
3. Suivre la progression via le todo list intégré
4. Référencer le plan dans les PRs d'implémentation

---

**Créé le** : 25 février 2026  
**Commit local** : 61a2a31  
**Branche locale** : docs/etape-5-planning
