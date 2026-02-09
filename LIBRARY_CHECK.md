# Project Dependencies & Status Report

This document lists all libraries planned for The VibeChecker (Sentinel) backend and frontend, verifying their current status.

## Backend (Python)

All packages are confirmed to be available on PyPI and compatible with Python 3.11+.

| Library | Version (Target) | Status | Notes |
| :--- | :--- | :--- | :--- |
| `fastapi` | `0.111.0` | ✅ Active | Core framework. Very stable. |
| `uvicorn[standard]` | `0.29.0` | ✅ Active | ASGI Server. Standard for FastAPI. |
| `google-generativeai` | `0.5.2` | ✅ Active | Official Gemini SDK. Frequently updated. |
| `pygithub` | `2.3.0` | ✅ Active | Standard GitHub API wrapper. |
| `python-multipart` | `0.0.9` | ✅ Active | Required for Form Data parsing. |
| `pydantic-settings` | `2.2.1` | ✅ Active | Standard for `.env` management in Pydantic V2. |
| `asyncpg` | `0.29.0` | ✅ Active | High-perf PostgreSQL driver (for prod). |
| `sqlalchemy[asyncio]` | `2.0.30` | ✅ Active | ORM. V2.0 is the modern standard. |
| `aiosqlite` | `0.20.0` | ✅ Active | Async SQLite driver (for dev/testing). |
| `fastapi-users` | `13.0.0` | ⚠️ Maintenance | In maintenance mode but widely used & stable. Good for Hackathons. |
| `fastapi-mail` | `1.4.1` | ✅ Active | Simple email sending for FastAPI. |
| `slowapi` | `0.1.9` | ✅ Active | Rate limiting. actively maintained wrapper around `limits`. |
| `httpx` | `0.27.0` | ✅ Active | Async HTTP client. |

**Verdict:** All Backend libraries are safe to use. `fastapi-users` is in maintenance but is the industry standard for quick auth setup in FastAPI.

---

## Frontend (Node.js / React)

Libraries to be installed via `npm` / `npx`.

| Library | Target | Status | Notes |
| :--- | :--- | :--- | :--- |
| `next` | `latest` (v16.x) | ✅ Active | User requested v16+. Current stable is v16.1+. |
| `react` | `latest` (v19) | ✅ Active | React 19 is now RC/Stable for Next.js 15+. |
| `react-dom` | `latest` (v19) | ✅ Active | Matches React version. |
| `tailwindcss` | `latest` (v3.4+) | ✅ Active | Standard utility-first CSS. |
| `shadcn-ui` | `latest` | ✅ Active | Component library (cli-based). |
| `lucide-react` | `latest` | ✅ Active | Standard icon set for Shadcn. |
| `axios` | `latest` | ✅ Active | HTTP Client. (Can also use `ky` or `fetch`). |
| `framer-motion` | `latest` | ✅ Active | Animation library. |
| `react-dropzone` | `latest` | ✅ Active | Drag & drop file upload. |
| `zod` | `latest` | ✅ Active | Schema validation (matches Pydantic on backend). |
| `react-hook-form` | `latest` | ✅ Active | Form state management. |
| `sonner` | `latest` | ✅ Active | Toast notifications (modern replacement for `react-hot-toast`). |

**Verdict:** All Frontend libraries are modern, standard, and actively maintained. Next.js 16 is cutting edge but stable enough for our needs.

---

## Next Steps

1.  Proceed with `pip install -r backend/requirements.txt` (using the verified list).
2.  Proceed with `npx create-next-app@latest frontend` and install the listed dependencies.
