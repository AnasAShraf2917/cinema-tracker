import urllib.request
import urllib.parse
import re
import os
import time
import random

TELEGRAM_BOT_TOKEN = "9220799581:AAHVmxcBIWq2WO42HYFV8NBhhmo5wscoCh0"
TELEGRAM_CHAT_ID = "1366960255"
URL = "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza"
STATE_FILE = "known_dates.txt"

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

def check_new_dates():
    html = fetch_html_with_retry(URL)
    
    if not html:
        print("All retry attempts failed. Will try again next 15-min cycle.")
        return
        
    try:
        date_pattern = r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'
        current_dates = set(re.findall(date_pattern, html))
        
        if not current_dates:
            print("Page loaded, but no dates found (Structure change).")
            return
            
        known_dates = set()
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                known_dates = set(f.read().splitlines())
                
        new_dates = current_dates - known_dates
        
        if new_dates:
            new_dates_list = sorted(list(new_dates))
            message = f"🚨 NEW DATES ADDED at City Centre Almaza!\n\nJust opened: {', '.join(new_dates_list)}\n\nBook now: {URL}"
            send_telegram_message(message)
            print(f"Alerted for new dates: {new_dates_list}")
            
            all_dates = known_dates.union(current_dates)
            with open(STATE_FILE, "w") as f:
                for d in all_dates:
                    f.write(f"{d}\n")
        else:
            print(f"No new dates. Currently tracking {len(known_dates)} known dates.")
            
            if not os.path.exists(STATE_FILE):
                with open(STATE_FILE, "w") as f:
                    for d in current_dates:
                        f.write(f"{d}\n")
                print("Initial dates logged. Waiting for updates.")

    except Exception as e:
        print(f"Error parsing dates: {e}")

if __name__ == "__main__":
    check_new_dates()
