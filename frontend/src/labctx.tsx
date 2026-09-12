import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, type Lab } from "./api/client";

type Ctx = {
  labs: Lab[];
  lab: Lab | null;
  setLabId: (id: number) => void;
  reload: () => Promise<void>;
  error: string | null;
};

const CtxRef = createContext<Ctx | null>(null);

export function LabProvider({ children }: { children: ReactNode }) {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [labId, setLabId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reload = async () => {
    setError(null);
    const rows = await api.listLabs();
    setLabs(rows);
    const id = labId && rows.some((l) => l.id === labId) ? labId : rows[0]?.id ?? null;
    setLabId(id);
  };

  useEffect(() => {
    reload().catch((e: Error) => setError(e.message));
  }, []);

  const lab = useMemo(() => labs.find((l) => l.id === labId) ?? null, [labs, labId]);

  return (
    <CtxRef.Provider
      value={{ labs, lab, setLabId: (id) => setLabId(id), reload, error }}
    >
      {children}
    </CtxRef.Provider>
  );
}

export function useLab() {
  const ctx = useContext(CtxRef);
  if (!ctx) throw new Error("useLab outside provider");
  return ctx;
}
