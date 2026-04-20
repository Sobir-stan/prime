import subprocess
import time
import urllib.request
import json


def start_ngrok(port=8000):
    print("Ngrok ishga tushirilmoqda...")
    try:
        # Ngrok ni orqa fonda subprocess orqali chaqirish
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("Xatolik: ngrok tizimda topilmadi. Iltimos, Ngrok.exe ni PATH ga qo'shganingizni tekshiring.")
        return None, None

    # Tunnel ulanishini biroz kutamiz
    time.sleep(3)

    try:
        # Ngrok'ning lokal API orqali faol public URL ni olish
        req = urllib.request.Request("http://127.0.0.1:4040/api/tunnels")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if "tunnels" in data and len(data["tunnels"]) > 0:
                public_url = data['tunnels'][0]['public_url']
                print(f"✅ Avtomatik tutilgan Ngrok URL manzili: {public_url}")
                return ngrok_process, public_url
    except Exception as e:
        print(f"Ngrok URL manzilini lokal API dan o'qishda ulanish xatosi (xatolik: {e})")
        ngrok_process.terminate()

    print("Ngrok urlni topib bo'lmadi.")
    return None, None
