export type Lab = {
  id: number;
  name: string;
  code: string;
  timezone: string;
  assay_count: number;
  sample_count: number;
  instrument_count: number;
};

export type Assay = {
  id: number;
  lab_id: number;
  code: string;
  name: string;
  unit: string;
  spec_type: string;
  lsl: number | null;
  usl: number | null;
  inclusive_lower: boolean;
  inclusive_upper: boolean;
  discrete_pass: string | null;
  retest_limit: number;
  notes: string | null;
};

export type Sample = {
  id: number;
  lab_id: number;
  sample_no: string;
  material: string;
  lot_no: string;
  status: string;
  received_ms: number;
  priority: number;
  notes: string | null;
};

export type WorkItem = {
  id: number;
  sample_id: number;
  assay_id: number;
  instrument_id: number | null;
  status: string;
  attempt: number;
  sample_no: string | null;
  assay_code: string | null;
  assay_name: string | null;
  priority: number | null;
};

export type Result = {
  id: number;
  work_item_id: number;
  numeric_value: number | null;
  text_value: string | null;
  verdict: string;
  recorded_ms: number;
  note: string | null;
};

export type Instrument = {
  id: number;
  lab_id: number;
  code: string;
  name: string;
  status: string;
};

export type Report = {
  id: number;
  sample_id: number;
  created_ms: number;
  overall: string;
  payload: Record<string, unknown> | null;
};

const BASE = "/api";

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) throw new Error((await res.text()) || res.statusText);
  return res.json() as Promise<T>;
}

export const api = {
  listLabs: () => json<Lab[]>("/labs"),
  listAssays: (labId: number) => json<Assay[]>(`/labs/${labId}/assays`),
  createAssay: (labId: number, body: Partial<Assay>) =>
    json<Assay>(`/labs/${labId}/assays`, { method: "POST", body: JSON.stringify(body) }),
  listSamples: (labId: number) => json<Sample[]>(`/labs/${labId}/samples`),
  createSample: (
    labId: number,
    body: {
      sample_no: string;
      material: string;
      lot_no?: string;
      priority?: number;
      assay_ids?: number[];
      notes?: string;
    },
  ) => json<Sample>(`/labs/${labId}/samples`, { method: "POST", body: JSON.stringify(body) }),
  listWorkItems: (labId: number) => json<WorkItem[]>(`/labs/${labId}/work-items`),
  listResults: (labId: number) => json<Result[]>(`/labs/${labId}/results`),
  recordResult: (
    workItemId: number,
    body: { numeric_value?: number | null; text_value?: string | null; note?: string },
  ) =>
    json<Result>(`/work-items/${workItemId}/results`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  evaluatePreview: (body: {
    assay_id: number;
    numeric_value?: number | null;
    text_value?: string | null;
    attempt?: number;
  }) =>
    json<{ judgement_verdict: string; reason: string; stored_verdict: string }>(
      "/evaluate-preview",
      { method: "POST", body: JSON.stringify(body) },
    ),
  listInstruments: (labId: number) => json<Instrument[]>(`/labs/${labId}/instruments`),
  bookingConflicts: (labId: number) =>
    json<{ count: number; conflicts: Array<Record<string, unknown>> }>(
      `/labs/${labId}/booking-conflicts`,
    ),
  listLabReports: (labId: number) => json<Report[]>(`/labs/${labId}/reports`),
  createReport: (sampleId: number) =>
    json<Report>(`/samples/${sampleId}/reports`, { method: "POST" }),
};
