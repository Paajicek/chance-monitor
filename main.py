import asyncio
from playwright.async_api import async_playwright
import os
import time
import requests

# Telegram konfigurace
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
KEYWORD = "počet es v zápasu"
URL = "https://www.chance.cz/kurzy/tenis"

already_sent = False  # abychom poslali upozornění jen jednou

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(telegram_url, data=data)

async def run_check():
    global already_sent
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)
        await page.wait_for_timeout(5000)  # počkej na načtení obsahu
        content = await page.content()

        if KEYWORD.lower() in content.lower():
            print("✅ Text nalezen.")
            if not already_sent:
                send_telegram_message(f"Na Chance.cz se objevil text: '{KEYWORD}'")
                already_sent = True
        else:
            print("❌ Text zatím nenalezen.")

        await browser.close()

while True:
    asyncio.run(run_check())
    time.sleep(15)
