from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.models import Sale, Product, Category
from app.schemas.schemas import (
    SalesAnalyticsResponse,
    SalesComparisonResponse,
    CategorySalesResponse,
    ProductSalesResponse
)

router = APIRouter()

@router.get("/revenue/daily", response_model=List[dict])
def get_daily_revenue(
    days: int = 7,
    db: Session = Depends(get_db)
):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    daily_revenue = db.query(
        func.date(Sale.sale_date).label('date'),
        func.sum(Sale.total_amount).label('revenue'),
        func.count(Sale.id).label('order_count')
    ).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).group_by(
        func.date(Sale.sale_date)
    ).all()
    
    return [
        {
            "date": str(revenue.date),
            "revenue": float(revenue.revenue),
            "order_count": revenue.order_count
        }
        for revenue in daily_revenue
    ]

@router.get("/revenue/monthly", response_model=List[dict])
def get_monthly_revenue(
    months: int = 12,
    db: Session = Depends(get_db)
):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30 * months)
    
    monthly_revenue = db.query(
        extract('year', Sale.sale_date).label('year'),
        extract('month', Sale.sale_date).label('month'),
        func.sum(Sale.total_amount).label('revenue'),
        func.count(Sale.id).label('order_count')
    ).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).group_by(
        extract('year', Sale.sale_date),
        extract('month', Sale.sale_date)
    ).all()
    
    return [
        {
            "year": int(revenue.year),
            "month": int(revenue.month),
            "revenue": float(revenue.revenue),
            "order_count": revenue.order_count
        }
        for revenue in monthly_revenue
    ]

@router.get("/revenue/by-category", response_model=List[dict])
def get_revenue_by_category(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        Category.id,
        Category.name,
        func.sum(Sale.total_amount).label('revenue'),
        func.sum(Sale.quantity).label('total_quantity')
    ).join(
        Product, Category.id == Product.category_id
    ).join(
        Sale, Product.id == Sale.product_id
    )
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    results = query.group_by(Category.id, Category.name).all()
    
    return [
        {
            "category_id": result.id,
            "category_name": result.name,
            "revenue": float(result.revenue),
            "total_quantity": result.total_quantity
        }
        for result in results
    ]

@router.get("/revenue/compare", response_model=dict)
def compare_revenue(
    period1_start: datetime,
    period1_end: datetime,
    period2_start: datetime,
    period2_end: datetime,
    db: Session = Depends(get_db)
):
    # Get revenue for period 1
    period1_revenue = db.query(
        func.sum(Sale.total_amount).label('revenue')
    ).filter(
        Sale.sale_date >= period1_start,
        Sale.sale_date <= period1_end
    ).scalar() or 0
    
    # Get revenue for period 2
    period2_revenue = db.query(
        func.sum(Sale.total_amount).label('revenue')
    ).filter(
        Sale.sale_date >= period2_start,
        Sale.sale_date <= period2_end
    ).scalar() or 0
    
    # Calculate percentage change
    if period1_revenue == 0:
        percentage_change = 100 if period2_revenue > 0 else 0
    else:
        percentage_change = ((period2_revenue - period1_revenue) / period1_revenue) * 100
    
    return {
        "period1": {
            "start": period1_start.isoformat(),
            "end": period1_end.isoformat(),
            "revenue": float(period1_revenue)
        },
        "period2": {
            "start": period2_start.isoformat(),
            "end": period2_end.isoformat(),
            "revenue": float(period2_revenue)
        },
        "percentage_change": float(percentage_change)
    } 