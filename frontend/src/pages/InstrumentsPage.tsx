import { useEffect, useState } from "react";
import { api, type Instrument } from "../api/client";
import { useLab } from "../labctx";

export function InstrumentsPage() {
  const { lab } = useLab();
  const [rows, setRows] = useState<Instrument[]>([]);
  const [conflicts, setConflicts] = useState<Array<Record<string, unknown>>>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!lab) return;
    (async () => {
      setRows(await api.listInstruments(lab.id));
      const c = await api.bookingConflicts(lab.id);
      setConflicts(c.conflicts);
    })().catch((e: Error) => setError(e.message));
  }, [lab?.id]);

  return (
    <div className="page">
      <div className="page-head">
        <h1>仪器台账</h1>
        <p>仪器状态与占用时段冲突检测（半开区间重叠）。</p>
      </div>
      {error && <div className="banner error">{error}</div>}
      <div className="grid-2">
        <section className="panel">
          <h2>仪器</h2>
          <table className="data">
            <thead>
              <tr>
                <th>编码</th>
                <th>名称</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((i) => (
                <tr key={i.id}>
                  <td>{i.code}</td>
                  <td>{i.name}</td>
                  <td>
                    <span className={`pill ${i.status}`}>{i.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        <section className="panel">
          <h2>占用冲突 ({conflicts.length})</h2>
          {!conflicts.length && <p className="muted">无冲突</p>}
          <ul className="issue-list">
            {conflicts.map((c, idx) => (
              <li key={idx} className="fail">
                <code>{String(c.instrument_code)}</code>
                <span>
                  booking #{String(c.a_id)} ↔ #{String(c.b_id)}
                </span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
