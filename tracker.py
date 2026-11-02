import os
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = "9248193398:AAH2wrrZmjImA8AWxP4wFXm5mjHQyrSFIg8"
TELEGRAM_CHAT_ID = "1366960255"
URL = "https://egy.voxcinemas.com/movies/avengers-doomsday-infinity-vision#showtimes"

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
        print("Telegram alert sent successfully!")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_cinema():
    with sync_playwright() as p:
        # Launch with arguments to bypass strict protocol blocks
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-http2", "--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        print(f"Visiting {URL}...")
        try:
            # Use 'domcontentloaded' to avoid waiting for heavy third-party tracking scripts
            page.goto(URL, timeout=60000, wait_until="domcontentloaded")
            
            # Wait for City Centre Almaza section or showtimes to appear
            page.wait_for_selector("text=City Centre Almaza", timeout=25000)
            
            page_text = page.inner_text("body")
            
            if "City Centre Almaza" in page_text:
                print("City Centre Almaza found successfully!")
                send_telegram_message("✅ Cinema Tracker checked successfully: City Centre Almaza showtimes page is up!")
            else:
                print("City Centre Almaza text not found.")
                
        except Exception as e:
            print(f"Error while scraping: {e}")
            send_telegram_message(f"⚠️ Cinema Tracker Warning/Error: {str(e)[:100]}")
            
        browser.close()

if __name__ == "__main__":
    check_cinema()
