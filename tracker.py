import urllib.request
import urllib.parse
import os

TELEGRAM_BOT_TOKEN = "9248193398:AAH2wrrZmjImA8AWxP4wFXm5mjHQyrSFIg8"
TELEGRAM_CHAT_ID = "1366960255"
SCRAPER_API_KEY = "3f8af86c7864a3b083dee0c5b1874a18"
STATE_FILE = "notified_avengers.txt"

TARGET_URL = "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-endgame-encore-infinity-vision&m=avengers-doomsday&m=avengers-doomsday-infinity-vision"
API_URL = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={urllib.parse.quote(TARGET_URL)}"

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_cinema():
    try:
        req = urllib.request.Request(API_URL)
        with urllib.request.urlopen(req, timeout=60) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            if "Avengers" in html_content and ("Standard" in html_content or "MAX" in html_content):
                if os.path.exists(STATE_FILE):
                    print("Avengers showtimes are available, but we already sent an alert previously.")
                else:
                    print("New Avengers showtimes found! Sending alert...")
                    send_telegram_message(f"🎬 Alert: Avengers showtimes are now available at City Centre Almaza! Book here: {TARGET_URL}")
                    with open(STATE_FILE, "w") as f:
                        f.write("notified")
            else:
                print("No active showtimes found for this filter yet.")
                
    except Exception as e:
        print(f"Skipped cycle due to API error: {e}")

if __name__ == "__main__":
    check_cinema()
