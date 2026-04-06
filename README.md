# ⚡ TalentAI v6.0 — Enterprise Recruitment Platform
SQLAlchemy ORM · Works with ANY database · Streamlit Cloud ready

---

## 🗄️ Supported Databases

Just change one line in `.streamlit/secrets.toml`:

| Database | URL Format |
|---|---|
| **SQLite** (local, zero setup) | `sqlite:///talentai.db` |
| **MySQL** (local) | `mysql+pymysql://root:pass@localhost/talentai_db` |
| **PostgreSQL** | `postgresql+psycopg2://user:pass@host:5432/db` |
| **Supabase** (free cloud) | `postgresql+psycopg2://user:pass@host:5432/db?sslmode=require` |
| **Neon** (free cloud) | `postgresql+psycopg2://user:pass@host/db?sslmode=require` |
| **Railway** | `mysql+pymysql://user:pass@host:port/db` |
| **PlanetScale** | `mysql+pymysql://user:pass@host/db?ssl_ca=/etc/ssl/certs/ca-certificates.crt` |

---

## 🚀 Local Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your database URL
Edit `.streamlit/secrets.toml`:
```toml
[database]
url = "mysql+pymysql://root:YOUR_PASSWORD@localhost/talentai_db"
```

### 3. Run
```bash
streamlit run app.py
```
Tables are **auto-created** on first launch. No SQL scripts needed.

---

## ☁️ Deploy to Streamlit Cloud

1. Push to a **GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select repo, branch `main`, file `app.py`
4. **Advanced settings → Secrets**, paste:

```toml
[database]
url = "postgresql+psycopg2://user:pass@host/db?sslmode=require"
```

### Free Cloud Databases for Streamlit Cloud:
- **[Supabase](https://supabase.com)** — PostgreSQL, 500MB free, web dashboard
- **[Neon](https://neon.tech)** — PostgreSQL, serverless, 512MB free
- **[PlanetScale](https://planetscale.com)** — MySQL compatible, 5GB free
- **[Railway](https://railway.app)** — MySQL/PostgreSQL, $5 credit/month free

---

## 📁 Structure
```
TalentAI_Complete/
├── app.py                    ← Main entry point
├── requirements.txt          ← SQLAlchemy + drivers
├── .streamlit/
│   ├── config.toml           ← Theme
│   └── secrets.toml          ← DATABASE_URL ← change this
├── database/
│   └── database.py           ← SQLAlchemy ORM (DB-agnostic)
├── modules/                  ← All page modules
└── utils/
    ├── resume_parser.py
    └── bert_scorer.py
```
