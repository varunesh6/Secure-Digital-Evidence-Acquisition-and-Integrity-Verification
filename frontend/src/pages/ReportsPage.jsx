import { useEffect, useState } from 'react';
import { generateReport, getReports } from '../services/api';

export default function ReportsPage() {
  const [reports, setReports] = useState([]);
  const [caseId, setCaseId] = useState('1');
  const [message, setMessage] = useState('');

  const loadReports = async () => {
    try {
      const response = await getReports();
      setReports(response.data.reports || []);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => { loadReports(); }, []);

  const handleGenerate = async () => {
    try {
      const response = await generateReport({ case_id: Number(caseId) });
      setMessage(response.data.message);
      await loadReports();
    } catch (error) {
      setMessage(error.response?.data?.error || 'Unable to generate report.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
        <h2 className="mb-4 text-xl font-semibold">PDF report generation</h2>
        <div className="flex gap-3">
          <input type="number" className="w-40 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={caseId} onChange={(e) => setCaseId(e.target.value)} />
          <button className="rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-slate-950" onClick={handleGenerate}>Generate report</button>
        </div>
        {message && <div className="mt-4 text-sm text-green-400">{message}</div>}
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
        <h2 className="mb-4 text-xl font-semibold">Report records</h2>
        <div className="space-y-3">
          {reports.length === 0 ? <div className="text-slate-400">No reports generated yet.</div> : reports.map((report) => (
            <div key={report.id} className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <div>
                <div className="font-semibold text-cyan-300">{report.report_id}</div>
                <div className="text-sm text-slate-400">Case #{report.case_id}</div>
              </div>
              <button className="rounded bg-cyan-500/15 px-3 py-1.5 text-sm text-cyan-300 border border-cyan-500/30">Download</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
