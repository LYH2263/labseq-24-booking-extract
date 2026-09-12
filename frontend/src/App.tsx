import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { LabProvider } from "./labctx";
import { AssaysPage } from "./pages/AssaysPage";
import { InstrumentsPage } from "./pages/InstrumentsPage";
import { LabsPage } from "./pages/LabsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { ResultsPage } from "./pages/ResultsPage";
import { SamplesPage } from "./pages/SamplesPage";
import { WorklistPage } from "./pages/WorklistPage";
import "./styles/app.css";

export default function App() {
  return (
    <BrowserRouter>
      <LabProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<LabsPage />} />
            <Route path="assays" element={<AssaysPage />} />
            <Route path="samples" element={<SamplesPage />} />
            <Route path="worklist" element={<WorklistPage />} />
            <Route path="results" element={<ResultsPage />} />
            <Route path="instruments" element={<InstrumentsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </LabProvider>
    </BrowserRouter>
  );
}
