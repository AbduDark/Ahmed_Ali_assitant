"""Management CLI commands."""

import asyncio
import sys
from sqlalchemy import text
from app.core.logging import setup_logging


async def create_admin(email: str, password: str, name: str) -> None:
    """Create the first admin user."""
    from app.database import async_session_factory, engine, Base
    from app.models.user import UserRole
    from app.services.auth_service import AuthService

    # Ensure tables and enum values exist in postgres
    async with engine.begin() as conn:
        for val in ["super_admin", "SUPER_ADMIN", "teacher", "TEACHER", "assistant", "ASSISTANT"]:
            try:
                await conn.execute(text(f"ALTER TYPE user_role ADD VALUE IF NOT EXISTS '{val}'"))
            except Exception:
                pass
        for val in ["student", "STUDENT", "assistant", "ASSISTANT", "system", "SYSTEM"]:
            try:
                await conn.execute(text(f"ALTER TYPE message_role ADD VALUE IF NOT EXISTS '{val}'"))
            except Exception:
                pass
        for val in ["pending", "PENDING", "processing", "PROCESSING", "ready", "READY", "failed", "FAILED"]:
            try:
                await conn.execute(text(f"ALTER TYPE reference_status ADD VALUE IF NOT EXISTS '{val}'"))
            except Exception:
                pass
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        try:
            user = await AuthService.create_user(
                email=email,
                password=password,
                name=name,
                role=UserRole.SUPER_ADMIN,
                db=db,
            )
            await db.commit()
            print("\n" + "=" * 50)
            print("🎉 Admin user created successfully!")
            print(f"   Email: {email}")
            print(f"   Name: {name}")
            print(f"   Role: {user.role.value if hasattr(user.role, 'value') else user.role}")
            print(f"   ID: {user.id}")
            print("=" * 50 + "\n")
        except Exception as e:
            print(f"\n❌ Error creating admin: {e}")
            sys.exit(1)

    await engine.dispose()


def main():
    setup_logging()
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli create-admin <email> <password> <name>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "create-admin":
        if len(sys.argv) < 5:
            print("Usage: python -m app.cli create-admin <email> <password> <name>")
            sys.exit(1)
        email = sys.argv[2]
        password = sys.argv[3]
        name = sys.argv[4]
        asyncio.run(create_admin(email, password, name))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
