import urllib.request
import urllib.parse
import urllib.error
import json
import re
import os

TELEGRAM_BOT_TOKEN = "9220799581:AAHVmxcBIWq2WO42HYFV8NBhhmo5wscoCh0"
TELEGRAM_CHAT_ID = "1366960255"

BRIGHT_DATA_API_KEY = "101011d0-63b7-4459-bbd4-ebc306ca4b22"
BRIGHT_DATA_ZONE = "web_unlocker1"

TARGET_URL = "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza"
STATE_FILE = "known_dates.txt"

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

def check_new_dates():
    try:
        html = fetch_via_brightdata(TARGET_URL)
        date_pattern = r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'
        current_dates = set(re.findall(date_pattern, html))

        if not current_dates:
            print("No dates found on page.")
            return

        known_dates = set()
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                known_dates = set(f.read().splitlines())

        if not known_dates:
            with open(STATE_FILE, "w") as f:
                for d in current_dates:
                    f.write(f"{d}\n")
            print("Initialized known dates quietly. No alert sent.")
            return

        new_dates = current_dates - known_dates

        if new_dates:
            new_dates_list = sorted(list(new_dates))
            message = f"🚨 NEW DATES ADDED at City Centre Almaza!\n\nJust opened: {', '.join(new_dates_list)}\n\nBook now: {TARGET_URL}"
            send_telegram_message(message)

            all_dates = known_dates.union(current_dates)
            with open(STATE_FILE, "w") as f:
                for d in all_dates:
                    f.write(f"{d}\n")
            print(f"Alerted for new dates: {new_dates_list}")
        else:
            print(f"No new dates. Currently tracking {len(known_dates)} dates.")

    except urllib.error.HTTPError as e:
        error_details = e.read().decode("utf-8", errors="ignore")
        print(f"Bright Data HTTP Error {e.code}: {error_details}")
    except Exception as e:
        print(f"Skipped cycle due to API error: {e}")

if __name__ == "__main__":
    check_new_dates()
