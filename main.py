# =====================================================================================
#  PAKEL MLBBSTORE — MAIN RUNNER
#  Jalanin Bot Telegram + API Flask sekaligus dalam 1 service
# =====================================================================================

import os
import threading
import time

# =====================================================================================
#  IMPORT FLASK APP (dari apk_api.py)
# =====================================================================================
from apk_api import app

# =====================================================================================
#  RUN BOT TELEGRAM DI BACKGROUND THREAD
# =====================================================================================
def run_bot():
    print("[MAIN] 🤖 Import pakeltest & starting Telegram bot...")
    try:
        import pakeltest
        print("[MAIN] ✅ pakeltest imported. Bot polling aktif di background.")
        # JALANKAN POLLING DI SINI
        # (karena di pakeltest.py ada if __name__ == '__main__' yang GAK JALAN saat di-import)
        pakeltest.bot.infinity_polling(timeout=60, long_polling_timeout=30)
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
        use_reloader=False,
        threaded=True
    )