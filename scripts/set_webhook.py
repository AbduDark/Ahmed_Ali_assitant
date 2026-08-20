"""Script to configure, test, and manage the Telegram Bot Webhook."""

import argparse
import json
import sys
import httpx


def manage_webhook():
    parser = argparse.ArgumentParser(description="Manage Telegram Bot Webhook")
    parser.add_argument("--token", required=True, help="Telegram Bot Token")
    parser.add_argument("--url", help="Public HTTPS domain (e.g. https://api.yourdomain.com or https://xxxx.ngrok-free.app)")
    parser.add_argument("--secret", default="", help="Telegram Webhook Secret Token")
    parser.add_argument("--info", action="store_true", help="Get current webhook info")
    parser.add_argument("--delete", action="store_true", help="Delete webhook (re-enable polling)")
    parser.add_argument("--drop-pending", action="store_true", help="Drop pending updates")

    args = parser.parse_args()
    bot_token = args.token.strip()
    api_url = f"https://api.telegram.org/bot{bot_token}"

    if args.info:
        # Get Webhook Info
        resp = httpx.get(f"{api_url}/getWebhookInfo")
        print("\n📡 Current Telegram Webhook Status:")
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        return

    if args.delete:
        # Delete Webhook
        resp = httpx.post(f"{api_url}/deleteWebhook", json={"drop_pending_updates": args.drop_pending})
        print("\n🗑️ Delete Webhook Response:")
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        return

    if not args.url:
        print("❌ Error: --url is required when setting a webhook.")
        sys.exit(1)

    # Base URL normalization
    base_url = args.url.rstrip("/")
    webhook_endpoint = f"{base_url}/webhooks/telegram"
    if args.secret:
        webhook_endpoint += f"/{args.secret}"

    payload = {
        "url": webhook_endpoint,
        "drop_pending_updates": args.drop_pending,
    }
    if args.secret:
        payload["secret_token"] = args.secret

    print(f"\n🚀 Setting Telegram Webhook to:\n   {webhook_endpoint}")
    resp = httpx.post(f"{api_url}/setWebhook", json=payload)
    data = resp.json()
    print("\n✅ Telegram API Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    if data.get("ok"):
        print("\n🎉 Webhook configured successfully!")
    else:
        print("\n❌ Failed to set webhook. Check the error message above.")


if __name__ == "__main__":
    manage_webhook()
