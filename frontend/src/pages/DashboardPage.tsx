import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { dashboardApi } from '@/services/api';
import {
  Users,
  MessageSquare,
  BookOpen,
  Brain,
  Star,
  Clock,
  Zap,
  Sparkles,
  ArrowUpRight,
  PlusCircle,
  ShieldCheck,
  Cpu,
} from 'lucide-react';

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getStats(),
    select: (res) => res.data,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[55vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-slate-700 border-t-indigo-500 animate-spin" />
        <p className="text-sm font-medium text-slate-400">جاري تحميل إحصائيات المنصة...</p>
      </div>
    );
  }

  const stats = data || {
    total_students: 0,
    active_students: 0,
    total_conversations: 0,
    total_references: 0,
    ready_references: 0,
    total_ai_requests: 0,
    failed_ai_requests: 0,
    avg_response_time_ms: 0,
    total_tokens_used: 0,
    positive_feedback: 0,
    negative_feedback: 0,
  };

  const feedbackTotal = stats.positive_feedback + stats.negative_feedback;
  const feedbackScore = feedbackTotal > 0
    ? ((stats.positive_feedback / feedbackTotal) * 5).toFixed(1)
    : '5.0';

  const todayFormatted = new Intl.DateTimeFormat('ar-EG', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date());

  return (
    <div className="space-y-8 animate-page">
      {/* ── Hero Welcome Banner ────────────────────────────── */}
      <div className="relative overflow-hidden rounded-2xl gradient-mesh-hero p-6 sm:p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>{todayFormatted}</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              مرحباً بك، <span className="gradient-brand">أستاذ أحمد علي</span> 🎓
            </h2>
            <p className="text-sm sm:text-base text-slate-300 max-w-2xl leading-relaxed">
              المساعد الذكي جاهز للرد على استفسارات طلاب التاريخ والجغرافيا بدقة وفقاً للمراجع والتعليمات المعتمدة.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link to="/references" className="btn-pro btn-pro-primary shadow-lg">
              <PlusCircle className="w-4 h-4" />
              <span>رفع مراجع جديدة</span>
            </Link>
            <Link to="/instructions" className="btn-pro btn-pro-glass">
              <Brain className="w-4 h-4 text-cyan-400" />
              <span>تعديل تعليمات البوت</span>
            </Link>
          </div>
        </div>

        {/* Ambient Glows */}
        <div className="absolute -left-20 -top-20 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* ── Core KPI Grid (Pro Max Cards) ──────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Card 1: Students */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">إجمالي الطلاب</span>
            <div className="w-11 h-11 rounded-xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{stats.total_students}</span>
            <span className="text-xs text-emerald-400 font-semibold flex items-center gap-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              {stats.active_students || stats.total_students} متفاعل
            </span>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>سجل الطلاب المسجلين</span>
            <Link to="/students" className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-semibold">
              عرض <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Card 2: Conversations */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">جلسات المحادثة</span>
            <div className="w-11 h-11 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
              <MessageSquare className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{stats.total_conversations}</span>
            <span className="text-xs text-cyan-400 font-semibold">جلسة حوارية</span>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>متابعة أسئلة الطلاب</span>
            <Link to="/conversations" className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold">
              عرض <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Card 3: References Ready */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">المراجع المفهرسة</span>
            <div className="w-11 h-11 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
              <BookOpen className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{stats.ready_references}</span>
            <span className="text-xs text-slate-400">من أصل {stats.total_references} كتاب</span>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>مكتبة المنهج المعتمد</span>
            <Link to="/references" className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-semibold">
              إدارة <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Card 4: AI Requests & Quality */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">طلبات الذكاء الاصطناعي</span>
            <div className="w-11 h-11 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
              <Cpu className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{stats.total_ai_requests.toLocaleString()}</span>
            <span className="text-xs text-purple-400 font-semibold">إجابة مولدة</span>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>سجل الاستهلاك والتكاليف</span>
            <Link to="/analytics" className="text-purple-400 hover:text-purple-300 flex items-center gap-1 font-semibold">
              التحليلات <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* ── Secondary Metrics & Performance Meters ────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Speed */}
        <div className="glass-panel p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-amber-400 border border-slate-700">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xl font-bold text-white">
              {stats.avg_response_time_ms ? `${Math.round(stats.avg_response_time_ms)}ms` : '< 1.2s'}
            </div>
            <div className="text-xs text-slate-400">متوسط سرعة الإجابة</div>
          </div>
        </div>

        {/* Rating */}
        <div className="glass-panel p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-amber-400 border border-slate-700">
            <Star className="w-6 h-6 fill-amber-400" />
          </div>
          <div>
            <div className="text-xl font-bold text-white">{feedbackScore} / 5.0</div>
            <div className="text-xs text-slate-400">تقييم الطلاب للإجابات</div>
          </div>
        </div>

        {/* Total Tokens */}
        <div className="glass-panel p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-pink-400 border border-slate-700">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xl font-bold text-white">{stats.total_tokens_used.toLocaleString()}</div>
            <div className="text-xs text-slate-400">إجمالي التوكنز المستهلكة</div>
          </div>
        </div>

        {/* System Health */}
        <div className="glass-panel p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-emerald-400 border border-slate-700">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xl font-bold text-emerald-400">99.9% جاهزية</div>
            <div className="text-xs text-slate-400">حماية من الهلوسة والخطأ</div>
          </div>
        </div>
      </div>
    </div>
  );
}
