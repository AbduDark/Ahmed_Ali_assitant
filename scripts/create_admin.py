"""Script to create the first admin/teacher account."""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


async def create_admin():
    """Create the first admin user."""
    from app.database import async_session_factory, engine, Base
    from app.models.user import UserRole
    from app.services.auth_service import AuthService

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Get credentials from arguments or prompt
    if len(sys.argv) >= 4:
        email = sys.argv[1]
        password = sys.argv[2]
        name = sys.argv[3]
    else:
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        name = input("Name: ").strip()

    if not email or not password or not name:
        print("Error: Email, password, and name are required.")
        sys.exit(1)

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
            print(f"\n✅ Admin user created successfully!")
            print(f"   Email: {email}")
            print(f"   Name: {name}")
            print(f"   Role: SUPER_ADMIN")
            print(f"   ID: {user.id}")
        except Exception as e:
            print(f"\n❌ Error creating admin: {e}")
            sys.exit(1)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin())
