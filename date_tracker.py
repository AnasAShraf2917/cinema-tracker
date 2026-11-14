import urllib.request
import urllib.parse
import urllib.error
import json
import re
import os
import time
from datetime import datetime

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

def fetch_via_brightdata(url, max_retries=3):
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

    brd_status = "unknown"
    brd_error = ""
    for attempt in range(1, max_retries + 1):
        req = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as response:
            brd_status = str(response.headers.get("x-brd-status-code", response.status))
            brd_error = response.headers.get("x-brd-error-code", "")
            html = response.read().decode("utf-8", errors="ignore")

            if brd_status == "200" and len(html) > 500:
                return html, brd_status, brd_error

            print(f"Attempt {attempt}/{max_retries} returned status {brd_status} (length: {len(html)}, error: {brd_error}).")
            if attempt < max_retries:
                time.sleep(3)

    return "", brd_status, brd_error

def extract_dates(html):
    # Remove scripts/styles and strip HTML tags so split <span>Mon</span><span>16</span><span>Nov</span> text joins cleanly
    no_scripts = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    visible_text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', no_scripts)).strip()

    date_pattern = r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'
    found_dates = set(re.findall(date_pattern, visible_text))

    # Also extract d=YYYYMMDD parameters from VOX date tab links (covers Today, Tomorrow, and all date tabs)
    for y, m, d in re.findall(r'[?&](?:amp;)?d=(20\d{2})(\d{2})(\d{2})\b', html):
        try:
            dt = datetime(int(y), int(m), int(d))
            found_dates.add(f"{dt.strftime('%a')} {dt.day} {dt.strftime('%b')}")
        except ValueError:
            pass

    # Also check data-date="YYYY-MM-DD" attributes
    for y, m, d in re.findall(r'data-date=["\'](20\d{2})-(\d{2})-(\d{2})["\']', html):
        try:
            dt = datetime(int(y), int(m), int(d))
            found_dates.add(f"{dt.strftime('%a')} {dt.day} {dt.strftime('%b')}")
        except ValueError:
            pass

    return found_dates, visible_text

def check_new_dates():
    try:
        html, status, brd_error = fetch_via_brightdata(TARGET_URL)
        if not html:
            print(f"Could not fetch valid HTML after retries (Status: {status}, Error: {brd_error}).")
            return

        current_dates, visible_text = extract_dates(html)

        if not current_dates:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, flags=re.DOTALL | re.IGNORECASE)
            page_title = title_match.group(1).strip() if title_match else "No title"
            print(f"No dates found on page (Status: {status}, Length: {len(html)}, Title: {page_title}). Text preview: {visible_text[:200]}")
            return

        known_dates = set()
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                known_dates = set(line.strip() for line in f if line.strip())

        if not known_dates:
            with open(STATE_FILE, "w") as f:
                for d in sorted(current_dates):
                    f.write(f"{d}\n")
            print(f"Initialized {len(current_dates)} known dates quietly: {sorted(current_dates)}")
            return

        new_dates = current_dates - known_dates

        if new_dates:
            new_dates_list = sorted(list(new_dates))
            message = f"🚨 NEW DATES ADDED at City Centre Almaza!\n\nJust opened: {', '.join(new_dates_list)}\n\nBook now: {TARGET_URL}"
            send_telegram_message(message)

            all_dates = known_dates.union(current_dates)
            with open(STATE_FILE, "w") as f:
                for d in sorted(all_dates):
                    f.write(f"{d}\n")
            print(f"Alerted for new dates: {new_dates_list}")
        else:
            print(f"No new dates. Currently tracking {len(known_dates)} dates: {sorted(known_dates)}")

    except urllib.error.HTTPError as e:
        error_details = e.read().decode("utf-8", errors="ignore")
        print(f"Bright Data HTTP Error {e.code}: {error_details}")
    except Exception as e:
        print(f"Skipped cycle due to API error: {e}")

if __name__ == "__main__":
    check_new_dates()
