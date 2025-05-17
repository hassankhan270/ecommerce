from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.models.models import Inventory, InventoryHistory, Product
from app.schemas.schemas import InventoryCreate, Inventory as InventorySchema, InventoryHistory as InventoryHistorySchema

router = APIRouter()

@router.post("/", response_model=InventorySchema)
def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(Product).filter(Product.id == inventory.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if inventory already exists
    existing_inventory = db.query(Inventory).filter(Inventory.product_id == inventory.product_id).first()
    if existing_inventory:
        raise HTTPException(status_code=400, detail="Inventory already exists for this product")
    
    db_inventory = Inventory(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

@router.get("/", response_model=List[InventorySchema])
def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).offset(skip).limit(limit).all()
    return inventory

@router.get("/alerts", response_model=List[dict])
def get_low_stock_alerts(db: Session = Depends(get_db)):
    low_stock = db.query(
        Inventory,
        Product.name.label('product_name')
    ).join(
        Product, Inventory.product_id == Product.id
    ).filter(
        Inventory.quantity <= Inventory.low_stock_threshold
    ).all()
    
    return [
        {
            "product_id": item.Inventory.product_id,
            "product_name": item.product_name,
            "current_quantity": item.Inventory.quantity,
            "low_stock_threshold": item.Inventory.low_stock_threshold
        }
        for item in low_stock
    ]

@router.put("/{product_id}", response_model=InventorySchema)
def update_inventory(
    product_id: int,
    quantity: int,
    reason: str,
    db: Session = Depends(get_db)
):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    previous_quantity = inventory.quantity
    inventory.quantity = quantity
    
    # Create inventory history
    history = InventoryHistory(
        inventory_id=inventory.id,
        previous_quantity=previous_quantity,
        new_quantity=quantity,
        change_reason=reason
    )
    db.add(history)
    
    db.commit()
    db.refresh(inventory)
    return inventory

@router.get("/history/{product_id}", response_model=List[InventoryHistorySchema])
def get_inventory_history(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    history = db.query(InventoryHistory).filter(
        InventoryHistory.inventory_id == inventory.id
    ).order_by(
        InventoryHistory.change_date.desc()
    ).offset(skip).limit(limit).all()
    
    return history 