import React, { useState, useRef, type FormEvent } from 'react';
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
  const [title, setTitle] = useState('');
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
        // Strip extension as default title
        setTitle(file.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleUpload = (e: FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!title) return;

    const formData = new FormData();
    formData.append('title', title);
    if (file) formData.append('file', file);
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
            رفع الكتب والمذكرات الدراسية ليقوم الذكاء الاصطناعي باستخراج الإجابات منها حصراً
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

      {/* ── Upload Modal ───────────────────────────────────── */}
      {showUpload && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                  <Upload className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-white">رفع مرجع دراسي جديد</h3>
              </div>
              <button
                onClick={() => setShowUpload(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpload} className="space-y-5">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  عنوان المرجع أو الكتاب *
                </label>
                <input
                  className="input-pro"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="مثال: كتاب التاريخ للثانوية العامة - الفصل الدراسي الأول"
                  required
                />
              </div>

              {/* Drag & Drop File Zone */}
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
                  <FileUp className="w-10 h-10 text-indigo-400 mx-auto mb-3" />
                  {selectedFileName ? (
                    <div className="font-bold text-sm text-emerald-400 flex items-center justify-center gap-2">
                      <CheckCircle className="w-4 h-4" />
                      <span>{selectedFileName}</span>
                    </div>
                  ) : (
                    <>
                      <p className="text-sm font-bold text-white mb-1">اضغط هنا لاختيار الملف أو اسحبه إلى هنا</p>
                      <p className="text-xs text-slate-400">يدعم ملفات PDF، Word، Text، PowerPoint بحد أقصى 100 ميجابايت</p>
                    </>
                  )}
                </div>
              </div>

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
                  {uploadMutation.isPending ? 'جاري رفع وفهرسة الملف...' : 'رفع وفهرسة الآن'}
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
            <p className="text-xs text-slate-400 font-medium">جاري فحص المراجع المفهرسة...</p>
          </div>
        ) : !references.length ? (
          <div className="text-center py-16 px-4">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mx-auto mb-4">
              <BookOpen className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-white mb-1">لا توجد مراجع مرفوعة بعد</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mb-6">
              قم برفع الكتب والمذكرات الدراسية حتى يعتمد عليها البوت في إجاباته للطلاب.
            </p>
            <button
              onClick={() => setShowUpload(true)}
              className="btn-pro btn-pro-primary"
            >
              <Plus className="w-4 h-4" />
              <span>رفع أول كتاب الآن</span>
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="pro-table">
              <thead>
                <tr>
                  <th>اسم المرجع / الكتاب</th>
                  <th>صيغة الملف</th>
                  <th>حالة الفهرسة</th>
                  <th>الأجزاء المفهرسة (Chunks)</th>
                  <th>تاريخ الرفع</th>
                  <th className="text-left">الإجراءات</th>
                </tr>
              </thead>
              <tbody>
                {references.map((ref: Record<string, unknown>) => {
                  const statusKey = (ref.status as string) || 'ready';
                  const conf = statusConfig[statusKey] || statusConfig.ready;
                  const StatusIcon = conf.icon;

                  return (
                    <tr key={ref.id as string}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 flex-shrink-0">
                            <FileText className="w-4 h-4" />
                          </div>
                          <div>
                            <div className="font-bold text-white text-sm">{ref.title as string}</div>
                            <div className="text-[11px] text-slate-400">ID: {ref.id as string}</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="chip chip-indigo uppercase text-[11px]">
                          {(ref.file_type as string)?.toUpperCase() || 'PDF'}
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
