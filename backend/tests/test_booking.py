from app.models.models import InstrumentBooking
from app.services.booking import find_booking_conflicts


def test_find_conflicts():
    existing = [
        InstrumentBooking(id=1, instrument_id=1, start_ms=0, end_ms=100),
        InstrumentBooking(id=2, instrument_id=1, start_ms=200, end_ms=300),
    ]
    hits = find_booking_conflicts(existing, start_ms=80, end_ms=120)
    assert [h.id for h in hits] == [1]
    assert find_booking_conflicts(existing, start_ms=100, end_ms=200) == []
