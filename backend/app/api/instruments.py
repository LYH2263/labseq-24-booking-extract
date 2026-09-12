from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Instrument, InstrumentBooking, Lab
from app.schemas.schemas import BookingCreate, BookingOut, InstrumentOut
from app.services.booking import find_booking_conflicts

router = APIRouter(tags=["instruments"])


@router.get("/labs/{lab_id}/instruments", response_model=list[InstrumentOut])
def list_instruments(lab_id: int, db: Session = Depends(get_db)):
    if db.get(Lab, lab_id) is None:
        raise HTTPException(404, "lab not found")
    return db.scalars(
        select(Instrument).where(Instrument.lab_id == lab_id).order_by(Instrument.id)
    ).all()


@router.get("/instruments/{instrument_id}/bookings", response_model=list[BookingOut])
def list_bookings(instrument_id: int, db: Session = Depends(get_db)):
    if db.get(Instrument, instrument_id) is None:
        raise HTTPException(404, "instrument not found")
    return db.scalars(
        select(InstrumentBooking)
        .where(InstrumentBooking.instrument_id == instrument_id)
        .order_by(InstrumentBooking.start_ms)
    ).all()


@router.get("/labs/{lab_id}/booking-conflicts")
def lab_booking_conflicts(lab_id: int, db: Session = Depends(get_db)):
    if db.get(Lab, lab_id) is None:
        raise HTTPException(404, "lab not found")
    instruments = db.scalars(
        select(Instrument)
        .where(Instrument.lab_id == lab_id)
        .options(joinedload(Instrument.bookings))
    ).unique().all()
    conflicts = []
    for inst in instruments:
        bookings = sorted(inst.bookings, key=lambda b: b.start_ms)
        for i in range(len(bookings)):
            for j in range(i + 1, len(bookings)):
                hits = find_booking_conflicts(
                    [bookings[j]],
                    start_ms=bookings[i].start_ms,
                    end_ms=bookings[i].end_ms,
                )
                if hits:
                    conflicts.append(
                        {
                            "instrument_id": inst.id,
                            "instrument_code": inst.code,
                            "a_id": bookings[i].id,
                            "b_id": bookings[j].id,
                            "a_start_ms": bookings[i].start_ms,
                            "a_end_ms": bookings[i].end_ms,
                            "b_start_ms": bookings[j].start_ms,
                            "b_end_ms": bookings[j].end_ms,
                        }
                    )
    return {"count": len(conflicts), "conflicts": conflicts}


@router.post("/bookings", response_model=BookingOut)
def create_booking(body: BookingCreate, db: Session = Depends(get_db)):
    inst = db.scalar(
        select(Instrument)
        .where(Instrument.id == body.instrument_id)
        .options(joinedload(Instrument.bookings))
    )
    if inst is None:
        raise HTTPException(404, "instrument not found")
    if body.end_ms <= body.start_ms:
        raise HTTPException(400, "end_ms must be > start_ms")
    conflicts = find_booking_conflicts(
        list(inst.bookings), start_ms=body.start_ms, end_ms=body.end_ms
    )
    if conflicts:
        raise HTTPException(
            409,
            f"booking conflicts with {[c.id for c in conflicts]}",
        )
    row = InstrumentBooking(
        instrument_id=body.instrument_id,
        work_item_id=body.work_item_id,
        start_ms=body.start_ms,
        end_ms=body.end_ms,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
