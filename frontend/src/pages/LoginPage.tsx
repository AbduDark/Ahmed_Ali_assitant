import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/services/api';
import { GraduationCap, Lock, Mail, ArrowLeft, ShieldAlert, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await authApi.login(email, password);
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      navigate('/');
    } catch {
      setError('البريد الإلكتروني أو كلمة المرور غير صحيحة');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 relative overflow-hidden bg-[#070A11]">
      {/* Dynamic Background Glows */}
      <div className="absolute top-1/4 -right-20 w-96 h-96 bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 -left-20 w-96 h-96 bg-cyan-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-30 pointer-events-none" />

      <div className="w-full max-w-md relative z-10 animate-page">
        {/* Brand Card */}
        <div className="glass-panel p-8 sm:p-10 border border-slate-700/60 shadow-2xl relative">
          {/* Brand Logo Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center mx-auto mb-4 shadow-xl shadow-indigo-500/30 border border-white/20">
              <GraduationCap className="w-9 h-9 text-white" />
            </div>
            <div className="flex items-center justify-center gap-2">
              <h1 className="text-2xl font-black text-white tracking-wide">الجنرال AI</h1>
              <Sparkles className="w-4 h-4 text-amber-400" />
            </div>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 font-medium">
              بوابة الإدارة المركزية للأستاذ أحمد علي
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-xs text-rose-300 animate-page">
              <ShieldAlert className="w-4 h-4 text-rose-400 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                البريد الإلكتروني
              </label>
              <div className="relative">
                <input
                  type="email"
                  className="input-pro pr-10 text-left ltr"
                  placeholder="admin@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  dir="ltr"
                />
                <Mail className="w-4 h-4 text-slate-400 absolute right-3.5 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                كلمة المرور
              </label>
              <div className="relative">
                <input
                  type="password"
                  className="input-pro pr-10 text-left ltr"
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  dir="ltr"
                />
                <Lock className="w-4 h-4 text-slate-400 absolute right-3.5 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-pro btn-pro-primary w-full py-3 text-sm justify-center shadow-lg shadow-indigo-600/30 mt-2"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  <span>جاري التحقق والدخول...</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <span>تسجيل الدخول للوحة التحكم</span>
                  <ArrowLeft className="w-4 h-4" />
                </div>
              )}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-800 text-center">
            <p className="text-[11px] text-slate-400">
              نظام إدارة المساعد التعليمي الذكي • إصدار آمن ومحمي 🔒
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
