import urllib.request
import urllib.parse
import re
import os

TELEGRAM_BOT_TOKEN = "9220799581:AAHVmxcBIWq2WO42HYFV8NBhhmo5wscoCh0"
TELEGRAM_CHAT_ID = "1366960255"
URL = "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza"
STATE_FILE = "known_dates.txt"

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_new_dates():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    req = urllib.request.Request(URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Extract all date strings from the HTML (e.g., "Thu 5 Nov", "Wed 16 Dec")
            # This regex looks for 3-letter day, 1-2 digit date, 3-letter month
            date_pattern = r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'
            current_dates = set(re.findall(date_pattern, html))
            
            if not current_dates:
                print("No dates found on page. Network block or site structure change.")
                return
                
            # Load previously known dates from our state file
            known_dates = set()
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r") as f:
                    known_dates = set(f.read().splitlines())
                    
            # Find any dates that are currently on the website but NOT in our known list
            new_dates = current_dates - known_dates
            
            if new_dates:
                # We found new dates! Send alert.
                new_dates_list = sorted(list(new_dates))
                message = f"🚨 NEW DATES ADDED at City Centre Almaza!\n\nJust opened: {', '.join(new_dates_list)}\n\nBook now: {URL}"
                send_telegram_message(message)
                print(f"Alerted for new dates: {new_dates_list}")
                
                # Update the state file with the new combined list so we don't alert again
                all_dates = known_dates.union(current_dates)
                with open(STATE_FILE, "w") as f:
                    for d in all_dates:
                        f.write(f"{d}\n")
            else:
                print(f"No new dates. Currently tracking {len(known_dates)} known dates.")
                
                # If this is the very first run (no state file), save the current dates quietly
                if not os.path.exists(STATE_FILE):
                    with open(STATE_FILE, "w") as f:
                        for d in current_dates:
                            f.write(f"{d}\n")
                    print("Initial dates logged. Waiting for updates.")

    except Exception as e:
        print(f"Skipped cycle due to network/parsing error: {e}")

if __name__ == "__main__":
    check_new_dates()
