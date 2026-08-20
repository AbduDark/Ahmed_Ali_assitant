import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { studentsApi } from '@/services/api';
import { Users, Search, MessageSquare, ExternalLink, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function StudentsPage() {
  const [search, setSearch] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['students', search],
    queryFn: () => studentsApi.list({ search: search || undefined, limit: 50 }),
    select: (res) => res.data,
  });

  const students = data?.students || [];

  return (
    <div className="space-y-6 animate-page">
      {/* ── Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">سجل الطلاب والنشاط</h1>
          <p className="text-sm text-slate-400 mt-1">متابعة حسابات الطلاب المتفاعلين مع بوت المساعد التعليمي</p>
        </div>
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-bold">
          <Users className="w-4 h-4 text-indigo-400" />
          <span>{students.length} طالب مسجل</span>
        </div>
      </div>

      {/* ── Search & Filter Bar ────────────────────────────── */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            className="input-pro pr-10"
            placeholder="بحث بالاسم أو اسم المستخدم على تليجرام..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-white"
            >
              مسح
            </button>
          )}
        </div>
      </div>

      {/* ── Data Table ────────────────────────────────────── */}
      <div className="glass-panel overflow-hidden">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-indigo-500 animate-spin" />
            <p className="text-xs text-slate-400 font-medium">جاري جلب سجل الطلاب...</p>
          </div>
        ) : !students.length ? (
          <div className="text-center py-16 px-4">
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto mb-4">
              <Users className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-white mb-1">لا يوجد طلاب مسجلون حالياً</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              بمجرد أن يبدأ الطلاب في محادثة البوت على تليجرام، سيتم تسجيل بياناتهم ومحادثاتهم هنا تلقائياً.
            </p>
          </div>
        ) : (
          <div className="table-container">
            <table className="pro-table">
              <thead>
                <tr>
                  <th>الطالب</th>
                  <th>معرف تليجرام</th>
                  <th>الصف الدراسي</th>
                  <th>اللغة</th>
                  <th>آخر ظهور</th>
                  <th>الحالة</th>
                  <th className="text-left">الإجراءات</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student: Record<string, unknown>) => {
                  const fullName = `${student.first_name || ''} ${student.last_name || ''}`.trim() || 'طالب مجهول';
                  const username = student.username as string;
                  const initial = fullName ? fullName[0].toUpperCase() : 'ط';

                  return (
                    <tr key={student.id as string}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600/40 to-cyan-500/40 border border-indigo-500/30 flex items-center justify-center text-indigo-300 font-bold text-sm">
                            {initial}
                          </div>
                          <div>
                            <div className="font-bold text-white text-sm">{fullName}</div>
                            <div className="text-[11px] text-slate-400">ID: {student.telegram_user_id as string || '—'}</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        {username ? (
                          <a
                            href={`https://t.me/${username}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                          >
                            <span>@{username}</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        ) : (
                          <span className="text-xs text-slate-400">غير متوفر</span>
                        )}
                      </td>
                      <td>
                        <span className="text-xs font-medium text-slate-300">
                          {student.grade as string || 'عام'}
                        </span>
                      </td>
                      <td>
                        <span className="text-xs text-slate-300">
                          {student.preferred_language as string === 'ar' ? '🇪🇬 العربية' : 'English'}
                        </span>
                      </td>
                      <td>
                        <div className="flex items-center gap-1.5 text-xs text-slate-400">
                          <Calendar className="w-3.5 h-3.5" />
                          <span>
                            {student.last_seen_at
                              ? new Date(student.last_seen_at as string).toLocaleDateString('ar-EG', {
                                  month: 'short',
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })
                              : '—'}
                          </span>
                        </div>
                      </td>
                      <td>
                        <span className={`chip ${student.is_active ? 'chip-emerald' : 'chip-rose'}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${student.is_active ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                          {student.is_active ? 'نشط' : 'معطل'}
                        </span>
                      </td>
                      <td className="text-left">
                        <Link
                          to={`/conversations?student_id=${student.id}`}
                          className="btn-pro btn-pro-glass text-xs py-1.5 px-3 flex items-center gap-1.5 text-indigo-300 hover:text-white"
                        >
                          <MessageSquare className="w-3.5 h-3.5" />
                          <span>المحادثات</span>
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
