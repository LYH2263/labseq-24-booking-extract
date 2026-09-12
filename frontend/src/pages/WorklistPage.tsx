import { useEffect, useState } from "react";
import { api, type WorkItem } from "../api/client";
import { useLab } from "../labctx";

export function WorklistPage() {
  const { lab } = useLab();
  const [rows, setRows] = useState<WorkItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!lab) return;
    api
      .listWorkItems(lab.id)
      .then(setRows)
      .catch((e: Error) => setError(e.message));
  }, [lab?.id]);

  return (
    <div className="page">
      <div className="page-head">
        <h1>工作单</h1>
        <p>按样品优先级排序的待检/在检任务队列。</p>
      </div>
      {error && <div className="banner error">{error}</div>}
      <section className="panel">
        <table className="data">
          <thead>
            <tr>
              <th>优先级</th>
              <th>样品</th>
              <th>项目</th>
              <th>状态</th>
              <th>尝试</th>
              <th>仪器</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((w) => (
              <tr key={w.id}>
                <td>{w.priority}</td>
                <td>{w.sample_no}</td>
                <td>
                  {w.assay_code} · {w.assay_name}
                </td>
                <td>
                  <span className={`pill ${w.status}`}>{w.status}</span>
                </td>
                <td>{w.attempt}</td>
                <td>{w.instrument_id ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
