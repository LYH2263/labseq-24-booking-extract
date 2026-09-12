import { Link } from "react-router-dom";
import { useLab } from "../labctx";

export function LabsPage() {
  const { labs, lab, setLabId, error } = useLab();
  return (
    <div className="page">
      <div className="page-head">
        <h1>实验室</h1>
        <p>选择质检室后，在检验项目、样品、工作单中完成收样到判定的主流程。</p>
      </div>
      {error && <div className="banner error">{error}</div>}
      <div className="card-grid">
        {labs.map((l) => (
          <button
            key={l.id}
            type="button"
            className={lab?.id === l.id ? "card active" : "card"}
            onClick={() => setLabId(l.id)}
          >
            <strong>
              {l.code} · {l.name}
            </strong>
            <span>
              {l.assay_count} 项目 · {l.sample_count} 样品 · {l.instrument_count} 仪器
            </span>
            <div className="card-links">
              <Link to="/samples" onClick={(e) => e.stopPropagation()}>
                样品
              </Link>
              <Link to="/worklist" onClick={(e) => e.stopPropagation()}>
                工作单
              </Link>
              <Link to="/results" onClick={(e) => e.stopPropagation()}>
                结果
              </Link>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
