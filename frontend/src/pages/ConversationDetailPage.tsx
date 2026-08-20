import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { conversationsApi } from '@/services/api';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  Clock,
  Brain,
  BookOpen,
  User,
  Bot,
  Zap,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
} from 'lucide-react';

export default function ConversationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['conversation', id],
    queryFn: () => conversationsApi.get(id!),
    select: (res) => res.data,
    enabled: !!id,
  });

  const handleCopy = (text: string, msgId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(msgId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-cyan-500 animate-spin" />
        <p className="text-xs text-slate-400 font-medium">جاري تحميل رسائل المحادثة...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="glass-panel p-12 text-center">
        <p className="text-slate-300 font-medium mb-4">المحادثة المطلوبة غير موجودة أو تم حذفها.</p>
        <button onClick={() => navigate('/conversations')} className="btn-pro btn-pro-primary">
          العودة للمحادثات
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-page max-w-4xl mx-auto">
      {/* ── Top Header ────────────────────────────────────── */}
      <div className="flex items-center justify-between gap-4 p-4 rounded-2xl glass-panel">
        <div className="flex items-center gap-3.5 min-w-0">
          <button
            onClick={() => navigate('/conversations')}
            className="btn-pro btn-pro-glass p-2.5 rounded-xl text-slate-300 hover:text-white"
            title="رجوع"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
          <div className="min-w-0">
            <h1 className="text-base sm:text-lg font-bold text-white truncate">
              {data.title || 'تفاصيل المحادثة التعليمية'}
            </h1>
            <p className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
              <span>{data.message_count} رسالة متبادلة</span>
              <span>•</span>
              <span>{new Date(data.created_at).toLocaleDateString('ar-EG', { dateStyle: 'long' })}</span>
            </p>
          </div>
        </div>
      </div>

      {/* ── Messages Stream (Telegram-Style UX) ─────────────── */}
      <div className="space-y-6 py-2">
        {data.messages?.map((msg: Record<string, unknown>) => {
          const isStudent = msg.role === 'student' || msg.role === 'user';
          const msgId = msg.id as string;
          const content = (msg.content as string) || '';
          const chunks = (msg.retrieved_chunks as Record<string, unknown>[]) || [];

          return (
            <div key={msgId} className={`flex flex-col ${isStudent ? 'items-start' : 'items-end'} animate-page`}>
              {/* Sender Tag */}
              <div className={`flex items-center gap-2 mb-1.5 px-1 text-xs font-bold ${isStudent ? 'text-indigo-400' : 'text-cyan-400'}`}>
                {isStudent ? (
                  <>
                    <div className="w-5 h-5 rounded-md bg-indigo-500/20 flex items-center justify-center">
                      <User className="w-3 h-3" />
                    </div>
                    <span>الطالب</span>
                  </>
                ) : (
                  <>
                    <div className="w-5 h-5 rounded-md bg-cyan-500/20 flex items-center justify-center">
                      <Bot className="w-3 h-3" />
                    </div>
                    <span>الجنرال AI (المساعد التعليمي)</span>
                  </>
                )}
              </div>

              {/* Message Bubble */}
              <div className={isStudent ? 'chat-bubble-student relative group' : 'chat-bubble-bot relative group'}>
                <div className="text-sm leading-relaxed whitespace-pre-wrap select-text">
                  {content}
                </div>

                {/* Quick Copy Action */}
                <button
                  onClick={() => handleCopy(content, msgId)}
                  className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg bg-slate-900/60 hover:bg-slate-900 text-slate-400 hover:text-white"
                  title="نسخ النص"
                >
                  {copiedId === msgId ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>

              {/* RAG Diagnostics & Metadata (Assistant Messages) */}
              {!isStudent && (
                <div className="mt-2 flex flex-wrap items-center gap-2 px-1 max-w-[82%]">
                  {/* Latency */}
                  {msg.response_time_ms ? (
                    <span className="chip chip-amber text-[11px]">
                      <Clock className="w-3 h-3" />
                      <span>{msg.response_time_ms as number}ms</span>
                    </span>
                  ) : null}

                  {/* AI Provider */}
                  {msg.ai_provider ? (
                    <span className="chip chip-indigo text-[11px]">
                      <Brain className="w-3 h-3" />
                      <span>{msg.ai_provider as string} ({msg.ai_model as string})</span>
                    </span>
                  ) : null}

                  {/* Confidence Score */}
                  {msg.confidence_score != null ? (
                    <span className={`chip ${(msg.confidence_score as number) > 0.6 ? 'chip-emerald' : 'chip-amber'} text-[11px]`}>
                      {(msg.confidence_score as number) > 0.6 ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                      <span>دقة الإجابة: {Math.round((msg.confidence_score as number) * 100)}%</span>
                    </span>
                  ) : null}

                  {/* Token Count */}
                  {(msg.input_tokens || msg.output_tokens) ? (
                    <span className="chip chip-cyan text-[11px]">
                      <Zap className="w-3 h-3" />
                      <span>{((msg.input_tokens as number || 0) + (msg.output_tokens as number || 0))} توكن</span>
                    </span>
                  ) : null}
                </div>
              )}

              {/* Retrieved Chunks Accordion */}
              {!isStudent && chunks.length > 0 && (
                <details className="mt-2 max-w-[82%] w-full glass-panel p-3 rounded-xl border border-indigo-500/20 text-xs">
                  <summary className="font-bold text-indigo-300 cursor-pointer flex items-center gap-1.5 select-none hover:text-indigo-200">
                    <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                    <span>المراجع المقتبس منها في الإجابة ({chunks.length} اقتباس)</span>
                  </summary>
                  <div className="mt-3 space-y-2 pt-2 border-t border-slate-800">
                    {chunks.map((chunk, i) => (
                      <div key={i} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                        <div className="font-bold text-indigo-300 mb-1 flex items-center justify-between">
                          <span>{chunk.reference_title as string || 'مرجع معتمد'} {chunk.page_number ? `(صفحة ${chunk.page_number})` : ''}</span>
                          <span className="text-[10px] text-slate-400">تطابق: {Math.round((chunk.score as number || 0) * 100)}%</span>
                        </div>
                        <p className="text-slate-300 text-[11px] leading-relaxed">
                          {chunk.content as string}
                        </p>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
