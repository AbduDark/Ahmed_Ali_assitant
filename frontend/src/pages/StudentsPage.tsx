import { useQuery } from '@tanstack/react-query';
import { studentsApi } from '@/services/api';
import { Users, Search } from 'lucide-react';
import { useState } from 'react';

export default function StudentsPage() {
  const [search, setSearch] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['students', search],
    queryFn: () => studentsApi.list({ search: search || undefined, limit: 50 }),
    select: (res) => res.data,
  });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">الطلاب</h1>
          <p className="page-subtitle">إدارة ومتابعة الطلاب</p>
        </div>
      </div>

      {/* Search */}
      <div style={{ marginBottom: '1.5rem', position: 'relative', maxWidth: 400 }}>
        <Search size={18} style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
        <input
          className="form-input"
          placeholder="بحث عن طالب..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ paddingRight: '2.5rem' }}
        />
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>جاري التحميل...</div>
        ) : !data?.students?.length ? (
          <div className="empty-state">
            <Users size={64} />
            <h3>لا يوجد طلاب</h3>
            <p>سيظهر الطلاب هنا بعد تفاعلهم مع البوت</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>الاسم</th>
                <th>اسم المستخدم</th>
                <th>الصف</th>
                <th>اللغة</th>
                <th>آخر ظهور</th>
                <th>الحالة</th>
              </tr>
            </thead>
            <tbody>
              {data.students.map((student: Record<string, unknown>) => (
                <tr key={student.id as string}>
                  <td style={{ fontWeight: 600 }}>{student.first_name as string} {student.last_name as string || ''}</td>
                  <td style={{ color: 'var(--color-text-secondary)' }}>@{student.username as string || '—'}</td>
                  <td>{student.grade as string || '—'}</td>
                  <td>{student.preferred_language as string === 'ar' ? '🇸🇦 عربي' : '🇺🇸 English'}</td>
                  <td style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                    {student.last_seen_at ? new Date(student.last_seen_at as string).toLocaleDateString('ar-EG') : '—'}
                  </td>
                  <td>
                    <span className={`badge ${student.is_active ? 'badge-success' : 'badge-danger'}`}>
                      {student.is_active ? 'نشط' : 'غير نشط'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
