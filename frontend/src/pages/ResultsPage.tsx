import { useEffect, useMemo, useState } from "react";
import { api, type Assay, type Result, type WorkItem } from "../api/client";
import { useLab } from "../labctx";

export function ResultsPage() {
  const { lab } = useLab();
  const [workItems, setWorkItems] = useState<WorkItem[]>([]);
  const [assays, setAssays] = useState<Assay[]>([]);
  const [results, setResults] = useState<Result[]>([]);
  const [workItemId, setWorkItemId] = useState<number | "">("");
  const [value, setValue] = useState("240");
  const [text, setText] = useState("OK");
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    if (!lab) return;
    const [w, a, r] = await Promise.all([
      api.listWorkItems(lab.id),
      api.listAssays(lab.id),
      api.listResults(lab.id),
    ]);
    setWorkItems(w);
    setAssays(a);
    setResults(r);
    if (workItemId === "" && w.length) setWorkItemId(w[0].id);
  };

  useEffect(() => {
    load().catch((e: Error) => setError(e.message));
  }, [lab?.id]);

  const selected = useMemo(
    () => workItems.find((w) => w.id === workItemId),
    [workItems, workItemId],
  );
  const assay = useMemo(
    () => assays.find((a) => a.id === selected?.assay_id),
    [assays, selected],
  );

  const onPreview = async () => {
    if (!selected || !assay) return;
    const body =
      assay.spec_type === "numeric"
        ? { assay_id: assay.id, numeric_value: Number(value), attempt: selected.attempt }
        : { assay_id: assay.id, text_value: text, attempt: selected.attempt };
    const p = await api.evaluatePreview(body);
    setPreview(`${p.stored_verdict} ← ${p.judgement_verdict}: ${p.reason}`);
  };

  const onRecord = async () => {
    if (!selected || !assay) return;
    setError(null);
    try {
      const body =
        assay.spec_type === "numeric"
          ? { numeric_value: Number(value) }
          : { text_value: text };
      await api.recordResult(selected.id, body);
      await load();
      await onPreview();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div className="page">
      <div className="page-head">
        <h1>结果判定</h1>
        <p>按检验项目规格引擎判定 pass / fail / retest / invalid。</p>
      </div>
      {error && <div className="banner error">{error}</div>}
      <div className="grid-2">
        <section className="panel">
          <h2>录入</h2>
          <div className="form-col">
            <label>
              工作项
              <select
                value={workItemId}
                onChange={(e) => setWorkItemId(Number(e.target.value))}
              >
                {workItems.map((w) => (
                  <option key={w.id} value={w.id}>
                    #{w.id} {w.sample_no} / {w.assay_code} ({w.status})
                  </option>
                ))}
              </select>
            </label>
            {assay?.spec_type === "numeric" ? (
              <label>
                数值
                <input value={value} onChange={(e) => setValue(e.target.value)} />
              </label>
            ) : (
              <label>
                文本
                <input value={text} onChange={(e) => setText(e.target.value)} />
              </label>
            )}
            <div className="form-row">
              <button type="button" onClick={() => onPreview().catch((e: Error) => setError(e.message))}>
                预览判定
              </button>
              <button type="button" className="primary" onClick={onRecord}>
                提交结果
              </button>
            </div>
            {preview && <p className="preview">{preview}</p>}
          </div>
        </section>
        <section className="panel">
          <h2>最近结果</h2>
          <ul className="issue-list">
            {results.slice(0, 12).map((r) => (
              <li key={r.id} className={r.verdict}>
                <code>{r.verdict}</code>
                <span>
                  WI#{r.work_item_id} · {r.numeric_value ?? r.text_value} · {r.note}
                </span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
