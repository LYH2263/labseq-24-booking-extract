from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Lab, Sample, WorkItem
from app.schemas.schemas import WorkItemOut

router = APIRouter(tags=["workitems"])


def _ser(wi: WorkItem) -> WorkItemOut:
    return WorkItemOut(
        id=wi.id,
        sample_id=wi.sample_id,
        assay_id=wi.assay_id,
        instrument_id=wi.instrument_id,
        status=wi.status,
        attempt=wi.attempt,
        sample_no=wi.sample.sample_no if wi.sample else None,
        assay_code=wi.assay.code if wi.assay else None,
        assay_name=wi.assay.name if wi.assay else None,
        priority=wi.sample.priority if wi.sample else None,
    )


@router.get("/labs/{lab_id}/work-items", response_model=list[WorkItemOut])
def list_work_items(lab_id: int, db: Session = Depends(get_db)):
    if db.get(Lab, lab_id) is None:
        raise HTTPException(404, "lab not found")
    rows = db.scalars(
        select(WorkItem)
        .join(Sample, WorkItem.sample_id == Sample.id)
        .where(Sample.lab_id == lab_id)
        .options(joinedload(WorkItem.sample), joinedload(WorkItem.assay))
        .order_by(Sample.priority, WorkItem.id)
    ).unique().all()
    return [_ser(w) for w in rows]


@router.patch("/work-items/{work_item_id}", response_model=WorkItemOut)
def update_work_item(
    work_item_id: int,
    status: str | None = None,
    instrument_id: int | None = None,
    db: Session = Depends(get_db),
):
    wi = db.scalar(
        select(WorkItem)
        .where(WorkItem.id == work_item_id)
        .options(joinedload(WorkItem.sample), joinedload(WorkItem.assay))
    )
    if wi is None:
        raise HTTPException(404, "work item not found")
    if status is not None:
        if status not in ("queued", "running", "done"):
            raise HTTPException(400, "invalid status")
        wi.status = status
    if instrument_id is not None:
        wi.instrument_id = instrument_id
    db.commit()
    db.refresh(wi)
    return _ser(wi)
