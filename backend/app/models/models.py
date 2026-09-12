from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Lab(Base):
    __tablename__ = "labs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai")

    assays: Mapped[list["Assay"]] = relationship(back_populates="lab", cascade="all, delete-orphan")
    samples: Mapped[list["Sample"]] = relationship(back_populates="lab", cascade="all, delete-orphan")
    instruments: Mapped[list["Instrument"]] = relationship(
        back_populates="lab", cascade="all, delete-orphan"
    )


class Assay(Base):
    """Test method / assay definition with specification limits."""

    __tablename__ = "assays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lab_id: Mapped[int] = mapped_column(ForeignKey("labs.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), default="")
    # numeric | discrete
    spec_type: Mapped[str] = mapped_column(String(32), default="numeric")
    lsl: Mapped[float | None] = mapped_column(Float, nullable=True)
    usl: Mapped[float | None] = mapped_column(Float, nullable=True)
    inclusive_lower: Mapped[bool] = mapped_column(Boolean, default=True)
    inclusive_upper: Mapped[bool] = mapped_column(Boolean, default=True)
    # comma-separated allowed tokens for discrete specs
    discrete_pass: Mapped[str | None] = mapped_column(String(500), nullable=True)
    retest_limit: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    lab: Mapped["Lab"] = relationship(back_populates="assays")
    work_items: Mapped[list["WorkItem"]] = relationship(back_populates="assay")


class Sample(Base):
    __tablename__ = "samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lab_id: Mapped[int] = mapped_column(ForeignKey("labs.id", ondelete="CASCADE"))
    sample_no: Mapped[str] = mapped_column(String(64), nullable=False)
    material: Mapped[str] = mapped_column(String(200), nullable=False)
    lot_no: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="received")  # received|testing|done
    received_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100)  # lower = higher priority
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    lab: Mapped["Lab"] = relationship(back_populates="samples")
    work_items: Mapped[list["WorkItem"]] = relationship(
        back_populates="sample", cascade="all, delete-orphan"
    )


class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lab_id: Mapped[int] = mapped_column(ForeignKey("labs.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="online")  # online|offline|calibration

    lab: Mapped["Lab"] = relationship(back_populates="instruments")
    bookings: Mapped[list["InstrumentBooking"]] = relationship(
        back_populates="instrument", cascade="all, delete-orphan"
    )
    work_items: Mapped[list["WorkItem"]] = relationship(back_populates="instrument")


class WorkItem(Base):
    __tablename__ = "work_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey("samples.id", ondelete="CASCADE"))
    assay_id: Mapped[int] = mapped_column(ForeignKey("assays.id", ondelete="RESTRICT"))
    instrument_id: Mapped[int | None] = mapped_column(
        ForeignKey("instruments.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), default="queued")  # queued|running|done
    attempt: Mapped[int] = mapped_column(Integer, default=1)

    sample: Mapped["Sample"] = relationship(back_populates="work_items")
    assay: Mapped["Assay"] = relationship(back_populates="work_items")
    instrument: Mapped["Instrument | None"] = relationship(back_populates="work_items")
    results: Mapped[list["Result"]] = relationship(
        back_populates="work_item", cascade="all, delete-orphan"
    )
    booking: Mapped["InstrumentBooking | None"] = relationship(
        back_populates="work_item", uselist=False
    )


class InstrumentBooking(Base):
    __tablename__ = "instrument_bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id", ondelete="CASCADE"))
    work_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("work_items.id", ondelete="SET NULL"), nullable=True
    )
    start_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    end_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)

    instrument: Mapped["Instrument"] = relationship(back_populates="bookings")
    work_item: Mapped["WorkItem | None"] = relationship(back_populates="booking")


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    work_item_id: Mapped[int] = mapped_column(ForeignKey("work_items.id", ondelete="CASCADE"))
    # numeric value stored as float; discrete also stored in text_value
    numeric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    text_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    verdict: Mapped[str] = mapped_column(String(32), nullable=False)  # pass|fail|retest|invalid
    recorded_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    work_item: Mapped["WorkItem"] = relationship(back_populates="results")


class ReportDraft(Base):
    __tablename__ = "report_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey("samples.id", ondelete="CASCADE"))
    created_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    overall: Mapped[str] = mapped_column(String(32), nullable=False)  # pass|fail|incomplete
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)

    sample: Mapped["Sample"] = relationship()
