# DevAPI Hub 🚀

A full-stack API marketplace platform where developers can publish, discover, test, and manage REST APIs — complete with authentication, API key management, ratings, comments, and an admin panel.

---

## ✨ Features

- **Browse & Discover** — Explore community-published APIs with live search and category filters
- **API Key Management** — Every user gets a unique API key on registration, regeneratable anytime
- **Publish APIs** — List any REST endpoint with name, description, category, and endpoint URL
- **Edit & Delete** — Full control over your own published APIs
- **Live Test Console** — Fire real GET requests and inspect JSON responses, status codes, and timing
- **Ratings System** — Community star ratings with rolling average calculation
- **Comments & Discussion** — Leave feedback on any API, admin can moderate
- **Admin Panel** — User management, request logs, and full moderation controls
- **Rate Limiting** — 30 requests/minute per API key with proper `X-RateLimit-*` headers
- **Request Logging** — Every API call logged with status, IP, and timestamp
- **Developer Profiles** — Public profiles showing each developer's published APIs
- **Built-in APIs** — `/api/weather`, `/api/joke`, `/api/status` ready to test out of the box
- **Cinematic Transitions** — Smooth 3-panel curtain page transitions
- **Responsive Design** — Works on desktop and mobile

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| Database | SQLite |
| Auth | Werkzeug (PBKDF2-SHA256 password hashing) |
| Frontend | HTML + CSS + Vanilla JS |
| Fonts | Outfit + Fira Code (Google Fonts) |

---

## 📁 Project Structure

```
Gen_API/
├── app.py              # App entry point — registers blueprints and error handlers
├── database.py         # DB connection, table creation, migrations
├── helpers.py          # Sanitization, rate limiting, decorators, URL validation
├── routes/
│   ├── __init__.py
│   ├── auth.py         # Register, login, logout
│   ├── dashboard.py    # Dashboard, regenerate API key
│   ├── apis.py         # Publish, edit, delete, view, rate APIs
│   ├── comments.py     # Add and delete comments
│   ├── admin.py        # Admin panel, delete users
│   ├── protected.py    # Protected API endpoints (/api/weather, /api/joke, /api/status)
│   └── pages.py        # Home, about, search, test console, health check
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── add_api.html
    ├── edit_api.html
    ├── api_details.html
    ├── api_key.html
    ├── api_test.html
    ├── developer.html
    ├── rate_api.html
    ├── admin.html
    ├── about.html
    └── 404.html
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/ShamGaneshan2008/devapi-hub.git
cd devapi-hub
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install flask werkzeug requests
```

### 5. Run the app

```bash
python app.py
```

### 6. Open in browser

```
http://127.0.0.1:5000
```

The database is created automatically on first run. The first user to register becomes **Admin**.

---

## 🔑 Built-in API Endpoints

All endpoints require a valid API key — get yours from the Dashboard after registering.

| Endpoint | Description |
|---|---|
| `GET /api/weather?key=YOUR_KEY` | Returns weather data for London |
| `GET /api/joke?key=YOUR_KEY` | Returns a random developer joke |
| `GET /api/status?key=YOUR_KEY` | Returns your usage stats and rate limit info |
| `GET /health` | Platform health check (no key required) |
| `GET /search?q=query&cat=ai` | Paginated JSON search (no key required) |

You can also pass your key as a header instead of a query param:
```
X-API-Key: YOUR_KEY
```

---

## 👑 Admin Access

The **first user to register** automatically becomes Admin. Admin features:

- Gold `👑 Admin` badge visible in the navbar and on your profile
- Access to `/admin` — view all users, all APIs, and last 50 request logs
- Delete any user or API from the platform
- Delete any comment on any API page

---

## 📸 Pages

| Route | Description |
|---|---|
| `/` | Homepage — browse and search all APIs |
| `/register` | Create an account |
| `/login` | Sign in |
| `/dashboard` | Your API key, published APIs, and request logs |
| `/add_api` | Publish a new API |
| `/edit_api/<id>` | Edit your API listing |
| `/api/<id>` | API detail page with ratings and comments |
| `/developer/<username>` | Public developer profile |
| `/api_test` | Live API test console |
| `/about` | About the platform |
| `/admin` | Admin panel (admin only) |

---

## 🔒 Security

- Passwords hashed with **PBKDF2-SHA256** via Werkzeug — never stored as plain text
- All form inputs sanitized — strips control characters, enforces max lengths
- Parameterized SQL queries — no SQL injection possible
- SSRF protection — test console blocks requests to internal/private addresses
- Rate limiting — 30 requests/minute per API key
- Admin routes protected by dual decorators (`@login_required` + `@admin_required`)
- Delete actions use POST forms — not GET links

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

Built with ❤️ using Python & Flask