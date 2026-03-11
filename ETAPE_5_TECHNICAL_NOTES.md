# Points d'Attention Techniques — Étape 5 Dashboard

Ce document liste les considérations techniques critiques pour l'implémentation de l'étape 5.

---

## 1. Gestion des Décimaux (CRITIQUE)

### ⚠️ Problème
JavaScript ne gère pas correctement les nombres flottants :
```javascript
// ❌ MAUVAIS
0.1 + 0.2 === 0.30000000000000004  // true
```

### ✅ Solution : Utiliser des strings dans l'API

**Backend (FastAPI)** :
```python
from decimal import Decimal
from pydantic import BaseModel

class DashboardSummary(BaseModel):
    total_balance: Decimal  # Automatiquement sérialisé en string
    
    class Config:
        json_encoders = {
            Decimal: str  # Force la conversion en string
        }
```

**Frontend (Next.js)** :
```typescript
interface DashboardSummary {
  total_balance: string;  // Pas number !
  expenses: {
    current: string;
    previous: string;
    delta_pct: number;  // Seulement les % en number
  };
}

// Affichage
const balance = parseFloat(data.total_balance).toFixed(2);
```

### Règle générale
- **Montants** → `Decimal` en backend, `string` en JSON, `parseFloat()` pour affichage
- **Pourcentages** → `float` acceptable car pas de manipulation monétaire
- **Compteurs** → `int` en backend, `number` en frontend

---

## 2. Calcul du Delta Pourcentage

### Formule
```python
def calculate_percentage_change(old_value: Decimal, new_value: Decimal) -> float:
    """
    Calcule le changement en pourcentage entre deux valeurs.
    
    Args:
        old_value: Valeur de référence (mois précédent)
        new_value: Nouvelle valeur (mois actuel)
    
    Returns:
        Pourcentage de changement (négatif = baisse, positif = hausse)
    
    Exemples:
        calculate_percentage_change(100, 80) → -20.0  (baisse de 20%)
        calculate_percentage_change(100, 120) → 20.0  (hausse de 20%)
        calculate_percentage_change(0, 50) → 0.0     (cas spécial)
    """
    if old_value == 0:
        return 0.0  # Éviter division par zéro
    
    delta = new_value - old_value
    percentage = (delta / old_value) * 100
    return round(float(percentage), 2)
```

### Tests à valider
```python
def test_percentage_change():
    # Baisse de dépenses (positif pour l'utilisateur)
    assert calculate_percentage_change(Decimal("100"), Decimal("80")) == -20.0
    
    # Hausse de dépenses (négatif pour l'utilisateur)
    assert calculate_percentage_change(Decimal("100"), Decimal("120")) == 20.0
    
    # Pas de changement
    assert calculate_percentage_change(Decimal("100"), Decimal("100")) == 0.0
    
    # Premier mois (pas d'historique)
    assert calculate_percentage_change(Decimal("0"), Decimal("500")) == 0.0
    
    # Arrondi
    assert calculate_percentage_change(Decimal("300"), Decimal("275")) == -8.33
```

---

## 3. Filtrage par Mois (SQL)

### ⚠️ Attention aux Timezones

**Problème** : Les dates peuvent être interprétées différemment selon la timezone.

**Solution** : Travailler en UTC et utiliser des comparaisons de dates pures.

```python
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

def get_month_range(month_str: str | None = None) -> tuple[date, date]:
    """
    Retourne le premier et dernier jour d'un mois.
    
    Args:
        month_str: Format "YYYY-MM" ou None (mois actuel)
    
    Returns:
        (start_date, end_date) exclusif
    
    Exemple:
        get_month_range("2026-02") → (date(2026, 2, 1), date(2026, 3, 1))
    """
    if month_str is None:
        today = date.today()
        year, month = today.year, today.month
    else:
        year, month = map(int, month_str.split("-"))
    
    start_date = date(year, month, 1)
    end_date = start_date + relativedelta(months=1)
    return start_date, end_date

# Utilisation dans une requête
def get_monthly_expenses(db: Session, user_id: UUID, month: str | None) -> Decimal:
    start_date, end_date = get_month_range(month)
    
    result = db.query(func.sum(Transaction.amount)).filter(
        Transaction.account_id.in_(user_account_ids),
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date < end_date,  # Exclusif !
        Transaction.amount < 0
    ).scalar()
    
    return abs(result or Decimal("0"))
```

### Pourquoi `< end_date` et pas `<= last_day` ?

```python
# ✅ BON : end_date exclusif
WHERE transaction_date >= '2026-02-01' AND transaction_date < '2026-03-01'
# Inclut du 1er février 00:00:00 au 28 février 23:59:59

# ❌ MAUVAIS : last_day inclusif
WHERE transaction_date >= '2026-02-01' AND transaction_date <= '2026-02-28'
# Peut exclure les transactions du 28 à 23:59:59 selon la précision
```

---

## 4. Optimisation des Requêtes SQL

### Principe : Agrégation SQL, pas Python

```python
# ❌ MAUVAIS : Boucle Python
transactions = db.query(Transaction).all()
total = sum(abs(t.amount) for t in transactions if t.amount < 0)

# ✅ BON : Agrégation SQL
from sqlalchemy import func

total = db.query(func.sum(Transaction.amount)).filter(
    Transaction.amount < 0
).scalar()
total = abs(total or Decimal("0"))
```

### Index à vérifier

```sql
-- Requis pour les filtres temporels
CREATE INDEX idx_transactions_account_date 
ON transactions (account_id, transaction_date);

-- Optionnel : si performance insuffisante sur categories_breakdown
CREATE INDEX idx_transactions_category_date 
ON transactions (category_id, transaction_date);

-- Optionnel : si performance insuffisante sur top_merchants
CREATE INDEX idx_transactions_merchant_date 
ON transactions (merchant_id, transaction_date);
```

### Éviter les N+1 queries

```python
# ❌ MAUVAIS : N+1 queries
categories = db.query(Category).all()
for cat in categories:
    # 1 query par catégorie !
    total = db.query(func.sum(Transaction.amount)).filter(
        Transaction.category_id == cat.id
    ).scalar()

# ✅ BON : 1 seule query avec GROUP BY
from sqlalchemy import func

results = db.query(
    Category.id,
    Category.name,
    func.sum(Transaction.amount).label("total"),
    func.count(Transaction.id).label("count")
).join(Transaction).group_by(Category.id, Category.name).all()
```

---

## 5. Gestion des Relations SQLAlchemy

### Récupérer le nom de la catégorie parent

```python
# Modèle (déjà présent dans models.py)
class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[UUID] = mapped_column(...)
    name: Mapped[str] = mapped_column(...)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("categories.id"))
    
    parent: Mapped[Optional["Category"]] = relationship(remote_side=[id])

# Requête avec jointure sur parent
from sqlalchemy.orm import aliased

ParentCategory = aliased(Category)

results = db.query(
    Category.id,
    Category.name,
    ParentCategory.name.label("parent_name"),
    func.sum(Transaction.amount).label("total")
).outerjoin(
    ParentCategory, Category.parent_id == ParentCategory.id
).join(
    Transaction, Transaction.category_id == Category.id
).group_by(
    Category.id, Category.name, ParentCategory.name
).all()
```

### Filtrer par comptes de l'utilisateur

```python
from sqlalchemy import select

# Subquery : IDs des comptes de l'utilisateur
user_account_ids = select(BankAccount.id).where(
    BankAccount.user_id == user_id,
    BankAccount.deleted_at.is_(None)  # Ignorer soft-deleted
)

# Utilisation
query = db.query(Transaction).filter(
    Transaction.account_id.in_(user_account_ids)
)
```

---

## 6. Calcul de `next_expected` pour les Abonnements

### Logique métier

```python
from datetime import date
from dateutil.relativedelta import relativedelta

def calculate_next_expected(
    last_detected: date, 
    frequency: str
) -> date:
    """
    Calcule la date de prochaine échéance attendue.
    
    Args:
        last_detected: Dernière date détectée
        frequency: "monthly" ou "yearly"
    
    Returns:
        Date de prochaine échéance
    """
    if frequency == "monthly":
        return last_detected + relativedelta(months=1)
    elif frequency == "yearly":
        return last_detected + relativedelta(years=1)
    else:
        raise ValueError(f"Fréquence invalide : {frequency}")

# Exemple
last = date(2026, 2, 15)
next_monthly = calculate_next_expected(last, "monthly")
# → date(2026, 3, 15)

last_yearly = date(2025, 12, 1)
next_yearly = calculate_next_expected(last_yearly, "yearly")
# → date(2026, 12, 1)
```

### Gestion des cas limites

```python
# 31 janvier → 28/29 février
last = date(2026, 1, 31)
next_expected = last + relativedelta(months=1)
# → date(2026, 2, 28)  ✅ Pas d'erreur

# 29 février (année bissextile) → 28 février
last = date(2024, 2, 29)
next_expected = last + relativedelta(years=1)
# → date(2025, 2, 28)  ✅ Pas d'erreur
```

---

## 7. Tests de Performance

### Benchmark simple

```python
import time
from contextlib import contextmanager

@contextmanager
def measure_time(label: str):
    """Context manager pour mesurer le temps d'exécution."""
    start = time.perf_counter()
    yield
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"⏱️  {label}: {elapsed_ms:.2f}ms")

# Utilisation
with measure_time("Dashboard summary"):
    balance = dashboard_service.get_consolidated_balance(db, user_id)
    comparison = dashboard_service.get_monthly_comparison(db, user_id)
```

### Test de charge avec pytest-benchmark

```python
def test_dashboard_summary_performance(benchmark, db_session, sample_user):
    """Summary doit répondre en < 300ms."""
    result = benchmark(
        dashboard_service.get_monthly_comparison,
        db_session,
        sample_user.id
    )
    assert result is not None
    # pytest-benchmark affiche automatiquement les stats
```

### Commande
```bash
cd /home/user/webapp && pytest tests/test_dashboard_service.py --benchmark-only
```

---

## 8. Gestion des Cas Limites

### Checklist de validation

- [ ] **Aucun compte** : retourner `balance = 0.00`
- [ ] **Aucune transaction** : retourner `expenses = {"current": 0, "previous": 0, "delta_pct": 0}`
- [ ] **Division par zéro** : delta = 0 si `previous = 0`
- [ ] **Catégorie sans parent** : `parent_category_name = null`
- [ ] **Transactions sans merchant** : exclues de `top-merchants`
- [ ] **Transactions sans category** : exclues de `categories-breakdown`
- [ ] **Mois futur** : accepté mais retourne probablement 0 transactions
- [ ] **Format de mois invalide** : 422 Unprocessable Entity
- [ ] **Limit hors limites** : 422 avec validation Pydantic
- [ ] **Token expiré/absent** : 401 Unauthorized

---

## 9. Structure de Réponse Cohérente

### Pattern à suivre

Tous les endpoints de liste doivent suivre cette structure :

```python
from pydantic import BaseModel

class ListResponse(BaseModel):
    """Pattern générique pour les réponses de type liste."""
    items: list[ItemType]
    # Métadonnées optionnelles selon le endpoint
    total: int | None = None
    month: str | None = None
```

### Exemples

```python
# Categories breakdown
class CategoriesBreakdown(BaseModel):
    month: str
    items: list[CategoryBreakdownItem]
    total_amount: Decimal

# Top merchants
class TopMerchants(BaseModel):
    month: str
    items: list[TopMerchantItem]
    # Pas de total ici, c'est un top N

# Recurring
class RecurringSubscriptions(BaseModel):
    items: list[RecurringSubscription]
    # Pas de métadonnées, c'est une liste complète
```

---

## 10. Logging et Debugging

### Activer les logs SQL (dev uniquement)

```python
# core/database.py
import logging

# En développement
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Les queries SQL s'affichent dans la console
```

### Log des temps de réponse

```python
import time
from fastapi import Request

@router.get("/summary")
async def get_dashboard_summary(request: Request, ...):
    start = time.perf_counter()
    
    # ... logique métier
    
    elapsed = (time.perf_counter() - start) * 1000
    print(f"⏱️  GET /dashboard/summary: {elapsed:.2f}ms")
    
    return result
```

---

## 11. Checklist Pre-Commit

Avant chaque commit, vérifier :

- [ ] `ruff check .` passe sans erreur
- [ ] `black .` a formaté le code
- [ ] `pytest tests/` passe à 100%
- [ ] Coverage ≥ 70% sur les nouveaux fichiers
- [ ] Aucun `print()` ou `console.log()` de debug oublié
- [ ] Tous les types sont annotés (mypy compatible)
- [ ] Documentation docstring sur les fonctions publiques
- [ ] Aucun secret hardcodé (API keys, tokens)

---

## 12. Commandes Utiles

```bash
# Tests unitaires uniquement dashboard
cd /home/user/webapp && pytest tests/test_dashboard_service.py -v

# Tests avec coverage
cd /home/user/webapp && pytest tests/test_dashboard_service.py --cov=services.dashboard_service

# Tests de performance
cd /home/user/webapp && pytest tests/test_dashboard_service.py --benchmark-only

# Linting
cd /home/user/webapp && ruff check services/dashboard_service.py

# Formatting
cd /home/user/webapp && black services/dashboard_service.py

# Type checking (optionnel)
cd /home/user/webapp && mypy services/dashboard_service.py

# Démarrer l'API en mode dev
cd /home/user/webapp && uvicorn main:app --reload --log-level debug

# Test manuel d'un endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/dashboard/summary | jq
```

---

**Référence** : PLAN_ETAPE_5.md · ETAPE_5_API_EXAMPLES.md
