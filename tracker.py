import urllib.request
import urllib.parse
import time
import random

TELEGRAM_BOT_TOKEN = "9248193398:AAH2wrrZmjImA8AWxP4wFXm5mjHQyrSFIg8"
TELEGRAM_CHAT_ID = "1366960255"
URL = "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-endgame-encore-infinity-vision&m=avengers-doomsday&m=avengers-doomsday-infinity-vision"

# Rotate between realistic browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def fetch_html_with_retry(url, max_retries=3):
    # Attempt to fetch the page multiple times if it gets blocked
    for attempt in range(max_retries):
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Network block on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait 5 seconds and try again
    return None

def check_cinema():
    html_content = fetch_html_with_retry(URL)
    
    if not html_content:
        print("All retry attempts failed. Will try again next 15-min cycle.")
        return
        
    try:
        # Check if active seating formats appear on the pre-filtered Avengers page
        if "Avengers" in html_content and ("Standard" in html_content or "MAX" in html_content):
            print("Showtimes found!")
            send_telegram_message(f"🎬 Alert: Avengers showtimes are now available at City Centre Almaza! Book here: {URL}")
        else:
            print("No active showtimes found for this specific filter yet.")
            
    except Exception as e:
        print(f"Skipped cycle due to parsing error: {e}")

if __name__ == "__main__":
    check_cinema()
