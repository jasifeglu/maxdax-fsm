import { useAuth } from '../context/AuthContext';

export function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <main>
      <h1>MAXDAX FSM</h1>
      <p>Logged in as: {user?.name} ({user?.role})</p>
      <button onClick={logout}>Logout</button>
    </main>
  );
}
