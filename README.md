# 🔍 The Sentinel (Visual Vibe Auditor)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-00a393.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)

An autonomous QA & Vibe Engineering Agent that watches video of an app's behavior, compares it to the codebase/design spec, and autonomously writes the code fix to match the intended "vibe."

## 🎯 One-Line Pitch

> **Input:** GitHub Repo URL + Screen Recording (Video) OR Screenshots (Images) OR Deployed URL  
> **Reasoning:** Spatial-Temporal analysis (Video) or Visual Reference (Images) vs. the code logic  
> **Output:** A precise Code Fix and a Pull Request

## ✨ Features

- 🤖 **AI-Powered Analysis**: Uses Google's Gemini AI to analyze visual context and code
- 🎥 **Multi-Modal Input**: Accepts video recordings, screenshots, or live URLs
- 🔍 **Smart File Scouting**: Automatically identifies relevant files in your codebase
- 📝 **Automated PR Creation**: Creates pull requests with fixes directly on GitHub
- 🔄 **Self-Correction Loop**: Monitors CI/CD and auto-corrects if builds fail
- 🔐 **Secure Authentication**: JWT-based auth with GitHub OAuth integration
- ⚡ **Rate Limiting**: Built-in protection against abuse
- 🎨 **Beautiful Dashboard**: Modern Next.js UI with real-time terminal output

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Next.js 16    │────────▶│   FastAPI        │────────▶│   Gemini AI     │
│   Dashboard     │  HTTP   │   Backend        │  API    │   Analysis      │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   GitHub API     │
                            │   PR Creation    │
                            └──────────────────┘
```

### Tech Stack

**Frontend:**
- Next.js 16 (App Router)
- TypeScript
- Tailwind CSS
- Shadcn UI components

**Backend:**
- Python 3.11+
- FastAPI
- Google Generative AI SDK
- PyGithub
- Playwright (for URL screenshot capture)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- GitHub Personal Access Token
- Google Gemini API Key

### 1. Clone & Setup

```bash
git clone <repository-url>
cd vibe-auditor
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

**Required Environment Variables:**

```env
# AI
GEMINI_API_KEY=your_gemini_api_key_here

# GitHub
GITHUB_TOKEN=your_github_token_here
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret

# Auth
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
FRONTEND_URL=http://localhost:3000
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 4. Run Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
.venv\Scripts\activate  # or source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access the Application

- Dashboard: http://localhost:3000/dashboard
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/api/v1/health

## 📖 API Documentation

### POST /api/v1/analyze

Analyze visual context and generate code fixes.

**Rate Limit:** 5 requests/hour

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer <token>" \
  -F "repo_url=https://github.com/user/repo" \
  -F "deployed_url=https://myapp.vercel.app" \
  -F "bug_description=Button colors don't match design" \
  -F "video=@recording.mp4"
```

**Response:**
```json
{
  "status": "success",
  "job_id": "12345-uuid",
  "analysis": {
    "analysis": "Button background color mismatch: found #3b82f6, expected #00ff00",
    "severity": "Medium",
    "fix": {
      "file_path": "src/components/Button.tsx",
      "code": "export const Button = () => {\n  return (\n    <button className=\"px-4 py-2 bg-[#00ff00] text-black rounded\">\n      Submit\n    </button>\n  );\n};"
    }
  },
  "pr_url": "https://github.com/user/repo/pull/42",
  "screenshots_captured": ["/tmp/capture_abc123_full.png"],
  "error": null
}
```

### Authentication Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/github` - GitHub OAuth redirect
- `GET /api/v1/auth/me` - Get current user

## 🔄 The Vibe Loop

Our patented "Vibe Loop" implementation:

1. **Ingest** - Capture visual context from video/images/URLs
2. **Scout** - Identify relevant files in the codebase
3. **Analyze** - AI compares visuals to code logic
4. **Generate** - Create precise code fixes
5. **Execute** - Commit to branch and create PR
6. **Verify** - Monitor CI/CD and self-correct if needed

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
pytest tests/
```

### Run Frontend Tests

```bash
cd frontend
npm test
```

## 📝 Usage Example

1. **Login** to the dashboard
2. **Upload** a screen recording or enter a deployed URL
3. **Enter** your GitHub repository URL
4. **Describe** the bug (optional but helpful)
5. **Click** "ANALYZE VIBE"
6. **Wait** as the AI analyzes and creates a PR
7. **Review** the PR on GitHub and merge!

## 🛡️ Security

- JWT-based authentication with secure token storage
- Rate limiting on all public endpoints
- CORS protection
- No secrets logged or exposed
- Input validation on all endpoints

## 🎨 Customization

### Adding Custom Themes

Edit `frontend/tailwind.config.ts`:

```typescript
colors: {
  vibe: {
    green: '#00ff00',
    lime: '#7fff00',
    glow: '#22c55e',
  },
}
```

### Modifying System Prompts

Edit `backend/app/services/gemini_service.py`:

```python
SYSTEM_PROMPT_SENTINEL = """Your custom prompt here..."""
```

## 🚢 Deployment

### Backend Deployment (Render/Railway)

1. Push code to GitHub
2. Connect repository to Render/Railway
3. Set environment variables
4. Deploy!

### Frontend Deployment (Vercel)

```bash
cd frontend
vercel --prod
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini API for the AI capabilities
- FastAPI team for the excellent framework
- Next.js team for the React framework
- All contributors and testers

## 📞 Support

- GitHub Issues: [Report a bug](https://github.com/yourusername/vibe-auditor/issues)
- Documentation: [Full Docs](https://docs.vibechecker.app)
- Email: support@vibechecker.app

---

<p align="center">
  <strong>Built with 💚 by The Sentinel Team</strong><br>
  <em>Engineering the Perfect Vibe</em>
</p>
"# the-Sentinel" 
