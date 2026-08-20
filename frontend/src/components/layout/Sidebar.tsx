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
  GraduationCap,
  Sparkles,
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'الرئيسية والإحصائيات', icon: LayoutDashboard, end: true },
  { path: '/students', label: 'الطلاب المشتركون', icon: Users },
  { path: '/conversations', label: 'المحادثات المباشرة', icon: MessageSquare },
  { path: '/references', label: 'المراجع والكتب المعتمدة', icon: BookOpen },
  { path: '/subjects', label: 'المنهج والدروس', icon: Layers },
  { path: '/instructions', label: 'تعليمات الأستاذ', icon: Brain },
  { path: '/corrections', label: 'قاعدة التصحيحات', icon: CheckCircle },
  { path: '/analytics', label: 'استهلاك الذكاء الاصطناعي', icon: BarChart3 },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/25 border border-white/20">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h2 className="text-base font-extrabold text-white tracking-wide brand-title">الجنرال AI</h2>
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            </div>
            <p className="text-[11px] font-medium text-slate-400 tracking-wider">منصة المساعد الذكي</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="py-4 flex-1 overflow-y-auto space-y-1">
        <div className="px-5 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          القائمة الرئيسية
        </div>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}
          >
            <item.icon className="w-[19px] h-[19px] flex-shrink-0" />
            <span className="nav-text truncate">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Teacher Profile Widget in Sidebar */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center font-bold text-white text-xs border border-white/10">
            أع
          </div>
          <div className="sidebar-profile-info truncate">
            <div className="text-xs font-bold text-slate-200 truncate">أ/ أحمد علي</div>
            <div className="text-[10px] text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              مدرس أول تاريخ وجغرافيا
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
