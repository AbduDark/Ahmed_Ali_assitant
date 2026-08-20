import { useLocation, Link, useNavigate } from 'react-router-dom';

const routeTitles: Record<string, string> = {
  '/': 'نظرة عامة والتحليلات',
  '/students': 'سجل الطلاب والتفاعل',
  '/conversations': 'سجل المحادثات والأسئلة',
  '/references': 'بنك المراجع والكتب',
  '/subjects': 'المنهج الدراسي والمواد',
  '/instructions': 'تعليمات وقواعد الأستاذ',
  '/corrections': 'تصحيحات الذكاء الاصطناعي',
  '/analytics': 'إحصائيات استهلاك الذكاء الاصطناعي',
};

export const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  const currentTitle = routeTitles[location.pathname] || 'لوحة التحكم';

  return (
    <header className="top-header">
      {/* Breadcrumb & Current View */}
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 text-sm text-slate-400">
          <Link to="/" className="hover:text-indigo-400 transition-colors">الرئيسية</Link>
          <span>/</span>
        </div>
        <h1 className="text-lg font-bold text-white tracking-tight">{currentTitle}</h1>
      </div>

      {/* Live Server Indicator & User Profile */}
      <div className="flex items-center gap-4">
        {/* System Status Pill */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
          <span className="live-dot"></span>
          <span>الخادم والذكاء الاصطناعي متصل</span>
        </div>

        {/* Telegram Bot Link */}
        <a
          href="https://t.me/Gen_Assis_Bot"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-pro btn-pro-glass text-xs py-1.5 px-3 flex items-center gap-1.5 text-indigo-300 hover:text-white"
          title="فتح البوت في تليجرام"
        >
          <svg className="w-4 h-4 text-cyan-400" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/>
          </svg>
          <span className="hidden sm:inline">البوت المباشر</span>
        </a>

        {/* User Info & Quick Logout */}
        <div className="flex items-center gap-3 border-r border-slate-700/60 pr-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center font-bold text-white text-sm shadow-md shadow-indigo-500/20">
            أ
          </div>
          <div className="hidden lg:block text-right">
            <div className="text-xs font-bold text-slate-200">الأستاذ أحمد علي</div>
            <div className="text-[11px] text-slate-400">المشرف العام</div>
          </div>
          <button
            onClick={handleLogout}
            className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
            title="تسجيل الخروج"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};
