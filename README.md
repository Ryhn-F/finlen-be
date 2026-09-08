# FinLen Backend Core API

Backend service for **FinLen**, an interactive AI-powered financial education platform. FinLen provides immersive, scenario-based roleplay simulations where users learn to navigate high-pressure debt collectors, predatory online loans (pinjol), credit card traps, investment scams, and impulsive spending.

> 📖 **Complete API Reference & AI Agent Contract**: For detailed endpoint payloads, schemas, error codes, and curl examples, see [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md).

---

## Tech Stack & Architecture

- **Framework**: Python 3.12+, FastAPI, Pydantic v2
- **Database**: PostgreSQL 17 + SQLAlchemy 2.0 (Async with `asyncpg`)
- **Migrations**: Alembic
- **Roleplay Runtime & Chat Store**: Firebase Firestore (`firebase-admin`)
- **AI Engine**: Google Gemini (`gemini-2.5-flash`)
- **Authentication**: JWT Bearer Tokens with `bcrypt` password hashing
- **Testing**: Pytest, Pytest-Asyncio, HTTPX

```
Frontend (Vite / Next.js)
       │
       ▼
FastAPI Application (/api/v1)
       │
       ├── Authentication (/api/v1/auth)
       │      ├── PostgreSQL (users)
       │      └── JWT Bearer Tokens & bcrypt Hashing
       │
       ├── Scenario Management (/api/v1/scenarios)
       │      ├── PostgreSQL (scenarios)
       │      └── 10 Predefined Realistic Seed Scenarios
       │
       ├── Roleplay Engine (/api/v1/roleplay)
       │      ├── PostgreSQL (roleplay_sessions: stats, instinct score, XP, status)
       │      ├── Firebase Firestore (roleplay_sessions/{id}/messages & session_state)
       │      └── Google Gemini (gemini-2.5-flash: turn evaluations, dialogue, stat deltas)
       │
       └── Progression & Scoring
              ├── Deterministic Financial Instinct Score Algorithm
              └── User XP & Level Calculation
```

---

## Environment Variables Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Available Settings

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Name of application | `FinLen API` |
| `APP_ENV` | Environment name | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `DATABASE_URL` | PostgreSQL asyncpg connection string | `postgresql+asyncpg://postgres:password@localhost:5432/finlen` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | Must be set securely in production |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `120` |
| `GEMINI_API_KEY` | Google Gemini API Key | your Gemini API key |
| `GEMINI_BASE_URL` | Google Gemini base URL | `https://generativelanguage.googleapis.com/v1beta` |
| `AI_MODEL` | AI Model name | `gemini-2.5-flash` |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON | `src/serviceAccountKey.json` |
| `FIREBASE_PROJECT_ID` | Firebase Project ID | `finlen-infinitera` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000,http://localhost:5173` |

---

## Installation & Setup

1. **Install uv** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Run database migrations**:
   ```bash
   uv run alembic upgrade head
   ```

4. **Seed Scenarios** (10 predefined scenarios will be inserted automatically on startup or run manually):
   ```bash
   uv run python -m finlen_be.db.seed
   ```

5. **Start Development Server**:
   ```bash
   uv run fastapi dev
   ```
   Or via python:
   ```bash
   uv run uvicorn finlen_be.main:app --reload --port 8000
   ```

---

## API Endpoints Overview

Swagger / OpenAPI documentation is interactively accessible at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 1. Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register` — Register a new account (`username`, `email`, `password`)
- `POST /api/v1/auth/login` — Authenticate and receive JWT access token
- `GET /api/v1/auth/me` — Retrieve current user profile and progression stats (Bearer Auth)

### 2. Scenarios (`/api/v1/scenarios`)
- `GET /api/v1/scenarios` — List all active scenarios with difficulty and NPC role
- `GET /api/v1/scenarios/{scenario_id}` — View complete financial context and learning objectives

### 3. Roleplay Engine (`/api/v1/roleplay`)
- `POST /api/v1/roleplay/sessions` — Start roleplay session, initializes PostgreSQL & Firestore with first NPC message
- `GET /api/v1/roleplay/sessions/{session_id}` — Get session status, current scores, and runtime state
- `POST /api/v1/roleplay/sessions/{session_id}/messages` — Submit player action/message; triggers AI evaluation, stat deltas, and NPC dialogue response
- `GET /api/v1/roleplay/sessions/{session_id}/messages` — Paginated conversation history from Firestore
- `POST /api/v1/roleplay/sessions/{session_id}/complete` — Finalize session, calculate final scores & XP, and update user progression

---

## Predefined Roleplay Scenarios

The platform includes 10 seeded scenarios:
1. **Aggressive Debt Collector** (`aggressive-debt-collector`): Overdue Rp3,000,000 loan after layoff, high-pressure collection.
2. **Illegal Pinjol Blackmail Threat** (`illegal-pinjol-threat`): Unregistered predatory lender threatening contact broadcast.
3. **Credit Card Minimum Payment Trap** (`credit-card-minimum-payment-trap`): 2.25% monthly compounding interest vs fixed restructuring.
4. **Impulsive Midnight Flash Sale FOMO** (`impulsive-flash-sale-fomo`): High-discount countdown sale tempting discretionary budget.
5. **Emergency Medical Expense Financing** (`emergency-medical-financing`): Urgent surgery deposit vs BPJS insurance coordination.
6. **High-Yield Guaranteed Investment Scam** (`high-yield-investment-scam`): 25% monthly return Ponzi red flags.
7. **Buy-Now-Pay-Later (BNPL) Snowball** (`bnpl-snowball-crisis`): Fragmented micro-loans colliding on payday.
8. **Salary Advance Payday Loan** (`salary-advance-payday-trap`): 12% upfront fee disguised as cheap advance.
9. **Friend Guilt-Tripping for an Unsecured Loan** (`friend-guilt-trip-loan`): Boundary setting and emergency fund protection.
10. **Vehicle Financing Installment Pressure** (`vehicle-financing-pressure`): DP 0 5-year lease total cost calculation.

---

## Running Tests

Automated tests cover authentication, scenario inspection, AI JSON parsing, and the complete roleplay lifecycle:

```bash
uv run pytest -v
```
