import { useEffect, useState } from 'react';
import { BarChart, Bar, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, PieChart, Pie, Cell } from 'recharts';
import { getDashboard } from '../services/api';

const panel = 'rounded-2xl border border-slate-800 bg-slate-900/80 p-5';
const colors = ['#22d3ee', '#60a5fa', '#34d399', '#f87171', '#fbbf24'];

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await getDashboard();
        setStats(response.data);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <div className="text-cyan-300">Loading dashboard...</div>;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ['Total cases', stats.stats.total_cases],
          ['Open cases', stats.stats.open_cases],
          ['Evidence items', stats.stats.total_registered_evidence],
          ['Verified', stats.stats.evidence_verified_successfully],
        ].map(([label, value]) => (
          <div key={label} className={panel}>
            <div className="text-sm text-slate-400">{label}</div>
            <div className="mt-3 text-3xl font-bold text-cyan-300">{value}</div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className={panel}>
          <div className="mb-4 text-lg font-semibold text-white">Case status distribution</div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.case_status_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#cbd5e1" />
                <YAxis stroke="#cbd5e1" />
                <Tooltip />
                <Bar dataKey="value" fill="#22d3ee" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className={panel}>
          <div className="mb-4 text-lg font-semibold text-white">Evidence file types</div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={stats.evidence_file_type_distribution} dataKey="value" nameKey="name" outerRadius={90} label>
                  {stats.evidence_file_type_distribution.map((entry, index) => (
                    <Cell key={entry.name} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className={panel}>
          <h3 className="mb-3 text-lg font-semibold text-white">Recent activity</h3>
          <div className="space-y-3">
            {stats.recent_activity.map((event, idx) => (
              <div key={idx} className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="text-sm font-medium text-cyan-300">{event.action_type}</div>
                <div className="text-sm text-slate-300">{event.description}</div>
                <div className="text-xs text-slate-500">{event.timestamp}</div>
              </div>
            ))}
          </div>
        </div>

        <div className={panel}>
          <h3 className="mb-3 text-lg font-semibold text-white">Recent verification results</h3>
          <div className="space-y-3">
            {stats.recent_verifications.map((result, idx) => (
              <div key={idx} className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="text-sm text-cyan-300">Evidence {result.evidence_id}</div>
                <div className="text-sm text-slate-300">{result.result}</div>
                <div className="text-xs text-slate-500">{result.verification_timestamp}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
