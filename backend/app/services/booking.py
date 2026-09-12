"""Instrument booking conflict checks."""

from __future__ import annotations

from app.models.models import InstrumentBooking
from app.services.spec import bookings_overlap


def find_booking_conflicts(
    existing: list[InstrumentBooking],
    *,
    start_ms: int,
    end_ms: int,
    ignore_id: int | None = None,
) -> list[InstrumentBooking]:
    hits: list[InstrumentBooking] = []
    for b in existing:
        if ignore_id is not None and b.id == ignore_id:
            continue
        if bookings_overlap(start_ms, end_ms, b.start_ms, b.end_ms):
            hits.append(b)
    return hits
