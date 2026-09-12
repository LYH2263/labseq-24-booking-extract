import { useEffect, useState } from "react";
import { api, type Assay, type Sample } from "../api/client";
import { useLab } from "../labctx";

export function SamplesPage() {
  const { lab } = useLab();
  const [rows, setRows] = useState<Sample[]>([]);
  const [assays, setAssays] = useState<Assay[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sampleNo, setSampleNo] = useState("");
  const [material, setMaterial] = useState("");
  const [selected, setSelected] = useState<number[]>([]);

  const load = async () => {
    if (!lab) return;
    const [s, a] = await Promise.all([api.listSamples(lab.id), api.listAssays(lab.id)]);
    setRows(s);
    setAssays(a);
  };

  useEffect(() => {
    load().catch((e: Error) => setError(e.message));
  }, [lab?.id]);

  const toggle = (id: number) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const onCreate = async () => {
    if (!lab || !sampleNo.trim() || !material.trim()) return;
    try {
      await api.createSample(lab.id, {
        sample_no: sampleNo.trim(),
        material: material.trim(),
        lot_no: "NEW",
        priority: 80,
        assay_ids: selected,
      });
      setSampleNo("");
      setMaterial("");
      setSelected([]);
      await load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div className="page">
      <div className="page-head">
        <h1>样品台账</h1>
        <p>收样并勾选检验项目，系统自动生成工作单。</p>
      </div>
      {error && <div className="banner error">{error}</div>}
      <section className="panel">
        <h2>收样</h2>
        <div className="form-row">
          <input
            placeholder="样品号"
            value={sampleNo}
            onChange={(e) => setSampleNo(e.target.value)}
          />
          <input
            placeholder="物料"
            value={material}
            onChange={(e) => setMaterial(e.target.value)}
          />
          <button type="button" className="primary" onClick={onCreate}>
            登记
          </button>
        </div>
        <div className="chip-row">
          {assays.map((a) => (
            <label key={a.id} className={selected.includes(a.id) ? "chip on" : "chip"}>
              <input
                type="checkbox"
                checked={selected.includes(a.id)}
                onChange={() => toggle(a.id)}
              />
              {a.code}
            </label>
          ))}
        </div>
      </section>
      <section className="panel">
        <table className="data">
          <thead>
            <tr>
              <th>样品号</th>
              <th>物料</th>
              <th>批次</th>
              <th>优先级</th>
              <th>状态</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.id}>
                <td>{s.sample_no}</td>
                <td>{s.material}</td>
                <td>{s.lot_no}</td>
                <td>{s.priority}</td>
                <td>
                  <span className={`pill ${s.status}`}>{s.status}</span>
                </td>
                <td className={s.notes?.includes("SEED") ? "seed" : ""}>{s.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
