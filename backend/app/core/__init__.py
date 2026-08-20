"""Custom exception classes for structured error handling."""

from __future__ import annotations

from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


# ── Authentication ───────────────────────────────────────────

class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بيانات الدخول غير صحيحة",  # Invalid credentials
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InsufficientPermissionsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك صلاحية للقيام بهذا الإجراء",
        )


# ── Resources ────────────────────────────────────────────────

class NotFoundError(HTTPException):
    def __init__(self, resource: str = "المورد"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} غير موجود",
        )


class AlreadyExistsError(HTTPException):
    def __init__(self, resource: str = "المورد"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} موجود بالفعل",
        )


# ── File Upload ──────────────────────────────────────────────

class FileTooLargeError(HTTPException):
    def __init__(self, max_size_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"حجم الملف يتجاوز الحد المسموح ({max_size_mb} ميجابايت)",
        )


class UnsupportedFileTypeError(HTTPException):
    def __init__(self, file_type: str):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"نوع الملف غير مدعوم: {file_type}",
        )


# ── Rate Limiting ────────────────────────────────────────────

class RateLimitExceededError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="تم الوصول إلى الحد المؤقت للطلبات. حاول مرة أخرى بعد قليل.",
        )


# ── AI ───────────────────────────────────────────────────────

class AIProviderError(AppException):
    """Raised when all AI providers fail."""

    def __init__(self, message: str = "جميع مزودي الذكاء الاصطناعي غير متاحين حالياً"):
        super().__init__(message=message, code="AI_PROVIDER_ERROR")


class DocumentProcessingError(AppException):
    """Raised when document processing fails."""

    def __init__(self, message: str = "فشل في معالجة المستند"):
        super().__init__(message=message, code="DOCUMENT_PROCESSING_ERROR")
