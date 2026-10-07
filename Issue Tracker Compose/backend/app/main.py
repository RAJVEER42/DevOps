"""Issue Tracker API: a small FastAPI service over PostgreSQL."""

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app import metrics, models, schemas
from app.config import settings
from app.db import get_db

app = FastAPI(title="Issue Tracker API", version=settings.app_version)
metrics.install(app)


@app.get("/")
def root():
    return {"service": "issue-tracker-api", "version": settings.app_version, "docs": "/docs"}


@app.get("/health")
def health():
    """Liveness: the process is up."""
    return {"status": "ok"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    """Readiness: the database answers."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - exercised only when the DB is down
        raise HTTPException(status_code=503, detail=f"database unavailable: {exc.__class__.__name__}")
    return {"status": "ready"}


@app.get("/api/issues", response_model=list[schemas.IssueOut])
def list_issues(status_: str | None = None, db: Session = Depends(get_db)):
    q = select(models.Issue).order_by(models.Issue.id.desc())
    if status_:
        q = q.where(models.Issue.status == status_)
    return db.scalars(q).all()


@app.get("/api/issues/stats", response_model=schemas.Stats)
def stats(db: Session = Depends(get_db)):
    by_status = dict(db.execute(select(models.Issue.status, func.count()).group_by(models.Issue.status)).all())
    by_priority = dict(db.execute(select(models.Issue.priority, func.count()).group_by(models.Issue.priority)).all())
    open_high = db.scalar(
        select(func.count()).where(models.Issue.status != "done", models.Issue.priority == "high")
    )
    return schemas.Stats(
        total=sum(by_status.values()),
        by_status={s: by_status.get(s, 0) for s in models.STATUSES},
        by_priority={p: by_priority.get(p, 0) for p in models.PRIORITIES},
        open_high_priority=open_high or 0,
    )


@app.get("/api/issues/{issue_id}", response_model=schemas.IssueOut)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.get(models.Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="issue not found")
    return issue


@app.post("/api/issues", response_model=schemas.IssueOut, status_code=status.HTTP_201_CREATED)
def create_issue(payload: schemas.IssueIn, db: Session = Depends(get_db)):
    issue = models.Issue(**payload.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    metrics.ISSUES_CREATED.inc()
    return issue


@app.put("/api/issues/{issue_id}", response_model=schemas.IssueOut)
def update_issue(issue_id: int, payload: schemas.IssueUpdate, db: Session = Depends(get_db)):
    issue = db.get(models.Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="issue not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(issue, key, value)
    db.commit()
    db.refresh(issue)
    return issue


@app.delete("/api/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.get(models.Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="issue not found")
    db.delete(issue)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
