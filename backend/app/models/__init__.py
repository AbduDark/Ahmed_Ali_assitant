"""Models package — import all models so SQLAlchemy registers them."""

from app.models.user import User, UserRole  # noqa: F401
from app.models.student import Student  # noqa: F401
from app.models.subject import Subject, Grade, Curriculum, Unit, Lesson  # noqa: F401
from app.models.reference import Reference, ReferenceStatus  # noqa: F401
from app.models.chunk import ReferenceChunk  # noqa: F401
from app.models.conversation import Conversation, Message, MessageRole  # noqa: F401
from app.models.instruction import TeacherInstruction  # noqa: F401
from app.models.correction import TeacherCorrection  # noqa: F401
from app.models.ai_usage import AIUsageLog  # noqa: F401
from app.models.feedback import Feedback  # noqa: F401

__all__ = [
    "User", "UserRole",
    "Student",
    "Subject", "Grade", "Curriculum", "Unit", "Lesson",
    "Reference", "ReferenceStatus",
    "ReferenceChunk",
    "Conversation", "Message", "MessageRole",
    "TeacherInstruction",
    "TeacherCorrection",
    "AIUsageLog",
    "Feedback",
]
