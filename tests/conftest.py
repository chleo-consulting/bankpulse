import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.database import get_db
from main import app
from model.models import Base, Category, CategoryRule

test_engine = create_engine(settings.DATABASE_TEST_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_categories(db_session) -> dict[str, Category]:
    """Crée une taxonomie minimale pour les tests (Alimentation → Supermarché)."""
    alimentation = Category(name="Alimentation")
    db_session.add(alimentation)
    db_session.flush()
    supermarche = Category(name="Supermarché", parent_id=alimentation.id)
    db_session.add(supermarche)
    db_session.flush()
    return {"alimentation": alimentation, "supermarche": supermarche}


@pytest.fixture
def seed_rules(db_session, seed_categories) -> list[CategoryRule]:
    """Crée une règle CARREFOUR → Supermarché pour les tests."""
    rule = CategoryRule(
        category_id=seed_categories["supermarche"].id,
        merchant_pattern=r"(?i)CARREFOUR",
        priority=10,
    )
    db_session.add(rule)
    db_session.flush()
    return [rule]
