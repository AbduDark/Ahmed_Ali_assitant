import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/services/api';
import {
  Users,
  MessageSquare,
  BookOpen,
  Brain,
  AlertTriangle,
  Star,
  Clock,
  Zap,
} from 'lucide-react';

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: string;
  bgColor: string;
}

function StatCard({ icon, label, value, color, bgColor }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-icon" style={{ background: bgColor, color }}>
        {icon}
      </div>
      <div>
        <div className="stat-value" style={{ color }}>{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getStats(),
    select: (res) => res.data,
  });

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <div style={{
          width: 48,
          height: 48,
          border: '3px solid var(--color-border)',
          borderTopColor: 'var(--color-primary)',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  const stats = data || {
    total_students: 0,
    active_students: 0,
    total_conversations: 0,
    total_references: 0,
    ready_references: 0,
    total_ai_requests: 0,
    failed_ai_requests: 0,
    avg_response_time_ms: 0,
    total_tokens_used: 0,
    positive_feedback: 0,
    negative_feedback: 0,
  };

  const feedbackTotal = stats.positive_feedback + stats.negative_feedback;
  const feedbackScore = feedbackTotal > 0
    ? ((stats.positive_feedback / feedbackTotal) * 5).toFixed(1)
    : '—';

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">لوحة التحكم</h1>
          <p className="page-subtitle">نظرة عامة على المساعد التعليمي</p>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={<Users size={24} />}
          label="الطلاب"
          value={stats.total_students}
          color="#818cf8"
          bgColor="rgba(99, 102, 241, 0.15)"
        />
        <StatCard
          icon={<MessageSquare size={24} />}
          label="المحادثات"
          value={stats.total_conversations}
          color="#06b6d4"
          bgColor="rgba(6, 182, 212, 0.15)"
        />
        <StatCard
          icon={<BookOpen size={24} />}
          label="المراجع الجاهزة"
          value={`${stats.ready_references}/${stats.total_references}`}
          color="#10b981"
          bgColor="rgba(16, 185, 129, 0.15)"
        />
        <StatCard
          icon={<Brain size={24} />}
          label="طلبات الذكاء"
          value={stats.total_ai_requests.toLocaleString()}
          color="#f59e0b"
          bgColor="rgba(245, 158, 11, 0.15)"
        />
        <StatCard
          icon={<AlertTriangle size={24} />}
          label="الطلبات الفاشلة"
          value={stats.failed_ai_requests}
          color="#ef4444"
          bgColor="rgba(239, 68, 68, 0.15)"
        />
        <StatCard
          icon={<Star size={24} />}
          label="متوسط التقييم"
          value={feedbackScore}
          color="#eab308"
          bgColor="rgba(234, 179, 8, 0.15)"
        />
        <StatCard
          icon={<Clock size={24} />}
          label="متوسط وقت الاستجابة"
          value={`${Math.round(stats.avg_response_time_ms)}ms`}
          color="#8b5cf6"
          bgColor="rgba(139, 92, 246, 0.15)"
        />
        <StatCard
          icon={<Zap size={24} />}
          label="إجمالي التوكنز"
          value={stats.total_tokens_used.toLocaleString()}
          color="#ec4899"
          bgColor="rgba(236, 72, 153, 0.15)"
        />
      </div>
    </div>
  );
}
