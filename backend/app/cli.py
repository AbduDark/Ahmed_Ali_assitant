"""Management CLI commands."""

import asyncio
import sys
from sqlalchemy import text
from app.config import settings
from app.core.logging import setup_logging


async def create_admin(email: str, password: str, name: str) -> None:
    """Create the first admin user."""
    from app.database import async_session_factory, engine, Base
    from app.models.user import UserRole
    from app.services.auth_service import AuthService

    # 1. Ensure all tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Safely alter any existing enum columns to standard VARCHAR in separate transactions
    alter_statements = [
        "ALTER TABLE IF EXISTS users ALTER COLUMN role TYPE VARCHAR(50) USING role::text;",
        "ALTER TABLE IF EXISTS messages ALTER COLUMN role TYPE VARCHAR(50) USING role::text;",
        "ALTER TABLE IF EXISTS references ALTER COLUMN status TYPE VARCHAR(50) USING status::text;",
    ]
    for sql in alter_statements:
        try:
            async with engine.begin() as conn:
                await conn.execute(text(sql))
        except Exception:
            pass

    # 3. Create the admin user
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


async def check_bot_status() -> None:
    """Check Telegram bot connectivity and current webhook info."""
    from telegram import Bot
    if not settings.telegram_bot_token:
        print("❌ TELEGRAM_BOT_TOKEN is not set in .env")
        return

    bot = Bot(token=settings.telegram_bot_token)
    try:
        me = await bot.get_me()
        print("\n" + "=" * 50)
        print("🤖 Telegram Bot Information:")
        print(f"   Name: {me.first_name}")
        print(f"   Username: @{me.username}")
        print(f"   ID: {me.id}")

        info = await bot.get_webhook_info()
        print("\n📡 Webhook Status on Telegram Servers:")
        print(f"   URL: {info.url or '(None - Polling mode active)'}")
        print(f"   Has Custom Certificate: {info.has_custom_certificate}")
        print(f"   Pending Updates Count: {info.pending_update_count}")
        if info.last_error_date:
            print(f"   Last Error Date: {info.last_error_date}")
            print(f"   Last Error Message: {info.last_error_message}")
        else:
            print("   Last Error: None (Healthy)")
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"❌ Error communicating with Telegram API: {e}")


async def set_webhook(url: str | None = None) -> None:
    """Register or update Telegram webhook."""
    from telegram import Bot
    if not settings.telegram_bot_token:
        print("❌ TELEGRAM_BOT_TOKEN is not set in .env")
        return

    bot = Bot(token=settings.telegram_bot_token)
    target_base = (url or settings.telegram_webhook_url).rstrip('/')
    secret = settings.telegram_webhook_secret
    webhook_url = f"{target_base}/webhooks/telegram/{secret}"

    print(f"Setting webhook to: {webhook_url} ...")
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        success = await bot.set_webhook(
            url=webhook_url,
            secret_token=secret,
            drop_pending_updates=False,
        )
        if success:
            print("✅ Telegram Webhook registered successfully!")
            await check_bot_status()
        else:
            print("❌ Failed to set webhook.")
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")


def main():
    setup_logging()
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli <create-admin|bot-info|set-webhook>")
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
    elif cmd in ("bot-info", "status"):
        asyncio.run(check_bot_status())
    elif cmd in ("set-webhook", "webhook"):
        custom_url = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(set_webhook(custom_url))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
