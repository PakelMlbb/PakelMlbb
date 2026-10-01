# =====================================================================================
#  PAKEL MLBBSTORE — MAIN RUNNER v3 (WAITRESS PRODUCTION)
#  Jalanin Bot Telegram + API Flask sekaligus dalam 1 service
# =====================================================================================

import os
import threading
import time

# Set default env kalau belum ada
if 'DATA_DIR' not in os.environ:
    os.environ['DATA_DIR'] = '/data'
if 'PORT' not in os.environ:
    os.environ['PORT'] = '8080'

print("=" * 60)
print("[MAIN] Pakel MlbbStore — Starting...")
print(f"[MAIN] DATA_DIR = {os.environ.get('DATA_DIR')}")
print(f"[MAIN] PORT = {os.environ.get('PORT')}")
print("=" * 60)

# Import flask app + ensure_stocks_file dari apk_api
from apk_api import app, ensure_stocks_file


# =====================================================================================
#  RUN BOT TELEGRAM DI BACKGROUND THREAD
# =====================================================================================
def run_bot():
    print("[MAIN] 🤖 Import pakeltest & starting Telegram bot...")
    try:
        import pakeltest
        print("[MAIN] ✅ pakeltest imported. Bot polling aktif di background.")
        # JALANKAN POLLING DI SINI
        pakeltest.bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"[MAIN] ❌ Bot error: {e}")
        import traceback
        traceback.print_exc()


# =====================================================================================
#  MAIN — START BOT + FLASK (WAITRESS)
# =====================================================================================
if __name__ == '__main__':
    # 1. Auto-bikin stocks.txt DI STARTUP (biar stok gak 0)
    print("[MAIN] 🔧 Running ensure_stocks_file()...")
    try:
        ensure_stocks_file()
        print("[MAIN] ✅ ensure_stocks_file() selesai")
    except Exception as e:
        print(f"[MAIN] ⚠️ ensure_stocks_file error: {e}")

    # 2. Start bot Telegram di background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # 3. Kasih waktu bot init dulu
    time.sleep(3)

    # 4. Run API pakai WAITRESS (production server)
    port = int(os.environ.get('PORT', 8080))
    print(f"[MAIN] 🌐 Starting API (WAITRESS) on port {port}")
    print(f"[MAIN] ✅ Bot + API running!")

    try:
        from waitress import serve
        print("[MAIN] Using WAITRESS production server")
        serve(app, host='0.0.0.0', port=port, threads=8, connection_limit=1000)
    except ImportError:
        print("[MAIN] ⚠️ waitress gak keinstall, fallback ke Flask dev server")
        print("[MAIN] Install: pip install waitress")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)