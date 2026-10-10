import { useEffect, useState } from 'react';
import { createCase, getCases } from '../services/api';

export default function CasesPage() {
  const [cases, setCases] = useState([]);
  const [form, setForm] = useState({ title: '', incident_category: 'Cybercrime', priority: 'MEDIUM', status: 'OPEN', notes: '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const loadCases = async () => {
    try {
      const response = await getCases();
      setCases(response.data.cases || []);
    } catch (err) {
      setError('Unable to load cases.');
    }
  };

  useEffect(() => { loadCases(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createCase(form);
      setMessage('Case created successfully.');
      setError('');
      setForm({ title: '', incident_category: 'Cybercrime', priority: 'MEDIUM', status: 'OPEN', notes: '' });
      await loadCases();
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to create case.');
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
        <h2 className="mb-4 text-xl font-semibold">Case registry</h2>
        <div className="space-y-3">
          {cases.length === 0 ? <div className="text-slate-400">No cases yet.</div> : cases.map((c) => (
            <div key={c.id} className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-cyan-300">{c.case_number}</div>
                  <div className="font-semibold text-white">{c.title}</div>
                </div>
                <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2 py-1 text-xs text-cyan-300">{c.status}</span>
              </div>
              <div className="mt-2 text-sm text-slate-400">Category: {c.incident_category} | Priority: {c.priority}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
        <h2 className="mb-4 text-xl font-semibold">Create case</h2>
        <form className="space-y-3" onSubmit={handleSubmit}>
          <input className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Case title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <select className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.incident_category} onChange={(e) => setForm({ ...form, incident_category: e.target.value })}>
            <option value="Cybercrime">Cybercrime</option>
            <option value="Fraud">Fraud</option>
            <option value="Harassment">Harassment</option>
            <option value="Data Breach">Data Breach</option>
          </select>
          <div className="grid gap-3 sm:grid-cols-2">
            <select className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
            <select className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              <option value="OPEN">Open</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>
          <textarea className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" rows="4" placeholder="Case notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          {message && <div className="text-sm text-green-400">{message}</div>}
          {error && <div className="text-sm text-red-400">{error}</div>}
          <button type="submit" className="w-full rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-slate-950">Create case</button>
        </form>
      </div>
    </div>
  );
}
