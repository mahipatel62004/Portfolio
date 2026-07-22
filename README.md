# Mahi Patel — Portfolio (Python Flask + PostgreSQL)

A full portfolio site with a working "Let's Connect" inquiry form backed by a real Flask API,
PostgreSQL database, email notifications, and an admin dashboard for managing inquiries.

## Structure

```
mahi-portfolio/
├── backend/                 Python Flask API
│   ├── app.py                App factory + entrypoint
│   ├── config.py             Env-driven configuration
│   ├── extensions.py         db, migrate, mail, limiter instances
│   ├── models.py             Inquiry model (SQLAlchemy)
│   ├── schemas.py            Marshmallow validation (create/update)
│   ├── routes/inquiries.py   REST API endpoints
│   ├── utils/mailer.py       Email notification on new inquiry
│   ├── utils/auth.py         Admin API key guard
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 Static site (no build step)
    ├── index.html             Public portfolio (About, Mission, What I Build, Connect)
    ├── admin.html             Admin "Inquiries" dashboard
    ├── css/style.css, admin.css
    └── js/main.js, admin.js
```

## 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then fill in real values
```

Create the PostgreSQL database, then run migrations:

```bash
flask --app app db init
flask --app app db migrate -m "init"
flask --app app db upgrade
```

Run the API:

```bash
python app.py        # http://localhost:5000
```

Health check: `GET http://localhost:5000/api/health`

## 2. Frontend setup

The frontend is plain HTML/CSS/JS — no build tools required.

1. Open `frontend/index.html` with a local server (e.g. VS Code "Live Server", or `python -m http.server 5500` from the `frontend/` folder).
2. If your API runs somewhere other than `http://localhost:5000/api`, set it before `main.js`/`admin.js` load:
   ```html
   <script>window.PORTFOLIO_API_BASE_URL = "https://your-api-domain.com/api";</script>
   <script src="js/main.js"></script>
   ```

## 3. Admin dashboard

Open `frontend/admin.html`, enter the `ADMIN_API_KEY` you set in `.env`. From there you can
search, filter by status, sort, open a full inquiry, mark it Read/Replied, or delete it.

## 4. API reference

| Method | Route                         | Auth        | Description                          |
|--------|--------------------------------|-------------|---------------------------------------|
| POST   | `/api/inquiries`               | Public, rate-limited | Submit a new inquiry            |
| GET    | `/api/inquiries`                | Admin key   | List/search/filter/sort inquiries    |
| GET    | `/api/inquiries/<id>`           | Admin key   | Get one inquiry in full              |
| PATCH  | `/api/inquiries/<id>/status`    | Admin key   | Update status (NEW/READ/REPLIED)     |
| DELETE | `/api/inquiries/<id>`           | Admin key   | Delete an inquiry                    |

Admin routes require header: `X-Admin-Key: <ADMIN_API_KEY>`

## 5. Security notes

- All secrets (DB URL, mail credentials, admin key) come from environment variables — nothing is hardcoded.
- Public submit route is rate-limited (5 requests / 15 min per IP) and protected by a honeypot field.
- Admin routes require a valid `X-Admin-Key` header.
- CORS is restricted to `CLIENT_ORIGIN`.
- Input is validated server-side with Marshmallow regardless of what the frontend sends.

## 6. Deployment notes

- Backend: run with `gunicorn app:app` behind a reverse proxy in production; set `FLASK_ENV=production`.
- Frontend: deploy the `frontend/` folder to any static host (Netlify, Vercel, GitHub Pages, S3, etc.) and point `PORTFOLIO_API_BASE_URL` at your deployed API.
- Use a real transactional mail provider (SendGrid, Mailgun, SES, etc.) in production instead of a personal Gmail account.
