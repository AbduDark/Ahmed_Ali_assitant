import { useState, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { instructionsApi } from '@/services/api';
import { Brain, Plus, Trash2, X, Sparkles, CheckCircle2 } from 'lucide-react';

export default function InstructionsPage() {
  const queryClient = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['instructions'],
    queryFn: () => instructionsApi.list(),
    select: (res) => res.data,
  });

  const createMutation = useMutation({
    mutationFn: (data: { content: string; title?: string }) => instructionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['instructions'] });
      setShowAdd(false);
      setContent('');
      setTitle('');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => instructionsApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['instructions'] }),
  });

  const handleCreate = (e: FormEvent) => {
    e.preventDefault();
    if (!content) return;
    createMutation.mutate({ content, title: title || undefined });
  };

  const instructions = (data as Record<string, unknown>[]) || [];

  return (
    <div className="space-y-6 animate-page">
      {/* ── Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">تعليمات وقواعد الأستاذ</h1>
          <p className="text-sm text-slate-400 mt-1">
            توجيه سلوك الذكاء الاصطناعي (طريقة الشرح، التبسيط، أسلوب الرد، والتنبيهات)
          </p>
        </div>
        <button className="btn-pro btn-pro-primary" onClick={() => setShowAdd(true)}>
          <Plus className="w-4 h-4" />
          <span>إضافة تعليمة جديدة</span>
        </button>
      </div>

      {/* ── Add Modal ──────────────────────────────────────── */}
      {showAdd && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                  <Brain className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-white">إضافة تعليمة جديدة للذكاء الاصطناعي</h3>
              </div>
              <button
                onClick={() => setShowAdd(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  عنوان التعليمة (اختياري)
                </label>
                <input
                  className="input-pro"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="مثال: أسلوب شرح المعارك التاريخية"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  نص التعليمة والتوجيه *
                </label>
                <textarea
                  className="input-pro min-h-[140px] resize-y"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="مثال: عند شرح أي موقع جغرافي، اذكر الموقع الفلكي والجغرافي وأهميته الاقتصادية..."
                  required
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  className="btn-pro btn-pro-glass"
                  onClick={() => setShowAdd(false)}
                >
                  إلغاء
                </button>
                <button
                  type="submit"
                  className="btn-pro btn-pro-primary"
                  disabled={createMutation.isPending}
                >
                  {createMutation.isPending ? 'جاري الحفظ...' : 'تطبيق التعليمة'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Instructions Cards ─────────────────────────────── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-indigo-500 animate-spin" />
          <p className="text-xs text-slate-400 font-medium">جاري جلب التعليمات المعتمدة...</p>
        </div>
      ) : !instructions.length ? (
        <div className="glass-panel text-center py-16 px-4">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto mb-4">
            <Brain className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-white mb-1">لا توجد تعليمات مخصصة</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-6">
            يعمل المساعد حالياً بالقواعد القياسية لمدرسي التاريخ والجغرافيا. يمكنك إضافة تعليمات إضافية في أي وقت.
          </p>
          <button onClick={() => setShowAdd(true)} className="btn-pro btn-pro-primary">
            <Plus className="w-4 h-4" />
            <span>إضافة تعليمة جديدة</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {instructions.map((inst) => (
            <div key={inst.id as string} className="glass-card p-5 flex flex-col justify-between group">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                      <Sparkles className="w-4 h-4" />
                    </div>
                    <span className="font-bold text-sm text-white">{inst.title as string || 'تعليمة مخصصة'}</span>
                  </div>
                  <button
                    className="btn-pro btn-pro-danger p-1.5 rounded-lg opacity-80 hover:opacity-100"
                    onClick={() => {
                      if (confirm('حذف هذه التعليمة؟')) deleteMutation.mutate(inst.id as string);
                    }}
                    title="حذف"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {inst.content as string}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="chip chip-emerald text-[11px]">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>نشط ومطبق على الإجابات</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
