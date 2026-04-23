# Shredly

Shredly is a calorie tracker and personal fitness coach app built to help users set fitness goals, track their progress, and stay on top of their health journey — all in one place.

> **Work in Progress** — Shredly is currently a backend-heavy project. A full frontend (React or similar) is planned once the API layer is solid and production-ready.

---

## What Shredly Will Do (Full Vision)

When fully built, Shredly will:

- Allow users to register, log in, and manage a personal fitness profile
- Track daily calorie intake and macronutrient breakdown
- Set and monitor weight loss / gain goals with a target date
- Act as a personal fitness coach by providing recommendations based on activity level, current weight, and goal weight
- Generate progress reports and insights over time
- Send email notifications for things like password resets and goal milestones
- Expose a clean REST API ready for a React frontend to consume

---

## Previous Version

An earlier version of Shredly was built using **Flask**. This version is a full rebuild using **FastAPI**, with a focus on async performance, better data validation, and a cleaner architecture built to scale toward a production deployment.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Framework | FastAPI |
| Database | SQLite (via `aiosqlite`) |
| ORM | SQLAlchemy (async) |
| Authentication | PyJWT (HS256), OAuth2 Bearer |
| Password Hashing | `pwdlib` with Argon2 |
| Data Validation | Pydantic v2 |
| Email | Resend API |
| Settings | `pydantic-settings` (.env) |
| Package Manager | `uv` |
| Server | Uvicorn |

---

## What's Already Implemented

### Authentication (`auth.py`)
- `POST /register` — Create a new user account with validated username, email, and password
- `POST /login` — Authenticate and receive a JWT bearer token
- `POST /reset-password-email` — Trigger a password reset email via Resend (runs as a background task)

### User Profiles (`users.py`)
- `POST /users/profile` — Create a fitness profile (protected route, one profile per user enforced)
- `PATCH /users/profile` — Edit an existing profile with partial updates (only fields sent are updated)

### Security (`security.py`)
- Password hashing and verification using Argon2
- JWT creation and decoding
- `get_current_user` dependency that protects routes and identifies the authenticated user

### Database (`database.py`, `models.py`)
- Async SQLite engine with SQLAlchemy
- `Users` and `UserProfile` models with a one-to-one relationship
- Tables auto-created on startup via lifespan — no migration files needed

### Email Service (`services/email.py`)
- Reusable email utility using the Resend API
- Password reset email with a tokenized link

### Validation (`schemas.py`)
- Password complexity enforcement (min 8 chars, uppercase, lowercase, digit, special character)
- Username length enforcement (min 8 chars)
- Partial update schema for profile editing

---

## Issues Encountered During Development

- **SQLAlchemy object expiry after commit** — After calling `db.commit()`, SQLAlchemy expires ORM object attributes by default. Had to set `expire_on_commit=False` on the session factory to avoid detached instance errors when returning data after a commit.
- **Misleading variable names** — A variable named `existing_user` was actually holding a `UserProfile` result, which caused confusion when reading the duplicate profile guard logic. Renamed for clarity.
- **Malformed JSON in testing** — A float value written as `6.` (missing trailing digit) caused a `422 Unprocessable Content` JSON decode error when testing via Swagger docs. Valid floats require digits on both sides of the decimal point (e.g., `6.0`).
- **Understanding 400 vs 422 errors** — 400 errors come from intentional business logic guards (e.g., duplicate profile). 422 errors come from Pydantic/FastAPI failing to parse the request body before it hits route logic.

---

## Requirements

Create a `.env` file at the project root with the following:

```
DATABASE_URL=sqlite+aiosqlite:///./app.db
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
RESEND_API_KEY=<your-resend-api-key>
```

---

## How to Run

**Install dependencies:**

```bash
uv sync
```

**Start the development server:**

```bash
uv run uvicorn main:app --reload
```

**Or run directly:**

```bash
uv run python main.py
```

The app runs at `http://127.0.0.1:8000`

Interactive API docs (Swagger UI) are available at `http://127.0.0.1:8000/docs`

---

## How to Use the API

1. **Register** — `POST /register` with your name, email, username, and password
2. **Login** — `POST /login` to receive a JWT bearer token
3. **Authorize** — Use the token in the `Authorization: Bearer <token>` header for all protected routes
4. **Create your profile** — `POST /users/profile` with your fitness details
5. **Update your profile** — `PATCH /users/profile` with only the fields you want to change

---


## Status

Shredly is an active work in progress. The backend API is the current focus. Frontend integration is planned as the next major phase once the API is stable and fully tested.
