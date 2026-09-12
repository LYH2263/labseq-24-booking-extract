"""Build sample report drafts from latest results."""

from __future__ import annotations

import json
import time

from sqlalchemy.orm import Session

from app.models.models import ReportDraft, Sample, WorkItem


def build_report_payload(sample: Sample) -> dict:
    items = []
    overall = "pass"
    has_incomplete = False

    for wi in sorted(sample.work_items, key=lambda x: x.id):
        latest = max(wi.results, key=lambda r: r.id, default=None)
        assay = wi.assay
        row = {
            "work_item_id": wi.id,
            "assay_code": assay.code if assay else None,
            "assay_name": assay.name if assay else None,
            "attempt": wi.attempt,
            "status": wi.status,
            "verdict": latest.verdict if latest else None,
            "numeric_value": latest.numeric_value if latest else None,
            "text_value": latest.text_value if latest else None,
        }
        items.append(row)
        if latest is None or wi.status != "done":
            has_incomplete = True
        elif latest.verdict in ("fail", "invalid"):
            overall = "fail"
        elif latest.verdict == "retest":
            has_incomplete = True

    if has_incomplete and overall != "fail":
        overall = "incomplete"

    return {
        "sample_no": sample.sample_no,
        "material": sample.material,
        "lot_no": sample.lot_no,
        "overall": overall,
        "items": items,
    }


def create_report_draft(db: Session, sample: Sample) -> ReportDraft:
    payload = build_report_payload(sample)
    draft = ReportDraft(
        sample_id=sample.id,
        created_ms=int(time.time() * 1000),
        overall=payload["overall"],
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft
