"""Telegram message formatting utilities."""

from __future__ import annotations


def truncate_message(text: str, max_length: int = 4096) -> str:
    """
    Telegram messages have a 4096 character limit.
    Truncate intelligently at sentence boundaries.
    """
    if len(text) <= max_length:
        return text

    # Try to cut at a sentence boundary
    truncated = text[: max_length - 50]
    last_period = max(
        truncated.rfind("."),
        truncated.rfind("。"),
        truncated.rfind("،"),
        truncated.rfind("\n"),
    )

    if last_period > max_length // 2:
        truncated = truncated[:last_period + 1]

    return truncated + "\n\n... (تم اختصار الإجابة)"


def format_error_message(error_type: str = "general") -> str:
    """Return a user-friendly Arabic error message."""
    messages = {
        "general": "عذراً، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى. 🔄",
        "rate_limit": "تم الوصول إلى الحد المؤقت للطلبات. حاول مرة أخرى بعد قليل. ⏳",
        "ai_unavailable": "عذراً، خدمة الذكاء الاصطناعي غير متاحة حالياً. يرجى المحاولة لاحقاً. 🔧",
        "file_too_large": "حجم الملف كبير جداً. الحد الأقصى المسموح هو 100 ميجابايت. 📁",
        "unsupported_file": "نوع الملف غير مدعوم. الأنواع المدعومة: PDF, DOCX, TXT, PPTX 📄",
    }
    return messages.get(error_type, messages["general"])


def format_welcome_message(first_name: str) -> str:
    """Format the welcome message for /start."""
    return (
        f"مرحباً {first_name}! 👋\n\n"
        "أنا مساعدك التعليمي في مادتي التاريخ والجغرافيا. 📚\n\n"
        "يمكنك سؤالي عن أي موضوع في المنهج وسأساعدك في فهمه.\n\n"
        "📝 **كيفية الاستخدام:**\n"
        "• اكتب سؤالك مباشرة وسأجيبك\n"
        "• /subjects - لعرض المواد المتاحة\n"
        "• /help - للمساعدة\n\n"
        "ابدأ بطرح سؤالك! 🎓"
    )


def format_help_message() -> str:
    """Format the help message."""
    return (
        "📖 **المساعدة**\n\n"
        "أنا مساعد تعليمي ذكي مصمم لمساعدتك في فهم مواد التاريخ والجغرافيا.\n\n"
        "**الأوامر المتاحة:**\n"
        "/start - بدء محادثة جديدة\n"
        "/help - عرض هذه الرسالة\n"
        "/subjects - عرض المواد المتاحة\n"
        "/cancel - إلغاء العملية الحالية\n\n"
        "**نصائح:**\n"
        "• اكتب سؤالك بوضوح للحصول على أفضل إجابة\n"
        "• حدد المادة أو الدرس إذا أمكن\n"
        "• يمكنك إرسال متابعة لسؤالك السابق\n"
        "• استخدم 👍 أو 👎 لتقييم الإجابة\n\n"
        "📌 جميع إجاباتي مبنية على مراجع المدرس المعتمدة."
    )


def format_feedback_prompt() -> str:
    """Ask for feedback after an answer."""
    return "\n\nهل كانت الإجابة مفيدة؟ 👍 أو 👎"
