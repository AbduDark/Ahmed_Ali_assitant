"""Schemas package."""

from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, UserResponse  # noqa: F401
from app.schemas.student import StudentResponse, StudentListResponse, StudentUpdateRequest  # noqa: F401
from app.schemas.subject import (  # noqa: F401
    SubjectCreate, SubjectUpdate, SubjectResponse,
    UnitCreate, UnitUpdate, UnitResponse,
    LessonCreate, LessonUpdate, LessonResponse,
)
from app.schemas.reference import (  # noqa: F401
    ReferenceCreate, ReferenceUpdate, ReferenceResponse, ReferenceListResponse,
)
from app.schemas.conversation import (  # noqa: F401
    ConversationResponse, ConversationDetailResponse,
    ConversationListResponse, MessageResponse,
)
from app.schemas.instruction import InstructionCreate, InstructionUpdate, InstructionResponse  # noqa: F401
from app.schemas.correction import CorrectionCreate, CorrectionUpdate, CorrectionResponse  # noqa: F401
from app.schemas.analytics import DashboardStats, AIUsageStats  # noqa: F401
