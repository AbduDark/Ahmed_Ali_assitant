import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function DashboardLayout() {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <main className="main-content animate-fade-in">
        <Outlet />
      </main>
    </div>
  );
}
