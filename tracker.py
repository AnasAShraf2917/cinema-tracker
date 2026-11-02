import os
import time
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright

# Your Telegram Config
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
    # Send a forced test notification immediately on run
    send_telegram_message("🤖 Cinema Tracker workflow started successfully! Checking Avengers at City Centre Almaza...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Checking VOX Cinemas for Avengers...")
        try:
            page.goto(URL, timeout=60000)
            page.wait_for_selector("text=City Centre Almaza", timeout=20000)
            page_text = page.inner_text("body")
            
            if "City Centre Almaza" in page_text:
                print("Found City Centre Almaza on the page.")
                # You can add custom conditions here later if new dates or seats open up
            else:
                print("City Centre Almaza text not found.")
                
        except Exception as e:
            print(f"Error while browsing: {e}")
            
        browser.close()

if __name__ == "__main__":
    check_cinema()
