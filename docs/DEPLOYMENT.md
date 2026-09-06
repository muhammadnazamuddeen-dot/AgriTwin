# AgriTwin AI — Production Deployment Guide

## Overview

This guide provides instructions for deploying AgriTwin AI on production infrastructure (e.g., Render, Railway, Vercel, AWS, or Docker containers).

---

## 1. Docker Deployment (Recommended)

The repository includes a production-ready `docker-compose.yml` for unified stack deployment.

```bash
# Build and start services
docker-compose up --build -d

# Verify running containers
docker-compose ps

# Check logs
docker-compose logs -f backend
```

---

## 2. Separate Service Deployment

### Backend (Render / Railway / AWS EC2)
- **Runtime:** Python 3.11 / 3.12
- **Build Command:** `pip install -r backend/requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Environment Variables:** Set environment variables specified in `.env.example`.

### Frontend (Vercel / Netlify)
- **Framework:** Next.js 16 (App Router)
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `.next`
- **Environment Variable:** `NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.onrender.com`

---

## 3. Database Migration (SQLite to PostgreSQL + PostGIS)

To migrate from SQLite to PostgreSQL for multi-region scale:

1. Update `DATABASE_URL` in environment:
   ```env
   DATABASE_URL="postgresql://agritwin:your_secure_password@db.example.com:5432/agritwin_prod"
   ```
2. Run Alembic migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```
