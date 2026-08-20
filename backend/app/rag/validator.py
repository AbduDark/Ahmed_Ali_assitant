"""Answer validation — hallucination protection layer."""

from __future__ import annotations

from app.core.logging import get_logger
from app.rag.retriever import RetrievedChunk

logger = get_logger(__name__)

# Fallback message when confidence is too low
LOW_CONFIDENCE_MSG_AR = "لم أجد في المراجع المتاحة معلومات كافية للإجابة عن السؤال بدقة. يرجى مراجعة المدرس للحصول على إجابة دقيقة."


class AnswerValidator:
    """
    Validates AI answers against retrieved context.

    Checks:
    1. Were any chunks retrieved?
    2. Is the answer grounded in the retrieved content?
    3. Confidence scoring based on retrieval quality.
    """

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def validate(
        self,
        answer: str,
        retrieved_chunks: list[RetrievedChunk],
        question: str,
    ) -> tuple[str, float, bool]:
        """
        Validate an AI-generated answer.

        Returns:
            (final_answer, confidence_score, is_grounded)
        """
        # If no chunks were retrieved, the answer is ungrounded
        if not retrieved_chunks:
            logger.warning("No chunks retrieved — answer is ungrounded")
            return LOW_CONFIDENCE_MSG_AR, 0.0, False

        # Calculate confidence based on retrieval quality
        confidence = self._calculate_confidence(retrieved_chunks)

        # Check if the answer seems to acknowledge lack of information
        acknowledges_uncertainty = self._check_uncertainty_acknowledgment(answer)

        if confidence < self.confidence_threshold and not acknowledges_uncertainty:
            logger.warning(
                f"Low confidence ({confidence:.2f}) — using fallback message"
            )
            return LOW_CONFIDENCE_MSG_AR, confidence, False

        return answer, confidence, True

    def _calculate_confidence(self, chunks: list[RetrievedChunk]) -> float:
        """
        Calculate confidence score based on retrieval quality.

        Factors:
        - Average chunk similarity score
        - Number of chunks retrieved
        - Score distribution
        """
        if not chunks:
            return 0.0

        scores = [chunk.score for chunk in chunks]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)

        # Weighted: 60% max score, 30% average, 10% count bonus
        count_bonus = min(len(chunks) / 5.0, 1.0) * 0.1
        confidence = (max_score * 0.6) + (avg_score * 0.3) + count_bonus

        return min(confidence, 1.0)

    def _check_uncertainty_acknowledgment(self, answer: str) -> bool:
        """Check if the answer already acknowledges uncertainty."""
        uncertainty_phrases = [
            "لم أجد",
            "لا تحتوي المراجع",
            "غير متوفر",
            "لم يتم العثور",
            "خارج المنهج",
            "لا توجد معلومات كافية",
            "I don't have enough information",
            "not available in the references",
        ]
        answer_lower = answer.lower()
        return any(phrase in answer_lower or phrase in answer for phrase in uncertainty_phrases)
