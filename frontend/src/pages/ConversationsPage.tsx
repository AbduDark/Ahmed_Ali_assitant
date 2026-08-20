import { useQuery } from '@tanstack/react-query';
import { conversationsApi } from '@/services/api';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, ChevronLeft } from 'lucide-react';

export default function ConversationsPage() {
  const navigate = useNavigate();

  const { data, isLoading } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => conversationsApi.list({ limit: 50 }),
    select: (res) => res.data,
  });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">المحادثات</h1>
          <p className="page-subtitle">عرض ومتابعة محادثات الطلاب مع المساعد</p>
        </div>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-muted)' }}>جاري التحميل...</div>
      ) : !data?.conversations?.length ? (
        <div className="card">
          <div className="empty-state">
            <MessageSquare size={64} />
            <h3>لا توجد محادثات</h3>
            <p>ستظهر المحادثات هنا عندما يبدأ الطلاب بإرسال أسئلة</p>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {data.conversations.map((conv: Record<string, unknown>) => (
            <div
              key={conv.id as string}
              className="card"
              onClick={() => navigate(`/conversations/${conv.id}`)}
              style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: '50%',
                    background: 'rgba(6, 182, 212, 0.15)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--color-accent)',
                    flexShrink: 0,
                  }}
                >
                  <MessageSquare size={20} />
                </div>
                <div>
                  <div style={{ fontWeight: 600 }}>{conv.title as string || 'محادثة بدون عنوان'}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: 2 }}>
                    {conv.message_count as number} رسالة • {new Date(conv.created_at as string).toLocaleDateString('ar-EG')}
                  </div>
                </div>
              </div>
              <ChevronLeft size={20} style={{ color: 'var(--color-text-muted)' }} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
