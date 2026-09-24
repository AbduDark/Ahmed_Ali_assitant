import {
  BookOpen,
  FileText,
  ScrollText,
  Landmark,
  Sword,
  Globe2,
  Flag,
  BookMarked,
  FileDown,
} from 'lucide-react';

/**
 * Fixed references — hardcoded, matching the backend prompt_builder.py
 * No database, no API calls, no control panel needed.
 */

interface FixedReference {
  author: string;
  title: string;
  topic: string;
  category: string;
}

const FIXED_REFERENCES: FixedReference[] = [
  // ─── مراجع عامة ───
  { author: "جمال حمدان", title: "شخصية مصر - دراسة فى عبقرية المكان", topic: "الموقع والجغرافيا التاريخية", category: "عامة" },
  { author: "أدولف إرمان", title: "ديانة مصر القديمة", topic: "الحضارة المصرية القديمة", category: "عامة" },
  { author: "سقراط", title: "الفلسفة اليونانية", topic: "الفكر الفلسفي القديم", category: "عامة" },
  { author: "توماس هوبز", title: "الفلسفة السياسية", topic: "الفلسفة السياسية", category: "عامة" },

  // ─── الحركة الوطنية ───
  { author: "عبد الرحمن الرافعى", title: "تاريخ الحركة الوطنية", topic: "الحركة الوطنية المصرية", category: "الحركة الوطنية" },

  // ─── ابن خلدون ───
  { author: "ابن خلدون", title: "المقدمة", topic: "علم الاجتماع والتاريخ", category: "عامة" },

  // ─── القوة العسكرية ───
  { author: "عمر طوسون", title: "بناء القوة العسكرية المصرية", topic: "التاريخ العسكري المصري", category: "عامة" },

  // ─── التجانس ───
  { author: "أندريه مارو", title: "التجانس", topic: "التجانس الاجتماعي", category: "عامة" },

  // ─── الوعاء الوطني ───
  { author: "مصطفى صادق الرافعي", title: "الوعاء الوطنى", topic: "الهوية الوطنية", category: "عامة" },

  // ─── مصر القديمة ───
  { author: "موسوعة مصر", title: "صلاية نعرمر", topic: "توحيد مصر القديمة", category: "مصر القديمة" },
  { author: "سليم حسن", title: "موسوعة مصر القديمة", topic: "تاريخ مصر القديمة الشامل", category: "مصر القديمة" },
  { author: "جمال حمدان", title: "الموقع", topic: "الموقع الجغرافي والتاريخي لمصر", category: "مصر القديمة" },
  { author: "بردية ساليه", title: "تاريخ مصر القديم", topic: "الوثائق المصرية القديمة", category: "مصر القديمة" },
  { author: "نجيب محفوظ", title: "كفاح أهل طيبة (رواية)", topic: "تحرير مصر من الهكسوس", category: "مصر القديمة" },
  { author: "مانيتون", title: "تاريخ مصر القديم", topic: "تقسيم الأسرات المصرية", category: "مصر القديمة" },
  { author: "—", title: "لوحة كامس", topic: "حرب التحرير ضد الهكسوس", category: "مصر القديمة" },

  // ─── العصر اليوناني والروماني ───
  { author: "استرابو", title: "جغرافية مصر (اليونان)", topic: "مصر في العصر اليوناني", category: "اليوناني والروماني" },
  { author: "مصطفى العبادى", title: "تاريخ الإغريق", topic: "تاريخ الإغريق", category: "اليوناني والروماني" },
  { author: "—", title: "مصر فى العصر الروماني", topic: "مصر تحت الحكم الروماني", category: "اليوناني والروماني" },

  // ─── الفتح الإسلامي والإسكندر ───
  { author: "—", title: "الفتح الإسلامي لمصر", topic: "الفتح الإسلامي", category: "الفتح الإسلامي" },
  { author: "—", title: "الإسكندر فى مصر", topic: "الإسكندر الأكبر في مصر", category: "اليوناني والروماني" },

  // ─── التاريخ الحديث والمعاصر ───
  { author: "عبد الرحمن الرافعى", title: "مجموعة عبد الرحمن الرافعى الكاملة", topic: "تاريخ مصر الحديث", category: "التاريخ الحديث" },
  { author: "عبد الرحمن الرافعى", title: "مقدمات ثورة 1919", topic: "ثورة 1919", category: "التاريخ الحديث" },
  { author: "رفعت السعيد", title: "حكايات ثورة 19", topic: "ثورة 1919", category: "التاريخ الحديث" },
  { author: "—", title: "كتاب عبد الناصر لثورة 1952", topic: "ثورة يوليو 1952", category: "التاريخ الحديث" },
  { author: "أنور السادات", title: "البحث عن الذات", topic: "السيرة الذاتية للسادات", category: "التاريخ الحديث" },
  { author: "إدريس أفندي", title: "إدريس أفندى فى مصر - الفرنسيين", topic: "الحملة الفرنسية على مصر", category: "التاريخ الحديث" },
  { author: "الجبرتى", title: "عجائب الآثار فى التراجم والأخبار", topic: "تاريخ مصر في العصر العثماني والحملة الفرنسية", category: "التاريخ الحديث" },
  { author: "شحاتة عيسى", title: "التاريخ الأسود للاحتلال البريطاني", topic: "الاحتلال البريطاني لمصر", category: "التاريخ الحديث" },
  { author: "جمال حماد", title: "ثورة 1952", topic: "ثورة يوليو 1952", category: "التاريخ الحديث" },

  // ─── ملفات PDF ───
  { author: "—", title: "EgyptianHistory-Ar-EB-part1.pdf", topic: "التاريخ المصري - الجزء الأول", category: "ملفات PDF" },
  { author: "—", title: "EgyptianHistory-Ar-EB-part2.pdf", topic: "التاريخ المصري - الجزء الثاني", category: "ملفات PDF" },
];

const categoryConfig: Record<string, { icon: React.ComponentType<{ className?: string }>; color: string; borderColor: string; bgColor: string }> = {
  "عامة": { icon: BookOpen, color: "text-indigo-400", borderColor: "border-indigo-500/20", bgColor: "bg-indigo-500/10" },
  "مصر القديمة": { icon: Landmark, color: "text-amber-400", borderColor: "border-amber-500/20", bgColor: "bg-amber-500/10" },
  "الحركة الوطنية": { icon: Flag, color: "text-emerald-400", borderColor: "border-emerald-500/20", bgColor: "bg-emerald-500/10" },
  "اليوناني والروماني": { icon: Globe2, color: "text-cyan-400", borderColor: "border-cyan-500/20", bgColor: "bg-cyan-500/10" },
  "الفتح الإسلامي": { icon: ScrollText, color: "text-green-400", borderColor: "border-green-500/20", bgColor: "bg-green-500/10" },
  "التاريخ الحديث": { icon: Sword, color: "text-rose-400", borderColor: "border-rose-500/20", bgColor: "bg-rose-500/10" },
  "ملفات PDF": { icon: FileDown, color: "text-purple-400", borderColor: "border-purple-500/20", bgColor: "bg-purple-500/10" },
};

export default function ReferencesPage() {
  // Group references by category
  const grouped = FIXED_REFERENCES.reduce<Record<string, FixedReference[]>>((acc, ref) => {
    if (!acc[ref.category]) acc[ref.category] = [];
    acc[ref.category].push(ref);
    return acc;
  }, {});

  const categoryOrder = ["عامة", "مصر القديمة", "اليوناني والروماني", "الفتح الإسلامي", "الحركة الوطنية", "التاريخ الحديث", "ملفات PDF"];

  return (
    <div className="space-y-6 animate-page">
      {/* ── Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">المراجع والمصادر المعتمدة</h1>
          <p className="text-sm text-slate-400 mt-1">
            قائمة ثابتة بالمراجع المعتمدة التي يعتمد عليها البوت في إجاباته — مادة التاريخ فقط
          </p>
        </div>
        <div className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-bold text-emerald-400">
            {FIXED_REFERENCES.length} مرجع معتمد ومفعّل
          </span>
        </div>
      </div>

      {/* ── Summary Stats ──────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {categoryOrder.map((cat) => {
          const conf = categoryConfig[cat];
          const count = grouped[cat]?.length || 0;
          const CatIcon = conf.icon;
          return (
            <div
              key={cat}
              className={`glass-card p-3.5 flex flex-col items-center gap-2 border ${conf.borderColor} hover:scale-[1.02] transition-transform cursor-default`}
            >
              <div className={`w-9 h-9 rounded-xl ${conf.bgColor} ${conf.color} flex items-center justify-center`}>
                <CatIcon className="w-4.5 h-4.5" />
              </div>
              <div className="text-center">
                <div className="text-lg font-extrabold text-white">{count}</div>
                <div className="text-[10px] font-semibold text-slate-400 leading-tight">{cat}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── References by Category ─────────────────────────── */}
      {categoryOrder.map((cat) => {
        const refs = grouped[cat];
        if (!refs || refs.length === 0) return null;

        const conf = categoryConfig[cat];
        const CatIcon = conf.icon;

        return (
          <div key={cat} className="glass-panel overflow-hidden">
            {/* Category Header */}
            <div className={`px-5 py-4 border-b border-slate-800/60 flex items-center gap-3`}>
              <div className={`w-9 h-9 rounded-xl ${conf.bgColor} border ${conf.borderColor} ${conf.color} flex items-center justify-center`}>
                <CatIcon className="w-4.5 h-4.5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">{cat}</h2>
                <p className="text-[11px] text-slate-400">{refs.length} مرجع</p>
              </div>
            </div>

            {/* References Grid */}
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
              {refs.map((ref, idx) => (
                <div
                  key={`${cat}-${idx}`}
                  className={`group relative p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 hover:bg-slate-800/40 transition-all duration-200`}
                >
                  {/* Reference Icon */}
                  <div className="flex items-start gap-3">
                    <div className={`w-8 h-8 rounded-lg ${conf.bgColor} ${conf.color} flex items-center justify-center flex-shrink-0 mt-0.5`}>
                      {cat === "ملفات PDF" ? (
                        <FileDown className="w-4 h-4" />
                      ) : (
                        <FileText className="w-4 h-4" />
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-bold text-sm text-white leading-snug mb-1 group-hover:text-indigo-300 transition-colors">
                        {ref.title}
                      </h3>
                      {ref.author && ref.author !== "—" && (
                        <div className="flex items-center gap-1.5 mb-1.5">
                          <BookMarked className="w-3 h-3 text-slate-500 flex-shrink-0" />
                          <span className="text-xs font-medium text-slate-400">{ref.author}</span>
                        </div>
                      )}
                      <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold ${conf.bgColor} ${conf.color}`}>
                        {ref.topic}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {/* ── Footer Note ────────────────────────────────────── */}
      <div className="glass-card p-4 border border-indigo-500/10 bg-indigo-500/5">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/15 text-indigo-400 flex items-center justify-center flex-shrink-0 mt-0.5">
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-indigo-300 mb-1">ملاحظة هامة</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              هذه المراجع مدمجة مباشرة في نظام الذكاء الاصطناعي. البوت يستخدم هذه المراجع كأساس
              لإجاباته ويذكرها عند الاستشهاد. لتعديل المراجع يرجى التواصل مع المطور.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
