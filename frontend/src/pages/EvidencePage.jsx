import { useEffect, useState } from 'react';
import { getEvidence, uploadEvidence, verifyEvidence } from '../services/api';

export default function EvidencePage() {
  const [items, setItems] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [caseId, setCaseId] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const loadData = async () => {
    try {
      const response = await getEvidence();
      setItems(response.data.evidence || []);
    } catch (err) {
      setError('Unable to load evidence.');
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Choose a file first.');
      return;
    }
    const form = new FormData();
    form.append('file', selectedFile);
    form.append('case_id', caseId || '1');
    form.append('source_device', 'Demo laptop');
    form.append('acquisition_method', 'FILE_UPLOAD');
    try {
      const response = await uploadEvidence(form);
      setMessage(response.data.message);
      setError('');
      setSelectedFile(null);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.error || 'File upload failed.');
    }
  };

  const handleVerify = async (id) => {
    try {
      const response = await verifyEvidence(id);
      setMessage(`Verification result: ${response.data.result}`);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.error || 'Verification failed.');
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
        <h2 className="mb-4 text-xl font-semibold">Evidence intake</h2>
        <form className="space-y-3" onSubmit={handleUpload}>
          <input type="number" className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Case ID" value={caseId} onChange={(e) => setCaseId(e.target.value)} />
          <input type="file" className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" onChange={(e) => setSelectedFile(e.target.files[0])} />
          {error && <div className="text-sm text-red-400">{error}</div>}
          {message && <div className="text-sm text-green-400">{message}</div>}
          <button type="submit" className="w-full rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-slate-950">Register evidence</button>
        </form>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
        <h2 className="mb-4 text-xl font-semibold">Evidence inventory</h2>
        <div className="space-y-3">
          {items.length === 0 ? <div className="text-slate-400">No evidence found.</div> : items.map((item) => (
            <div key={item.id} className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-cyan-300">Evidence #{item.id}</div>
                  <div className="font-semibold text-white">{item.original_filename}</div>
                </div>
                <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-1 text-xs text-emerald-300">{item.status}</span>
              </div>
              <div className="mt-2 text-sm text-slate-400">SHA256: {item.original_sha256?.slice(0, 24)}...</div>
              <div className="mt-3 flex gap-2">
                <button onClick={() => handleVerify(item.id)} className="rounded bg-amber-500/15 px-3 py-1.5 text-sm text-amber-300 border border-amber-500/30">Verify</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
