import os
import asyncio
from playwright.async_api import async_playwright
import requests

# Telegram konfigurace
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

URL = "https://www.chance.cz/kurzy/"
TARGET_TEXT = "Počet gamů v zápasu"
ALERT_ALREADY_SENT = False  # Hlídá, zda už upozornění bylo posláno
VISITED_URLS = set()  # Hlídá, které zápasy jsme už kontrolovali

async def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Chyba při odesílání zprávy: {e}")

async def check_site(playwright):
    global ALERT_ALREADY_SENT
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(URL, timeout=60000)
await page.wait_for_selector('a[href^="/kurzy/zapas/"]', timeout=10000)

links = await page.locator('a[href^="/kurzy/zapas/"]').all()
print(f"Nalezeno {len(links)} zápasů ke kontrole.")

for link in links:
    print(await link.get_attribute("href"))

    for link in links:
        href = await link.get_attribute("href")
        if not href or href in VISITED_URLS:
            continue

        full_url = f"https://www.chance.cz{href}"
        VISITED_URLS.add(href)

        print(f"Kontroluji {full_url}...")
        try:
            sub_page = await browser.new_page()
            await sub_page.goto(full_url, timeout=60000)
            await sub_page.wait_for_timeout(3000)

            content = await sub_page.content()
            if TARGET_TEXT in content:
                print(f"Text nalezen na: {full_url}")
                if not ALERT_ALREADY_SENT:
                    await send_telegram_message(f"Text '{TARGET_TEXT}' nalezen na: {full_url}")
                    ALERT_ALREADY_SENT = True
                await sub_page.close()
                continue
            else:
                print("Text nenalezen.")

            await sub_page.close()
        except Exception as e:
            print(f"Chyba při kontrole stránky {full_url}: {e}")

    await browser.close()

async def main():
    async with async_playwright() as playwright:
        while True:
            await check_site(playwright)
            print("Čekám 15 sekund...")
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(main())
