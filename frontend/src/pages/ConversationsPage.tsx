import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { conversationsApi } from '@/services/api';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, ChevronLeft, Calendar, Search, User } from 'lucide-react';

export default function ConversationsPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => conversationsApi.list({ limit: 50 }),
    select: (res) => res.data,
  });

  const conversations = data?.conversations || [];
  const filtered = conversations.filter((c: Record<string, unknown>) => {
    if (!search) return true;
    const title = (c.title as string || '').toLowerCase();
    return title.includes(search.toLowerCase());
  });

  return (
    <div className="space-y-6 animate-page">
      {/* ── Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">سجل المحادثات والأسئلة</h1>
          <p className="text-sm text-slate-400 mt-1">مراجعة المحادثات المباشرة بين الطلاب والمساعد الذكي</p>
        </div>
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-bold">
          <MessageSquare className="w-4 h-4 text-cyan-400" />
          <span>{conversations.length} جلسة محادثة</span>
        </div>
      </div>

      {/* ── Search Bar ────────────────────────────────────── */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          className="input-pro pr-10"
          placeholder="بحث في مواضيع وأسئلة المحادثات..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* ── Conversation Cards ────────────────────────────── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-cyan-500 animate-spin" />
          <p className="text-xs text-slate-400 font-medium">جاري تحميل سجل المحادثات...</p>
        </div>
      ) : !filtered.length ? (
        <div className="glass-panel text-center py-16 px-4">
          <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mx-auto mb-4">
            <MessageSquare className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-white mb-1">لا توجد محادثات مسجلة</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            ستظهر هنا جميع الجلسات الحوارية والأسئلة فور بدء تفاعل الطلاب عبر تليجرام.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((conv: Record<string, unknown>) => (
            <div
              key={conv.id as string}
              onClick={() => navigate(`/conversations/${conv.id}`)}
              className="glass-card p-5 cursor-pointer flex items-center justify-between group"
            >
              <div className="flex items-start gap-3.5 min-w-0">
                <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-cyan-500/20 to-indigo-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 flex-shrink-0 group-hover:scale-105 transition-transform">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                  <h3 className="font-bold text-sm text-white truncate group-hover:text-cyan-300 transition-colors">
                    {conv.title as string || 'محادثة تعليمية جديدة'}
                  </h3>
                  <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-3 h-3 text-cyan-400" />
                      <span>{conv.message_count as number || 0} رسالة</span>
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-slate-400" />
                      <span>{new Date(conv.created_at as string).toLocaleDateString('ar-EG')}</span>
                    </span>
                  </div>
                </div>
              </div>

              <div className="w-8 h-8 rounded-lg bg-slate-800/80 flex items-center justify-center text-slate-400 group-hover:text-cyan-300 group-hover:bg-cyan-500/10 transition-all mr-2 flex-shrink-0">
                <ChevronLeft className="w-4 h-4" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
