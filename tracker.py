import os
import urllib.parse
import urllib.request
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = "9248193398:AAH2wrrZmjImA8AWxP4wFXm5mjHQyrSFIg8"
TELEGRAM_CHAT_ID = "1366960255"
STATE_FILE = "notified_avengers.txt"
TARGET_URL = "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-endgame-encore-infinity-vision&m=avengers-doomsday&m=avengers-doomsday-infinity-vision"

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_cinema():
    if os.path.exists(STATE_FILE):
        print("Avengers alert already sent previously. Skipping check.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        try:
            page.goto(TARGET_URL, timeout=60000)
            page.wait_for_timeout(5000)  # Wait for JavaScript to render showtimes
            html_content = page.content()
            
            if "Avengers" in html_content and ("Standard" in html_content or "MAX" in html_content):
                print("New Avengers showtimes found!")
                send_telegram_message(f"🎬 Alert: Avengers showtimes are now available at City Centre Almaza! Book here: {TARGET_URL}")
                with open(STATE_FILE, "w") as f:
                    f.write("notified")
            else:
                print("No active showtimes found for this filter yet.")
        except Exception as e:
            print(f"Playwright error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_cinema()
