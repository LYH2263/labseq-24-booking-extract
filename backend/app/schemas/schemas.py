from pydantic import BaseModel, Field


class LabOut(BaseModel):
    id: int
    name: str
    code: str
    timezone: str
    assay_count: int = 0
    sample_count: int = 0
    instrument_count: int = 0

    model_config = {"from_attributes": True}


class AssayOut(BaseModel):
    id: int
    lab_id: int
    code: str
    name: str
    unit: str
    spec_type: str
    lsl: float | None
    usl: float | None
    inclusive_lower: bool
    inclusive_upper: bool
    discrete_pass: str | None
    retest_limit: int
    notes: str | None = None

    model_config = {"from_attributes": True}


class AssayCreate(BaseModel):
    code: str
    name: str
    unit: str = ""
    spec_type: str = "numeric"
    lsl: float | None = None
    usl: float | None = None
    inclusive_lower: bool = True
    inclusive_upper: bool = True
    discrete_pass: str | None = None
    retest_limit: int = 1
    notes: str | None = None


class SampleOut(BaseModel):
    id: int
    lab_id: int
    sample_no: str
    material: str
    lot_no: str
    status: str
    received_ms: int
    priority: int
    notes: str | None = None

    model_config = {"from_attributes": True}


class SampleCreate(BaseModel):
    sample_no: str
    material: str
    lot_no: str = ""
    priority: int = 100
    notes: str | None = None
    assay_ids: list[int] = Field(default_factory=list)


class InstrumentOut(BaseModel):
    id: int
    lab_id: int
    code: str
    name: str
    status: str

    model_config = {"from_attributes": True}


class BookingOut(BaseModel):
    id: int
    instrument_id: int
    work_item_id: int | None
    start_ms: int
    end_ms: int

    model_config = {"from_attributes": True}


class BookingCreate(BaseModel):
    instrument_id: int
    work_item_id: int | None = None
    start_ms: int
    end_ms: int


class WorkItemOut(BaseModel):
    id: int
    sample_id: int
    assay_id: int
    instrument_id: int | None
    status: str
    attempt: int
    sample_no: str | None = None
    assay_code: str | None = None
    assay_name: str | None = None
    priority: int | None = None

    model_config = {"from_attributes": True}


class ResultOut(BaseModel):
    id: int
    work_item_id: int
    numeric_value: float | None
    text_value: str | None
    verdict: str
    recorded_ms: int
    note: str | None = None

    model_config = {"from_attributes": True}


class ResultCreate(BaseModel):
    numeric_value: float | None = None
    text_value: str | None = None
    note: str | None = None


class ReportOut(BaseModel):
    id: int
    sample_id: int
    created_ms: int
    overall: str
    payload: dict | None = None

    model_config = {"from_attributes": True}


class EvaluatePreviewIn(BaseModel):
    assay_id: int
    numeric_value: float | None = None
    text_value: str | None = None
    attempt: int = 1


class EvaluatePreviewOut(BaseModel):
    judgement_verdict: str
    reason: str
    stored_verdict: str
