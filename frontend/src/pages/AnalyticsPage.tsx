import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/services/api';
import {
  BarChart3,
  Cpu,
  Zap,
  AlertTriangle,
  Clock,
  TrendingUp,
  Server,
  Layers,
  Sparkles,
} from 'lucide-react';

export default function AnalyticsPage() {
  const { data: usage, isLoading } = useQuery({
    queryKey: ['ai-usage'],
    queryFn: () => analyticsApi.getAiUsage(30),
    select: (res) => res.data,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-indigo-500 animate-spin" />
        <p className="text-xs text-slate-400 font-medium">جاري تحليل بيانات استهلاك الذكاء الاصطناعي...</p>
      </div>
    );
  }

  const stats = usage || {
    total_requests: 0,
    total_input_tokens: 0,
    total_output_tokens: 0,
    total_tokens: 0,
    avg_latency_ms: 0,
    error_rate: 0,
    requests_by_provider: {},
    requests_by_model: {},
  };

  const totalTokens = stats.total_tokens || 1;
  const inputPct = Math.round((stats.total_input_tokens / totalTokens) * 100);
  const outputPct = Math.round((stats.total_output_tokens / totalTokens) * 100);

  return (
    <div className="space-y-8 animate-page">
      {/* ── Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">تحليلات استهلاك الذكاء الاصطناعي</h1>
          <p className="text-sm text-slate-400 mt-1">مراقبة التوكنز، سرعة الاستجابة، ونماذج التوليد خلال آخر 30 يوماً</p>
        </div>
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-bold">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span>تحديث فوري مباشر</span>
        </div>
      </div>

      {/* ── Top Metric Cards ───────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Requests */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">إجمالي الطلبات</span>
            <div className="w-10 h-10 rounded-xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Cpu className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-white">{stats.total_requests.toLocaleString()}</div>
            <div className="text-xs text-indigo-300 mt-1">طلب معالجة وإجابة</div>
          </div>
        </div>

        {/* Total Tokens */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">التوكنز المستهلكة</span>
            <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Zap className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-white">{stats.total_tokens.toLocaleString()}</div>
            <div className="text-xs text-cyan-300 mt-1">إجمالي Input + Output</div>
          </div>
        </div>

        {/* Avg Latency */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">متوسط سرعة الإجابة</span>
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-white">
              {stats.avg_latency_ms ? `${Math.round(stats.avg_latency_ms)}ms` : '< 1s'}
            </div>
            <div className="text-xs text-amber-300 mt-1">زمن التوليد والرد</div>
          </div>
        </div>

        {/* Error Rate */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">معدل النجاح</span>
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Server className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-emerald-400">
              {(100 - (stats.error_rate || 0)).toFixed(1)}%
            </div>
            <div className="text-xs text-slate-400 mt-1">نسبة الأخطاء {stats.error_rate?.toFixed(1) || '0.0'}%</div>
          </div>
        </div>
      </div>

      {/* ── Visual Analytics Grids ─────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Token Distribution Breakdown */}
        <div className="glass-panel p-6 space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              <h3 className="font-bold text-base text-white">توزيع التوكنز (Tokens)</h3>
            </div>
            <span className="text-xs text-slate-400">Input vs Output</span>
          </div>

          <div className="space-y-5">
            {/* Input Tokens */}
            <div>
              <div className="flex justify-between text-xs font-bold mb-2">
                <span className="text-indigo-300">توكنز الإدخال (السياق والأسئلة)</span>
                <span className="text-white">{stats.total_input_tokens.toLocaleString()} ({inputPct}%)</span>
              </div>
              <div className="h-3 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full transition-all duration-700"
                  style={{ width: `${inputPct}%` }}
                />
              </div>
            </div>

            {/* Output Tokens */}
            <div>
              <div className="flex justify-between text-xs font-bold mb-2">
                <span className="text-cyan-300">توكنز الإخراج (إجابات المساعد)</span>
                <span className="text-white">{stats.total_output_tokens.toLocaleString()} ({outputPct}%)</span>
              </div>
              <div className="h-3 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-cyan-400 to-emerald-400 rounded-full transition-all duration-700"
                  style={{ width: `${outputPct}%` }}
                />
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 flex items-center justify-between">
            <span>التكلفة التقديرية (مجاني عبر Groq / Gemini):</span>
            <span className="font-bold text-emerald-400">$0.00 USD</span>
          </div>
        </div>

        {/* AI Providers Distribution */}
        <div className="glass-panel p-6 space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-cyan-400" />
              <h3 className="font-bold text-base text-white">توزيع مزودي الذكاء الاصطناعي</h3>
            </div>
            <span className="text-xs text-slate-400">سجل الاستدعاء</span>
          </div>

          {Object.keys(stats.requests_by_provider || {}).length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-400">
              لا توجد طلبات مسجلة بعد. عند إجابة الطلاب على تليجرام ستظهر الإحصائيات هنا.
            </div>
          ) : (
            <div className="space-y-3">
              {Object.entries(stats.requests_by_provider).map(([provider, count]) => (
                <div
                  key={provider}
                  className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-xs uppercase">
                      {provider.substring(0, 2)}
                    </div>
                    <div>
                      <div className="font-bold text-sm text-white uppercase">{provider}</div>
                      <div className="text-[11px] text-slate-400">نموذج التوليد الأساسي</div>
                    </div>
                  </div>
                  <span className="chip chip-indigo font-bold text-xs">
                    {(count as number).toLocaleString()} طلب
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
