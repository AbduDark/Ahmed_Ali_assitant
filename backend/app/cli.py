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


async def seed_pdfs() -> None:
    """Auto-register and process the fixed PDF references from the project root."""
    import os
    from pathlib import Path
    from app.database import async_session_factory, engine, Base
    from app.models.reference import Reference, ReferenceStatus
    from app.document.processor import DocumentProcessor
    from sqlalchemy import select

    # PDF files to seed
    # In Docker: PDFs are mounted at /app/ (container WORKDIR)
    # In local dev: PDFs are at the project root (backend/../)
    BACKEND_DIR = Path(__file__).resolve().parent.parent  # .../backend/
    PROJECT_ROOT = BACKEND_DIR.parent                     # .../BotAssistant/

    PDF_FILES = [
        {
            "filename": "EgyptianHistory-Ar-EB-part1.pdf",
            "title": "التاريخ المصري - الجزء الأول",
            "description": "كتاب التاريخ المصري بالعربية - الجزء الأول",
        },
        {
            "filename": "EgyptianHistory-Ar-EB-part2.pdf",
            "title": "التاريخ المصري - الجزء الثاني",
            "description": "كتاب التاريخ المصري بالعربية - الجزء الثاني",
        },
    ]

    def _find_pdf(filename: str) -> Path | None:
        """Find PDF in Docker mount (/app/) or project root."""
        candidates = [
            BACKEND_DIR / filename,   # Docker: /app/<file>.pdf
            PROJECT_ROOT / filename,  # Local dev: project_root/<file>.pdf
        ]
        for p in candidates:
            if p.exists():
                return p
        return None

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    processor = DocumentProcessor()

    for pdf_info in PDF_FILES:
        pdf_path = _find_pdf(pdf_info["filename"])
        if not pdf_path:
            print(f"⚠️  File not found: {pdf_info['filename']}")
            continue

        file_size = pdf_path.stat().st_size
        print(f"\n📄 Processing: {pdf_info['filename']} ({file_size / 1024 / 1024:.1f} MB)")

        async with async_session_factory() as db:
            # Check if already registered
            result = await db.execute(
                select(Reference).where(
                    Reference.file_name == pdf_info["filename"],
                    Reference.deleted_at.is_(None),
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                if existing.status == ReferenceStatus.READY.value or existing.status == ReferenceStatus.READY:
                    print(f"   ✅ Already indexed ({existing.chunk_count or 0} chunks). Skipping.")
                    continue
                else:
                    print(f"   🔄 Re-processing (current status: {existing.status})...")
                    reference_id = existing.id
            else:
                # Create new reference entry
                # Copy PDF to uploads directory for consistent access
                upload_dir = Path(settings.upload_dir) / "references"
                upload_dir.mkdir(parents=True, exist_ok=True)
                dest_path = upload_dir / pdf_info["filename"]

                # Only copy if not already there
                if not dest_path.exists():
                    import shutil
                    print(f"   📁 Copying to uploads directory...")
                    shutil.copy2(pdf_path, dest_path)

                reference = Reference(
                    title=pdf_info["title"],
                    description=pdf_info["description"],
                    file_path=str(dest_path),
                    file_name=pdf_info["filename"],
                    file_type="pdf",
                    file_size=file_size,
                    language="ar",
                    status=ReferenceStatus.PENDING,
                )
                db.add(reference)
                await db.commit()
                reference_id = reference.id
                print(f"   📝 Registered in database (ID: {reference_id})")

            # Process the document
            try:
                print(f"   ⏳ Extracting text, chunking, and generating embeddings...")
                print(f"      (This may take a while for large files)")
                await processor.process_reference(reference_id, db)
                await db.commit()

                # Re-fetch to show final stats
                result = await db.execute(
                    select(Reference).where(Reference.id == reference_id)
                )
                ref = result.scalar_one()
                print(f"   ✅ Done! {ref.chunk_count or 0} chunks, {ref.page_count or 0} pages indexed.")
            except Exception as e:
                print(f"   ❌ Processing failed: {e}")

    await engine.dispose()
    print("\n" + "=" * 50)
    print("🎉 PDF seeding complete!")
    print("=" * 50 + "\n")


def main():
    setup_logging()
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli <create-admin|bot-info|set-webhook|seed-pdfs>")
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
    elif cmd in ("seed-pdfs", "seed-references"):
        asyncio.run(seed_pdfs())
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()

