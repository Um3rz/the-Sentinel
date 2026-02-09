# 📂 FINAL_SENTINEL_CONTEXT.md

**Status:** APPROVED
**Version:** 1.0
**Date:** 2026-02-09

---

## 1. Project Overview

**Product Name:** The VibeChecker (Visual Vibe Auditor)
**Type:** Autonomous QA & Vibe Engineering Agent (SaaS Dashboard)
**Hackathon Track:** Vibe Engineering / The Marathon Agent
**One-Line Pitch:** An autonomous agent that watches video of an app's behavior, compares it to the codebase/design spec (1M token context), and autonomously writes the code fix to match the intended "vibe."

### Core Value Prop

* **Input:** GitHub Repo URL + Screen Recording (Video) OR Screenshots (Images) OR Deployed URL + Optional Bug Description.
* **Reasoning:** Spatial-Temporal analysis (Video) or Visual Reference (Images) vs. the code logic.
* **Output:** A precise Code Fix and a Pull Request.

---

## 2. Technical Architecture

### **Frontend (The Dashboard)**

* **Framework:** Next.js 16 (App Router).
* **Styling:** Tailwind CSS + Shadcn UI (for speed and polish).
* **State Management:** React Hooks / Context API.
* **Deployment:** Vercel (recommended) or local `localhost:3000`.

### **Backend (The Brain)**

* **Language:** Python 3.11+.
* **Framework:** FastAPI (high performance, auto-OpenAPI docs).
* **AI Engine:** Google Generative AI SDK (`google-generativeai`).
* **Visual Engine:** Playwright (Headless Browser for capturing deployed URLs).
* **Integrations:** `PyGithub` and GitHub OAuth (for secure, per-user Repo fetching & PR creation).
* **Authentication:** JWT-based Auth (FastAPI Users or custom) + Email Verification (`fastapi-mail`).
* **Rate Limiting:** `slowapi` (based on `limits`) for all endpoints.
* **Deployment:** Render / Google Cloud Run / `localhost:8000`.

---

## 3. Strict Coding Standards & Guidelines (Judging Criteria: 40%)

*All generated code must adhere to these rules to ensure "Quality Application Development."*

### **General Principles**

1. **Functional over Class-based:** Use functional programming where possible (React Components, Python utility functions).
2. **Type Safety:** Strict typing is **mandatory**.
3. **Error Handling:** No silent failures. Every API call and AI interaction must have `try/except` blocks with meaningful error logging.
4. **Comments:** Docstrings for every function explaining *Input*, *Output*, and *Logic*.

### **Python (Backend)**

* **Standard:** PEP 8 compliance.
* **Type Hints:** Must use Python `typing` (`List`, `Optional`, `Dict`, `Any`) and Pydantic Models for all data structures.
* **Linter:** Code should pass `flake8` or `ruff`.
* **Async/Await:** Use `async` for all I/O bound operations (Gemini API calls, GitHub API calls).
* **Security:** Start all endpoints with Dependency Injection for Auth (except login/register).
* **Rate Limits:** Apply `@limiter.limit("5/minute")` (or appropriate) to all public endpoints.
* **Project Structure:**
```text
/backend
  /app
    /api        # Routes (endpoints)
    /core       # Config (env vars)
    /services   # Business logic (Gemini, GitHub)
    /models     # Pydantic schemas
  main.py       # Entry point
```

### **TypeScript/React (Frontend)**

* **Components:** Functional components only. Use strict `interface` for Props.
* **Hooks:** Use `useState`, `useEffect`, and custom hooks for logic separation.
* **Fetching:** Use `fetch` or `axios` with strictly typed responses.
* **UI:** Mobile-responsive by default (Tailwind).

### **API Specification (OpenAPI/Swagger)**

* The API must expose a valid `openapi.json`.
* Use Pydantic models to define Request/Response schemas automatically.

---

## 4. The "Vibe Loop" Implementation Logic

Since we cannot build a full sandboxed OS in 24 hours, we simulate the "Antigravity" loop using **Chain-of-Thought** prompting.

### **Backend Workflow (The `analyze_vibe` endpoint)**

1. **Ingest (Smart Scouting):**
* **Step A (Map):** Fetch the Repository File Tree (list of paths).
* **Step B (Scout):** Send File Tree + User's Bug Description + Video/URL Summary to Gemini (Flash Model). Ask: "Which files are likely relevant to this bug? Return a list of file paths."
* **Step C (Fetch):** Fetch raw text ONLY for the identified relevant files (e.g., `Button.tsx`, `index.css`).
* **Step D (Assemble):** Construct a highly relevant, optimized Context string.
* **Step E (Capture - Optional):** If a `deployed_url` is provided, use **Playwright** to capture high-fidelity screenshots of the current state.

2. **Gemini Call (The Fixer):**
* **Model:** `gemini-2.0-flash-exp` (or `gemini-3-flash` if available).
* **Input:** Optimized Context + Video/Screenshots (User uploaded or Playwright captured) + Bug Description.
* **Reasoning:** Analyze the provided code + video. Identify the discrepancy.
* **Output:** Generate the JSON with the fix.

3. **Output Parsing:**
* The model returns JSON:
```json
{
  "visual_analysis": "Button turns red, spec implies blue.",
  "timestamp": "00:04",
  "file_to_change": "src/components/Button.tsx",
  "original_code_snippet": "...",
  "fixed_code_snippet": "..."
}
```

4. **Execution:**
* Backend creates a new branch `fix-vibe-{id}`.
* Backend commits the `fixed_code_snippet` to `file_to_change`.
* Backend opens a PR.

5. **Verification & Iteration (The "Marathon" Loop):**
* **Monitor:** The Agent polls the PR for CI/CD status (GitHub Actions).
* **Detect:** If Build/Lint fails, the Agent reads the error logs.
* **Refine:** The Agent effectively "Self-Corrects" by sending the Error Log + Failed Code back to Gemini.
* **Push:** The Agent pushes a new commit to fix the build error.
* **Repeat:** Until CI is Green.

---

## 5. System Prompts (The "Brain")

**Role:** `SYSTEM_PROMPT_SENTINEL`

> "You are The Sentinel, an elite Design Engineer and QA Specialist.
> You possess 'Vibe Intelligence'—the ability to map visual behavior in a video to the underlying code logic.
> **Your Task:**
> 1. Watch the provided video frame-by-frame OR analyze provided screenshots.
> 2. Read the provided Codebase Context and Bug Description (if any).
> 3. Identify where the Codebase implementation diverges from the visual behavior seen in the media (or where it conflicts with the bug description).
> 4. Generate the SPECIFIC code fix. Do not explain *how* to fix it; provide the *actual code block* to replace.
> 
> **Output Format (JSON Only):**
> {
> "analysis": "Short description of the visual bug",
> "severity": "High/Medium/Low",
> "fix": {
> "file_path": "path/to/file",
> "code": "The full corrected code block"
> }
> }"

---

## 6. API Endpoints Specification

### `POST /api/v1/analyze`

**Summary:** Uploads video and repo info to trigger the agent. **[Rate Limit: 5/hour]**
**Security:** Bearer Token required.
**Request (Form Data):**
* `video`: File (MP4/WebM) - Optional
* `images`: List[File] (PNG/JPG) - Optional, Multiple
* `deployed_url`: String (e.g. "https://myapp.vercel.app") - Optional
* `bug_description`: String (Text) - Optional
* `repo_url`: String (e.g., "https://github.com/user/repo")
* `github_token`: String (Optional, for private repos)

**Response (JSON):**
```json
{
  "status": "success",
  "job_id": "12345",
  "analysis": {
    "issue": "Animation timing function is linear, should be ease-out.",
    "timestamp": "0:02"
  },
  "pr_url": "https://github.com/user/repo/pull/42"
}
```

### `POST /api/v1/auth/register`
**Summary:** Register a new user and send verification email.
**Request:** `{"email": "user@example.com", "password": "securepassword"}`

### `POST /api/v1/auth/login`
**Summary:** Login and get access token.
**Request:** `{"username": "user@example.com", "password": "securepassword"}`
**Response:** `{"access_token": "jwt_token...", "token_type": "bearer"}`

### `POST /api/v1/auth/verify`
**Summary:** Verify email address using token from email.

### `GET /api/v1/health`

**Summary:** Simple health check for the judges to see the API is live. **[Rate Limit: 60/minute]**
**Response:** `{"status": "ok", "version": "0.1.0"}`

---

## 7. Execution Plan (Phase-wise)

This plan is optimized for a 24-48 hour Hackathon timeline.

### **Phase 1: Project Scaffolding & Environment Setup**
**Goal:** Establish a working "Hello World" for both Frontend and Backend.

1.  **Repository Initialization:**
    *   Create monorepo structure: `/frontend`, `/backend`.
    *   Initialize Git repository.
2.  **Backend Setup:**
    *   Set up Python virtual environment (`venv`).
    *   Install dependencies: `fastapi`, `uvicorn`, `google-generativeai`, `pygithub`, `python-multipart`, `pydantic-settings`, `playwright`, `pytest-playwright`.
    *   Create `main.py` with `/api/v1/health` endpoint.
    *   Configure environment variables (`.env`).
    *   Initialize Playwright browsers (`playwright install`).
3.  **Frontend Setup:**
    *   Install Shadcn UI and Tailwind CSS.
    *   Create a basic landing page verifying backend connection.

### **Phase 1.5: Security Layer (Auth & Rate Limits)**
**Goal:** Secure the API before building core logic.

1.  **Rate Limiting:**
    *   Setup `slowapi`. Configure global limits and specific endpoint limits.
2.  **Authentication:**
    *   Implement User Model (SQLAlchemy/Tortoise ORM/Pydantic).
    *   Implement JWT generation/validation logic.
    *   Implement `/register`, `/login` endpoints.
    *   Setup `fastapi-mail` for sending verification codes.
    *   Protect routes with `Depends(get_current_user)`.

### **Phase 2: The Core "Brain" (Backend Logic)**
**Goal:** Implement the logic to fetch code, analyze video, and generate fixes.

1.  **Service Integration - GitHub:**
    *   Implement `GitHubService` to fetch file contents from a given repo URL.
    *   Implement method to create a branch and commit changes.
    *   Implement method to open a Pull Request.
2.  **Service Integration - Gemini:**
    *   Implement `GeminiService` to initialize the model with the System Prompt.
    *   Implement `analyze_video(video_path, code_context)` function.
    *   Ensure strict JSON output parsing from Gemini response.
3.  **API Implementation:**
    *   Implement `POST /api/v1/analyze`.
    *   Handle file upload (video) and form data (repo URL).
    *   Orchestrate the flow: Upload -> Fetch Code -> Call Gemini -> Create PR.

### **Phase 3: The Dashboard (Frontend UI)**
**Goal:** A clean, high-vibe interface for users to submit requests.

1.  **UI Components:**
    *   Create `MediaUpload` component (drag & drop for Video OR Images OR URL Input).
    *   Create `BugDescription` component (TextArea - Optional).
    *   Create `RepoInput` component.
    *   Create `AnalysisStatus` component (stepper/loader to show progress).
    *   Create `ResultCard` component (displays PR link and analysis summary).
    *   **Figma Integration:** Strictly follow the provided `figma-screens/` mockups for all UI components.
        *   `home-screen.png` -> Landing Page
        *   `dashboard.png` -> Main Dashboard
        *   `login-signup.png` -> Auth Pages
2.  **State Management:**
    *   Manage upload state, processing state, and error handling.
3.  **API Integration:**
    *   Connect the Frontend form to `POST /api/v1/analyze`.

### **Phase 4: Integration & The "Vibe Loop"**
**Goal:** Connect all pieces and verify the end-to-end flow.

1.  **End-to-End Test:**
    *   Run the system with a sample video and a target "playground" repository.
    *   Verify that the "Vibe Loop" completes: Video in -> PR out.
2.  **Verification Loop Implementation:**
    *   Implement logic to poll GitHub PR checks.
    *   Implement "Error Log Analysis" prompt for Gemini.
    *   Implement iterative commit logic.
3.  **Refinement:**
    *   Tune the System Prompt based on results (adjust for better code accuracy).
    *   Handle edge cases (e.g., invalid repo URL, rate limits).

### **Phase 5: Polish & Final Review**
**Goal:** Ensure the project is demo-ready and adheres to all coding standards.

1.  **Code Quality Check:**
    *   Run linters (`flake8`/`ruff` for Python, `eslint` for TS).
    *   Add docstrings and type hints where missing.
2.  **UI Polish:**
    *   Add transitions/animations.
    *   Ensure responsive design.
3.  **Documentation:**
    *   Generate `README.md` with setup instructions.
    *   Verify `openapi.json` is accessible.

---

## 8. Testing Strategy

### **Unit Testing**
*   **Backend:** Use `pytest`.
    *   Test `GitHubService` with mocked API responses (ensure it constructs PRs correctly).
    *   Test `GeminiService` prompt construction (ensure context is formatted correctly).
    *   Test API endpoints for validation errors (missing fields, wrong file types).
*   **Frontend:** Use Manual Testing (due to Hackathon constraints) or basic `Jest` snapshots for key components.

### **Integration Testing**
*   **Gemini Integration:** Create a script to send a dummy video + text prompt to Gemini and verify it returns valid JSON.
*   **GitHub Integration:** Create a script to fetch a public repo's file list to verify token permissions and API logic.

### **User Acceptance Testing (UAT)**
*   **The Happy Path:**
    1.  User opens Dashboard.
    2.  User pastes a valid GitHub Repo URL.
    3.  User uploads a short screen recording (MP4).
    4.  User clicks "Analyze".
    5.  System displays "Analyzing...".
    6.  System displays "Fix Generated!" with a clickable Link to the PR.
    7.  User clicks Link -> Github PR opens showing correct changes.

---

**[END OF FINAL CONTEXT DOCUMENT]**
