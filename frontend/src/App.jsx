import { useEffect, useState } from 'react';
import { Navigate, Route, Routes, Link, useNavigate, useLocation } from 'react-router-dom';
import { getMe, logout } from './services/api';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CasesPage from './pages/CasesPage';
import EvidencePage from './pages/EvidencePage';
import ReportsPage from './pages/ReportsPage';
import AuditPage from './pages/AuditPage';
import UsersPage from './pages/UsersPage';

const layoutClasses = 'min-h-screen bg-slate-950 text-slate-100';

function ProtectedRoute({ user, children }) {
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function AppShell({ user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const navItems = [
    { label: 'Dashboard', to: '/dashboard' },
    { label: 'Cases', to: '/cases' },
    { label: 'Evidence', to: '/evidence' },
    { label: 'Reports', to: '/reports' },
    { label: 'Audit', to: '/audit' },
    { label: 'Users', to: '/users' },
  ];

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error(error);
    }
    onLogout();
    navigate('/login');
  };

  return (
    <div className={layoutClasses}>
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-800">
          <div>
            <div className="text-sm uppercase tracking-[0.28em] text-cyan-400">Evidence</div>
            <div className="text-xl font-bold">Console</div>
          </div>
        </div>
        <nav className="p-4 space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={`block rounded-lg px-3 py-2 text-sm transition ${location.pathname === item.to ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-300 hover:bg-slate-800'}`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      <main className="ml-64 min-h-screen p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-400">Secure digital evidence</p>
            <h1 className="mt-1 text-2xl font-bold">Operations dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm">
              <div className="text-slate-400">Signed in as</div>
              <div className="font-semibold text-cyan-300">{user?.full_name || user?.username}</div>
            </div>
            <button className="rounded-lg bg-red-500/15 px-4 py-2 text-sm text-red-200 border border-red-500/30" onClick={handleLogout}>Logout</button>
          </div>
        </div>
        <Routes>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/cases" element={<CasesPage />} />
          <Route path="/evidence" element={<EvidencePage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/audit" element={<AuditPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await getMe();
        setUser(res.data.user);
      } catch (error) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center bg-slate-950 text-cyan-300">Loading evidence console...</div>;
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage onLogin={(u) => setUser(u)} />} />
      <Route path="/" element={<ProtectedRoute user={user}><AppShell user={user} onLogout={() => setUser(null)} /></ProtectedRoute>} />
      <Route path="*" element={<ProtectedRoute user={user}><AppShell user={user} onLogout={() => setUser(null)} /></ProtectedRoute>} />
    </Routes>
  );
}
