import { useState, useRef, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { referencesApi } from '@/services/api';
import {
  BookOpen,
  Upload,
  Trash2,
  RefreshCw,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
  Plus,
  X,
  FileUp,
  Globe,
  ExternalLink,
} from 'lucide-react';

const statusConfig: Record<string, { label: string; chipClass: string; icon: React.ComponentType<{ className?: string }> }> = {
  ready: { label: 'مفهرس وجاهز', chipClass: 'chip-emerald', icon: CheckCircle },
  processing: { label: 'جاري المعالجة والفهرسة', chipClass: 'chip-indigo', icon: RefreshCw },
  pending: { label: 'قيد الانتظار', chipClass: 'chip-amber', icon: Clock },
  failed: { label: 'فشلت الفهرسة', chipClass: 'chip-rose', icon: AlertCircle },
};

export default function ReferencesPage() {
  const queryClient = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [uploadMode, setUploadMode] = useState<'file' | 'url'>('file');
  const [title, setTitle] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);

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
      setSourceUrl('');
      setSelectedFileName(null);
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFileName(file.name);
      if (!title) {
        setTitle(file.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleUpload = (e: FormEvent) => {
    e.preventDefault();
    if (!title) return;

    const formData = new FormData();
    formData.append('title', title);

    if (uploadMode === 'file') {
      const file = fileRef.current?.files?.[0];
      if (file) formData.append('file', file);
    } else {
      if (!sourceUrl) return;
      formData.append('source_url', sourceUrl);
    }

    uploadMutation.mutate(formData);
  };

  const references = data?.references || [];

  return (
    <div className="space-y-6 animate-page">
      {/* ── Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">بنك المراجع والكتب المعتمدة</h1>
          <p className="text-sm text-slate-400 mt-1">
            إضافة الكتب والمذكرات أو الروابط والمقالات التعليمية ليقوم الذكاء الاصطناعي بالاعتماد عليها
          </p>
        </div>
        <button
          className="btn-pro btn-pro-primary"
          onClick={() => setShowUpload(true)}
        >
          <Plus className="w-4 h-4" />
          <span>إضافة مرجع جديد</span>
        </button>
      </div>

      {/* ── Upload / Add URL Modal ──────────────────────────── */}
      {showUpload && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                  <Upload className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-white">إضافة مرجع دراسي جديد</h3>
              </div>
              <button
                onClick={() => setShowUpload(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Mode Tabs (File vs URL) */}
            <div className="flex rounded-xl bg-slate-900/80 p-1 border border-slate-800 mb-5">
              <button
                type="button"
                onClick={() => setUploadMode('file')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-bold transition-all ${
                  uploadMode === 'file'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>رفع ملف (PDF / Word)</span>
              </button>
              <button
                type="button"
                onClick={() => setUploadMode('url')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-bold transition-all ${
                  uploadMode === 'url'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Globe className="w-3.5 h-3.5" />
                <span>رابط موقع / مقال ويب (URL)</span>
              </button>
            </div>

            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  عنوان المرجع أو المقال *
                </label>
                <input
                  className="input-pro"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder={
                    uploadMode === 'file'
                      ? 'مثال: كتاب التاريخ للثانوية العامة - الفصل الأول'
                      : 'مثال: مقال تاريخي عن معركة حطين وسقوط بيت المقدس'
                  }
                  required
                />
              </div>

              {uploadMode === 'file' ? (
                /* Drag & Drop File Zone */
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                    الملف الدراسي (PDF, DOCX, TXT, PPTX)
                  </label>
                  <div
                    onClick={() => fileRef.current?.click()}
                    className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-2xl p-6 text-center cursor-pointer transition-colors bg-slate-900/40 hover:bg-indigo-500/5"
                  >
                    <input
                      type="file"
                      ref={fileRef}
                      onChange={handleFileChange}
                      accept=".pdf,.docx,.txt,.md,.pptx"
                      className="hidden"
                    />
                    <FileUp className="w-10 h-10 text-indigo-400 mx-auto mb-2" />
                    {selectedFileName ? (
                      <div className="font-bold text-sm text-emerald-400 flex items-center justify-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        <span>{selectedFileName}</span>
                      </div>
                    ) : (
                      <>
                        <p className="text-sm font-bold text-white mb-1">اضغط لاختيار الملف أو اسحبه هنا</p>
                        <p className="text-xs text-slate-400">PDF, Word, Text, PowerPoint بحد أقصى 100MB</p>
                      </>
                    )}
                  </div>
                </div>
              ) : (
                /* URL Input */
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                    رابط الصفحة أو المقال التعليمي (URL) *
                  </label>
                  <div className="relative">
                    <input
                      type="url"
                      className="input-pro text-left ltr pl-10"
                      value={sourceUrl}
                      onChange={(e) => setSourceUrl(e.target.value)}
                      placeholder="https://example.com/history/article"
                      required
                      dir="ltr"
                    />
                    <Globe className="w-4 h-4 text-cyan-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
                    💡 سيقوم الذكاء الاصطناعي بزيارة الرابط واستخراج محتواه وفهرسته تلقائياً في قاعدة المعرفة.
                  </p>
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  className="btn-pro btn-pro-glass"
                  onClick={() => setShowUpload(false)}
                >
                  إلغاء
                </button>
                <button
                  type="submit"
                  className="btn-pro btn-pro-primary"
                  disabled={uploadMutation.isPending}
                >
                  {uploadMutation.isPending
                    ? uploadMode === 'url' ? 'جاري جلب وفهرسة الرابط...' : 'جاري رفع وفهرسة الملف...'
                    : uploadMode === 'url' ? 'جلب وفهرسة الرابط' : 'رفع وفهرسة الآن'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── References Table ───────────────────────────────── */}
      <div className="glass-panel overflow-hidden">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-emerald-500 animate-spin" />
            <p className="text-xs text-slate-400 font-medium">جاري فحص المراجع والمصادر...</p>
          </div>
        ) : !references.length ? (
          <div className="text-center py-16 px-4">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mx-auto mb-4">
              <BookOpen className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-white mb-1">لا توجد مراجع أو روابط مضافة بعد</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mb-6">
              قم برفع الكتب والمذكرات أو إضافة روابط المقالات التعليمية ليعتمد عليها البوت في إجاباته.
            </p>
            <button
              onClick={() => setShowUpload(true)}
              className="btn-pro btn-pro-primary"
            >
              <Plus className="w-4 h-4" />
              <span>إضافة أول مرجع الآن</span>
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="pro-table">
              <thead>
                <tr>
                  <th>اسم المرجع / المقال</th>
                  <th>نوع المصدر</th>
                  <th>حالة الفهرسة</th>
                  <th>الأجزاء المفهرسة</th>
                  <th>تاريخ الإضافة</th>
                  <th className="text-left">الإجراءات</th>
                </tr>
              </thead>
              <tbody>
                {references.map((ref: Record<string, unknown>) => {
                  const statusKey = (ref.status as string) || 'ready';
                  const conf = statusConfig[statusKey] || statusConfig.ready;
                  const StatusIcon = conf.icon;
                  const isUrl = !!ref.source_url;

                  return (
                    <tr key={ref.id as string}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className={`w-9 h-9 rounded-xl border flex items-center justify-center flex-shrink-0 ${
                            isUrl
                              ? 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400'
                              : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                          }`}>
                            {isUrl ? <Globe className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                          </div>
                          <div className="min-w-0">
                            <div className="font-bold text-white text-sm truncate">{ref.title as string}</div>
                            {isUrl && ref.source_url ? (
                              <a
                                href={ref.source_url as string}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-[11px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1 mt-0.5 truncate max-w-xs"
                                dir="ltr"
                              >
                                <ExternalLink className="w-3 h-3 flex-shrink-0" />
                                <span className="truncate">{ref.source_url as string}</span>
                              </a>
                            ) : (
                              <div className="text-[11px] text-slate-400">ملف دراسي محلي</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={`chip uppercase text-[11px] ${isUrl ? 'chip-cyan' : 'chip-indigo'}`}>
                          {isUrl ? 'رابط ويب (URL)' : ((ref.file_type as string)?.toUpperCase() || 'PDF')}
                        </span>
                      </td>
                      <td>
                        <span className={`chip ${conf.chipClass}`}>
                          <StatusIcon className="w-3.5 h-3.5" />
                          <span>{conf.label}</span>
                        </span>
                      </td>
                      <td>
                        <span className="text-xs font-semibold text-slate-300">
                          {ref.chunk_count as number || 0} قطعة نصية
                        </span>
                      </td>
                      <td>
                        <span className="text-xs text-slate-400">
                          {new Date(ref.created_at as string).toLocaleDateString('ar-EG')}
                        </span>
                      </td>
                      <td className="text-left">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            className="btn-pro btn-pro-glass py-1.5 px-2.5 text-xs text-slate-300 hover:text-cyan-400"
                            onClick={() => reprocessMutation.mutate(ref.id as string)}
                            title="إعادة المعالجة والفهرسة"
                          >
                            <RefreshCw className="w-3.5 h-3.5" />
                          </button>
                          <button
                            className="btn-pro btn-pro-danger py-1.5 px-2.5 text-xs"
                            onClick={() => {
                              if (confirm('هل أنت متأكد من حذف هذا المرجع نهائياً؟')) {
                                deleteMutation.mutate(ref.id as string);
                              }
                            }}
                            title="حذف المرجع"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
