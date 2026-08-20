import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/services/api';
import { BarChart3, Cpu, Zap, AlertTriangle, Clock, TrendingUp } from 'lucide-react';

export default function AnalyticsPage() {
  const { data: usage, isLoading } = useQuery({
    queryKey: ['ai-usage'],
    queryFn: () => analyticsApi.getAiUsage(30),
    select: (res) => res.data,
  });

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-muted)' }}>جاري التحميل...</div>;
  }

  const stats = usage || {
    total_requests: 0,
    total_input_tokens: 0,
    total_output_tokens: 0,
    total_tokens: 0,
    avg_latency_ms: 0,
    error_rate: 0,
    requests_by_provider: {},
    requests_by_model: {},
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">التحليلات واستهلاك الذكاء</h1>
          <p className="page-subtitle">إحصائيات الاستخدام خلال آخر 30 يوم</p>
        </div>
      </div>

      {/* AI Usage Stats */}
      <div className="stats-grid" style={{ marginBottom: '2rem' }}>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
            <Cpu size={24} />
          </div>
          <div>
            <div className="stat-value" style={{ color: '#818cf8' }}>{stats.total_requests.toLocaleString()}</div>
            <div className="stat-label">إجمالي الطلبات</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
            <Zap size={24} />
          </div>
          <div>
            <div className="stat-value" style={{ color: '#10b981' }}>{stats.total_tokens.toLocaleString()}</div>
            <div className="stat-label">إجمالي التوكنز</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' }}>
            <Clock size={24} />
          </div>
          <div>
            <div className="stat-value" style={{ color: '#f59e0b' }}>{Math.round(stats.avg_latency_ms)}ms</div>
            <div className="stat-label">متوسط الاستجابة</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <div className="stat-value" style={{ color: '#ef4444' }}>{stats.error_rate.toFixed(1)}%</div>
            <div className="stat-label">نسبة الأخطاء</div>
          </div>
        </div>
      </div>

      {/* Token Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        <div className="card">
          <h3 style={{ fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingUp size={18} style={{ color: 'var(--color-primary-light)' }} />
            توزيع التوكنز
          </h3>
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>توكنز الإدخال</span>
                <span style={{ fontWeight: 600 }}>{stats.total_input_tokens.toLocaleString()}</span>
              </div>
              <div style={{ height: 8, background: 'var(--color-bg)', borderRadius: 4, overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: stats.total_tokens ? `${(stats.total_input_tokens / stats.total_tokens) * 100}%` : '0%',
                    background: 'linear-gradient(90deg, #6366f1, #818cf8)',
                    borderRadius: 4,
                    transition: 'width 0.5s ease',
                  }}
                />
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>توكنز الإخراج</span>
                <span style={{ fontWeight: 600 }}>{stats.total_output_tokens.toLocaleString()}</span>
              </div>
              <div style={{ height: 8, background: 'var(--color-bg)', borderRadius: 4, overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: stats.total_tokens ? `${(stats.total_output_tokens / stats.total_tokens) * 100}%` : '0%',
                    background: 'linear-gradient(90deg, #06b6d4, #22d3ee)',
                    borderRadius: 4,
                    transition: 'width 0.5s ease',
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Provider Distribution */}
        <div className="card">
          <h3 style={{ fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BarChart3 size={18} style={{ color: 'var(--color-primary-light)' }} />
            توزيع المزودين
          </h3>
          {Object.keys(stats.requests_by_provider || {}).length === 0 ? (
            <div style={{ color: 'var(--color-text-muted)', textAlign: 'center', padding: '2rem' }}>لا توجد بيانات</div>
          ) : (
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              {Object.entries(stats.requests_by_provider).map(([provider, count]) => (
                <div key={provider} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--color-text-secondary)' }}>{provider}</span>
                  <span className="badge badge-primary">{(count as number).toLocaleString()} طلب</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
