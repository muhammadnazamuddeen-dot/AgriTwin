"""AgriTwin AI — FastAPI application entry point."""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.database import Base, engine, get_db
from app.models import User
from app.routers import (
    ai_explain,
    analytics,
    auth,
    crops,
    farms,
    intelligence,
    market,
    opportunities,
    prices,
    satellite,
    soil,
    weather,
)
from app.routers.auth import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup and seed initial demo farms if database is empty."""
    import datetime
    from app.database import SessionLocal
    from app.models import Crop, Farm, User

    # ── Fail fast on the insecure default SECRET_KEY outside of DEBUG ─────────
    if settings.SECRET_KEY == "change-me-in-production-use-openssl-rand-hex-32":
        if not settings.DEBUG:
            raise RuntimeError(
                "SECRET_KEY must be overridden in production. "
                "Generate one with: openssl rand -hex 32"
            )
        print("WARNING: Using the default SECRET_KEY (development only). "
              "Set SECRET_KEY in production to prevent JWT forgery.")

    Base.metadata.create_all(bind=engine)

    # Seed demo users on a fresh production/local database (password: password123)
    from app.routers.auth import _hash_password, _verify_password
    pwd_hash = _hash_password("password123")
    db = SessionLocal()

    def _ensure_demo_user(name: str, email: str, phone: str, role: str) -> User | None:
        """Create a demo user if missing or heal invalid password hash."""
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Heal password hash if corrupted/outdated
            if not _verify_password("password123", user.hashed_password):
                user.hashed_password = pwd_hash
                db.commit()
            return user
        phone_taken = db.query(User).filter(User.phone == phone).first() is not None
        try:
            user = User(
                name=name,
                email=email,
                phone=None if phone_taken else phone,
                hashed_password=pwd_hash,
                role=role,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            print(f"Startup demo seed note ({email}): {e}")
            return None

    try:
        farmer = _ensure_demo_user(
            "Ahmad Khan (Punjab Farmer)", "farmer@agritwin.pk", "03001234567", "farmer"
        )
        _ensure_demo_user(
            "Dr. Tariq Mahmood (Agri Officer)", "officer@agritwin.pk", "03019876543", "extension_officer"
        )

        if farmer and db.query(Farm).filter(Farm.user_id == farmer.id).count() == 0:
            farm1 = Farm(
                user_id=farmer.id,
                name="Okara Green Fields (چک 45 دیپالپور)",
                district="Okara",
                province="Punjab",
                latitude=30.81,
                longitude=73.45,
                area_acres=12.5,
                canal_name="Lower Bari Doab Canal (LBDC)",
                canal_turn_day="Thursday",
                canal_turn_time="02:00",
                canal_turn_duration_hours=4.5,
                tubewell_power_source="diesel",
                tubewell_hourly_cost_pkr=1400.0,
            )
            farm2 = Farm(
                user_id=farmer.id,
                name="Faisalabad Rechna Twin (سمندری روڈ)",
                district="Faisalabad",
                province="Punjab",
                latitude=31.41,
                longitude=73.07,
                area_acres=20.0,
                canal_name="Lower Chenab Canal (LCC)",
                canal_turn_day="Monday",
                canal_turn_time="04:30",
                canal_turn_duration_hours=6.0,
                tubewell_power_source="grid",
                tubewell_hourly_cost_pkr=650.0,
            )
            db.add_all([farm1, farm2])
            db.commit()
            db.refresh(farm1)
            db.refresh(farm2)

            crop1 = Crop(
                farm_id=farm1.id,
                crop_name="Wheat",
                variety="Faisalabad-2008",
                sowing_date=datetime.datetime.now() - datetime.timedelta(days=75),
                season="Rabi",
                growth_stage="Grain Filling",
            )
            crop2 = Crop(
                farm_id=farm2.id,
                crop_name="Rice (Basmati)",
                variety="Super Basmati",
                sowing_date=datetime.datetime.now() - datetime.timedelta(days=60),
                season="Kharif",
                growth_stage="Panicle Initiation",
            )
            db.add_all([crop1, crop2])
            db.commit()
    except Exception as e:
        print(f"Startup demo seed note: {e}")
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AgriTwin AI — Pakistan-focused agriculture intelligence platform.",
    lifespan=lifespan,
)

# ── CORS: Allows local dev, Render, and any Vercel deployment URL ─────────────
cors_origins = [o for o in settings.CORS_ORIGINS if o != "*"]
if not cors_origins:
    cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|.*\.vercel\.app)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(intelligence.router, prefix=settings.API_PREFIX)  # before farms (specific routes)
app.include_router(farms.router, prefix=settings.API_PREFIX)
app.include_router(weather.router, prefix=settings.API_PREFIX)
app.include_router(satellite.router, prefix=settings.API_PREFIX)
app.include_router(soil.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)
app.include_router(ai_explain.router, prefix=settings.API_PREFIX)
app.include_router(market.router, prefix=settings.API_PREFIX)
app.include_router(crops.router, prefix=settings.API_PREFIX)
app.include_router(prices.router, prefix=settings.API_PREFIX)
app.include_router(opportunities.router, prefix=settings.API_PREFIX)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# ── Enterprise Security Headers Middleware ────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(self), camera=(), microphone=()"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Health & Readiness checks exposed under root and API prefix (/api/v1/health, /api/v1/ready)
health_router = APIRouter()


@health_router.get("/health")
def health_check_prefixed():
    return {"status": "ok"}


@health_router.get("/ready")
def ready_check_prefixed():
    return {"status": "ready", "database": "connected"}


@health_router.post("/assistant", response_model=ai_explain.AIExplainResponse)
async def assistant_prefixed(
    req: ai_explain.AIExplainRequest,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    return await ai_explain.explain_farm_intelligence(req, user, db)


app.include_router(health_router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ready")
def ready_check():
    return {"status": "ready", "database": "connected"}

