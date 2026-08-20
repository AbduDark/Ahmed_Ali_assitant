import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/services/api';
import { GraduationCap, Eye, EyeOff, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await authApi.login(email, password);
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      navigate('/', { replace: true });
    } catch {
      setError('بيانات الدخول غير صحيحة');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Background decoration */}
      <div
        style={{
          position: 'absolute',
          top: '20%',
          right: '10%',
          width: 300,
          height: 300,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)',
          filter: 'blur(40px)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '20%',
          left: '15%',
          width: 250,
          height: 250,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(6,182,212,0.12) 0%, transparent 70%)',
          filter: 'blur(40px)',
        }}
      />

      <div className="login-card animate-fade-in">
        <div className="login-logo">
          <div
            className="gradient-primary"
            style={{
              width: 64,
              height: 64,
              borderRadius: 'var(--radius)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem',
            }}
          >
            <GraduationCap size={32} color="white" />
          </div>
          <h1>المساعد التعليمي الذكي</h1>
          <p>تسجيل دخول لوحة التحكم</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="email">البريد الإلكتروني</label>
            <input
              id="email"
              type="email"
              className="form-input"
              placeholder="admin@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              dir="ltr"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">كلمة المرور</label>
            <div style={{ position: 'relative' }}>
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                className="form-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                dir="ltr"
                style={{ paddingLeft: '3rem' }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  left: '0.75rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'var(--color-text-muted)',
                  cursor: 'pointer',
                }}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {error && (
            <div
              style={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.75rem 1rem',
                color: 'var(--color-danger)',
                fontSize: '0.875rem',
                marginBottom: '1rem',
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', padding: '0.875rem', fontSize: '1rem' }}
          >
            {loading ? (
              <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
            ) : (
              'تسجيل الدخول'
            )}
          </button>
        </form>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
