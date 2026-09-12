"""Seed lab with intentional out-of-spec and booking conflicts."""

import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import (
    Assay,
    Instrument,
    InstrumentBooking,
    Lab,
    Result,
    Sample,
    WorkItem,
)


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(Lab).limit(1)) is not None:
        return

    now = int(time.time() * 1000)
    lab = Lab(name="正极材料质检室", code="CATHODE-QC", timezone="Asia/Shanghai")
    db.add(lab)
    db.flush()

    assays = [
        Assay(
            lab_id=lab.id,
            code="PSA-TAP",
            name="振实密度",
            unit="g/cm3",
            spec_type="numeric",
            lsl=2.2,
            usl=2.8,
            inclusive_lower=True,
            inclusive_upper=True,
            retest_limit=1,
        ),
        Assay(
            lab_id=lab.id,
            code="H2O-KF",
            name="水分（卡尔费休）",
            unit="ppm",
            spec_type="numeric",
            lsl=None,
            usl=200.0,
            inclusive_upper=True,
            retest_limit=1,
            notes="仅上限",
        ),
        Assay(
            lab_id=lab.id,
            code="APPEAR",
            name="外观目检",
            unit="",
            spec_type="discrete",
            discrete_pass="OK,PASS",
            retest_limit=0,
        ),
        Assay(
            lab_id=lab.id,
            code="PH-BAD",
            name="浆料 pH（坏规格种子）",
            unit="",
            spec_type="numeric",
            lsl=None,
            usl=None,
            retest_limit=1,
            notes="SEED: 未配置规格限 → 录入结果会 invalid",
        ),
    ]
    db.add_all(assays)
    db.flush()
    by_code = {a.code: a for a in assays}

    instruments = [
        Instrument(lab_id=lab.id, code="TAP-01", name="振实密度仪", status="online"),
        Instrument(lab_id=lab.id, code="KF-02", name="水分仪", status="online"),
        Instrument(lab_id=lab.id, code="VIS-01", name="目检台", status="online"),
    ]
    db.add_all(instruments)
    db.flush()
    inst = {i.code: i for i in instruments}

    s1 = Sample(
        lab_id=lab.id,
        sample_no="S-2026-001",
        material="NCM811 正极粉",
        lot_no="L-A01",
        status="testing",
        received_ms=now - 86_400_000,
        priority=10,
        notes="主流程样品",
    )
    s2 = Sample(
        lab_id=lab.id,
        sample_no="S-2026-002",
        material="NCM811 正极粉",
        lot_no="L-B02",
        status="received",
        received_ms=now - 3_600_000,
        priority=50,
        notes="SEED: 含水超标待复测",
    )
    db.add_all([s1, s2])
    db.flush()

    items = [
        WorkItem(
            sample_id=s1.id,
            assay_id=by_code["PSA-TAP"].id,
            instrument_id=inst["TAP-01"].id,
            status="done",
            attempt=1,
        ),
        WorkItem(
            sample_id=s1.id,
            assay_id=by_code["APPEAR"].id,
            instrument_id=inst["VIS-01"].id,
            status="done",
            attempt=1,
        ),
        WorkItem(
            sample_id=s1.id,
            assay_id=by_code["H2O-KF"].id,
            instrument_id=inst["KF-02"].id,
            status="queued",
            attempt=1,
        ),
        WorkItem(
            sample_id=s2.id,
            assay_id=by_code["H2O-KF"].id,
            instrument_id=inst["KF-02"].id,
            status="running",
            attempt=1,
        ),
        WorkItem(
            sample_id=s2.id,
            assay_id=by_code["PH-BAD"].id,
            instrument_id=None,
            status="queued",
            attempt=1,
        ),
    ]
    db.add_all(items)
    db.flush()

    db.add_all(
        [
            Result(
                work_item_id=items[0].id,
                numeric_value=2.45,
                text_value=None,
                verdict="pass",
                recorded_ms=now - 80_000_000,
                note="合格",
            ),
            Result(
                work_item_id=items[1].id,
                numeric_value=None,
                text_value="OK",
                verdict="pass",
                recorded_ms=now - 79_000_000,
            ),
            Result(
                work_item_id=items[3].id,
                numeric_value=260.0,
                text_value=None,
                verdict="retest",
                recorded_ms=now - 1_000_000,
                note="SEED: 超 USL=200，attempt<=retest_limit → retest",
            ),
        ]
    )

    # Overlapping bookings on KF-02 (intentional conflict for instruments page)
    base = now + 3_600_000
    db.add_all(
        [
            InstrumentBooking(
                instrument_id=inst["KF-02"].id,
                work_item_id=items[3].id,
                start_ms=base,
                end_ms=base + 3_600_000,
            ),
            InstrumentBooking(
                instrument_id=inst["KF-02"].id,
                work_item_id=items[2].id,
                start_ms=base + 1_800_000,
                end_ms=base + 5_400_000,
            ),
        ]
    )

    db.commit()
