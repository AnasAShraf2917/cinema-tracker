import urllib.request
import urllib.parse
import urllib.error
import json
import os

TELEGRAM_BOT_TOKEN = "9248193398:AAH2wrrZmjImA8AWxP4wFXm5mjHQyrSFIg8"
TELEGRAM_CHAT_ID = "1366960255"

BRIGHT_DATA_API_KEY = "101011d0-63b7-4459-bbd4-ebc306ca4b22"
BRIGHT_DATA_ZONE = "web_unlocker1"

STATE_FILE = "notified_avengers.txt"
TARGET_URL = "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-endgame-encore-infinity-vision&m=avengers-doomsday&m=avengers-doomsday-infinity-vision"

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def fetch_via_brightdata(url):
    endpoint = "https://api.brightdata.com/request"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}",
        "User-Agent": "Mozilla/5.0"
    }
    payload = json.dumps({
        "zone": BRIGHT_DATA_ZONE,
        "url": url,
        "format": "raw"
    }).encode("utf-8")

    req = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read().decode("utf-8", errors="ignore")

def check_cinema():
    if os.path.exists(STATE_FILE):
        print("Avengers alert already sent previously. Skipping check.")
        return

    try:
        html_content = fetch_via_brightdata(TARGET_URL)
        if "Avengers" in html_content and ("Standard" in html_content or "MAX" in html_content):
            print("New Avengers showtimes found! Sending alert...")
            send_telegram_message(f"🎬 Alert: Avengers showtimes are now available at City Centre Almaza! Book here: {TARGET_URL}")
            with open(STATE_FILE, "w") as f:
                f.write("notified")
        else:
            print("No active showtimes found for this filter yet.")
    except urllib.error.HTTPError as e:
        error_details = e.read().decode("utf-8", errors="ignore")
        print(f"Bright Data HTTP Error {e.code}: {error_details}")
    except Exception as e:
        print(f"Skipped cycle due to API error: {e}")

if __name__ == "__main__":
    check_cinema()
