import os
import urllib.request
import urllib.parse
import json

TELEGRAM_BOT_TOKEN = "9248193398:AAH2wrrZmjImA8AWxP4wFXm5mjHQyrSFIg8"
TELEGRAM_CHAT_ID = "1366960255"

def send_telegram_message(message):
    text = urllib.parse.quote(message)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    try:
        urllib.request.urlopen(api_url)
        print("Telegram alert sent successfully!")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_cinema():
    print("Checking VOX Cinemas availability...")
    
    # VOX Cinemas main movies page / general health check
    url = "https://egy.voxcinemas.com/movies/avengers-doomsday-infinity-vision"
    
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
            
            # Check if City Centre Almaza is mentioned in the raw page source
            if "City Centre Almaza" in html_content:
                print("City Centre Almaza found in page data!")
                send_telegram_message("🎬 Cinema Tracker Update: City Centre Almaza is visible on the Avengers page! Check dates/showtimes now.")
            else:
                print("City Centre Almaza not listed yet.")
                
    except Exception as e:
        print(f"Error fetching page: {e}")
        send_telegram_message(f"⚠️ Tracker lightweight check notice: Connection reset by cinema firewall, retrying next cycle.")

if __name__ == "__main__":
    check_cinema()
