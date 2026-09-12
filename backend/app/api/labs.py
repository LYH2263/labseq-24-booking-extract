from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Assay, Instrument, Lab, Sample
from app.schemas.schemas import LabOut

router = APIRouter(prefix="/labs", tags=["labs"])


@router.get("", response_model=list[LabOut])
def list_labs(db: Session = Depends(get_db)):
    labs = db.scalars(select(Lab).order_by(Lab.id)).all()
    out = []
    for lab in labs:
        out.append(
            LabOut(
                id=lab.id,
                name=lab.name,
                code=lab.code,
                timezone=lab.timezone,
                assay_count=db.scalar(
                    select(func.count()).select_from(Assay).where(Assay.lab_id == lab.id)
                )
                or 0,
                sample_count=db.scalar(
                    select(func.count()).select_from(Sample).where(Sample.lab_id == lab.id)
                )
                or 0,
                instrument_count=db.scalar(
                    select(func.count())
                    .select_from(Instrument)
                    .where(Instrument.lab_id == lab.id)
                )
                or 0,
            )
        )
    return out


@router.get("/{lab_id}", response_model=LabOut)
def get_lab(lab_id: int, db: Session = Depends(get_db)):
    lab = db.get(Lab, lab_id)
    if lab is None:
        raise HTTPException(404, "lab not found")
    return LabOut(
        id=lab.id,
        name=lab.name,
        code=lab.code,
        timezone=lab.timezone,
        assay_count=db.scalar(select(func.count()).select_from(Assay).where(Assay.lab_id == lab.id))
        or 0,
        sample_count=db.scalar(
            select(func.count()).select_from(Sample).where(Sample.lab_id == lab.id)
        )
        or 0,
        instrument_count=db.scalar(
            select(func.count()).select_from(Instrument).where(Instrument.lab_id == lab.id)
        )
        or 0,
    )
