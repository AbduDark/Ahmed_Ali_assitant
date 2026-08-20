import React, { useState, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { correctionsApi } from '@/services/api';
import { CheckCircle, Plus, Trash2, X, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react';

export default function CorrectionsPage() {
  const queryClient = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [question, setQuestion] = useState('');
  const [correctAnswer, setCorrectAnswer] = useState('');
  const [badAnswer, setBadAnswer] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['corrections'],
    queryFn: () => correctionsApi.list(),
    select: (res) => res.data,
  });

  const createMutation = useMutation({
    mutationFn: (data: { question: string; correct_answer: string; bad_answer?: string }) =>
      correctionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['corrections'] });
      setShowAdd(false);
      setQuestion('');
      setCorrectAnswer('');
      setBadAnswer('');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => correctionsApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['corrections'] }),
  });

  const handleCreate = (e: FormEvent) => {
    e.preventDefault();
    if (!question || !correctAnswer) return;
    createMutation.mutate({ question, correct_answer: correctAnswer, bad_answer: badAnswer || undefined });
  };

  const corrections = (data as Record<string, unknown>[]) || [];

  return (
    <div className="space-y-6 animate-page">
      {/* ── Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">قاعدة تصحيحات المدرس</h1>
          <p className="text-sm text-slate-400 mt-1">
            تصحيح الأسئلة الشائعة وتثبيت إجابات نموذجية معتمدة لها أولوية قصوى على الذكاء الاصطناعي
          </p>
        </div>
        <button className="btn-pro btn-pro-primary" onClick={() => setShowAdd(true)}>
          <Plus className="w-4 h-4" />
          <span>إضافة تصحيح معتمد</span>
        </button>
      </div>

      {/* ── Add Modal ──────────────────────────────────────── */}
      {showAdd && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <CheckCircle className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-white">إضافة تصحيح وإجابة معتمدة</h3>
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
                  السؤال أو المسألة *
                </label>
                <textarea
                  className="input-pro min-h-[70px] resize-y"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="مثال: ما هي أسباب فشل الحملة الفرنسية على بلاد الشام؟"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  الإجابة الخاطئة أو غير الدقيقة (اختياري)
                </label>
                <textarea
                  className="input-pro min-h-[70px] resize-y"
                  value={badAnswer}
                  onChange={(e) => setBadAnswer(e.target.value)}
                  placeholder="الإجابة التي قدمها البوت وتريد تصحيحها..."
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2">
                  الإجابة النموذجية المعتمدة *
                </label>
                <textarea
                  className="input-pro min-h-[100px] resize-y border-emerald-500/40 focus:border-emerald-400"
                  value={correctAnswer}
                  onChange={(e) => setCorrectAnswer(e.target.value)}
                  placeholder="اكتب الإجابة الدقيقة وفقاً للمنهج والامتحانات..."
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
                  {createMutation.isPending ? 'جاري الحفظ...' : 'حفظ التصحيح المعتمد'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Corrections List ───────────────────────────────── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-emerald-500 animate-spin" />
          <p className="text-xs text-slate-400 font-medium">جاري فحص قاعدة التصحيحات...</p>
        </div>
      ) : !corrections.length ? (
        <div className="glass-panel text-center py-16 px-4">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mx-auto mb-4">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-white mb-1">لا توجد تصحيحات مضافة</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-6">
            يمكنك إضافة إجابات نموذجية للأسئلة الشائعة ليتم الرد بها تلقائياً للطلاب.
          </p>
          <button onClick={() => setShowAdd(true)} className="btn-pro btn-pro-primary">
            <Plus className="w-4 h-4" />
            <span>إضافة أول تصحيح معتمد</span>
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {corrections.map((corr) => (
            <div key={corr.id as string} className="glass-card p-6 border border-slate-800/80">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400 flex-shrink-0">
                    <HelpCircle className="w-4 h-4" />
                  </div>
                  <h3 className="font-bold text-sm sm:text-base text-white leading-snug">
                    {corr.question as string}
                  </h3>
                </div>
                <button
                  className="btn-pro btn-pro-danger p-1.5 rounded-lg flex-shrink-0"
                  onClick={() => {
                    if (confirm('حذف هذا التصحيح؟')) deleteMutation.mutate(corr.id as string);
                  }}
                  title="حذف"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {corr.bad_answer ? (
                  <div className="p-3.5 rounded-xl bg-rose-500/5 border border-rose-500/20 text-xs">
                    <div className="font-bold text-rose-400 flex items-center gap-1.5 mb-1.5">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>الإجابة غير الدقيقة:</span>
                    </div>
                    <p className="text-slate-300 leading-relaxed">{corr.bad_answer as string}</p>
                  </div>
                ) : null}

                <div className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-xs md:col-span-1">
                  <div className="font-bold text-emerald-400 flex items-center gap-1.5 mb-1.5">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>الإجابة النموذجية المعتمدة:</span>
                  </div>
                  <p className="text-slate-200 leading-relaxed font-medium">{corr.correct_answer as string}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
