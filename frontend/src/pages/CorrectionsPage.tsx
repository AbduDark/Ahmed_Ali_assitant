import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { correctionsApi } from '@/services/api';
import { CheckCircle, Plus, Trash2 } from 'lucide-react';
import { useState, type FormEvent } from 'react';

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

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">تصحيحات المدرس</h1>
          <p className="page-subtitle">تصحيح إجابات المساعد وإضافة إجابات معتمدة</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
          <Plus size={18} /> إضافة تصحيح
        </button>
      </div>

      {showAdd && (
        <div className="card animate-fade-in" style={{ marginBottom: '1.5rem' }}>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label className="form-label">السؤال *</label>
              <textarea className="form-input form-textarea" style={{ minHeight: 80 }} value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="السؤال الذي أجاب عنه المساعد بشكل خاطئ" required />
            </div>
            <div className="form-group">
              <label className="form-label">الإجابة الخاطئة (اختياري)</label>
              <textarea className="form-input form-textarea" style={{ minHeight: 80 }} value={badAnswer} onChange={(e) => setBadAnswer(e.target.value)} placeholder="الإجابة الخاطئة التي قدمها المساعد" />
            </div>
            <div className="form-group">
              <label className="form-label">الإجابة الصحيحة *</label>
              <textarea className="form-input form-textarea" style={{ minHeight: 80 }} value={correctAnswer} onChange={(e) => setCorrectAnswer(e.target.value)} placeholder="الإجابة الصحيحة المعتمدة" required />
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button type="submit" className="btn btn-primary">حفظ</button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowAdd(false)}>إلغاء</button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-muted)' }}>جاري التحميل...</div>
      ) : !(data as unknown[])?.length ? (
        <div className="card">
          <div className="empty-state">
            <CheckCircle size={64} />
            <h3>لا توجد تصحيحات</h3>
            <p>أضف تصحيحات لتحسين دقة إجابات المساعد</p>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {(data as Record<string, unknown>[]).map((corr) => (
            <div key={corr.id as string} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, marginBottom: '0.75rem' }}>❓ {corr.question as string}</div>
                  {corr.bad_answer ? (
                    <div style={{ marginBottom: '0.5rem', padding: '0.5rem 0.75rem', background: 'rgba(239,68,68,0.08)', borderRadius: 'var(--radius-sm)', borderRight: '3px solid var(--color-danger)' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-danger)', fontWeight: 600, marginBottom: '0.25rem' }}>❌ الإجابة الخاطئة:</div>
                      <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>{corr.bad_answer as string}</div>
                    </div>
                  ) : null}
                  <div style={{ padding: '0.5rem 0.75rem', background: 'rgba(16,185,129,0.08)', borderRadius: 'var(--radius-sm)', borderRight: '3px solid var(--color-success)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-success)', fontWeight: 600, marginBottom: '0.25rem' }}>✅ الإجابة الصحيحة:</div>
                    <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>{corr.correct_answer as string}</div>
                  </div>
                </div>
                <button
                  className="btn btn-danger"
                  style={{ padding: '0.375rem', flexShrink: 0, marginRight: '1rem' }}
                  onClick={() => { if (confirm('حذف هذا التصحيح؟')) deleteMutation.mutate(corr.id as string); }}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
