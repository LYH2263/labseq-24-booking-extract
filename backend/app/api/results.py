import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Assay, Result, WorkItem
from app.schemas.schemas import (
    EvaluatePreviewIn,
    EvaluatePreviewOut,
    ResultCreate,
    ResultOut,
)
from app.services.spec import evaluate_assay_result, next_verdict_with_retest

router = APIRouter(tags=["results"])


@router.get("/work-items/{work_item_id}/results", response_model=list[ResultOut])
def list_results(work_item_id: int, db: Session = Depends(get_db)):
    if db.get(WorkItem, work_item_id) is None:
        raise HTTPException(404, "work item not found")
    return db.scalars(
        select(Result).where(Result.work_item_id == work_item_id).order_by(Result.id)
    ).all()


@router.get("/labs/{lab_id}/results", response_model=list[ResultOut])
def list_lab_results(lab_id: int, db: Session = Depends(get_db)):
    from app.models.models import Sample

    rows = db.scalars(
        select(Result)
        .join(WorkItem, Result.work_item_id == WorkItem.id)
        .join(Sample, WorkItem.sample_id == Sample.id)
        .where(Sample.lab_id == lab_id)
        .order_by(Result.id.desc())
    ).all()
    return rows


@router.post("/work-items/{work_item_id}/results", response_model=ResultOut)
def record_result(work_item_id: int, body: ResultCreate, db: Session = Depends(get_db)):
    wi = db.scalar(
        select(WorkItem)
        .where(WorkItem.id == work_item_id)
        .options(joinedload(WorkItem.assay), joinedload(WorkItem.sample))
    )
    if wi is None:
        raise HTTPException(404, "work item not found")
    assay = wi.assay
    if assay is None:
        raise HTTPException(400, "assay missing")

    judgement = evaluate_assay_result(
        spec_type=assay.spec_type,
        numeric_value=body.numeric_value,
        text_value=body.text_value,
        lsl=assay.lsl,
        usl=assay.usl,
        inclusive_lower=assay.inclusive_lower,
        inclusive_upper=assay.inclusive_upper,
        discrete_pass=assay.discrete_pass,
    )
    stored = next_verdict_with_retest(
        judgement, attempt=wi.attempt, retest_limit=assay.retest_limit
    )
    note = body.note or judgement.reason
    result = Result(
        work_item_id=wi.id,
        numeric_value=body.numeric_value,
        text_value=body.text_value,
        verdict=stored,
        recorded_ms=int(time.time() * 1000),
        note=note,
    )
    db.add(result)

    if stored == "retest":
        wi.attempt += 1
        wi.status = "queued"
    elif stored in ("pass", "fail", "invalid"):
        wi.status = "done"

    sample = wi.sample
    if sample is not None:
        # refresh collection view after status change
        db.flush()
        items = list(sample.work_items)
        if items and all(x.status == "done" for x in items):
            sample.status = "done"
        else:
            sample.status = "testing"

    db.commit()
    db.refresh(result)
    return result


@router.post("/evaluate-preview", response_model=EvaluatePreviewOut)
def evaluate_preview(body: EvaluatePreviewIn, db: Session = Depends(get_db)):
    assay = db.get(Assay, body.assay_id)
    if assay is None:
        raise HTTPException(404, "assay not found")
    judgement = evaluate_assay_result(
        spec_type=assay.spec_type,
        numeric_value=body.numeric_value,
        text_value=body.text_value,
        lsl=assay.lsl,
        usl=assay.usl,
        inclusive_lower=assay.inclusive_lower,
        inclusive_upper=assay.inclusive_upper,
        discrete_pass=assay.discrete_pass,
    )
    stored = next_verdict_with_retest(
        judgement, attempt=body.attempt, retest_limit=assay.retest_limit
    )
    return EvaluatePreviewOut(
        judgement_verdict=judgement.verdict,
        reason=judgement.reason,
        stored_verdict=stored,
    )
