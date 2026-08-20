import { useState, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { subjectsApi } from '@/services/api';
import { Layers, Plus, ChevronDown, ChevronLeft, BookMarked, Folder, FileText, X } from 'lucide-react';

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

  const subjects = (data as Record<string, unknown>[]) || [];

  return (
    <div className="space-y-6 animate-page">
      {/* ── Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">المواد والمنهج الدراسي</h1>
          <p className="text-sm text-slate-400 mt-1">تنظيم المواد والوحدات والدروس لربطها بالمراجع والإجابات</p>
        </div>
        <button className="btn-pro btn-pro-primary" onClick={() => setShowAdd(true)}>
          <Plus className="w-4 h-4" />
          <span>إضافة مادة دراسية</span>
        </button>
      </div>

      {/* ── Add Subject Modal ──────────────────────────────── */}
      {showAdd && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                  <BookMarked className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-white">إضافة مادة دراسية جديدة</h3>
              </div>
              <button
                onClick={() => setShowAdd(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  اسم المادة بالعربية *
                </label>
                <input
                  className="input-pro"
                  value={nameAr}
                  onChange={(e) => setNameAr(e.target.value)}
                  placeholder="مثال: التاريخ للثانوية العامة"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  اسم المادة بالإنجليزية (اختياري)
                </label>
                <input
                  className="input-pro text-left ltr"
                  value={nameEn}
                  onChange={(e) => setNameEn(e.target.value)}
                  placeholder="History"
                  dir="ltr"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  className="btn-pro btn-pro-glass"
                  onClick={() => setShowAdd(false)}
                >
                  إلغاء
                </button>
                <button
                  type="submit"
                  className="btn-pro btn-pro-primary"
                  disabled={createMutation.isPending}
                >
                  {createMutation.isPending ? 'جاري الحفظ...' : 'حفظ المادة'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Subjects Hierarchy View ────────────────────────── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-indigo-500 animate-spin" />
          <p className="text-xs text-slate-400 font-medium">جاري تحميل المواد الدراسية...</p>
        </div>
      ) : !subjects.length ? (
        <div className="glass-panel text-center py-16 px-4">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto mb-4">
            <Layers className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-white mb-1">لا توجد مواد مضافة بعد</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-6">
            أضف المواد (مثل التاريخ، الجغرافيا) لتنظيم المنهج الدراسي وربطه بالمراجع.
          </p>
          <button onClick={() => setShowAdd(true)} className="btn-pro btn-pro-primary">
            <Plus className="w-4 h-4" />
            <span>إضافة أول مادة الآن</span>
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {subjects.map((subject) => {
            const subjectId = subject.id as string;
            const isExpanded = expandedSubject === subjectId;
            const units = (subject.units as Record<string, unknown>[]) || [];

            return (
              <div key={subjectId} className="glass-panel overflow-hidden border border-slate-800/80">
                <div
                  onClick={() => setExpandedSubject(isExpanded ? null : subjectId)}
                  className="p-5 flex items-center justify-between cursor-pointer hover:bg-slate-800/40 transition-colors select-none"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                      <BookMarked className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-base font-bold text-white">{subject.name_ar as string}</div>
                      {subject.name_en ? (
                        <div className="text-xs text-slate-400">{subject.name_en as string}</div>
                      ) : null}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="chip chip-indigo">
                      <Folder className="w-3 h-3" />
                      <span>{units.length} وحدة</span>
                    </span>
                    <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400">
                      {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
                    </div>
                  </div>
                </div>

                {/* Expanded Units & Lessons */}
                {isExpanded && (
                  <div className="p-5 pt-0 border-t border-slate-800/60 bg-slate-900/30 space-y-4">
                    {units.length > 0 ? (
                      units.map((unit) => {
                        const lessons = (unit.lessons as Record<string, unknown>[]) || [];
                        return (
                          <div key={unit.id as string} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                            <div className="font-bold text-indigo-300 text-sm flex items-center gap-2 mb-2">
                              <Folder className="w-4 h-4 text-indigo-400" />
                              <span>{unit.name_ar as string}</span>
                            </div>
                            <div className="pr-6 space-y-1.5 border-r border-slate-800 mr-2">
                              {lessons.map((lesson) => (
                                <div key={lesson.id as string} className="text-xs text-slate-300 flex items-center gap-2 py-1">
                                  <FileText className="w-3.5 h-3.5 text-cyan-400" />
                                  <span>{lesson.name_ar as string}</span>
                                </div>
                              ))}
                              {!lessons.length && (
                                <div className="text-xs text-slate-500 italic py-1">لا توجد دروس مضافة في هذه الوحدة</div>
                              )}
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <div className="text-xs text-slate-400 text-center py-4">
                        لا توجد وحدات مضافة تحت هذه المادة حالياً.
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
