from fastapi import APIRouter
from app.api.v1.endpoints import products, sales, inventory, analytics

api_router = APIRouter()

api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"]) 