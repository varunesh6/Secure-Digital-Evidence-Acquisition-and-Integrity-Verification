import { useEffect, useState } from 'react';
import { getUsers, createUser } from '../services/api';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ username: '', email: '', full_name: '', password: '', role: 'Investigator' });
  const [message, setMessage] = useState('');

  const loadUsers = async () => {
    try {
      const response = await getUsers();
      setUsers(response.data.users || []);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => { loadUsers(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createUser(form);
      setMessage('User created');
      setForm({ username: '', email: '', full_name: '', password: '', role: 'Investigator' });
      await loadUsers();
    } catch (error) {
      setMessage(error.response?.data?.error || 'Unable to create user.');
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
        <h2 className="mb-4 text-xl font-semibold">User management</h2>
        <div className="space-y-3">
          {users.map((user) => (
            <div key={user.id} className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <div className="font-semibold text-white">{user.full_name}</div>
              <div className="text-sm text-slate-400">{user.username} • {user.role}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
        <h2 className="mb-4 text-xl font-semibold">Add user</h2>
        <form className="space-y-3" onSubmit={handleSubmit}>
          <input className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          <input className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <input type="password" className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <select className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="Investigator">Investigator</option>
            <option value="Auditor">Auditor</option>
            <option value="Administrator">Administrator</option>
          </select>
          <button type="submit" className="w-full rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-slate-950">Create user</button>
          {message && <div className="text-sm text-cyan-300">{message}</div>}
        </form>
      </div>
    </div>
  );
}
