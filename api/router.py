from fastapi import APIRouter

from api.v1 import (
    accounts_router,
    auth,
    categories_router,
    dashboard_router,
    health,
    import_router,
    transactions_router,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(import_router.router)
api_router.include_router(accounts_router.router)
api_router.include_router(categories_router.router)
api_router.include_router(transactions_router.router)
api_router.include_router(dashboard_router.router)
