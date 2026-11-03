import os
import urllib.request
import urllib.parse

TELEGRAM_BOT_TOKEN = "9248193398:AAH2wrrZmjImA8AWxP4wFXm5mjHQyrSFIg8"
TELEGRAM_CHAT_ID = "1366960255"
URL = "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-endgame-encore-infinity-vision&m=avengers-doomsday&m=avengers-doomsday-infinity-vision"

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_cinema():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    
    req = urllib.request.Request(URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # Since the URL already filters for the exact movies and location, 
            # we just check if active seating formats (like "Standard" or "MAX") appear on the page.
            if "Avengers" in html_content and ("Standard" in html_content or "MAX" in html_content):
                print("Showtimes found!")
                send_telegram_message(f"🎬 Alert: Avengers showtimes are now available at City Centre Almaza! Book here: {URL}")
            else:
                print("No active showtimes found for this specific filter yet.")
                
    except Exception as e:
        print(f"Skipped cycle due to network filter: {e}")

if __name__ == "__main__":
    check_cinema()
