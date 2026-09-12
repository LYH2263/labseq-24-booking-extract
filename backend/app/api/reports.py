import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import ReportDraft, Sample, WorkItem
from app.schemas.schemas import ReportOut
from app.services.report import create_report_draft

router = APIRouter(tags=["reports"])


@router.get("/samples/{sample_id}/reports", response_model=list[ReportOut])
def list_reports(sample_id: int, db: Session = Depends(get_db)):
    if db.get(Sample, sample_id) is None:
        raise HTTPException(404, "sample not found")
    rows = db.scalars(
        select(ReportDraft)
        .where(ReportDraft.sample_id == sample_id)
        .order_by(ReportDraft.id.desc())
    ).all()
    return [
        ReportOut(
            id=r.id,
            sample_id=r.sample_id,
            created_ms=r.created_ms,
            overall=r.overall,
            payload=json.loads(r.payload_json),
        )
        for r in rows
    ]


@router.post("/samples/{sample_id}/reports", response_model=ReportOut)
def create_report(sample_id: int, db: Session = Depends(get_db)):
    sample = db.scalar(
        select(Sample)
        .where(Sample.id == sample_id)
        .options(
            joinedload(Sample.work_items).joinedload(WorkItem.assay),
            joinedload(Sample.work_items).joinedload(WorkItem.results),
        )
    )
    if sample is None:
        raise HTTPException(404, "sample not found")
    draft = create_report_draft(db, sample)
    return ReportOut(
        id=draft.id,
        sample_id=draft.sample_id,
        created_ms=draft.created_ms,
        overall=draft.overall,
        payload=json.loads(draft.payload_json),
    )


@router.get("/labs/{lab_id}/reports", response_model=list[ReportOut])
def list_lab_reports(lab_id: int, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(ReportDraft)
        .join(ReportDraft.sample)
        .where(Sample.lab_id == lab_id)
        .order_by(ReportDraft.id.desc())
    ).all()
    return [
        ReportOut(
            id=r.id,
            sample_id=r.sample_id,
            created_ms=r.created_ms,
            overall=r.overall,
            payload=json.loads(r.payload_json),
        )
        for r in rows
    ]
