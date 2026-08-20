import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  MessageSquare,
  BookOpen,
  Layers,
  Brain,
  CheckCircle,
  BarChart3,
  LogOut,
  GraduationCap,
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'الرئيسية', icon: LayoutDashboard, end: true },
  { path: '/students', label: 'الطلاب', icon: Users },
  { path: '/conversations', label: 'المحادثات', icon: MessageSquare },
  { path: '/references', label: 'المراجع', icon: BookOpen },
  { path: '/subjects', label: 'المواد', icon: Layers },
  { path: '/instructions', label: 'تعليمات الذكاء', icon: Brain },
  { path: '/corrections', label: 'تصحيحات المدرس', icon: CheckCircle },
  { path: '/analytics', label: 'التحليلات', icon: BarChart3 },
];

export default function Sidebar() {
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div style={{ padding: '1.5rem 1.25rem', borderBottom: '1px solid var(--color-border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            className="gradient-primary"
            style={{
              width: 40,
              height: 40,
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <GraduationCap size={22} color="white" />
          </div>
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 700 }}>المساعد التعليمي</h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>لوحة التحكم</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ padding: '0.75rem 0', flex: 1 }}>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            style={{ position: 'relative' }}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div style={{ padding: '1rem 0.75rem', borderTop: '1px solid var(--color-border)' }}>
        <button
          onClick={handleLogout}
          className="nav-item"
          style={{
            width: '100%',
            border: 'none',
            background: 'none',
            cursor: 'pointer',
            color: 'var(--color-danger)',
          }}
        >
          <LogOut size={20} />
          <span>تسجيل الخروج</span>
        </button>
      </div>
    </aside>
  );
}
