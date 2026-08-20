import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { subjectsApi } from '@/services/api';
import { Layers, Plus, ChevronDown, ChevronLeft } from 'lucide-react';
import { useState, type FormEvent } from 'react';

export default function SubjectsPage() {
  const queryClient = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [nameAr, setNameAr] = useState('');
  const [nameEn, setNameEn] = useState('');
  const [expandedSubject, setExpandedSubject] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => subjectsApi.list(),
    select: (res) => res.data,
  });

  const createMutation = useMutation({
    mutationFn: (data: { name_ar: string; name_en?: string }) => subjectsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] });
      setShowAdd(false);
      setNameAr('');
      setNameEn('');
    },
  });

  const handleCreate = (e: FormEvent) => {
    e.preventDefault();
    if (!nameAr) return;
    createMutation.mutate({ name_ar: nameAr, name_en: nameEn || undefined });
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">المواد الدراسية</h1>
          <p className="page-subtitle">إدارة المواد والوحدات والدروس</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
          <Plus size={18} /> إضافة مادة
        </button>
      </div>

      {/* Add Form */}
      {showAdd && (
        <div className="card animate-fade-in" style={{ marginBottom: '1.5rem' }}>
          <form onSubmit={handleCreate}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">اسم المادة بالعربية *</label>
                <input className="form-input" value={nameAr} onChange={(e) => setNameAr(e.target.value)} placeholder="التاريخ" required />
              </div>
              <div className="form-group">
                <label className="form-label">اسم المادة بالإنجليزية</label>
                <input className="form-input" value={nameEn} onChange={(e) => setNameEn(e.target.value)} placeholder="History" dir="ltr" />
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button type="submit" className="btn btn-primary">حفظ</button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowAdd(false)}>إلغاء</button>
            </div>
          </form>
        </div>
      )}

      {/* Subjects List */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-muted)' }}>جاري التحميل...</div>
      ) : !data?.length ? (
        <div className="card">
          <div className="empty-state">
            <Layers size={64} />
            <h3>لا توجد مواد</h3>
            <p>أضف مادة دراسية للبدء</p>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {(data as Record<string, unknown>[]).map((subject) => (
            <div key={subject.id as string} className="card">
              <div
                onClick={() => setExpandedSubject(expandedSubject === (subject.id as string) ? null : (subject.id as string))}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>{subject.name_ar as string}</div>
                  {subject.name_en && <div style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>{subject.name_en as string}</div>}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span className="badge badge-primary">{((subject.units as unknown[]) || []).length} وحدة</span>
                  {expandedSubject === subject.id ? <ChevronDown size={20} /> : <ChevronLeft size={20} />}
                </div>
              </div>

              {/* Expanded Units */}
              {expandedSubject === (subject.id as string) && (
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
                  {((subject.units as Record<string, unknown>[]) || []).map((unit) => (
                    <div key={unit.id as string} style={{ marginBottom: '1rem' }}>
                      <div style={{ fontWeight: 600, color: 'var(--color-primary-light)', marginBottom: '0.5rem' }}>
                        📘 {unit.name_ar as string}
                      </div>
                      <div style={{ paddingRight: '1.5rem' }}>
                        {((unit.lessons as Record<string, unknown>[]) || []).map((lesson) => (
                          <div
                            key={lesson.id as string}
                            style={{ padding: '0.375rem 0', color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}
                          >
                            📄 {lesson.name_ar as string}
                          </div>
                        ))}
                        {!((unit.lessons as unknown[]) || []).length && (
                          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>لا توجد دروس</div>
                        )}
                      </div>
                    </div>
                  ))}
                  {!((subject.units as unknown[]) || []).length && (
                    <div style={{ color: 'var(--color-text-muted)' }}>لا توجد وحدات</div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
