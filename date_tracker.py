import urllib.request
import urllib.parse
import re
import os

TELEGRAM_BOT_TOKEN = "9220799581:AAHVmxcBIWq2WO42HYFV8NBhhmo5wscoCh0"
TELEGRAM_CHAT_ID = "1366960255"
SCRAPER_API_KEY = "3f8af86c7864a3b083dee0c5b1874a18"

TARGET_URL = "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza"
API_URL = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={urllib.parse.quote(TARGET_URL)}"
STATE_FILE = "known_dates.txt"

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_new_dates():
    try:
        req = urllib.request.Request(API_URL)
        with urllib.request.urlopen(req, timeout=60) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
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

    except Exception as e:
        print(f"Skipped cycle due to API error: {e}")

if __name__ == "__main__":
    check_new_dates()
