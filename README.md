## Features

- Sales Status and Analysis
  - Retrieve and filter sales data
  - Revenue analysis (daily, weekly, monthly, annual)
  - Period and category comparison
  - Date range, product, and category-based sales data

- Inventory Management
  - Current inventory status
  - Low stock alerts
  - Inventory level updates
  - Historical inventory tracking

## Tech Stack

- Python 3.8+
- FastAPI
- MySQL
- SQLAlchemy
- Pydantic

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/hassankhan270/ecommerce.git
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ecommerce_db
SECRET_KEY=your-secret-key
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Sales Endpoints
- `GET /api/sales/` - Get all sales data
- `GET /api/sales/analytics/daily` - Get daily sales analytics
- `GET /api/sales/analytics/weekly` - Get weekly sales analytics
- `GET /api/sales/analytics/monthly` - Get monthly sales analytics
- `GET /api/sales/analytics/annual` - Get annual sales analytics
- `GET /api/sales/compare` - Compare sales across periods
- `GET /api/sales/by-category` - Get sales by category
- `GET /api/sales/by-product` - Get sales by product

### Inventory Endpoints
- `GET /api/inventory/` - Get current inventory status
- `GET /api/inventory/alerts` - Get low stock alerts
- `PUT /api/inventory/{product_id}` - Update inventory levels
- `GET /api/inventory/history/{product_id}` - Get inventory history

### Product Endpoints
- `POST /api/products/` - Register new product
- `GET /api/products/` - Get all products
- `GET /api/products/{product_id}` - Get product details
- `PUT /api/products/{product_id}` - Update product
- `DELETE /api/products/{product_id}` - Delete product

## Database Schema

The database consists of the following main tables:

1. `products`
   - id (Primary Key)
   - name
   - description
   - price
   - category_id (Foreign Key)
   - created_at
   - updated_at

2. `categories`
   - id (Primary Key)
   - name
   - description

3. `inventory`
   - id (Primary Key)
   - product_id (Foreign Key)
   - quantity
   - low_stock_threshold
   - last_updated

4. `sales`
   - id (Primary Key)
   - product_id (Foreign Key)
   - quantity
   - total_amount
   - sale_date
   - created_at

5. `inventory_history`
   - id (Primary Key)
   - product_id (Foreign Key)
   - previous_quantity
   - new_quantity
   - change_date
   - change_reason
