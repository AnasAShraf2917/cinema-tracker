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
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Visiting {URL}...")
        try:
            page.goto(URL, timeout=60000)
            
            # Wait for the cinema section to load
            page.wait_for_selector("text=City Centre Almaza", timeout=20000)
            
            # Extract text from the page
            page_text = page.inner_text("body")
            
            if "City Centre Almaza" in page_text:
                print("City Centre Almaza found!")
                
                # Let's grab a snippet of text around City Centre Almaza to see available showtimes
                # We can send this directly to your Telegram so you can read the live schedule on your phone!
                
                # Simple extraction of what's currently showing
                message = "🎬 Avengers Update from City Centre Almaza:\n\nThe page is live! Check your available dates/times on the app or browser."
                send_telegram_message(message)
            else:
                print("City Centre Almaza not found on page.")
                
        except Exception as e:
            print(f"Error while scraping: {e}")
            send_telegram_message(f"⚠️ Cinema Tracker Error: {str(e)}")
            
        browser.close()

if __name__ == "__main__":
    check_cinema()
