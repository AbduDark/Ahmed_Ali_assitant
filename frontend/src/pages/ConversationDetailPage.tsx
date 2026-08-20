import { useQuery } from '@tanstack/react-query';
import { conversationsApi } from '@/services/api';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowRight, Clock, Brain, BookOpen } from 'lucide-react';

export default function ConversationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data, isLoading } = useQuery({
    queryKey: ['conversation', id],
    queryFn: () => conversationsApi.get(id!),
    select: (res) => res.data,
    enabled: !!id,
  });

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-muted)' }}>جاري التحميل...</div>;
  }

  if (!data) {
    return <div style={{ textAlign: 'center', padding: '3rem' }}>المحادثة غير موجودة</div>;
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => navigate('/conversations')}
            className="btn btn-secondary"
            style={{ padding: '0.5rem' }}
          >
            <ArrowRight size={20} />
          </button>
          <div>
            <h1 className="page-title">{data.title || 'تفاصيل المحادثة'}</h1>
            <p className="page-subtitle">{data.message_count} رسالة</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div style={{ maxWidth: 800 }}>
        {data.messages?.map((msg: Record<string, unknown>) => (
          <div key={msg.id as string} className="animate-fade-in" style={{ marginBottom: '1.5rem' }}>
            <div
              className={`message-bubble ${msg.role === 'student' ? 'message-student' : 'message-assistant'}`}
            >
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.5rem', fontWeight: 600 }}>
                {msg.role === 'student' ? '👨‍🎓 الطالب' : '🤖 المساعد'}
              </div>
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content as string}</div>
            </div>

            {/* RAG Metadata — only for assistant messages */}
            {msg.role === 'assistant' && (
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '0.5rem', paddingRight: '1rem' }}>
                {msg.response_time_ms && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Clock size={12} /> {msg.response_time_ms as number}ms
                  </span>
                )}
                {msg.ai_provider && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Brain size={12} /> {msg.ai_provider as string}/{msg.ai_model as string}
                  </span>
                )}
                {msg.confidence_score != null && (
                  <span style={{ fontSize: '0.75rem', color: (msg.confidence_score as number) > 0.7 ? 'var(--color-success)' : 'var(--color-warning)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    ثقة: {((msg.confidence_score as number) * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            )}

            {/* Retrieved Chunks */}
            {msg.role === 'assistant' && (msg.retrieved_chunks as unknown[])?.length > 0 && (
              <details style={{ marginTop: '0.5rem', paddingRight: '1rem' }}>
                <summary style={{ fontSize: '0.8rem', color: 'var(--color-primary-light)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <BookOpen size={14} /> عرض المصادر المسترجعة ({(msg.retrieved_chunks as unknown[]).length})
                </summary>
                <div style={{ marginTop: '0.5rem', display: 'grid', gap: '0.5rem' }}>
                  {(msg.retrieved_chunks as Record<string, unknown>[]).map((chunk, i) => (
                    <div
                      key={i}
                      style={{
                        background: 'var(--color-bg)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '0.75rem',
                        fontSize: '0.8rem',
                      }}
                    >
                      <div style={{ color: 'var(--color-primary-light)', fontWeight: 600, marginBottom: '0.25rem' }}>
                        {chunk.reference_title as string} {chunk.page_number ? `(ص${chunk.page_number})` : ''}
                      </div>
                      <div style={{ color: 'var(--color-text-secondary)' }}>
                        {(chunk.content as string)?.substring(0, 200)}...
                      </div>
                      <div style={{ color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                        تطابق: {((chunk.score as number) * 100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
