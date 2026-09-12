import { useEffect, useState } from "react";
import { api, type Report, type Sample } from "../api/client";
import { useLab } from "../labctx";

export function ReportsPage() {
  const { lab } = useLab();
  const [samples, setSamples] = useState<Sample[]>([]);
  const [sampleId, setSampleId] = useState<number | "">("");
  const [reports, setReports] = useState<Report[]>([]);
  const [selected, setSelected] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    if (!lab) return;
    const [s, r] = await Promise.all([api.listSamples(lab.id), api.listLabReports(lab.id)]);
    setSamples(s);
    setReports(r);
    if (sampleId === "" && s.length) setSampleId(s[0].id);
  };

  useEffect(() => {
    load().catch((e: Error) => setError(e.message));
  }, [lab?.id]);

  const onCreate = async () => {
    if (sampleId === "") return;
    try {
      const draft = await api.createReport(sampleId);
      setSelected(draft);
      await load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div className="page">
      <div className="page-head row-between">
        <div>
          <h1>报告草稿</h1>
          <p>汇总样品各检验项最新结果，给出 overall 结论。</p>
        </div>
        <div className="actions">
          <select value={sampleId} onChange={(e) => setSampleId(Number(e.target.value))}>
            {samples.map((s) => (
              <option key={s.id} value={s.id}>
                {s.sample_no}
              </option>
            ))}
          </select>
          <button type="button" className="primary" onClick={onCreate}>
            生成草稿
          </button>
        </div>
      </div>
      {error && <div className="banner error">{error}</div>}
      <div className="grid-2">
        <section className="panel">
          <h2>历史</h2>
          <ul className="row-list">
            {reports.map((r) => (
              <li key={r.id}>
                <button
                  type="button"
                  className={selected?.id === r.id ? "row active" : "row"}
                  onClick={() => setSelected(r)}
                >
                  <strong>
                    #{r.id} · sample {r.sample_id} · {r.overall}
                  </strong>
                  <span>{new Date(r.created_ms).toLocaleString()}</span>
                </button>
              </li>
            ))}
            {!reports.length && <li className="muted">暂无报告</li>}
          </ul>
        </section>
        <section className="panel">
          <h2>载荷</h2>
          {!selected && <p className="muted">选择一条报告</p>}
          {selected && <pre className="pre">{JSON.stringify(selected.payload, null, 2)}</pre>}
        </section>
      </div>
    </div>
  );
}
