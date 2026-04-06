"""
database/database.py — TalentAI SQLAlchemy Database Layer

Works with ANY database:
  MySQL      → DATABASE_URL = "mysql+pymysql://user:pass@host/db"
  PostgreSQL → DATABASE_URL = "postgresql+psycopg2://user:pass@host/db"
  Supabase   → DATABASE_URL = "postgresql+psycopg2://user:pass@host/db"
  Neon       → DATABASE_URL = "postgresql+psycopg2://user:pass@host/db?sslmode=require"
  SQLite     → DATABASE_URL = "sqlite:///talentai.db"

Set DATABASE_URL in .streamlit/secrets.toml (local) or
Streamlit Cloud → App Settings → Secrets.
"""

import streamlit as st
from sqlalchemy import (
    create_engine, text, Column, Integer, String,
    Float, DateTime, Date, Time, Text, ForeignKey,
    func, event
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool
from datetime import datetime
import os

# ──────────────────────────────────────────────────────────
# Connection — reads from st.secrets
# ──────────────────────────────────────────────────────────

def _get_url() -> str:
    """
    Read DATABASE_URL from st.secrets.
    Falls back to SQLite for local dev with no secrets file.
    """
    try:
        return st.secrets["database"]["url"]
    except Exception:
        # Local fallback — SQLite (zero config, works everywhere)
        db_path = os.path.join(os.path.dirname(__file__), "..", "talentai.db")
        return f"sqlite:///{os.path.abspath(db_path)}"


@st.cache_resource
def _engine():
    url = _get_url()
    kwargs = dict(echo=False)

    if url.startswith("sqlite"):
        # SQLite needs connect_args for thread safety
        from sqlalchemy.pool import StaticPool
        kwargs["connect_args"] = {"check_same_thread": False}
        kwargs["poolclass"]    = StaticPool
    else:
        kwargs["pool_size"]    = 5
        kwargs["pool_recycle"] = 280   # prevent stale connections
        kwargs["pool_pre_ping"] = True

    engine = create_engine(url, **kwargs)

    # Enable WAL mode for SQLite
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_wal(conn, _):
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")

    return engine


def _session() -> Session:
    SessionLocal = sessionmaker(bind=_engine(), autocommit=False, autoflush=False)
    return SessionLocal()


# ──────────────────────────────────────────────────────────
# ORM Models
# ──────────────────────────────────────────────────────────

Base = declarative_base()


class Candidate(Base):
    __tablename__ = "candidates"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(255), nullable=False)
    email       = Column(String(255), unique=True)
    phone       = Column(String(50))
    role        = Column(String(255))
    skills      = Column(Text)
    experience  = Column(Float, default=0)
    score       = Column(Float, default=0)
    status      = Column(String(50), default="Pending")
    resume_text = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobRole(Base):
    __tablename__ = "job_roles"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    title           = Column(String(255), nullable=False)
    description     = Column(Text)
    required_skills = Column(Text)
    min_experience  = Column(Float, default=0)
    created_at      = Column(DateTime, default=datetime.utcnow)


class Interview(Base):
    __tablename__ = "interviews"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id   = Column(Integer, ForeignKey("candidates.id", ondelete="SET NULL"), nullable=True)
    candidate_name = Column(String(255))
    role           = Column(String(255))
    interview_date = Column(Date)
    interview_time = Column(String(20))
    interviewer    = Column(String(255))
    mode           = Column(String(50), default="Online")
    status         = Column(String(50), default="Scheduled")
    notes          = Column(Text)
    created_at     = Column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────────────────────
# Bootstrap — create all tables
# ──────────────────────────────────────────────────────────

def create_database_if_not_exists():
    Base.metadata.create_all(_engine())


# ──────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────

def _row_to_dict(row) -> dict:
    """Convert ORM object to plain dict."""
    d = {}
    for col in row.__table__.columns:
        val = getattr(row, col.name)
        if isinstance(val, datetime):
            val = val.strftime("%Y-%m-%d %H:%M:%S")
        d[col.name] = val
    return d


# ──────────────────────────────────────────────────────────
# Candidates
# ──────────────────────────────────────────────────────────

def insert_candidate(name, email, phone, role, skills,
                     experience, score, resume_text) -> int:
    db = _session()
    try:
        existing = db.query(Candidate).filter(Candidate.email == email).first()
        if existing:
            existing.name        = name
            existing.phone       = phone
            existing.role        = role
            existing.skills      = skills
            existing.experience  = experience
            existing.score       = score
            existing.resume_text = resume_text
            existing.updated_at  = datetime.utcnow()
            db.commit()
            return existing.id
        else:
            c = Candidate(name=name, email=email, phone=phone, role=role,
                          skills=skills, experience=experience, score=score,
                          resume_text=resume_text, status="Pending")
            db.add(c)
            db.commit()
            db.refresh(c)
            return c.id
    finally:
        db.close()


def get_all_candidates() -> list[dict]:
    db = _session()
    try:
        rows = db.query(Candidate).order_by(Candidate.score.desc()).all()
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def get_candidates_by_role(role: str) -> list[dict]:
    db = _session()
    try:
        rows = (db.query(Candidate)
                  .filter(Candidate.role == role)
                  .order_by(Candidate.score.desc())
                  .all())
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def update_candidate_status(candidate_id: int, status: str):
    db = _session()
    try:
        db.query(Candidate).filter(Candidate.id == candidate_id).update(
            {"status": status, "updated_at": datetime.utcnow()}
        )
        db.commit()
    finally:
        db.close()


def update_candidate_score(candidate_id: int, score: float):
    db = _session()
    try:
        db.query(Candidate).filter(Candidate.id == candidate_id).update(
            {"score": score, "updated_at": datetime.utcnow()}
        )
        db.commit()
    finally:
        db.close()


def delete_candidate(candidate_id: int):
    db = _session()
    try:
        db.query(Candidate).filter(Candidate.id == candidate_id).delete()
        db.commit()
    finally:
        db.close()


def get_dashboard_stats() -> dict:
    db = _session()
    try:
        total  = db.query(func.count(Candidate.id)).scalar() or 0
        sl     = db.query(func.count(Candidate.id)).filter(Candidate.status == "Shortlisted").scalar() or 0
        rej    = db.query(func.count(Candidate.id)).filter(Candidate.status == "Rejected").scalar() or 0
        hired  = db.query(func.count(Candidate.id)).filter(Candidate.status == "Hired").scalar() or 0
        pend   = db.query(func.count(Candidate.id)).filter(Candidate.status == "Pending").scalar() or 0
        avg_sc = db.query(func.avg(Candidate.score)).scalar()
        avg_sc = round((avg_sc or 0) * 100, 1)
        roles  = db.query(func.count(func.distinct(Candidate.role))).scalar() or 0
        return {
            "total": total, "shortlisted": sl, "rejected": rej,
            "hired": hired, "pending": pend, "avg_score": avg_sc, "roles": roles,
        }
    finally:
        db.close()


# ──────────────────────────────────────────────────────────
# Job Roles
# ──────────────────────────────────────────────────────────

def insert_job_role(title, description, required_skills, min_experience):
    db = _session()
    try:
        jr = JobRole(title=title, description=description,
                     required_skills=required_skills, min_experience=min_experience)
        db.add(jr)
        db.commit()
    finally:
        db.close()


def get_all_job_roles() -> list[dict]:
    db = _session()
    try:
        rows = db.query(JobRole).order_by(JobRole.created_at.desc()).all()
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def get_job_role_titles() -> list[str]:
    db = _session()
    try:
        rows = db.query(JobRole.title).order_by(JobRole.title).all()
        return [r[0] for r in rows] or [
            "Data Scientist", "Data Analyst", "ML Engineer",
            "Backend Developer", "Frontend Developer"
        ]
    finally:
        db.close()


def delete_job_role(role_id: int):
    db = _session()
    try:
        db.query(JobRole).filter(JobRole.id == role_id).delete()
        db.commit()
    finally:
        db.close()


# ──────────────────────────────────────────────────────────
# Interviews
# ──────────────────────────────────────────────────────────

def schedule_interview(candidate_id, candidate_name, role,
                       interview_date, interview_time, interviewer, mode, notes):
    db = _session()
    try:
        iv = Interview(
            candidate_id=candidate_id, candidate_name=candidate_name,
            role=role, interview_date=interview_date,
            interview_time=str(interview_time), interviewer=interviewer,
            mode=mode, notes=notes,
        )
        db.add(iv)
        db.commit()
    finally:
        db.close()


def get_all_interviews() -> list[dict]:
    db = _session()
    try:
        rows = (db.query(Interview)
                  .order_by(Interview.interview_date.asc(), Interview.interview_time.asc())
                  .all())
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def update_interview_status(interview_id: int, status: str):
    db = _session()
    try:
        db.query(Interview).filter(Interview.id == interview_id).update({"status": status})
        db.commit()
    finally:
        db.close()


def delete_interview(interview_id: int):
    db = _session()
    try:
        db.query(Interview).filter(Interview.id == interview_id).delete()
        db.commit()
    finally:
        db.close()


# ──────────────────────────────────────────────────────────
# Analytics
# ──────────────────────────────────────────────────────────

def get_daily_analytics(days: int = 30) -> list[dict]:
    db = _session()
    try:
        url = _get_url()
        if url.startswith("sqlite"):
            date_fn = func.date(Candidate.uploaded_at)
            cutoff  = text(f"datetime('now', '-{days} days')")
            rows = (db.query(date_fn.label("event_date"),
                             func.count(Candidate.id).label("applications"),
                             func.sum((Candidate.status == "Shortlisted").cast(Integer)).label("shortlisted"),
                             func.sum((Candidate.status == "Rejected").cast(Integer)).label("rejected"),
                             func.sum((Candidate.status == "Hired").cast(Integer)).label("hired"))
                      .filter(Candidate.uploaded_at >= cutoff)
                      .group_by(date_fn)
                      .order_by(date_fn)
                      .all())
        else:
            from sqlalchemy import cast, Integer as SAInt
            date_fn = func.date(Candidate.uploaded_at)
            cutoff  = text(f"NOW() - INTERVAL '{days} days'" if "postgresql" in url
                          else f"DATE_SUB(NOW(), INTERVAL {days} DAY)")
            rows = (db.query(date_fn.label("event_date"),
                             func.count(Candidate.id).label("applications"),
                             func.sum(cast(Candidate.status == "Shortlisted", SAInt)).label("shortlisted"),
                             func.sum(cast(Candidate.status == "Rejected",    SAInt)).label("rejected"),
                             func.sum(cast(Candidate.status == "Hired",       SAInt)).label("hired"))
                      .filter(Candidate.uploaded_at >= cutoff)
                      .group_by(date_fn)
                      .order_by(date_fn)
                      .all())
        return [
            {"event_date": str(r.event_date), "applications": r.applications or 0,
             "shortlisted": r.shortlisted or 0, "rejected": r.rejected or 0,
             "hired": r.hired or 0}
            for r in rows
        ]
    finally:
        db.close()


def get_role_distribution() -> list[dict]:
    db = _session()
    try:
        rows = (db.query(Candidate.role.label("role"),
                         func.count(Candidate.id).label("total"))
                  .filter(Candidate.role.isnot(None))
                  .group_by(Candidate.role)
                  .order_by(func.count(Candidate.id).desc())
                  .all())
        return [{"role": r.role, "total": r.total} for r in rows]
    finally:
        db.close()


def get_score_distribution() -> list[dict]:
    db = _session()
    try:
        from sqlalchemy import case
        band = case(
            (Candidate.score >= 0.8, "Excellent (80-100%)"),
            (Candidate.score >= 0.6, "Good (60-79%)"),
            (Candidate.score >= 0.4, "Average (40-59%)"),
            else_="Low (<40%)"
        ).label("band")
        rows = (db.query(band, func.count(Candidate.id).label("total"))
                  .group_by(band)
                  .all())
        return [{"band": r.band, "total": r.total} for r in rows]
    finally:
        db.close()


def get_status_distribution() -> list[dict]:
    db = _session()
    try:
        rows = (db.query(Candidate.status.label("status"),
                         func.count(Candidate.id).label("total"))
                  .group_by(Candidate.status)
                  .all())
        return [{"status": r.status, "total": r.total} for r in rows]
    finally:
        db.close()
