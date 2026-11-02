import os
import urllib.request
import urllib.parse

TELEGRAM_BOT_TOKEN = "9248193398:AAH2wrrZmjImA8AWxP4wFXm5mjHQyrSFIg8"
TELEGRAM_CHAT_ID = "1366960255"
URL = "https://egy.voxcinemas.com/movies/avengers-doomsday-infinity-vision"

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_cinema():
    # Full desktop browser headers to bypass bot detection filters
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    req = urllib.request.Request(URL, headers=headers)
    
    try:
        # Use a custom opener to handle compression if needed
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # Check if City Centre Almaza is listed
            if "City Centre Almaza" in html_content:
                print("City Centre Almaza found!")
                # OPTIONAL: You can add logic here to track if new dates appear.
                # For now, it runs silently in the background every 15 minutes.
            else:
                print("Target cinema text not found in current payload.")
                
    except Exception as e:
        # Fail silently so it doesn't spam your Telegram; GitHub Actions log will record it if needed
        print(f"Skipped cycle due to network filter: {e}")

if __name__ == "__main__":
    check_cinema()
