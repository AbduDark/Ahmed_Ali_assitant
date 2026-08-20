"""Teacher instructions service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import NotFoundError
from app.models.instruction import TeacherInstruction
from app.schemas.instruction import InstructionCreate, InstructionUpdate


class InstructionService:
    """Business logic for custom AI teaching rules and instructions."""

    @staticmethod
    async def list_instructions(db: AsyncSession) -> list[TeacherInstruction]:
        """List all instructions ordered by priority."""
        result = await db.execute(
            select(TeacherInstruction).order_by(TeacherInstruction.priority.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_instruction(
        data: InstructionCreate,
        teacher_id: str,
        db: AsyncSession,
    ) -> TeacherInstruction:
        """Create a new teaching instruction."""
        instruction = TeacherInstruction(
            teacher_id=teacher_id,
            **data.model_dump(),
        )
        db.add(instruction)
        await db.commit()
        await db.refresh(instruction)
        return instruction

    @staticmethod
    async def update_instruction(
        instruction_id: str,
        data: InstructionUpdate,
        db: AsyncSession,
    ) -> TeacherInstruction:
        """Update existing instruction."""
        result = await db.execute(
            select(TeacherInstruction).where(TeacherInstruction.id == instruction_id)
        )
        instruction = result.scalar_one_or_none()
        if not instruction:
            raise NotFoundError("التعليمة")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(instruction, field, value)

        await db.commit()
        await db.refresh(instruction)
        return instruction

    @staticmethod
    async def delete_instruction(
        instruction_id: str,
        db: AsyncSession,
    ) -> None:
        """Delete an instruction."""
        result = await db.execute(
            select(TeacherInstruction).where(TeacherInstruction.id == instruction_id)
        )
        instruction = result.scalar_one_or_none()
        if not instruction:
            raise NotFoundError("التعليمة")
        await db.delete(instruction)
        await db.commit()
