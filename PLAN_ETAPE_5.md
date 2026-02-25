# Plan d'implémentation — Étape 5 : Dashboard Principal

**Date** : 25 février 2026  
**Objectif** : L'utilisateur dispose d'une vue synthétique de sa situation financière en moins de 30 secondes  
**Prérequis** : Étapes 1-4 complétées ✅

---

## Vue d'ensemble

L'étape 5 consiste à créer une API de dashboard qui agrège les données financières de l'utilisateur pour fournir une vue consolidée et des indicateurs clés en temps réel.

### User Stories ciblées

1. **Vue solde consolidé** : Voir le solde global sur tous les comptes dès l'ouverture
2. **Comparaison mensuelle** : Comparer les dépenses M vs M-1 avec delta %
3. **Répartition par catégorie** : Visualiser la répartition des dépenses (donut chart)
4. **Top marchands** : Identifier les 5 principaux marchands du mois
5. **Abonnements récurrents** : Suivre les abonnements détectés automatiquement

---

## Architecture technique

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
│  /api/v1/dashboard/dashboard_router.py                      │
│    ├─ GET /dashboard/summary                                │
│    ├─ GET /dashboard/categories-breakdown?month=YYYY-MM     │
│    ├─ GET /dashboard/top-merchants?month=YYYY-MM            │
│    └─ GET /dashboard/recurring                              │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Service Layer (Business Logic)                 │
│  services/dashboard_service.py                              │
│    ├─ get_consolidated_balance(user_id)                     │
│    ├─ get_monthly_comparison(user_id, current, previous)    │
│    ├─ get_categories_breakdown(user_id, month)              │
│    ├─ get_top_merchants(user_id, month, limit=5)            │
│    └─ get_recurring_subscriptions(user_id)                  │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer (Models)                     │
│  model/models.py (existing)                                 │
│    ├─ User                                                  │
│    ├─ BankAccount → balance                                 │
│    ├─ Transaction → amount, transaction_date                │
│    ├─ Category                                              │
│    ├─ Merchant                                              │
│    └─ RecurringRule                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Décomposition des tâches

### 🔴 Tâche 1 : Schémas Pydantic (schemas/dashboard.py)

**Fichier** : `schemas/dashboard.py`

**Objectif** : Définir les structures de réponse pour chaque endpoint du dashboard.

#### Schémas à créer

```python
# Summary
class MonthlySummary(BaseModel):
    current: Decimal
    previous: Decimal
    delta_pct: float

class DashboardSummary(BaseModel):
    total_balance: Decimal
    expenses: MonthlySummary

# Categories breakdown
class CategoryBreakdownItem(BaseModel):
    category_id: UUID
    category_name: str
    parent_category_name: str | None
    amount: Decimal
    percentage: float
    transaction_count: int

class CategoriesBreakdown(BaseModel):
    month: str  # YYYY-MM
    items: list[CategoryBreakdownItem]
    total_amount: Decimal

# Top merchants
class TopMerchantItem(BaseModel):
    merchant_id: UUID
    merchant_name: str
    amount: Decimal
    transaction_count: int

class TopMerchants(BaseModel):
    month: str  # YYYY-MM
    items: list[TopMerchantItem]

# Recurring subscriptions
class RecurringSubscription(BaseModel):
    recurring_rule_id: UUID
    merchant_id: UUID
    merchant_name: str
    expected_amount: Decimal | None
    frequency: str  # monthly | yearly
    last_detected: date | None
    next_expected: date | None  # calculé

class RecurringSubscriptions(BaseModel):
    items: list[RecurringSubscription]
```

**Critères d'acceptation** :
- ✅ Tous les champs sont typés strictement
- ✅ Validation Pydantic activée
- ✅ Documentation docstring sur chaque classe
- ✅ Utilisation de Decimal pour les montants

---

### 🔴 Tâche 2 : Service Layer (services/dashboard_service.py)

**Fichier** : `services/dashboard_service.py`

**Objectif** : Implémenter la logique métier pour tous les calculs d'agrégation.

#### Fonctions à implémenter

##### 2.1 `get_consolidated_balance(db: Session, user_id: UUID) -> Decimal`

```python
def get_consolidated_balance(db: Session, user_id: UUID) -> Decimal:
    """
    Calcule le solde consolidé de tous les comptes actifs de l'utilisateur.
    
    Requête SQL :
        SELECT SUM(balance) FROM bank_accounts 
        WHERE user_id = ? AND deleted_at IS NULL
    """
    pass
```

**Critères** :
- Ignorer les comptes soft-deleted
- Retourner Decimal(0) si aucun compte
- Tester avec 0, 1, N comptes

---

##### 2.2 `get_monthly_expenses(db: Session, user_id: UUID, month: date) -> Decimal`

```python
def get_monthly_expenses(db: Session, user_id: UUID, month: date) -> Decimal:
    """
    Calcule le total des dépenses (amount < 0) pour un mois donné.
    
    Requête SQL :
        SELECT SUM(amount) FROM transactions
        WHERE account_id IN (user's accounts)
          AND transaction_date >= '2026-02-01'
          AND transaction_date < '2026-03-01'
          AND amount < 0
    """
    pass
```

**Critères** :
- Filtrer uniquement les dépenses (montant négatif)
- Retourner la valeur absolue
- Gérer les mois sans transactions

---

##### 2.3 `get_monthly_comparison(db: Session, user_id: UUID) -> dict`

```python
def get_monthly_comparison(db: Session, user_id: UUID) -> dict:
    """
    Compare les dépenses du mois en cours vs mois précédent.
    
    Returns:
        {
            "current": Decimal("1842.50"),
            "previous": Decimal("2100.00"),
            "delta_pct": -12.3
        }
    """
    today = date.today()
    current_month = date(today.year, today.month, 1)
    previous_month = current_month - relativedelta(months=1)
    
    current_expenses = get_monthly_expenses(db, user_id, current_month)
    previous_expenses = get_monthly_expenses(db, user_id, previous_month)
    
    delta_pct = calculate_percentage_change(previous_expenses, current_expenses)
    
    return {
        "current": current_expenses,
        "previous": previous_expenses,
        "delta_pct": delta_pct
    }
```

**Critères** :
- Delta négatif = économie, positif = dépense supplémentaire
- Gérer division par zéro (previous = 0)
- Utiliser `dateutil.relativedelta` pour le calcul de mois

---

##### 2.4 `get_categories_breakdown(db: Session, user_id: UUID, month: str | None) -> list[dict]`

```python
def get_categories_breakdown(
    db: Session, 
    user_id: UUID, 
    month: str | None = None
) -> list[dict]:
    """
    Agrège les dépenses par catégorie pour un mois donné.
    
    Args:
        month: Format YYYY-MM (ex: "2026-02")
    
    Returns:
        [
            {
                "category_id": UUID,
                "category_name": "Supermarché",
                "parent_category_name": "Alimentation",
                "amount": Decimal("450.00"),
                "percentage": 24.5,
                "transaction_count": 12
            },
            ...
        ]
        Trié par montant décroissant
    """
    # Si month is None, utiliser le mois en cours
    if month is None:
        month = date.today().strftime("%Y-%m")
    
    # Parse month string
    year, month_num = map(int, month.split("-"))
    
    # Requête SQL avec JOIN sur categories
    # GROUP BY category_id
    # ORDER BY SUM(amount) DESC
    pass
```

**Critères** :
- Inclure nom de la catégorie parent
- Calculer pourcentage par rapport au total
- Filtrer les dépenses (amount < 0)
- Top 10 catégories maximum (ou toutes si < 10)

---

##### 2.5 `get_top_merchants(db: Session, user_id: UUID, month: str | None, limit: int = 5) -> list[dict]`

```python
def get_top_merchants(
    db: Session, 
    user_id: UUID, 
    month: str | None = None,
    limit: int = 5
) -> list[dict]:
    """
    Top N marchands par montant dépensé.
    
    Returns:
        [
            {
                "merchant_id": UUID,
                "merchant_name": "Carrefour",
                "amount": Decimal("230.50"),
                "transaction_count": 5
            },
            ...
        ]
    """
    # Requête SQL avec JOIN sur merchants
    # GROUP BY merchant_id
    # ORDER BY SUM(amount) DESC
    # LIMIT N
    pass
```

**Critères** :
- Filtrer les dépenses (amount < 0)
- Ignorer les transactions sans merchant_id (NULL)
- Paramètre limit configurable (défaut 5)

---

##### 2.6 `get_recurring_subscriptions(db: Session, user_id: UUID) -> list[dict]`

```python
def get_recurring_subscriptions(db: Session, user_id: UUID) -> list[dict]:
    """
    Liste les abonnements récurrents détectés pour l'utilisateur.
    
    Returns:
        [
            {
                "recurring_rule_id": UUID,
                "merchant_id": UUID,
                "merchant_name": "Netflix",
                "expected_amount": Decimal("-15.99"),
                "frequency": "monthly",
                "last_detected": date(2026, 2, 15),
                "next_expected": date(2026, 3, 15)  # calculé
            },
            ...
        ]
    """
    # Requête sur recurring_rules avec JOIN merchants
    # Calcul de next_expected basé sur frequency et last_detected
    pass
```

**Critères** :
- Calculer `next_expected` : last_detected + frequency
- Filtrer par user_id via transactions → accounts
- Ordonner par next_expected (plus proche en premier)

---

### 🔴 Tâche 3-6 : Endpoints API (api/v1/dashboard_router.py)

**Fichier** : `api/v1/dashboard_router.py`

#### 3.1 GET /dashboard/summary

```python
@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardSummary:
    """
    Retourne le résumé du dashboard : solde consolidé + comparaison mensuelle.
    
    Response:
        {
            "total_balance": 12450.75,
            "expenses": {
                "current": 1842.50,
                "previous": 2100.00,
                "delta_pct": -12.3
            }
        }
    """
    balance = dashboard_service.get_consolidated_balance(db, current_user.id)
    comparison = dashboard_service.get_monthly_comparison(db, current_user.id)
    
    return DashboardSummary(
        total_balance=balance,
        expenses=MonthlySummary(**comparison)
    )
```

---

#### 3.2 GET /dashboard/categories-breakdown

```python
@router.get("/categories-breakdown", response_model=CategoriesBreakdown)
def get_categories_breakdown(
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoriesBreakdown:
    """
    Répartition des dépenses par catégorie.
    
    Query params:
        - month: YYYY-MM (défaut: mois en cours)
    """
    items = dashboard_service.get_categories_breakdown(db, current_user.id, month)
    total = sum(item["amount"] for item in items)
    
    return CategoriesBreakdown(
        month=month or date.today().strftime("%Y-%m"),
        items=[CategoryBreakdownItem(**item) for item in items],
        total_amount=total
    )
```

---

#### 3.3 GET /dashboard/top-merchants

```python
@router.get("/top-merchants", response_model=TopMerchants)
def get_top_merchants(
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TopMerchants:
    """
    Top N marchands par montant dépensé.
    
    Query params:
        - month: YYYY-MM (défaut: mois en cours)
        - limit: nombre de résultats (1-20, défaut 5)
    """
    items = dashboard_service.get_top_merchants(db, current_user.id, month, limit)
    
    return TopMerchants(
        month=month or date.today().strftime("%Y-%m"),
        items=[TopMerchantItem(**item) for item in items]
    )
```

---

#### 3.4 GET /dashboard/recurring

```python
@router.get("/recurring", response_model=RecurringSubscriptions)
def get_recurring_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecurringSubscriptions:
    """
    Liste des abonnements récurrents détectés.
    """
    items = dashboard_service.get_recurring_subscriptions(db, current_user.id)
    
    return RecurringSubscriptions(
        items=[RecurringSubscription(**item) for item in items]
    )
```

---

### 🟡 Tâche 7 : Tests unitaires (tests/test_dashboard_service.py)

**Fichier** : `tests/test_dashboard_service.py`

#### Structure des tests

```python
import pytest
from datetime import date
from decimal import Decimal
from uuid import uuid4

from services import dashboard_service
from model.models import User, BankAccount, Transaction, Merchant, Category

@pytest.fixture
def sample_user(db_session):
    """Fixture créant un utilisateur de test."""
    user = User(email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_accounts(db_session, sample_user):
    """Fixture créant 2 comptes avec soldes."""
    accounts = [
        BankAccount(user_id=sample_user.id, balance=1000.00),
        BankAccount(user_id=sample_user.id, balance=500.50),
    ]
    db_session.add_all(accounts)
    db_session.commit()
    return accounts

class TestConsolidatedBalance:
    def test_sum_multiple_accounts(self, db_session, sample_accounts):
        """Doit sommer correctement plusieurs comptes."""
        balance = dashboard_service.get_consolidated_balance(db_session, sample_accounts[0].user_id)
        assert balance == Decimal("1500.50")
    
    def test_zero_accounts(self, db_session, sample_user):
        """Doit retourner 0 si aucun compte."""
        balance = dashboard_service.get_consolidated_balance(db_session, sample_user.id)
        assert balance == Decimal("0")
    
    def test_ignores_deleted_accounts(self, db_session, sample_accounts):
        """Doit ignorer les comptes soft-deleted."""
        sample_accounts[0].deleted_at = datetime.utcnow()
        db_session.commit()
        
        balance = dashboard_service.get_consolidated_balance(db_session, sample_accounts[0].user_id)
        assert balance == Decimal("500.50")

class TestMonthlyComparison:
    def test_delta_negative_when_saving(self, db_session, sample_user, sample_accounts):
        """Delta négatif = économie."""
        # Créer transactions : M-1 = -2000, M = -1500
        # Delta doit être ≈ -25%
        pass
    
    def test_delta_positive_when_overspending(self):
        """Delta positif = dépense supplémentaire."""
        pass
    
    def test_handles_zero_previous_month(self):
        """Gérer division par zéro."""
        pass

# ... autres tests pour categories_breakdown, top_merchants, recurring
```

**Critères** :
- ✅ Coverage ≥ 70% sur dashboard_service.py
- ✅ Tests isolés (fixtures indépendantes)
- ✅ Cas limites : 0 transactions, mois incomplets, divisions par zéro

---

### 🟡 Tâche 8 : Tests d'intégration (tests/test_dashboard_api.py)

**Fichier** : `tests/test_dashboard_api.py`

```python
from fastapi.testclient import TestClient

def test_get_summary_returns_200(client: TestClient, auth_headers):
    """GET /dashboard/summary doit retourner 200."""
    response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_balance" in data
    assert "expenses" in data
    assert "current" in data["expenses"]
    assert "delta_pct" in data["expenses"]

def test_categories_breakdown_filters_by_month(client, auth_headers):
    """Doit filtrer par mois via query param."""
    response = client.get("/api/v1/dashboard/categories-breakdown?month=2026-02", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == "2026-02"

def test_top_merchants_respects_limit(client, auth_headers):
    """Limit param doit limiter les résultats."""
    response = client.get("/api/v1/dashboard/top-merchants?limit=3", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 3

def test_dashboard_requires_auth(client):
    """Tous les endpoints doivent nécessiter authentification."""
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 401
```

**Critères** :
- ✅ Tester tous les endpoints
- ✅ Tester les query params (month, limit)
- ✅ Tester l'authentification
- ✅ Tester les cas d'erreur (404, 422)

---

### 🟡 Tâche 9 : Optimisation et performance

#### 9.1 Indexation des requêtes

Vérifier que les index existants couvrent les requêtes :

```sql
-- Index existants à vérifier
CREATE INDEX idx_transactions_account_date ON transactions (account_id, transaction_date);
CREATE INDEX idx_audit_entity ON audit_logs (entity_type, entity_id);
```

**Nouveaux index potentiels** :
```sql
-- Si performance insuffisante sur categories_breakdown
CREATE INDEX idx_transactions_category_date ON transactions (category_id, transaction_date);

-- Si performance insuffisante sur top_merchants
CREATE INDEX idx_transactions_merchant_date ON transactions (merchant_id, transaction_date);
```

#### 9.2 Requêtes SQL optimisées

Utiliser des agrégations SQL natives plutôt que des boucles Python :

```python
# ✅ BON : agrégation SQL
from sqlalchemy import func

expenses = db.query(
    func.sum(Transaction.amount).label("total")
).filter(
    Transaction.account_id.in_(user_account_ids),
    Transaction.amount < 0,
    Transaction.transaction_date >= start_date
).scalar()

# ❌ MAUVAIS : boucle Python
transactions = db.query(Transaction).all()
total = sum(t.amount for t in transactions)
```

#### 9.3 Tests de performance

```python
import time

def test_dashboard_summary_performance(client, auth_headers):
    """Dashboard summary doit répondre en < 300ms."""
    start = time.time()
    response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    elapsed = (time.time() - start) * 1000  # ms
    
    assert response.status_code == 200
    assert elapsed < 300, f"Trop lent : {elapsed:.2f}ms"
```

---

### 🟢 Tâche 10 : Documentation OpenAPI

**Action** : Vérifier que FastAPI génère automatiquement la documentation.

```bash
# Lancer l'API
cd /home/user/webapp && uvicorn main:app --reload

# Accéder à la doc
# http://localhost:8000/docs
```

**Critères** :
- ✅ Tous les endpoints visibles dans Swagger UI
- ✅ Query params documentés
- ✅ Schémas de réponse affichés
- ✅ Exemples de réponses clairs

---

### 🟢 Tâche 11 : Validation finale

#### Checklist Definition of Done

- [ ] **Endpoints API documentés** : Swagger auto-généré accessible
- [ ] **Tests unitaires** : Coverage ≥ 70% sur `dashboard_service.py`
- [ ] **Tests d'intégration** : Tous les endpoints testés
- [ ] **Migration Alembic** : Aucune migration nécessaire (étape 5 utilise schéma existant)
- [ ] **Déployable** : `docker compose up` fonctionne
- [ ] **Performance** : Temps de réponse p95 < 300ms validé

#### Test end-to-end manuel

```bash
# 1. Démarrer l'environnement
cd /home/user/webapp && docker compose up -d

# 2. Créer un utilisateur test
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# 3. Se connecter
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

# 4. Créer un compte et importer des transactions (étapes 3-4)
# ...

# 5. Tester le dashboard
curl http://localhost:8000/api/v1/dashboard/summary \
  -H "Authorization: Bearer $TOKEN"

curl http://localhost:8000/api/v1/dashboard/categories-breakdown?month=2026-02 \
  -H "Authorization: Bearer $TOKEN"

curl http://localhost:8000/api/v1/dashboard/top-merchants?limit=5 \
  -H "Authorization: Bearer $TOKEN"

curl http://localhost:8000/api/v1/dashboard/recurring \
  -H "Authorization: Bearer $TOKEN"
```

---

## Dépendances externes

### Packages Python requis

```bash
# Déjà présents (vérifier pyproject.toml)
- fastapi
- sqlalchemy>=2.0
- pydantic>=2.0
- python-dateutil  # Pour relativedelta
```

### Ajout si manquant

```bash
cd /home/user/webapp && uv add python-dateutil
```

---

## Risques et mitigation

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Performance lente sur agrégations SQL | High | Medium | Ajouter index sur (category_id, merchant_id, transaction_date) |
| Données incohérentes (soldes non à jour) | Medium | Low | Valider l'import CSV (étape 3) met à jour les soldes |
| Mois sans transactions → erreur division par zéro | Low | High | Gérer le cas previous_expenses = 0 |
| Abonnements non détectés | Medium | Medium | Phase 2 : améliorer la détection récurrente |

---

## Ordre d'exécution recommandé

1. **Schémas Pydantic** (Tâche 1) — base pour la suite
2. **Service Layer** (Tâche 2) — logique métier isolée, testable unitairement
3. **Tests unitaires** (Tâche 7) — TDD : tester pendant le développement
4. **Endpoints API** (Tâches 3-6) — connecter service au router
5. **Tests d'intégration** (Tâche 8) — valider le flux complet
6. **Optimisation** (Tâche 9) — mesurer et améliorer si nécessaire
7. **Documentation** (Tâche 10) — vérifier Swagger
8. **Validation finale** (Tâche 11) — test end-to-end manuel

---

## Timeline estimée

| Tâche | Estimation | Priorité |
|-------|-----------|----------|
| Tâche 1 (Schémas) | 1h | P0 |
| Tâche 2 (Service) | 4h | P0 |
| Tâche 3-6 (API) | 2h | P0 |
| Tâche 7 (Tests unitaires) | 3h | P0 |
| Tâche 8 (Tests intégration) | 2h | P0 |
| Tâche 9 (Performance) | 1h | P1 |
| Tâche 10-11 (Doc + validation) | 1h | P1 |
| **Total** | **14h** | - |

---

## Prochaines étapes après l'étape 5

Une fois l'étape 5 livrée :
- **Étape 6** : Vue Transactions (Power User) — filtres avancés, recherche, tags, export CSV
- **Étape 7** : Budget Tracking — définition de budgets, alertes dépassement
- **Étape 8** : Frontend Next.js — assemblage UI complète

---

## Questions ouvertes

| # | Question | Décision |
|---|----------|----------|
| Q1 | Faut-il implémenter le cache Redis dès le MVP (P1) ? | **Non** : Phase 2 si performance insuffisante |
| Q2 | Filtrage par compte individuel dans les endpoints dashboard ? | **P1** : Non bloquant pour MVP, ajout via query param `?account_id=` |
| Q3 | Format de `next_expected` pour les abonnements : date ou string ? | **date** : plus facile à manipuler côté frontend |

---

## Références

- **SPEC_MVP.md** : Étape 5 (lignes 185-222)
- **model/models.py** : Schéma de données existant
- **api/v1/transactions_router.py** : Exemple de structure de router
- **services/categorization_service.py** : Exemple de service layer

---

**Statut** : ✅ Plan validé — prêt pour implémentation
