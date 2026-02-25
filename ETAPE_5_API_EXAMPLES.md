# Exemples de Réponses API — Étape 5 Dashboard

Ce document fournit des exemples concrets de réponses JSON pour chaque endpoint du dashboard, facilitant le développement et les tests.

---

## 1. GET /api/v1/dashboard/summary

### Request
```http
GET /api/v1/dashboard/summary HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response 200 OK
```json
{
  "total_balance": "12450.75",
  "expenses": {
    "current": "1842.50",
    "previous": "2100.00",
    "delta_pct": -12.26
  }
}
```

### Cas limite : Aucun compte
```json
{
  "total_balance": "0.00",
  "expenses": {
    "current": "0.00",
    "previous": "0.00",
    "delta_pct": 0.0
  }
}
```

### Cas limite : Premier mois d'utilisation
```json
{
  "total_balance": "5000.00",
  "expenses": {
    "current": "450.30",
    "previous": "0.00",
    "delta_pct": 0.0
  }
}
```

### Notes d'implémentation
- `delta_pct` négatif = économie (dépenses en baisse)
- `delta_pct` positif = augmentation des dépenses
- Si `previous == 0`, `delta_pct` doit être `0.0` (éviter division par zéro)
- Format des montants : string pour éviter les erreurs d'arrondi JavaScript

---

## 2. GET /api/v1/dashboard/categories-breakdown

### Request
```http
GET /api/v1/dashboard/categories-breakdown?month=2026-02 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response 200 OK
```json
{
  "month": "2026-02",
  "total_amount": "1842.50",
  "items": [
    {
      "category_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
      "category_name": "Supermarché",
      "parent_category_name": "Alimentation",
      "amount": "450.75",
      "percentage": 24.47,
      "transaction_count": 12
    },
    {
      "category_id": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
      "category_name": "Essence",
      "parent_category_name": "Transport",
      "amount": "320.00",
      "percentage": 17.37,
      "transaction_count": 8
    },
    {
      "category_id": "c3d4e5f6-a7b8-6c7d-0e1f-2a3b4c5d6e7f",
      "category_name": "Restaurants",
      "parent_category_name": "Alimentation",
      "amount": "285.50",
      "percentage": 15.50,
      "transaction_count": 9
    },
    {
      "category_id": "d4e5f6a7-b8c9-7d8e-1f2a-3b4c5d6e7f8g",
      "category_name": "Loyer",
      "parent_category_name": "Logement",
      "amount": "800.00",
      "percentage": 43.42,
      "transaction_count": 1
    }
  ]
}
```

### Cas limite : Aucune transaction dans le mois
```json
{
  "month": "2026-01",
  "total_amount": "0.00",
  "items": []
}
```

### Cas limite : Catégorie orpheline (pas de parent)
```json
{
  "month": "2026-02",
  "total_amount": "150.00",
  "items": [
    {
      "category_id": "e5f6a7b8-c9d0-8e9f-2a3b-4c5d6e7f8g9h",
      "category_name": "Divers",
      "parent_category_name": null,
      "amount": "150.00",
      "percentage": 100.0,
      "transaction_count": 3
    }
  ]
}
```

### Notes d'implémentation
- Trier par `amount` décroissant
- Limiter à top 10 ou retourner toutes si < 10
- `percentage` calculé : `(amount / total_amount) * 100`
- Filtrer uniquement les dépenses (`amount < 0`), afficher en valeur absolue
- Si `month` non fourni, utiliser le mois en cours

---

## 3. GET /api/v1/dashboard/top-merchants

### Request
```http
GET /api/v1/dashboard/top-merchants?month=2026-02&limit=5 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response 200 OK
```json
{
  "month": "2026-02",
  "items": [
    {
      "merchant_id": "f6a7b8c9-d0e1-9f0a-3b4c-5d6e7f8g9h0i",
      "merchant_name": "CARREFOUR",
      "amount": "230.50",
      "transaction_count": 5
    },
    {
      "merchant_id": "a7b8c9d0-e1f2-0a1b-4c5d-6e7f8g9h0i1j",
      "merchant_name": "TOTAL ENERGIES",
      "amount": "180.00",
      "transaction_count": 4
    },
    {
      "merchant_id": "b8c9d0e1-f2a3-1b2c-5d6e-7f8g9h0i1j2k",
      "merchant_name": "UBER EATS",
      "amount": "125.75",
      "transaction_count": 8
    },
    {
      "merchant_id": "c9d0e1f2-a3b4-2c3d-6e7f-8g9h0i1j2k3l",
      "merchant_name": "AMAZON",
      "amount": "98.30",
      "transaction_count": 3
    },
    {
      "merchant_id": "d0e1f2a3-b4c5-3d4e-7f8g-9h0i1j2k3l4m",
      "merchant_name": "NETFLIX",
      "amount": "15.99",
      "transaction_count": 1
    }
  ]
}
```

### Request avec limit personnalisé
```http
GET /api/v1/dashboard/top-merchants?month=2026-02&limit=3 HTTP/1.1
```

### Response 200 OK (top 3)
```json
{
  "month": "2026-02",
  "items": [
    {
      "merchant_id": "f6a7b8c9-d0e1-9f0a-3b4c-5d6e7f8g9h0i",
      "merchant_name": "CARREFOUR",
      "amount": "230.50",
      "transaction_count": 5
    },
    {
      "merchant_id": "a7b8c9d0-e1f2-0a1b-4c5d-6e7f8g9h0i1j",
      "merchant_name": "TOTAL ENERGIES",
      "amount": "180.00",
      "transaction_count": 4
    },
    {
      "merchant_id": "b8c9d0e1-f2a3-1b2c-5d6e-7f8g9h0i1j2k",
      "merchant_name": "UBER EATS",
      "amount": "125.75",
      "transaction_count": 8
    }
  ]
}
```

### Cas limite : Aucun marchand identifié
```json
{
  "month": "2026-02",
  "items": []
}
```

### Notes d'implémentation
- Trier par `amount` décroissant
- `limit` : min=1, max=20, défaut=5
- Filtrer les transactions avec `merchant_id IS NOT NULL`
- Filtrer uniquement les dépenses (`amount < 0`), afficher en valeur absolue
- Si `month` non fourni, utiliser le mois en cours

---

## 4. GET /api/v1/dashboard/recurring

### Request
```http
GET /api/v1/dashboard/recurring HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response 200 OK
```json
{
  "items": [
    {
      "recurring_rule_id": "e1f2a3b4-c5d6-4e5f-a7b8-c9d0e1f2a3b4",
      "merchant_id": "d0e1f2a3-b4c5-3d4e-7f8g-9h0i1j2k3l4m",
      "merchant_name": "NETFLIX",
      "expected_amount": "-15.99",
      "frequency": "monthly",
      "last_detected": "2026-02-15",
      "next_expected": "2026-03-15"
    },
    {
      "recurring_rule_id": "f2a3b4c5-d6e7-5f6a-b8c9-d0e1f2a3b4c5",
      "merchant_id": "e1f2a3b4-c5d6-4e5f-a7b8-c9d0e1f2a3b4",
      "merchant_name": "SPOTIFY",
      "expected_amount": "-9.99",
      "frequency": "monthly",
      "last_detected": "2026-02-20",
      "next_expected": "2026-03-20"
    },
    {
      "recurring_rule_id": "a3b4c5d6-e7f8-6a7b-c9d0-e1f2a3b4c5d6",
      "merchant_id": "f2a3b4c5-d6e7-5f6a-b8c9-d0e1f2a3b4c5",
      "merchant_name": "OVH",
      "expected_amount": "-12.00",
      "frequency": "monthly",
      "last_detected": "2026-02-01",
      "next_expected": "2026-03-01"
    },
    {
      "recurring_rule_id": "b4c5d6e7-f8a9-7b8c-d0e1-f2a3b4c5d6e7",
      "merchant_id": "a3b4c5d6-e7f8-6a7b-c9d0-e1f2a3b4c5d6",
      "merchant_name": "MUTUELLE",
      "expected_amount": "-85.00",
      "frequency": "monthly",
      "last_detected": "2026-02-05",
      "next_expected": "2026-03-05"
    }
  ]
}
```

### Cas limite : Abonnement annuel
```json
{
  "items": [
    {
      "recurring_rule_id": "c5d6e7f8-a9b0-8c9d-e1f2-a3b4c5d6e7f8",
      "merchant_id": "b4c5d6e7-f8a9-7b8c-d0e1-f2a3b4c5d6e7",
      "merchant_name": "APPLE ONE",
      "expected_amount": "-199.00",
      "frequency": "yearly",
      "last_detected": "2025-12-15",
      "next_expected": "2026-12-15"
    }
  ]
}
```

### Cas limite : Aucun abonnement détecté
```json
{
  "items": []
}
```

### Notes d'implémentation
- `next_expected` calculé : 
  - Si `frequency == "monthly"` : `last_detected + 1 mois`
  - Si `frequency == "yearly"` : `last_detected + 1 an`
- Trier par `next_expected` (plus proche en premier)
- Filtrer par user_id via : `recurring_rules.merchant_id → merchants → transactions → bank_accounts → users`
- `expected_amount` peut être `null` si pas encore établi
- Format date : `YYYY-MM-DD` (ISO 8601)

---

## 5. Erreurs communes

### 401 Unauthorized — Token manquant ou expiré
```json
{
  "detail": "Not authenticated"
}
```

### 422 Unprocessable Entity — Format de query param invalide
```http
GET /api/v1/dashboard/categories-breakdown?month=02-2026
```

```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["query", "month"],
      "msg": "String should match pattern '^\\d{4}-\\d{2}$'",
      "input": "02-2026"
    }
  ]
}
```

### 422 Unprocessable Entity — Limit hors limites
```http
GET /api/v1/dashboard/top-merchants?limit=50
```

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["query", "limit"],
      "msg": "Input should be less than or equal to 20",
      "input": "50"
    }
  ]
}
```

---

## 6. Scenarios de test end-to-end

### Scenario 1 : Nouvel utilisateur, aucune donnée

**Étapes** :
1. Créer un compte
2. Se connecter
3. Appeler `/dashboard/summary`

**Résultat attendu** :
```json
{
  "total_balance": "0.00",
  "expenses": {
    "current": "0.00",
    "previous": "0.00",
    "delta_pct": 0.0
  }
}
```

---

### Scenario 2 : Utilisateur avec 3 comptes et 50 transactions

**Étapes** :
1. Créer 3 comptes bancaires
2. Importer un CSV avec 50 transactions (février 2026)
3. Appeler tous les endpoints dashboard

**Résultats attendus** :
- `/dashboard/summary` : solde consolidé des 3 comptes
- `/categories-breakdown` : top 5-10 catégories
- `/top-merchants` : top 5 marchands
- `/recurring` : abonnements détectés (Netflix, Spotify, etc.)

---

### Scenario 3 : Performance avec 10 000 transactions

**Étapes** :
1. Importer un dataset de 10 000 transactions sur 2 ans
2. Appeler `/dashboard/summary` avec mesure de temps

**Critères de succès** :
- Temps de réponse < 300ms (p95)
- Pas de timeout
- Résultats corrects

---

## 7. Checklist de validation

### Fonctionnalités
- [ ] `/summary` retourne le solde consolidé correct
- [ ] `/summary` calcule correctement le delta M vs M-1
- [ ] `/categories-breakdown` agrège par catégorie
- [ ] `/categories-breakdown` respecte le filtre `?month=`
- [ ] `/top-merchants` respecte le param `?limit=`
- [ ] `/recurring` calcule correctement `next_expected`

### Sécurité
- [ ] Tous les endpoints nécessitent authentification JWT
- [ ] Impossible d'accéder aux données d'un autre utilisateur
- [ ] Validation des query params (format, limites)

### Performance
- [ ] `/summary` répond en < 300ms avec 1000 transactions
- [ ] `/categories-breakdown` répond en < 500ms avec 5000 transactions
- [ ] Pas de N+1 queries (vérifier SQLAlchemy logs)

### Documentation
- [ ] Swagger UI affiche tous les endpoints
- [ ] Exemples de réponses visibles dans Swagger
- [ ] Descriptions des query params claires

---

## 8. Commandes de test rapide

```bash
# Variables d'environnement
export API_URL="http://localhost:8000/api/v1"
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Summary
curl -H "Authorization: Bearer $TOKEN" $API_URL/dashboard/summary | jq

# Categories breakdown (mois en cours)
curl -H "Authorization: Bearer $TOKEN" $API_URL/dashboard/categories-breakdown | jq

# Categories breakdown (février 2026)
curl -H "Authorization: Bearer $TOKEN" "$API_URL/dashboard/categories-breakdown?month=2026-02" | jq

# Top 3 marchands
curl -H "Authorization: Bearer $TOKEN" "$API_URL/dashboard/top-merchants?limit=3" | jq

# Abonnements récurrents
curl -H "Authorization: Bearer $TOKEN" $API_URL/dashboard/recurring | jq

# Test performance (10 fois)
for i in {1..10}; do
  time curl -s -H "Authorization: Bearer $TOKEN" $API_URL/dashboard/summary > /dev/null
done
```

---

**Référence** : SPEC_MVP.md — Étape 5 (lignes 185-222)
