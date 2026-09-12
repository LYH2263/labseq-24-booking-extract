from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Assay, Lab
from app.schemas.schemas import AssayCreate, AssayOut

router = APIRouter(tags=["assays"])


@router.get("/labs/{lab_id}/assays", response_model=list[AssayOut])
def list_assays(lab_id: int, db: Session = Depends(get_db)):
    if db.get(Lab, lab_id) is None:
        raise HTTPException(404, "lab not found")
    return db.scalars(select(Assay).where(Assay.lab_id == lab_id).order_by(Assay.id)).all()


@router.post("/labs/{lab_id}/assays", response_model=AssayOut)
def create_assay(lab_id: int, body: AssayCreate, db: Session = Depends(get_db)):
    if db.get(Lab, lab_id) is None:
        raise HTTPException(404, "lab not found")
    if body.spec_type not in ("numeric", "discrete"):
        raise HTTPException(400, "spec_type must be numeric|discrete")
    assay = Assay(lab_id=lab_id, **body.model_dump())
    db.add(assay)
    db.commit()
    db.refresh(assay)
    return assay


@router.get("/assays/{assay_id}", response_model=AssayOut)
def get_assay(assay_id: int, db: Session = Depends(get_db)):
    assay = db.get(Assay, assay_id)
    if assay is None:
        raise HTTPException(404, "assay not found")
    return assay
