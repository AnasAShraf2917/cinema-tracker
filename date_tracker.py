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

def fetch_via_brightdata(url, render_js=True, as_markdown=True):
    endpoint = "https://api.brightdata.com/request"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}",
        "User-Agent": "Mozilla/5.0"
    }
    body = {
        "zone": BRIGHT_DATA_ZONE,
        "url": url,
        "format": "raw"
    }
    if render_js:
        body["render"] = "true"
    if as_markdown:
        body["data_format"] = "markdown"

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            status = response.headers.get("x-brd-status-code", response.status)
            content = response.read().decode("utf-8", errors="ignore")
            return content, status
    except urllib.error.HTTPError as e:
        if e.code == 400 and (render_js or as_markdown):
            return fetch_via_brightdata(url, render_js=False, as_markdown=False)
        raise

def extract_visible_text(content):
    no_scripts = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', content, flags=re.DOTALL | re.IGNORECASE)
    no_tags = re.sub(r'<[^>]+>', ' ', no_scripts)
    return re.sub(r'\s+', ' ', no_tags).strip()

def check_new_dates():
    try:
        content, status = fetch_via_brightdata(TARGET_URL, render_js=True, as_markdown=True)
        visible_text = extract_visible_text(content)

        date_pattern = r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'
        current_dates = set(re.findall(date_pattern, visible_text))
        current_dates.update(re.findall(date_pattern, content))

        if not current_dates:
            print(f"No dates found on page (Status: {status}, Length: {len(content)}). Preview: {visible_text[:200]}")
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
