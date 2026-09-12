import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Assay, Lab, Sample, WorkItem
from app.schemas.schemas import SampleCreate, SampleOut

router = APIRouter(tags=["samples"])


@router.get("/labs/{lab_id}/samples", response_model=list[SampleOut])
def list_samples(lab_id: int, db: Session = Depends(get_db)):
    if db.get(Lab, lab_id) is None:
        raise HTTPException(404, "lab not found")
    return db.scalars(
        select(Sample).where(Sample.lab_id == lab_id).order_by(Sample.priority, Sample.id)
    ).all()


@router.post("/labs/{lab_id}/samples", response_model=SampleOut)
def create_sample(lab_id: int, body: SampleCreate, db: Session = Depends(get_db)):
    if db.get(Lab, lab_id) is None:
        raise HTTPException(404, "lab not found")
    sample = Sample(
        lab_id=lab_id,
        sample_no=body.sample_no,
        material=body.material,
        lot_no=body.lot_no,
        status="received",
        received_ms=int(time.time() * 1000),
        priority=body.priority,
        notes=body.notes,
    )
    db.add(sample)
    db.flush()
    for assay_id in body.assay_ids:
        assay = db.get(Assay, assay_id)
        if assay is None or assay.lab_id != lab_id:
            raise HTTPException(400, f"invalid assay_id {assay_id}")
        db.add(WorkItem(sample_id=sample.id, assay_id=assay_id, status="queued", attempt=1))
    if body.assay_ids:
        sample.status = "testing"
    db.commit()
    db.refresh(sample)
    return sample


@router.get("/samples/{sample_id}", response_model=SampleOut)
def get_sample(sample_id: int, db: Session = Depends(get_db)):
    sample = db.get(Sample, sample_id)
    if sample is None:
        raise HTTPException(404, "sample not found")
    return sample
