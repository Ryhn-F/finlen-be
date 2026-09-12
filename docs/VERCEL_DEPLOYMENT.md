# Vercel Deployment Guide for FinLen Backend

This guide walks you through deploying the **FinLen Backend (FastAPI)** application to **Vercel** serverless functions.

---

## 1. Prerequisites

1. A [Vercel Account](https://vercel.com).
2. GitHub / GitLab / Bitbucket repository containing this codebase.
3. Supabase project (PostgreSQL database).
4. Google Gemini API key.
5. Firebase project (Firestore) credentials.

---

## 2. Architecture & File Overview

| File | Purpose |
| :--- | :--- |
| [`api/index.py`](file:///d:/Projects/finlen-be/api/index.py) | Vercel Serverless Function entrypoint. Injects `src/` into Python's `sys.path` and exports the FastAPI `app`. |
| [`vercel.json`](file:///d:/Projects/finlen-be/vercel.json) | Configures URL rewrites to route all traffic (`/(.*)`) to `/api/index.py`. |
| [`.vercelignore`](file:///d:/Projects/finlen-be/.vercelignore) | Keeps the deployment bundle small and fast by excluding tests, virtual environments, local caches, and secrets. |
| [`requirements.txt`](file:///d:/Projects/finlen-be/requirements.txt) | Clean, pinned production dependencies without local editable `-e .` flags. |

---

## 3. Step-by-Step Deployment Instructions

### Step 3.1: Push Changes to Git

Commit and push your project to your GitHub repository:
```bash
git add api/ vercel.json .vercelignore requirements.txt src/ docs/
git commit -m "feat: configure vercel serverless deployment"
git push origin main
```

### Step 3.2: Import Project into Vercel

1. Log in to [vercel.com](https://vercel.com) and click **"Add New..."** > **"Project"**.
2. Select your `finlen-be` Git repository.
3. **Framework Preset**: Leave as **Other** (Vercel will automatically detect Python and FastAPI via `api/index.py`).
4. **Root Directory**: `./` (leave default).

---

### Step 3.3: Configure Environment Variables

Under **Environment Variables** in the Vercel project configuration, add the following variables:

#### Core API Settings
| Variable Name | Value Description | Example / Recommended |
| :--- | :--- | :--- |
| `APP_NAME` | Name of the application | `FinLen API` |
| `APP_ENV` | Environment mode | `production` |
| `DEBUG` | Debug mode | `False` |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend domains | `https://your-frontend.vercel.app,http://localhost:3000` |

#### Database (Supabase PostgreSQL)
| Variable Name | Value Description | Example / Recommended |
| :--- | :--- | :--- |
| `DATABASE_URL` | Async PostgreSQL connection string | Use Supabase **Transaction Connection Pooler** (Port 6543) for serverless environments: `postgresql+asyncpg://postgres:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres` |
| `SEED_DB_ON_STARTUP` | Seed initial scenarios on cold start | `False` once scenarios are seeded in the DB (speeds up cold starts) |

> [!TIP]
> **Supabase Serverless Connection**: In Supabase Dashboard, go to **Project Settings > Database > Connection Pooling**. Select **Transaction Mode** (Port `6543`). The backend automatically sets `statement_cache_size=0` when port `6543` or `pooler` is in the `DATABASE_URL`.

#### Supabase Storage (Learning Material PDFs)
| Variable Name | Value Description | Example / Recommended |
| :--- | :--- | :--- |
| `SUPABASE_URL` | Your Supabase project URL | `https://<project-ref>.supabase.co` |
| `SUPABASE_KEY` | Supabase API key (anon or service role) used only to build public storage URLs | Found in **Project Settings > API** |
| `SUPABASE_STORAGE_BUCKET` | Name of the public storage bucket containing learning material PDFs | `learning-materials` |

> [!NOTE]
> The bucket referenced by `SUPABASE_STORAGE_BUCKET` must be public (or the objects must be publicly readable) for `get_public_url` to return a usable link. If the bucket is private, switch to signed URLs instead.

#### JWT Authentication
| Variable Name | Value Description | Example / Recommended |
| :--- | :--- | :--- |
| `JWT_SECRET_KEY` | Strong random secret key for JWT signing | `openssl rand -hex 32` |
| `JWT_ALGORITHM` | Hashing algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan | `120` |

#### Google Gemini AI
| Variable Name | Value Description | Example / Recommended |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Gemini API Key | `AIzaSy...` |
| `AI_MODEL` | Gemini model name | `gemini-2.5-flash` |

#### Firebase Admin SDK (Firestore Sync)
Instead of uploading `serviceAccountKey.json`, configure Firebase via environment variables:
| Variable Name | Value from `serviceAccountKey.json` |
| :--- | :--- |
| `FIREBASE_PROJECT_ID` | `"project_id"` |
| `FIREBASE_PRIVATE_KEY_ID` | `"private_key_id"` |
| `FIREBASE_PRIVATE_KEY` | `"private_key"` (keep the `\n` characters or paste the full PEM key) |
| `FIREBASE_CLIENT_EMAIL` | `"client_email"` |
| `FIREBASE_CLIENT_ID` | `"client_id"` |

---

### Step 3.4: Deploy

1. Click **Deploy**.
2. Wait for Vercel to install dependencies from `requirements.txt` and package the serverless function.
3. Once finished, Vercel will provide your production URL (e.g. `https://finlen-be.vercel.app`).

---

## 4. Verification

After deployment, test the endpoints using your Vercel URL:

- **Health Check**:
  ```bash
  curl https://your-app.vercel.app/health
  # Response: {"status": "healthy"}
  ```

- **Interactive Swagger Docs**:
  Open `https://your-app.vercel.app/docs` in your browser.

- **Scenarios Endpoint**:
  ```bash
  curl https://your-app.vercel.app/api/v1/scenarios
  ```
