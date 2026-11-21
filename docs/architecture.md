# Architecture and methodology

React/Vite provides the browser interface. FastAPI is the primary data API and validates uploads before persistence. SQLAlchemy defines customers, products, orders, order items, and import history. SQLite is used for local setup; set `DATABASE_URL` to a PostgreSQL URL in hosted environments. The Streamlit application imports the same SQLAlchemy models, ingestion service, and analytics functions.

## Data model and import shape

Imports are transaction-line based. Required fields are customer ID, product ID, order ID, and order date. Quantity and unit price are needed to build order items; `total_amount` may supply the unit price when no unit price exists. Customer and product descriptive fields are optional. Existing IDs are reused, orders and products have unique external IDs, and invalid date/numeric rows are removed before insertion. The import history records accepted line counts.

The ingestion format uses one row per product line. Repeated order IDs should share the same customer and date. Orders are stored once and their line items are stored separately. For reliable order totals, provide `total_amount` per order line or make `unit_price × quantity` equal the desired line amount.

## Analytics

Revenue and average order value aggregate stored order totals. Monthly revenue groups orders by calendar month. Product revenue and units aggregate order-item subtotals and quantities. RFM uses each customer's latest order date for recency, distinct order count for frequency, and total order value for monetary value. Segments use transparent rule thresholds in the analytics module: Champions (4+ orders, <=30 days), Loyal (3+), Potential Loyalists (2, <=60 days), New (1, <=30 days), At Risk (<=90 days), otherwise Lost. Repeat purchase rate is the share of customers with more than one order. CLV/K-means are intentionally omitted until enough business-specific history and calibration exists; these simple measures are easier to explain and validate.

## Deployment boundaries

Netlify serves only the compiled frontend. FastAPI must be deployed separately with `DATABASE_URL` and `CORS_ORIGINS`. Streamlit Community Cloud reads the same PostgreSQL URL from `st.secrets`. Never put credentials in Vite variables; `VITE_API_BASE_URL` is a public API endpoint only.
