import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { instructionsApi } from '@/services/api';
import { Brain, Plus, Trash2, Edit } from 'lucide-react';
import { useState, type FormEvent } from 'react';

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

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">تعليمات الذكاء الاصطناعي</h1>
          <p className="page-subtitle">تخصيص سلوك المساعد وطريقة الإجابة</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
          <Plus size={18} /> إضافة تعليمة
        </button>
      </div>

      {showAdd && (
        <div className="card animate-fade-in" style={{ marginBottom: '1.5rem' }}>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label className="form-label">عنوان (اختياري)</label>
              <input className="form-input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="مثال: طريقة الشرح" />
            </div>
            <div className="form-group">
              <label className="form-label">محتوى التعليمة *</label>
              <textarea
                className="form-input form-textarea"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="مثال: أريدك أن تشرح للطالب بطريقة بسيطة جدًا. استخدم أمثلة من المنهج..."
                required
              />
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
            <Brain size={64} />
            <h3>لا توجد تعليمات</h3>
            <p>أضف تعليمات لتخصيص طريقة إجابة المساعد</p>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {(data as Record<string, unknown>[]).map((inst) => (
            <div key={inst.id as string} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  {inst.title && <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>{inst.title as string}</div>}
                  <div style={{ color: 'var(--color-text-secondary)', lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>{inst.content as string}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.75rem' }}>
                    {inst.is_active ? <span className="badge badge-success">مفعّل</span> : <span className="badge badge-danger">معطّل</span>}
                  </div>
                </div>
                <button
                  className="btn btn-danger"
                  style={{ padding: '0.375rem', flexShrink: 0 }}
                  onClick={() => { if (confirm('حذف هذه التعليمة؟')) deleteMutation.mutate(inst.id as string); }}
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
