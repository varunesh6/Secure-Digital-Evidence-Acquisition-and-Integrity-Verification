import { useEffect, useState } from 'react';
import { getAuditLogs } from '../services/api';

export default function AuditPage() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await getAuditLogs();
        setLogs(response.data.logs || []);
      } catch (error) {
        console.error(error);
      }
    };
    load();
  }, []);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
      <h2 className="mb-4 text-xl font-semibold">Audit logs</h2>
      <div className="space-y-3">
        {logs.length === 0 ? <div className="text-slate-400">No audit activity.</div> : logs.map((log) => (
          <div key={log.id} className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
            <div className="flex items-center justify-between gap-4">
              <div className="text-cyan-300">{log.action_type}</div>
              <div className="text-xs text-slate-500">{log.timestamp}</div>
            </div>
            <div className="mt-2 text-sm text-slate-300">{log.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
