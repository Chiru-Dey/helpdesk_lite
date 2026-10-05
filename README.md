# HelpDesk Lite

A full-stack customer support ticketing system. Customers raise tickets, agents work on them (update, comment, resolve), and admins manage users, categories and reports.

The backend is a JSON REST API built with Flask and SQLAlchemy. The frontend is a single-page application built with Vue 3 and Axios. Access is controlled by three roles: **admin**, **agent** and **customer**.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Ticket Lifecycle](#ticket-lifecycle)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Demo Accounts](#demo-accounts)
- [API Documentation](#api-documentation)
- [Database](#database)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Backend | Python 3.12, Flask, SQLAlchemy, Flask-Migrate, Flask-Login, bcrypt, Flask-CORS |
| Frontend | Vue 3 (Composition API), Vite, Pinia, Vue Router, Axios |
| Database | SQLite (development), managed with Alembic migrations |
| Tooling | uv (Python package manager), npm, Git |

## Features

### Authentication and Security

- User registration and login with bcrypt-hashed passwords
- Session-cookie authentication for the web app
- Bearer-token authentication for API clients, with a token regeneration endpoint
- Role-based access control enforced in the API and in the frontend router

### Customer

- Register and log in
- Create tickets with category and priority
- View only their own tickets, filtered by status
- Comment on their tickets

### Agent

- View assigned tickets and unassigned open tickets
- Change ticket status through the lifecycle: open, in progress, resolved, closed
- Update priority and comment on tickets
- View dashboard metrics

### Admin

- Everything agents and customers can do
- Assign tickets to agents
- Manage categories (create, update, delete)
- Manage users (create, edit roles, activate/deactivate, delete with safeguards)
- View the full dashboard with status and priority breakdowns

### Dashboard

- Total, open, in-progress, resolved-today and closed ticket counts
- Ticket counts grouped by status and by priority
- List of the five most recent tickets

## Ticket Lifecycle

```
open -> in_progress -> resolved -> closed
```

**Priorities:** `low`, `medium`, `high`, `urgent`

## Project Structure

```
helpdesk_lite/
├── app/
│   ├── __init__.py            # application factory
│   ├── config.py              # configuration
│   ├── extensions.py          # SQLAlchemy, Migrate, LoginManager, CORS
│   ├── api/                   # REST blueprints (auth, users, categories, tickets, comments, dashboard, health)
│   ├── models/                # SQLAlchemy models (user, category, ticket, comment)
│   ├── services/              # dashboard_service.py (reporting queries)
│   └── utils/                 # decorators.py (roles_required)
├── migrations/                # Flask-Migrate (Alembic) migration scripts
├── instance/                  # SQLite database file (gitignored)
├── frontend/
│   └── src/
│       ├── api/               # Axios API clients
│       ├── router/            # routes and navigation guards
│       ├── stores/            # Pinia stores (auth)
│       └── views/             # page components
├── docs/screenshots/          # application screenshots
├── seed.py                    # demo data seeder
└── run.py                     # development server entry point
```

## Installation

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Node.js 18+, Git.

### Backend

From the project root:

```powershell
uv sync
.venv\Scripts\activate
uv run flask --app run.py db upgrade
uv run python seed.py
uv run python run.py
```

The API runs at <http://127.0.0.1:5000>.

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The app runs at <http://localhost:5173> and proxies `/api` to the Flask backend.

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | password123 |
| Agent | agent@example.com | password123 |
| Customer | customer@example.com | password123 |

## API Documentation

### Auth

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/auth/register` | Public | Register a new customer account |
| POST | `/api/auth/login` | Public | Log in, returns user and access token |
| POST | `/api/auth/logout` | Authenticated | Log out current user |
| GET | `/api/auth/me` | Authenticated | Current user profile |
| POST | `/api/auth/token/regenerate` | Authenticated | Rotate the API access token |

### Users

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/users` | Admin | List users, optional `?role=` filter |
| GET | `/api/users/<id>` | Admin | Get one user |
| POST | `/api/users` | Admin | Create user with roles |
| PATCH | `/api/users/<id>` | Admin | Update name, active status, roles |
| DELETE | `/api/users/<id>` | Admin | Delete user (blocked if tickets exist) |

### Categories

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/categories` | Authenticated | List categories |
| POST | `/api/categories` | Admin | Create category |
| PATCH | `/api/categories/<id>` | Admin | Update category |
| DELETE | `/api/categories/<id>` | Admin | Delete category |

### Tickets

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/tickets` | Authenticated | Create ticket (admin may create for others) |
| GET | `/api/tickets` | Authenticated | List tickets, role-scoped, `?status=` and `?priority=` filters |
| GET | `/api/tickets/<id>` | Authenticated | Ticket detail, role-scoped |
| PATCH | `/api/tickets/<id>` | Authenticated | Update fields (customers: subject/description on open tickets only; staff: priority/category) |
| DELETE | `/api/tickets/<id>` | Admin | Delete ticket |
| POST | `/api/tickets/<id>/assign` | Admin | Assign or unassign an agent |
| POST | `/api/tickets/<id>/status` | Agent/Admin | Change ticket status |

### Comments

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/tickets/<id>/comments` | Authenticated | List comments, role-scoped |
| POST | `/api/tickets/<id>/comments` | Authenticated | Add a comment, role-scoped |

### Dashboard

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/dashboard` | Agent/Admin | Ticket metrics and recent tickets |

### Health

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/health` | Public | Service health check |

### Authentication Example (PowerShell)

```powershell
$login = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/auth/login -ContentType "application/json" -Body '{"email":"admin@example.com","password":"password123"}'
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/tickets -Headers @{ Authorization = "Bearer $($login.token)" }
```

## Database

Development uses SQLite stored at `instance/helpdesk.db`. Apply schema changes with Flask-Migrate:

```powershell
uv run flask --app run.py db migrate -m "Describe change"
uv run flask --app run.py db upgrade
```

### Reset the Database

```powershell
Remove-Item instance\helpdesk.db
Remove-Item -Recurse -Force migrations
uv run flask --app run.py db init
uv run flask --app run.py db migrate -m "Initial models"
uv run flask --app run.py db upgrade
uv run python seed.py
```

