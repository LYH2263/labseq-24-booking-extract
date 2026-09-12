import { NavLink, Outlet } from "react-router-dom";
import { useLab } from "../labctx";

export function Layout() {
  const { labs, lab, setLabId } = useLab();
  return (
    <div className="shell">
      <aside className="sidebar">
        <p className="brand">Labseq</p>
        <p className="brand-note">工业质检</p>
        <nav className="nav">
          <p className="nav-group">建档</p>
          <NavLink to="/" end>实验室</NavLink>
          <NavLink to="/assays">检验项目</NavLink>
          <p className="nav-group">流转</p>
          <NavLink to="/samples">样品</NavLink>
          <NavLink to="/worklist">工作单</NavLink>
          <NavLink to="/instruments">仪器</NavLink>
          <p className="nav-group">判定</p>
          <NavLink to="/results">结果判定</NavLink>
          <NavLink to="/reports">报告</NavLink>
        </nav>
      </aside>
      <div className="bench">
        <header className="util">
          <span>当前实验室</span>
          <select
            value={lab?.id ?? ""}
            onChange={(e) => setLabId(Number(e.target.value))}
            aria-label="当前实验室"
          >
            {labs.map((l) => (
              <option key={l.id} value={l.id}>
                {l.code} · {l.name}
              </option>
            ))}
          </select>
        </header>
        <Outlet />
      </div>
    </div>
  );
}
