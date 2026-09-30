# =====================================================================================
#  PAKEL MLBBSTORE — MAIN RUNNER
#  Jalanin Bot Telegram + API Flask sekaligus dalam 1 service
#  TANPA mengubah script pakeltest.py atau apk_api.py
# =====================================================================================

import os
import threading
import time

# =====================================================================================
#  IMPORT FLASK APP (dari apk_api.py) — AMAN, GAK ADA POLLING
# =====================================================================================
from apk_api import app

# =====================================================================================
#  RUN BOT TELEGRAM DI BACKGROUND THREAD
#  Import pakeltest DI DALAM fungsi → polling jalan di thread ini
# =====================================================================================
def run_bot():
    print("[MAIN] 🤖 Import pakeltest & starting Telegram bot...")
    try:
        # Import di dalam fungsi — biar polling-nya jalan di thread ini,
        # BUKAN di main thread yang bikin Flask ke-blok
        import pakeltest
        print("[MAIN] ✅ pakeltest imported. Bot polling aktif di background.")
        # Thread ini bakal ke-blok di pakeltest (infinity_polling)
        # Selama bot hidup, thread ini hidup.
        while True:
            time.sleep(3600)
    except Exception as e:
        print(f"[MAIN] ❌ Bot error: {e}")

# =====================================================================================
#  START BOT THREAD
# =====================================================================================
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

# Kasih waktu bot buat init dulu
time.sleep(3)

# =====================================================================================
#  RUN FLASK DI MAIN THREAD (Railway butuh buka port)
# =====================================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"[MAIN] 🌐 Starting API on port {port}")
    print(f"[MAIN] ✅ Bot + API running!")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,   # WAJIB False biar bot gak jalan 2x
        threaded=True
    )
