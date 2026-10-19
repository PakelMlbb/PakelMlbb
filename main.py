# =====================================================================================
#  PAKEL MLBBSTORE — MAIN RUNNER v4 (WAITRESS PRODUCTION)
#  Jalanin Bot Telegram + API Flask sekaligus dalam 1 service
#
#  Perubahan v4 (hasil audit):
#  - Bot thread auto-restart kalau crash (dulu mati diam-diam sampai service di-restart manual)
#  - SystemExit dari pakeltest (mis. TELEGRAM_TOKEN kosong) ikut ditangkap & dilog jelas
#  - Waitress: threads 4 -> 16 + timeout. Dengan 4 thread, 4 request yang menunggu Telegram
#    (timeout sampai 30 dtk) cukup bikin SELURUH API macet ("APK loading terus").
#  - Hapus time.sleep(3) sebelum API start (bikin health-check Railway telat)
#  - Log di-flush tiap baris supaya langsung muncul di Railway
# =====================================================================================

import os
import sys
import threading
import time
import traceback

try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

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

# Import flask app + helper dari apk_api
from apk_api import app, ensure_stocks_file, ensure_proofs_folder


# =====================================================================================
#  RUN BOT TELEGRAM DI BACKGROUND THREAD (auto-restart)
# =====================================================================================
def run_bot():
    backoff = 5
    while True:
        try:
            print("[MAIN] 🤖 Import pakeltest & starting Telegram bot...")
            import pakeltest
            print("[MAIN] ✅ pakeltest imported. Bot polling aktif di background.")
            backoff = 5
            # infinity_polling sudah auto-reconnect; kalau sampai keluar/exception, loop ini start ulang
            pakeltest.bot.infinity_polling(timeout=60, long_polling_timeout=30)
            print("[MAIN] ⚠️ infinity_polling berhenti, restart...")
        except SystemExit as e:
            # Biasanya TELEGRAM_TOKEN belum di-set. Restart tidak akan membantu -> berhenti, API tetap jalan.
            print(f"[MAIN] ❌ Bot berhenti (SystemExit: {e.code}). Cek env TELEGRAM_TOKEN. API tetap jalan.")
            return
        except Exception as e:
            print(f"[MAIN] ❌ Bot error: {e}")
            traceback.print_exc()
        print(f"[MAIN] 🔁 Restart bot dalam {backoff} detik...")
        time.sleep(backoff)
        backoff = min(backoff * 2, 60)


# =====================================================================================
#  MAIN — START BOT + FLASK (WAITRESS)
# =====================================================================================
if __name__ == '__main__':
    # 1. Siapkan file & folder yang dibutuhkan (tidak menimpa stok yang sudah ada)
    print("[MAIN] 🔧 Running ensure_stocks_file()...")
    try:
        ensure_stocks_file()
        ensure_proofs_folder()
        print("[MAIN] ✅ ensure_stocks_file() selesai")
    except Exception as e:
        print(f"[MAIN] ⚠️ ensure_stocks_file error: {e}")

    # 2. Start bot Telegram di background thread
    bot_thread = threading.Thread(target=run_bot, name="telegram-bot", daemon=True)
    bot_thread.start()

    # 3. Run API pakai WAITRESS (production server)
    port = int(os.environ.get('PORT', 8080))
    print(f"[MAIN] 🌐 Starting API (WAITRESS) on port {port}")

    try:
        from waitress import serve
        print("[MAIN] Using WAITRESS production server")
        serve(
            app,
            host='0.0.0.0',
            port=port,
            threads=16,                              # dulu 4 -> gampang kehabisan thread
            connection_limit=200,
            channel_timeout=120,                     # tutup koneksi macet
            max_request_body_size=13 * 1024 * 1024,  # sedikit di atas batas upload 12 MB
        )
    except ImportError:
        print("[MAIN] ⚠️ waitress gak keinstall, fallback ke Flask dev server")
        print("[MAIN] Install: pip install waitress")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
