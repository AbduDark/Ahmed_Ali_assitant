"""Teacher instructions API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import NotFoundError
from app.database import get_async_session
from app.dependencies import CurrentUserId
from app.models.instruction import TeacherInstruction
from app.schemas.instruction import InstructionCreate, InstructionResponse, InstructionUpdate

router = APIRouter(prefix="/instructions", tags=["Instructions"])


@router.get("", response_model=list[InstructionResponse])
async def list_instructions(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """List all teacher instructions."""
    result = await db.execute(
        select(TeacherInstruction).order_by(TeacherInstruction.priority.desc())
    )
    instructions = list(result.scalars().all())
    return [InstructionResponse.model_validate(i) for i in instructions]


@router.post("", response_model=InstructionResponse, status_code=201)
async def create_instruction(
    data: InstructionCreate,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new teacher instruction."""
    instruction = TeacherInstruction(
        teacher_id=user_id,
        **data.model_dump(),
    )
    db.add(instruction)
    await db.flush()
    return InstructionResponse.model_validate(instruction)


@router.patch("/{instruction_id}", response_model=InstructionResponse)
async def update_instruction(
    instruction_id: str,
    data: InstructionUpdate,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Update a teacher instruction."""
    result = await db.execute(
        select(TeacherInstruction).where(TeacherInstruction.id == instruction_id)
    )
    instruction = result.scalar_one_or_none()
    if not instruction:
        raise NotFoundError("التعليمة")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(instruction, field, value)

    return InstructionResponse.model_validate(instruction)


@router.delete("/{instruction_id}", status_code=204)
async def delete_instruction(
    instruction_id: str,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a teacher instruction."""
    result = await db.execute(
        select(TeacherInstruction).where(TeacherInstruction.id == instruction_id)
    )
    instruction = result.scalar_one_or_none()
    if not instruction:
        raise NotFoundError("التعليمة")
    await db.delete(instruction)
