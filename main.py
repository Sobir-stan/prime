import os
import sys
import subprocess


# Ushbu fayl loyihani osongina ishga tushirish uchun mo'ljallangan yordamchi skript.
# U avtomatik tarzda virtual muhit (.venv) yaratadi, kerakli paketlarni o'rnatadi va serverni ishga tushiradi.

def main():
    # Virtual muhit papkasining manzilini olish
    venv_dir = os.path.abspath(".venv")

    # Operatsion tizimga qarab python va pip manzillarini belgilash
    if os.name == 'nt':
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        venv_pip = os.path.join(venv_dir, "bin", "pip")

    # Agar dastur virtual muhit ichidan ishga tushmagan bo'lsa
    if os.path.abspath(sys.executable) != venv_python:
        print("Atrof-muhit tekshirilmoqda...")
        # Virtual muhit yo'q bo'lsa uni yaratish
        if not os.path.exists(venv_python):
            print("Virtual muhit yaratilmoqda...")
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

        # Kutubxonalarni requirements.txt dan o'qib o'rnatish
        print("Talab qilingan paketlar tekshirilmoqda va o'rnatilmoqda...")
        subprocess.check_call([venv_pip, "install", "-r", "requirements.txt"])

        # Dasturni virtual muhit yordamida qayta ishga tushirish
        print("Dastur virtual muhitda ishga tushirilmoqda...")
        sys.exit(subprocess.call([venv_python] + sys.argv))

    # Uvicorn serveri va Telegram botni birgalikda ishga tushirish

    # 1. Ngrok ni uvicorn dagi 8000 port bilan mutanosib tarzda boshlash
    from ngrok_managers import start_ngrok
    ngrok_proc, ngrok_url = start_ngrok(8000)
    if ngrok_url:
        os.environ["NGROK_URL"] = ngrok_url

    print("Telegram bot orqa fonda ishga tushirilmoqda...")
    bot_process = subprocess.Popen([sys.executable, "-m", "bot.main"])

    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
        )
    finally:
        print("Bot va qolgan xizmatlar to'xtatilmoqda...")
        bot_process.terminate()
        bot_process.wait()

        if ngrok_proc:
            ngrok_proc.terminate()
            ngrok_proc.wait()


# Dastur to'g'ridan-to'g'ri chaqirilganda main() ni ishga tushirish
if __name__ == "__main__":
    main()
