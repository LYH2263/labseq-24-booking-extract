import { useEffect, useState } from "react";
import { api, type Assay } from "../api/client";
import { useLab } from "../labctx";

export function AssaysPage() {
  const { lab } = useLab();
  const [rows, setRows] = useState<Assay[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [lsl, setLsl] = useState("0");
  const [usl, setUsl] = useState("100");

  const load = async () => {
    if (!lab) return;
    setRows(await api.listAssays(lab.id));
  };

  useEffect(() => {
    load().catch((e: Error) => setError(e.message));
  }, [lab?.id]);

  const onCreate = async () => {
    if (!lab || !code.trim() || !name.trim()) return;
    try {
      await api.createAssay(lab.id, {
        code: code.trim(),
        name: name.trim(),
        unit: "",
        spec_type: "numeric",
        lsl: Number(lsl),
        usl: Number(usl),
        inclusive_lower: true,
        inclusive_upper: true,
        retest_limit: 1,
      });
      setCode("");
      setName("");
      await load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div className="page">
      <div className="page-head">
        <h1>检验项目</h1>
        <p>规格限与离散合格集定义。notes 中带 SEED 的为故意坏配置。</p>
      </div>
      {error && <div className="banner error">{error}</div>}
      <section className="panel">
        <h2>新建数值型项目</h2>
        <div className="form-row">
          <input placeholder="编码" value={code} onChange={(e) => setCode(e.target.value)} />
          <input placeholder="名称" value={name} onChange={(e) => setName(e.target.value)} />
          <input placeholder="LSL" value={lsl} onChange={(e) => setLsl(e.target.value)} />
          <input placeholder="USL" value={usl} onChange={(e) => setUsl(e.target.value)} />
          <button type="button" className="primary" onClick={onCreate}>
            添加
          </button>
        </div>
      </section>
      <section className="panel">
        <table className="data">
          <thead>
            <tr>
              <th>编码</th>
              <th>名称</th>
              <th>类型</th>
              <th>规格</th>
              <th>复测</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.id}>
                <td>{a.code}</td>
                <td>{a.name}</td>
                <td>{a.spec_type}</td>
                <td>
                  {a.spec_type === "numeric"
                    ? `${a.lsl ?? "−∞"} ~ ${a.usl ?? "+∞"} ${a.unit}`
                    : a.discrete_pass}
                </td>
                <td>{a.retest_limit}</td>
                <td className={a.notes?.includes("SEED") ? "seed" : ""}>{a.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
