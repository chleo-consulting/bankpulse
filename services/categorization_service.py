import re

from sqlalchemy.orm import Session

from model.models import Category, CategoryRule, Merchant, Transaction


class CategorizationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_category_for_merchant(self, merchant: Merchant) -> Category | None:
        """Applique les règles RegExp par priorité décroissante, retourne la première qui matche."""
        rules = (
            self.db.query(CategoryRule)
            .filter(CategoryRule.deleted_at.is_(None))
            .order_by(CategoryRule.priority.desc())
            .all()
        )
        for rule in rules:
            if re.search(rule.merchant_pattern, merchant.normalized_name or ""):
                return (
                    self.db.query(Category)
                    .filter(
                        Category.id == rule.category_id,
                        Category.deleted_at.is_(None),
                    )
                    .first()
                )
        return None

    def categorize_transaction(self, txn: Transaction) -> bool:
        """Catégorise une transaction via son merchant. Retourne True si catégorisée."""
        if txn.merchant_id is None:
            return False
        merchant = self.db.get(Merchant, txn.merchant_id)
        if not merchant:
            return False
        category = self.get_category_for_merchant(merchant)
        if category:
            txn.category_id = category.id
            return True
        return False
