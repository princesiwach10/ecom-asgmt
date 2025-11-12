# E-Commerce Assignment API (Django + DRF) + React (Vite)

In-memory e-commerce assignment: products, cart, checkout, and **every Nth order** gets a **single-use 10% discount** (admin-generated).  
All data is in memory and resets on process restart.

## Requirements

- Python 3.10+
- Node 24+ (for the frontend)
- Django 4.x, DRF
- drf-spectacular (for OpenAPI/Swagger)

## Backend (Django)

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows (PowerShell): .\.venv\Scripts\activate

pip install -r requirements.txt

# .env
# NTH_ORDER_FOR_DISCOUNT=3
# DISCOUNT_PERCENT=10
# ADMIN_API_KEY=supersecret

python manage.py runserver  # http://127.0.0.1:8000
```

**API docs** (auto-generated via drf-spectacular):

- Swagger: `http://127.0.0.1:8000/api/docs/`
- Redoc: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI: `http://127.0.0.1:8000/api/schema/`

> For details/usage, follow **drf-spectacular** documentation.

**Headers**

- `X-User-Id` (optional) identifies the user for cart/checkout.
- `X-Admin-Key` is required for `/api/admin/*` (must match `ADMIN_API_KEY`).

**Tests**

```bash
python manage.py test -v 2
```

## Frontend (Vite React, JavaScript)

Located in **`/web`**

```bash
cd web
npm install

# set backend API base
echo VITE_API_BASE=http://localhost:8000/api > .env

npm run dev   # http://localhost:5173
```

**CORS**
Backend is configured for `http://localhost:5173` and allows custom headers `X-User-Id` & `X-Admin-Key`.

## Project Layout

```
ecom-asgmt/
├─ manage.py
├─ config/            # Django project (settings/urls)
├─ store/           # Django app (in-memory store, APIs, tests)
├─ requirements.txt
├─ README.md
└─ web/             # Vite frontend (JS) – dev only
```
