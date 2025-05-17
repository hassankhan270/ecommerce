from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    category_id: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Inventory Schemas
class InventoryBase(BaseModel):
    quantity: int = Field(ge=0)
    low_stock_threshold: int = Field(ge=0)

class InventoryCreate(InventoryBase):
    product_id: int

class Inventory(InventoryBase):
    id: int
    product_id: int
    last_updated: datetime

    class Config:
        from_attributes = True

# Inventory History Schemas
class InventoryHistoryBase(BaseModel):
    previous_quantity: int
    new_quantity: int
    change_reason: str

class InventoryHistoryCreate(InventoryHistoryBase):
    inventory_id: int

class InventoryHistory(InventoryHistoryBase):
    id: int
    inventory_id: int
    change_date: datetime

    class Config:
        from_attributes = True

# Sale Schemas
class SaleBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    total_amount: float = Field(gt=0)

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    sale_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics Schemas
class SalesAnalytics(BaseModel):
    period: str
    total_sales: float
    total_quantity: int
    average_order_value: float

class SalesComparison(BaseModel):
    period1: str
    period2: str
    period1_sales: float
    period2_sales: float
    percentage_change: float

class CategorySales(BaseModel):
    category_id: int
    category_name: str
    total_sales: float
    total_quantity: int

class ProductSales(BaseModel):
    product_id: int
    product_name: str
    total_sales: float
    total_quantity: int

# Response Models
class SalesAnalyticsResponse(BaseModel):
    analytics: List[SalesAnalytics]

class SalesComparisonResponse(BaseModel):
    comparison: SalesComparison

class CategorySalesResponse(BaseModel):
    category_sales: List[CategorySales]

class ProductSalesResponse(BaseModel):
    product_sales: List[ProductSales] 