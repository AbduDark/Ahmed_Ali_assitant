import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { referencesApi } from '@/services/api';
import { BookOpen, Upload, Trash2, RefreshCw } from 'lucide-react';
import { useState, useRef, type FormEvent } from 'react';

const statusLabels: Record<string, { label: string; class: string }> = {
  pending: { label: 'قيد الانتظار', class: 'badge-warning' },
  processing: { label: 'جاري المعالجة', class: 'badge-primary' },
  ready: { label: 'جاهز', class: 'badge-success' },
  failed: { label: 'فشل', class: 'badge-danger' },
};

export default function ReferencesPage() {
  const queryClient = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [title, setTitle] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['references'],
    queryFn: () => referencesApi.list({ limit: 50 }),
    select: (res) => res.data,
  });

  const uploadMutation = useMutation({
    mutationFn: (formData: FormData) => referencesApi.create(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['references'] });
      setShowUpload(false);
      setTitle('');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => referencesApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['references'] }),
  });

  const reprocessMutation = useMutation({
    mutationFn: (id: string) => referencesApi.reprocess(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['references'] }),
  });

  const handleUpload = (e: FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!title) return;

    const formData = new FormData();
    formData.append('title', title);
    if (file) formData.append('file', file);
    uploadMutation.mutate(formData);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">المراجع</h1>
          <p className="page-subtitle">إدارة المراجع والمستندات التعليمية</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowUpload(!showUpload)}>
          <Upload size={18} /> رفع مرجع
        </button>
      </div>

      {/* Upload Form */}
      {showUpload && (
        <div className="card animate-fade-in" style={{ marginBottom: '1.5rem' }}>
          <form onSubmit={handleUpload}>
            <div className="form-group">
              <label className="form-label">عنوان المرجع *</label>
              <input className="form-input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="مثال: كتاب التاريخ - الوحدة الأولى" required />
            </div>
            <div className="form-group">
              <label className="form-label">الملف (PDF, DOCX, TXT, PPTX)</label>
              <input type="file" ref={fileRef} accept=".pdf,.docx,.txt,.md,.pptx" className="form-input" />
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button type="submit" className="btn btn-primary" disabled={uploadMutation.isPending}>
                {uploadMutation.isPending ? 'جاري الرفع...' : 'رفع'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowUpload(false)}>إلغاء</button>
            </div>
          </form>
        </div>
      )}

      {/* References List */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>جاري التحميل...</div>
        ) : !data?.references?.length ? (
          <div className="empty-state">
            <BookOpen size={64} />
            <h3>لا توجد مراجع</h3>
            <p>ارفع مرجعاً تعليمياً للبدء</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>العنوان</th>
                <th>النوع</th>
                <th>الحالة</th>
                <th>الأجزاء</th>
                <th>التاريخ</th>
                <th>إجراءات</th>
              </tr>
            </thead>
            <tbody>
              {data.references.map((ref: Record<string, unknown>) => {
                const status = statusLabels[(ref.status as string) || 'pending'];
                return (
                  <tr key={ref.id as string}>
                    <td style={{ fontWeight: 600 }}>{ref.title as string}</td>
                    <td style={{ color: 'var(--color-text-secondary)' }}>{(ref.file_type as string)?.toUpperCase() || '—'}</td>
                    <td><span className={`badge ${status.class}`}>{status.label}</span></td>
                    <td>{ref.chunk_count as number || 0}</td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                      {new Date(ref.created_at as string).toLocaleDateString('ar-EG')}
                    </td>
                    <td style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '0.375rem' }}
                        onClick={() => reprocessMutation.mutate(ref.id as string)}
                        title="إعادة المعالجة"
                      >
                        <RefreshCw size={16} />
                      </button>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '0.375rem' }}
                        onClick={() => { if (confirm('هل تريد حذف هذا المرجع؟')) deleteMutation.mutate(ref.id as string); }}
                        title="حذف"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
