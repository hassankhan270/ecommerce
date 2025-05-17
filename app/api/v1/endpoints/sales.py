from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.models import Sale, Product, Inventory
from app.schemas.schemas import SaleCreate, Sale as SaleSchema

router = APIRouter()

@router.post("/", response_model=SaleSchema)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(Product).filter(Product.id == sale.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == sale.product_id).first()
    if not inventory or inventory.quantity < sale.quantity:
        raise HTTPException(status_code=400, detail="Insufficient inventory")
    
    # Create sale
    db_sale = Sale(**sale.model_dump())
    db.add(db_sale)
    
    # Update inventory
    inventory.quantity -= sale.quantity
    
    # Create inventory history
    from app.models.models import InventoryHistory
    history = InventoryHistory(
        inventory_id=inventory.id,
        previous_quantity=inventory.quantity + sale.quantity,
        new_quantity=inventory.quantity,
        change_reason=f"Sale of {sale.quantity} units"
    )
    db.add(history)
    
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.get("/", response_model=List[SaleSchema])
def read_sales(
    skip: int = 0,
    limit: int = 100,
    start_date: datetime = None,
    end_date: datetime = None,
    product_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(Sale)
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    
    sales = query.offset(skip).limit(limit).all()
    return sales

@router.get("/daily", response_model=List[dict])
def get_daily_sales(
    days: int = 7,
    db: Session = Depends(get_db)
):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    daily_sales = db.query(
        func.date(Sale.sale_date).label('date'),
        func.sum(Sale.total_amount).label('total_sales'),
        func.sum(Sale.quantity).label('total_quantity')
    ).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).group_by(
        func.date(Sale.sale_date)
    ).all()
    
    return [
        {
            "date": str(sale.date),
            "total_sales": float(sale.total_sales),
            "total_quantity": sale.total_quantity
        }
        for sale in daily_sales
    ]

@router.get("/by-product", response_model=List[dict])
def get_sales_by_product(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        Product.id,
        Product.name,
        func.sum(Sale.total_amount).label('total_sales'),
        func.sum(Sale.quantity).label('total_quantity')
    ).join(
        Sale, Product.id == Sale.product_id
    )
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    results = query.group_by(Product.id, Product.name).all()
    
    return [
        {
            "product_id": result.id,
            "product_name": result.name,
            "total_sales": float(result.total_sales),
            "total_quantity": result.total_quantity
        }
        for result in results
    ] 