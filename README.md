# Customer Purchase Analysis & Business Intelligence Platform

Northstar is a full-stack customer and sales analytics portfolio project. It includes a React dashboard, FastAPI service, shared Pandas/SQLAlchemy analytics, and an independent Streamlit application. Metrics are calculated from persisted records, not seeded dashboard values.

## Features

- Revenue, order, customer, AOV, and unit metrics from the database
- Monthly revenue trends, product/category performance, recent orders
- RFM customer analysis and repeat purchase rate
- CSV/Excel validation, cleaning, import history, and CSV export
- Email/password registration and sign-in, with protected analytics and upload APIs
- Interactive rotatable 3D RFM customer value map
- PostgreSQL in production; SQLite for quick local development
- Responsive React/Vite UI and interactive Plotly Streamlit views
- Swagger API docs at `/docs`

## Architecture

See [docs/architecture.md](docs/architecture.md). FastAPI and Streamlit use the same SQLAlchemy models, ingestion code, and analytics functions in `backend/app`, avoiding duplicate business rules.

## Project structure

```text
backend/app/       FastAPI, database models, ingestion and analytics
frontend/          React, Vite, Recharts, Netlify config
streamlit_app/     Streamlit analytics application
shared/            Shared logic notes
data/              Sample dataset location
docs/              Architecture and methodology
```

## Local setup (PowerShell)

Python 3.10+ and Node.js 20+ are recommended.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`; create an account on the sign-in screen. API docs are at `http://localhost:8000/docs`. SQLite creates `customer_analysis.db` in the backend process working directory. Set `DATABASE_URL` before launching to use PostgreSQL instead. Set `AUTH_SECRET` to a long random value for any shared or deployed environment. To change the browser API URL locally, copy `frontend/.env.example` to `frontend/.env.local` and edit `VITE_API_BASE_URL`.

Run Streamlit from the repository root:

```powershell
pip install -r streamlit_app\requirements.txt
streamlit run streamlit_app\app.py
```

The browser frontend uses `VITE_API_BASE_URL` (default `http://localhost:8000/api`). Copy `.env.example` to `.env` for backend settings. For uploaded data, use one row per product line with `customer_id`, `product_id`, `order_id`, `order_date`, `quantity`, and `unit_price`. Optional fields include `customer_name`, `city`, `product_name`, `category`, `payment_method`, and `total_amount`.

## Database

SQLite is the zero-configuration local fallback. For PostgreSQL, create a database and set, for example:

```powershell
$env:DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require"
```

The API creates tables at startup for quick local development. An Alembic baseline is included; use `alembic -c backend/alembic.ini upgrade head` for managed schema rollout and future migrations.

## Deployment

### FastAPI

Deploy `backend/` on a Python-capable host (Render, Railway, Fly.io, etc.) with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT` and root/import path configured for `backend`. Set `DATABASE_URL`, `CORS_ORIGINS` (your Netlify origin), and a cryptographically random `AUTH_SECRET`. Confirm `/api/health` reports connected. Accounts authenticate access to the shared deployment workspace; records are not isolated per account.

### Netlify frontend

Import the repository, set base directory to `frontend`, build command `npm run build`, publish directory `dist`. Set `VITE_API_BASE_URL` to the public backend URL ending in `/api`, then deploy. SPA redirects are configured in `frontend/netlify.toml`.

### Streamlit Community Cloud

Deploy this repository with main file `streamlit_app/app.py` and dependency file `streamlit_app/requirements.txt`. Add a `DATABASE_URL` secret in app settings, for example:

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require"
```

For the Streamlit process, set `DATABASE_URL` from `st.secrets` in your deployment environment if the host does not expose secrets as environment variables. Netlify never receives database credentials.

### Supabase PostgreSQL

Create a hosted PostgreSQL database and use its pooled or direct connection string as `DATABASE_URL` for FastAPI and Streamlit. Keep secrets in the respective hosting dashboards. The web client only needs the public FastAPI base URL.

## GitHub

Inspect your remote and branch before first push. Suggested commands:

```powershell
git init
git add .
git commit -m "Build customer purchase intelligence platform"
git branch -M main
git remote add origin https://github.com/<your-account>/customer-purchase-analysis.git
git push -u origin main
```

Review staged files before committing. `.env`, databases, virtual environments, caches, and `node_modules` are ignored.

## Screenshots and links

- Screenshots: add captures here after running with your own data.
- Netlify: configure after backend hosting.
- Streamlit Cloud: configure after PostgreSQL provisioning.

## Testing and limitations

The repository includes typed validation at the import boundary and API health checks. Run `python -m compileall backend` and `npm run build` for local build checks. The 3D RFM map is an interactive projection of actual recency, frequency, and monetary fields. Imported records share the workspace across accounts; per-user data isolation is not implemented. Date-filter controls, customer-level CLV estimation, and K-Means are future improvements. Do not treat sample/demo data as actual business results.
