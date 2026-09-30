import telebot
from telebot import types
import random
import time
import threading
import io
import os
import urllib.parse
import hashlib
import shutil
from datetime import datetime, timezone, timedelta

# ==== TAMBAHAN UNTUK APK API ====
from flask import Flask, request, jsonify
from flask_cors import CORS

# =====================================================================================
#  OFFICIAL PAKEL MLBBSTORE - MASTER ULTIMATE v10 (VOUCHER MANAGEMENT + AUTO-BC)
#  ⚠️ JANGAN SHARE FILE INI - TOKEN SENSITIVE
# =====================================================================================

# Ambil token dari Railway env var (aman, gak keliatan di file)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    print("[FATAL] TELEGRAM_TOKEN belum di-set di Railway Variables!")
    print("[INFO] Tambahkan TELEGRAM_TOKEN di Railway → Variables")
    exit(1)
print(f"[INFO] Bot token loaded: {TOKEN[:15]}...")
bot = telebot.TeleBot(TOKEN)

try:
    bot.remove_webhook()
except Exception:
    pass

# ==== SETUP FLASK API (buat APK) ====
app = Flask(__name__)
CORS(app)  # Biar APK bisa akses

ADMIN_USERNAME = "@PakelMlbbOfficial"
ADMIN_LINK = "https://t.me/PakelMlbbOfficial"
CHANNEL_TESTI_LINK = "https://t.me/PakelMlbb/368"
ADMIN_TELEGRAM_ID = 8772023108

GROUP_CHAT_ID = "@PakelMlbb"
GROUP_TOPIC_ID = 368

GROUP_PAY_ID = "@Paysukses"
GROUP_PAY_TOPIC_ID = 5

INFO_DANA = "085188371150"
INFO_GOPAY = "085188371150"
INFO_SAWERIA = "https://saweria.co/PakelMlbb"

# =====================================================================================
#  KONFIGURASI QRIS
# =====================================================================================
QRIS_IMAGE_URL = "https://i.ibb.co.com/JRXZvJkR/IMG-20260927-110643-128.jpg"

WIB = timezone(timedelta(hours=7))

TRANSAKSI_TIMEOUT_DETIK = 900
PAYMENT_REMINDER_SEBELUM_DETIK = 300
ARCHIVE_UMUR_HARI = 30
AUTO_BACKUP_INTERVAL_DETIK = 3600  # FIX v11: backup tiap 1 jam

# =====================================================================================
#  KONFIGURASI FITUR
# =====================================================================================
ANTISPAM_CMD_COOLDOWN = 2
ANTISPAM_CALLBACK_COOLDOWN = 1
ANTISPAM_PHOTO_COOLDOWN = 5
ANTISPAM_VOUCHER_COOLDOWN = 30
MAX_SUSPICIOUS_BEFORE_BAN = 3

LUCKY_DRAW_COOLDOWN_JAM = 24
LUCKY_DRAW_HADIAH = [
    ("🪙 +5 Poin",      "poin",  5,  30),
    ("🪙 +10 Poin",     "poin",  10, 25),
    ("🪙 +15 Poin",     "poin",  15, 20),
    ("🪙 +25 Poin",     "poin",  25, 12),
    ("🪙 +50 Poin",     "poin",  50, 7),
    ("🎁 Diskon 5%",    "diskon", 5,  3),
    ("🎁 Diskon 10%",   "diskon", 10, 2),
    ("💎 Paket Semi-Safe GRATIS", "paket_gratis", 0, 1),
]

TIER_BRONZE   = ("🥉 Bronze",   0,  4,   1.0, 0)
TIER_SILVER   = ("🥈 Silver",   5,  14,  1.2, 5)
TIER_GOLD     = ("🥇 Gold",     15, 29,  1.5, 10)
TIER_PLATINUM = ("💎 Platinum", 30, 9999, 2.0, 15)

STOCK_THRESHOLD_RESTOCK = 20
STOCK_RESTOCK_MIN = 150
STOCK_RESTOCK_MAX = 250
STOCK_FAKE_REDUCE_MIN = 1
STOCK_FAKE_REDUCE_MAX = 3

F_USERS = "users.txt"
F_BANNED = "banned.txt"
F_COUPONS = "coupons.txt"
F_POINTS = "points.txt"
F_POINTLOG = "point_log.txt"
F_REVIEWS = "reviews.txt"
F_ORDERS = "orders.txt"
F_ARCHIVE = "history_archive.txt"
F_REFERRALS = "referrals.txt"
F_PROOFS = "used_proofs.txt"
F_ADMINS = "admins.txt"
F_ERRORLOG = "error.log"
F_STOCKS = "stocks.txt"
F_LASTSEEN = "last_seen.txt"
F_SPINLOG = "spin_log.txt"
F_VOUCHERS = "vouchers.txt"
F_USER_VOUCHER = "user_voucher.txt"
F_SUSPICIOUS = "suspicious_log.txt"
F_SUSPICIOUS_COUNT = "suspicious_count.txt"
F_CHECKSUM = "checksum.txt"
F_LASTTIER = "last_tier.txt"
F_FLASHSALE = "flashsale.txt"
FOLDER_PROOFS = "proofs"

# FIX v15: AI CS Groq — DIMATIIN
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_MODEL = "llama-3.3-70b-versatile"
AI_ENABLED = False   # ← INI YANG BIKIN AI MATI

# FAQ Auto-Reply Database
FAQ_RESPONSES = {
    "aman gak": "🛡️ <b>100% AMAN KAK!</b>\n\nScript kita udah pake enkripsi <i>high-tier anti-detect</i> paling stabil se-Indonesia. Aman buat main di Ranked Mythic sekalipun!\n\n💎 Proses cepat & amanah.",
    "aman ga": "🛡️ <b>100% AMAN KAK!</b>\n\nScript kita udah pake enkripsi <i>high-tier anti-detect</i> paling stabil se-Indonesia. Aman buat main di Ranked Mythic sekalipun!\n\n💎 Proses cepat & amanah.",
    "bisa ban ga": "🛡️ <b>AMAN DARI BAN KAK!</b>\n\nKita udah pake anti-cheat bypass paling canggih. Ratusan user udah buktiin aman!\n\n💎 Garansi aman atau uang kembali.",
    "cara pakai": "📖 <b>CARA PAKAI SCRIPT:</b>\n\n1. Order paket pilihan\n2. Bayar & kirim bukti\n3. Admin ACC\n4. Dapet link/file script\n5. Ikuti tutorial dari admin\n\n📌 Ada pertanyaan lain? Chat admin ya!",
    "cara order": "🛒 <b>CARA ORDER:</b>\n\n1. Ketik /katalog\n2. Pilih paket\n3. Pilih metode bayar (Transfer/QRIS/Poin)\n4. Bayar sesuai nominal\n5. Kirim bukti transfer ke bot ini\n6. Tunggu ACC admin\n\n⚡ Proses cepat & amanah!",
    "refund": "💰 <b>KEBIJAKAN REFUND:</b>\n\nRefund hanya berlaku jika:\n• Script tidak berfungsi\n• Kesalahan dari pihak toko\n\nTidak berlaku jika:\n• User salah pakai\n• Akun kena ban karena kelalaian user\n\n📩 Chat admin buat info lanjut.",
    "admin": f"💬 <b>HUBUNGI ADMIN:</b>\n\n📌 {ADMIN_USERNAME}\n\nAdmin siap bantu 24/7 (jam 07:00 - 00:00 WIB).",
    "harga": "💰 <b>HARGA PAKET:</b>\n\nPaket mulai dari <b>Rp 75.000</b>!\n\nLihat katalog lengkap: /katalog\n\n🎁 Bonus: Free Server Lag Panel & Drone View!",
    "promo": "🎁 <b>PROMO HARI INI:</b>\n\n• Promo Member Baru: Diskon Rp 10.000\n• Diskon Tier (5% - 15%)\n• Voucher Manual\n• Flash Sale\n\nCek /promo buat detail!",
    "poin": "🪙 <b>POIN LOYALITAS:</b>\n\nDapet poin gratis tiap transaksi sukses!\nBisa ditukar buat bayar paket.\n\nCek poin kamu: /poin\nLihat paket: /katalog",
    "testimoni": "🌟 <b>TESTIMONI REAL:</b>\n\nCek channel testi kita:\nhttps://t.me/PakelMlbb/368\n\n💎 Ratusan user udah buktiin!",
    "trusted ga": "✅ <b>100% TRUSTED KAK!</b>\n\nToko udah jalan lama, ratusan transaksi sukses, banyak testimoni asli. Aman & amanah!\n\nCek testimoni: https://t.me/PakelMlbb/368",
}

processing_lock = set()
pending_flow = {}
last_command_time = {}
last_callback_time = {}
last_photo_time = {}
last_voucher_time = {}

# FIX v11: Thread Locks untuk anti race-condition
voucher_lock = threading.Lock()
user_voucher_lock = threading.Lock()
coupon_lock = threading.Lock()
points_lock = threading.Lock()
orders_lock = threading.Lock()
stocks_lock = threading.Lock()
referrals_lock = threading.Lock()
users_lock = threading.Lock()

# =====================================================================================
#  MASTER KATALOG PAKET
# =====================================================================================
MASTER_PAKET = {
    'buy_natural': (
        "Natural Balance (30 Hari)", 120000, "Rp 120.000", 45,
        "🎯 <b>Fungsi:</b> Dirancang khusus untuk pemain yang mengutamakan keamanan akun. "
        "Pengaturan damage dapat disesuaikan secara mandiri (seperti 2 hit yang tidak mencolok), "
        "sehingga performa tetap optimal namun senyap."
    ),
    'buy_light': (
        "Light VIP + Drone (30 Hari)", 95000, "Rp 95.000", 35,
        "🎯 <b>Fungsi:</b> Pilihan ekonomis untuk pemakaian bulanan. Kombinasi pas antara damage "
        "yang disetel wajar agar tidak terlihat brutal, ditambah pandangan map yang lebih luas "
        "untuk membaca pergerakan lawan."
    ),
    'buy_semisafe': (
        "Semi-Safe 14 Hari", 75000, "Rp 75.000", 25,
        "🎯 <b>Fungsi:</b> Paket harian yang sangat terjangkau. Menghadirkan setelan damage "
        "fleksibel yang terkontrol serta kestabilan koneksi yang terjaga selama dua minggu penuh."
    ),
    'buy_lifetimesafe': (
        "Lifetime Safe Permanent", 200000, "Rp 200.000", 75,
        "🎯 <b>Fungsi:</b> Solusi hemat jangka panjang tanpa biaya langganan bulanan. Memberikan "
        "akses selamanya dengan fitur damage fleksibel yang aman dan stabil digunakan sewaktu-waktu."
    ),
    'buy_sultan': (
        "Sultan One Hit 100% (30 Hari)", 150000, "Rp 150.000", 55,
        "🎯 <b>Fungsi:</b> Damage tembus batas, instant kill musuh dalam sekali hit, bypass "
        "anti-cheat paling aman, khusus untuk player serius yang ingin dominasi mutlak di setiap match."
    ),
    'buy_pro': (
        "VIP Pro One Hit 80% (30 Hari)", 100000, "Rp 100.000", 40,
        "🎯 <b>Fungsi:</b> Udah dapet damage sakit, semua skin kebuka, pandangan luas, lengkap "
        "jadi satu! Paling dicari para top global untuk push rank tanpa hambatan."
    ),
    'buy_semiprivate': (
        "Semi-Private 14 Hari", 75000, "Rp 75.000", 25,
        "🎯 <b>Fungsi:</b> Performanya stabil, anti patah-patah dijamin lancar jaya buat bantai "
        "musuh seharian tanpa khawatir lag atau disconnect mendadak."
    ),
    'buy_permanent': (
        "Permanent Legend (Lifetime)", 250000, "Rp 250.000", 90,
        "🎯 <b>Fungsi:</b> Sekali bayar, nikmati update script seumur hidup tanpa perlu perpanjang "
        "langganan tiap bulan. Auto untung buat jangka panjang dan paling worth it!"
    ),
}

# =====================================================================================
#  BAGIAN 2: KEAMANAN, ERROR LOGGING & MULTI-ADMIN
# =====================================================================================

def log_error(context, e):
    try:
        with open(F_ERRORLOG, "a") as f:
            f.write(f"{datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S')} | {context} | {e}\n")
    except Exception:
        pass

def is_banned(chat_id):
    try:
        with open(F_BANNED, "r") as f:
            banned = {line.strip() for line in f if line.strip()}
        return str(chat_id) in banned
    except FileNotFoundError:
        return False

def ban_user(chat_id):
    try:
        if is_banned(chat_id):
            return
        with open(F_BANNED, "a") as f:
            f.write(f"{chat_id}\n")
    except Exception as e:
        log_error("ban_user", e)

def unban_user(chat_id):
    try:
        with open(F_BANNED, "r") as f:
            rows = [line.strip() for line in f if line.strip() and line.strip() != str(chat_id)]
        with open(F_BANNED, "w") as f:
            f.write("\n".join(rows) + ("\n" if rows else ""))
    except FileNotFoundError:
        pass
    except Exception as e:
        log_error("unban_user", e)

def get_admin_role(chat_id):
    if int(chat_id) == int(ADMIN_TELEGRAM_ID):
        return "super"
    try:
        with open(F_ADMINS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2 and parts[0] == str(chat_id):
                    return parts[1]
    except FileNotFoundError:
        pass
    return None

def is_any_admin(chat_id):
    return get_admin_role(chat_id) is not None

def is_super_admin(chat_id):
    return get_admin_role(chat_id) == "super"

def is_proof_used(proof_unique_id):
    try:
        with open(F_PROOFS, "r") as f:
            used = {line.strip() for line in f if line.strip()}
        return proof_unique_id in used
    except FileNotFoundError:
        return False

# FIX v12: Tier Upgrade Notif
def get_user_last_tier(chat_id):
    try:
        if not os.path.exists(F_LASTTIER):
            return None
        with open(F_LASTTIER, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2 and parts[0] == str(chat_id):
                    return parts[1]
    except Exception:
        pass
    return None

def set_user_last_tier(chat_id, tier_label):
    try:
        rows = []
        updated = False
        chat_id_str = str(chat_id)
        if os.path.exists(F_LASTTIER):
            with open(F_LASTTIER, "r") as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 2:
                        if parts[0] == chat_id_str:
                            rows.append(f"{chat_id_str}|{tier_label}\n")
                            updated = True
                        else:
                            rows.append(line.strip() + "\n")
        if not updated:
            rows.append(f"{chat_id_str}|{tier_label}\n")
        with open(F_LASTTIER, "w") as f:
            f.writelines(rows)
    except Exception as e:
        log_error("set_user_last_tier", e)

def check_tier_upgrade(chat_id):
    try:
        current_tier, _, diskon = get_user_tier(chat_id)
        last_tier = get_user_last_tier(chat_id)
        if last_tier is None:
            set_user_last_tier(chat_id, current_tier)
            return
        if current_tier != last_tier:
            set_user_last_tier(chat_id, current_tier)
            try:
                bot.send_message(
                    chat_id,
                    f"🎉 <b>TIER UPGRADE!</b>\n\n"
                    f"Selamat Kak! Tier kamu naik dari:\n"
                    f"<b>{last_tier}</b> → <b>{current_tier}</b>\n\n"
                    f"🎁 Bonus: Diskon <b>{diskon}%</b> otomatis aktif!\n"
                    f"🪙 Bonus poin per transaksi juga naik!\n\n"
                    "Terima kasih sudah jadi pelanggan setia! 🙏",
                    parse_mode="HTML"
                )
            except Exception:
                pass
    except Exception as e:
        log_error("check_tier_upgrade", e)

# FIX v12: Notif Order Baru ke Admin
def notify_admin_new_order(chat_id, user, paket, harga, resi, payment_method):
    try:
        now_str = datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S WIB')
        notif_text = (
            f"🛒 <b>ORDER BARU MASUK!</b>\n\n"
            f"👤 User: @{user.username or user.first_name}\n"
            f"🆔 ID: <code>{chat_id}</code>\n"
            f"📦 Paket: <b>{paket}</b>\n"
            f"💵 Harga: <b>{harga}</b>\n"
            f"💳 Metode: <b>{payment_method}</b>\n"
            f"🔑 Resi: <code>{resi}</code>\n"
            f"⏱️ Waktu: {now_str}\n\n"
            "💡 <i>User tinggal bayar & kirim bukti transfer.</i>"
        )
        bot.send_message(ADMIN_TELEGRAM_ID, notif_text, parse_mode="HTML")
    except Exception as e:
        log_error("notify_admin_new_order", e)


# FIX v12: Auto Cleanup
def cleanup_old_logs():
    try:
        now_epoch = int(time.time())

        # 1. Hapus marker reminder lama (>7 hari)
        for fname in os.listdir("."):
            if fname.startswith(".reminded_"):
                if os.path.isfile(fname):
                    file_age = now_epoch - int(os.path.getmtime(fname))
                    if file_age > 7 * 86400:
                        try:
                            os.remove(fname)
                        except Exception:
                            pass

        # 2. Hapus pending_review lama (>7 hari)
        for fname in os.listdir("."):
            if fname.startswith("pending_review_"):
                if os.path.isfile(fname):
                    file_age = now_epoch - int(os.path.getmtime(fname))
                    if file_age > 7 * 86400:
                        try:
                            os.remove(fname)
                        except Exception:
                            pass

        # 3. Hapus backup lama (>50 file di backup_data)
        backup_dir = "backup_data"
        if os.path.exists(backup_dir) and os.path.isdir(backup_dir):
            all_files = []
            for fname in os.listdir(backup_dir):
                fpath = os.path.join(backup_dir, fname)
                if os.path.isfile(fpath):
                    all_files.append((os.path.getmtime(fpath), fpath))
            all_files.sort()
            if len(all_files) > 50:
                for _, fpath in all_files[:-50]:
                    try:
                        os.remove(fpath)
                    except Exception:
                        pass

        # 4. Hapus point_log lama (>90 hari)
        if os.path.exists(F_POINTLOG):
            try:
                with open(F_POINTLOG, "r") as f:
                    lines = f.readlines()
                new_lines = []
                for line in lines:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        try:
                            log_time = datetime.strptime(parts[1], '%d-%m-%Y %H:%M:%S')
                            log_epoch = int(log_time.replace(tzinfo=WIB).timestamp())
                            if now_epoch - log_epoch < 90 * 86400:
                                new_lines.append(line)
                        except ValueError:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                if len(new_lines) < len(lines):
                    with open(F_POINTLOG, "w") as f:
                        f.writelines(new_lines)
            except Exception:
                pass
    except Exception as e:
        log_error("cleanup_old_logs", e)


# FIX v12: Flash Sale
def get_active_flashsale():
    try:
        if not os.path.exists(F_FLASHSALE):
            return 0, 0
        with open(F_FLASHSALE, "r") as f:
            line = f.read().strip()
        if not line:
            return 0, 0
        parts = line.split('|')
        if len(parts) != 2:
            return 0, 0
        diskon = int(parts[0])
        expired_ts = int(parts[1])
        now_ts = int(time.time())
        if now_ts >= expired_ts:
            return 0, 0
        return diskon, expired_ts - now_ts
    except Exception:
        return 0, 0

def set_flashsale(diskon, durasi_jam):
    try:
        expired_ts = int(time.time()) + (durasi_jam * 3600)
        with open(F_FLASHSALE, "w") as f:
            f.write(f"{diskon}|{expired_ts}")
    except Exception as e:
        log_error("set_flashsale", e)

def clear_flashsale():
    try:
        if os.path.exists(F_FLASHSALE):
            os.remove(F_FLASHSALE)
    except Exception:
        pass

def broadcast_flashsale(diskon, durasi_jam):
    try:
        with open(F_USERS, "r") as f:
            users = [line.strip() for line in f.read().splitlines() if line.strip()]
    except FileNotFoundError:
        return

    bc_text = (
        "⚡ <b>FLASH SALE MENDADAK!</b> ⚡\n\n"
        f"🔥 Diskon <b>{diskon}%</b> untuk SEMUA PAKET!\n"
        f"⏱️ Hanya berlaku <b>{durasi_jam} jam</b> ke depan!\n\n"
        "⚡ <i>Buruan checkout sebelum diskon berakhir!</i>\n\n"
        f"🛒 Checkout sekarang: @{bot.get_me().username}"
    )

    success = 0
    for chat_id in set(users):
        try:
            bot.send_message(chat_id, bc_text, parse_mode="HTML",
                             disable_web_page_preview=True)
            success += 1
            time.sleep(0.05)
        except Exception:
            pass

    try:
        bot.send_message(ADMIN_TELEGRAM_ID,
                         f"📢 Broadcast Flash Sale selesai. Sukses: {success} user",
                         parse_mode="HTML")
    except Exception:
        pass


# FIX v13: Notif User Baru Join
def notify_admin_new_user(chat_id, user):
    """Kirim notif ke admin kalau ada user baru."""
    try:
        now_str = datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S WIB')
        # Hitung total user
        total_users = 0
        try:
            with open(F_USERS, "r") as f:
                total_users = len([ln for ln in f if ln.strip()])
        except FileNotFoundError:
            pass

        username_display = f"@{user.username}" if user.username else "(no username)"
        nama = user.first_name + (f" {user.last_name}" if user.last_name else "")

        bot.send_message(
            ADMIN_TELEGRAM_ID,
            f"🆕 <b>USER BARU JOIN!</b>\n\n"
            f"👤 Nama: <b>{nama}</b>\n"
            f"🔗 Username: {username_display}\n"
            f"🆔 ID: <code>{chat_id}</code>\n"
            f"⏱️ Waktu: {now_str}\n\n"
            f"👥 Total User Sekarang: <b>{total_users}</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        log_error("notify_admin_new_user", e)


# FIX v13: Notif Order Hampir Expired ke Admin
def notify_admin_order_will_expire():
    """Cek order pending yang sisa < 5 menit, kirim notif ke admin (1x per order)."""
    try:
        now_epoch = int(datetime.now(WIB).timestamp())
        reminded_file = "admin_expired_reminded.txt"

        # Baca log remind
        reminded = set()
        if os.path.exists(reminded_file):
            with open(reminded_file, "r") as f:
                reminded = {ln.strip() for ln in f if ln.strip()}

        new_reminded = []

        for parts in _read_all_orders():
            if len(parts) < 8:
                continue
            chat_id = parts[0]
            resi = parts[6]
            status = parts[7]
            epoch = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else now_epoch

            if status != "PENDING":
                continue

            sisa = TRANSAKSI_TIMEOUT_DETIK - (now_epoch - epoch)
            # Notif kalau sisa antara 4-5 menit
            if 240 <= sisa <= 300:
                if resi in reminded:
                    continue
                try:
                    user_info = bot.get_chat(int(chat_id))
                    nama = user_info.first_name
                    username = f"@{user_info.username}" if user_info.username else "-"
                except Exception:
                    nama = "User"
                    username = "-"

                try:
                    bot.send_message(
                        ADMIN_TELEGRAM_ID,
                        f"⏰ <b>ORDER AKAN EXPIRED!</b>\n\n"
                        f"👤 User: <b>{nama}</b> ({username})\n"
                        f"🆔 ID: <code>{chat_id}</code>\n"
                        f"🔑 Resi: <code>{resi}</code>\n"
                        f"⏱️ Sisa Waktu: <b>~{int(sisa//60)} menit lagi</b>\n\n"
                        f"💡 <i>Follow up user buat selesaikan pembayaran!</i>",
                        parse_mode="HTML"
                    )
                    new_reminded.append(resi)
                except Exception as e:
                    log_error("notify_admin_order_will_expire_send", e)

        # Simpan log
        if new_reminded:
            with open(reminded_file, "a") as f:
                for r in new_reminded:
                    f.write(f"{r}\n")

        # Cleanup log lama (kalau > 500 entri)
        try:
            if os.path.exists(reminded_file):
                with open(reminded_file, "r") as f:
                    lines = [ln.strip() for ln in f if ln.strip()]
                if len(lines) > 500:
                    with open(reminded_file, "w") as f:
                        f.write("\n".join(lines[-500:]) + "\n")
        except Exception:
            pass

    except Exception as e:
        log_error("notify_admin_order_will_expire", e)


# FIX v14: Reminder Voucher Hampir Expired
def remind_expiring_user_vouchers():
    """Cek voucher user yang hampir expired & kirim reminder."""
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return

        # Baca semua voucher aktif user
        user_vouchers = {}
        try:
            with open(F_USER_VOUCHER, "r") as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 3 and parts[1].startswith("VOUCHER_"):
                        chat_id = parts[0]
                        kode = parts[1].replace("VOUCHER_", "")
                        try:
                            diskon = int(parts[2])
                        except ValueError:
                            diskon = 0
                        if chat_id not in user_vouchers:
                            user_vouchers[chat_id] = []
                        user_vouchers[chat_id].append({
                            'kode': kode,
                            'diskon': diskon
                        })
        except Exception:
            return

        # Cek voucher publik yang user redeem
        all_vouchers = _read_all_vouchers()
        now_ts = int(time.time())
        reminded_file = "voucher_reminded.txt"

        # Baca log remind
        reminded = set()
        if os.path.exists(reminded_file):
            with open(reminded_file, "r") as f:
                reminded = {ln.strip() for ln in f if ln.strip()}

        new_reminded = []

        for chat_id, vouchers in user_vouchers.items():
            for v in vouchers:
                kode = v['kode']
                diskon = v['diskon']

                # Cari info expired voucher publik
                if kode in all_vouchers:
                    exp_ts = all_vouchers[kode]['expired']
                    if exp_ts > 0:
                        sisa_detik = exp_ts - now_ts
                        # Remind kalau sisa < 1 jam & > 0
                        if 0 < sisa_detik <= 3600:
                            key = f"{chat_id}|{kode}"
                            if key in reminded:
                                continue
                            try:
                                sisa_menit = int(sisa_detik // 60)
                                bot.send_message(
                                    chat_id,
                                    f"⏰ <b>VOUCHER KAMU HAMPIR EXPIRED!</b>\n\n"
                                    f"🎫 Kode: <code>{kode}</code>\n"
                                    f"💵 Diskon: <b>Rp {diskon:,}</b>\n"
                                    f"⏱️ Sisa Waktu: <b>{sisa_menit} menit lagi!</b>\n\n"
                                    f"⚡ Buruan checkout paket sebelum voucher hangus!\n"
                                    f"🛒 Langsung sikat ke /katalog ya Kak!",
                                    parse_mode="HTML"
                                )
                                new_reminded.append(key)
                            except Exception:
                                pass

        # Simpan log remind
        if new_reminded:
            with open(reminded_file, "a") as f:
                for k in new_reminded:
                    f.write(f"{k}\n")
    except Exception as e:
        log_error("remind_expiring_user_vouchers", e)


# FIX v14: Auto-Notif Pendapatan Per 4 Jam
def notify_admin_income_update():
    """Kirim update pendapatan hari ini ke admin."""
    try:
        today_str = datetime.now(WIB).strftime('%d-%m-%Y')
        sukses = 0
        total_pendapatan = 0
        poin_ditukar = 0
        pending = 0

        for parts in _read_all_orders():
            if len(parts) < 8:
                continue
            if parts[1] != today_str:
                continue
            status = parts[7]
            pay = parts[9] if len(parts) > 9 else "TRANSFER"
            harga = parts[5]

            if status == "BERHASIL":
                sukses += 1
                if pay == "POIN":
                    poin_ditukar += int(parts[10]) if len(parts) > 10 and parts[10].isdigit() else 0
                else:
                    total_pendapatan += int(''.join(ch for ch in harga if ch.isdigit()) or 0)
            elif status == "PENDING":
                pending += 1

        now_str = datetime.now(WIB).strftime('%H:%M:%S WIB')

        text = (
            f"💰 <b>UPDATE PENDAPATAN HARI INI</b>\n"
            f"🕐 Jam: <b>{now_str}</b>\n"
            f"🗓️ Tanggal: <b>{today_str}</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Transaksi Sukses : <b>{sukses}</b>\n"
            f"⏳ Masih Pending    : <b>{pending}</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"💵 <b>Total Pendapatan</b> : <b>Rp {total_pendapatan:,}</b>\n"
            f"🪙 Poin Ditukar     : <b>{poin_ditukar} Poin</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <i>Cek detail: /stats</i>"
        )
        bot.send_message(ADMIN_TELEGRAM_ID, text, parse_mode="HTML")
    except Exception as e:
        log_error("notify_admin_income_update", e)


# FIX v14: Auto-Simpan Bukti Transfer ke Folder
def save_proof_to_folder(chat_id_buyer, resi_code, file_id, user_caption=""):
    """Simpan bukti transfer ke folder proofs/."""
    try:
        # Buat folder kalau belum ada
        os.makedirs(FOLDER_PROOFS, exist_ok=True)

        # Nama file: resi_user.jpg
        safe_resi = resi_code.replace("/", "_").replace("\\", "_").strip()
        fname = f"{FOLDER_PROOFS}/{safe_resi}_{chat_id_buyer}.jpg"

        # Download file dari Telegram
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open(fname, "wb") as f:
            f.write(downloaded)

        # Simpan juga metadata ke file .txt
        meta_fname = f"{FOLDER_PROOFS}/{safe_resi}_{chat_id_buyer}.txt"
        with open(meta_fname, "w", encoding="utf-8") as f:
            f.write(f"Resi: {resi_code}\n")
            f.write(f"Chat ID: {chat_id_buyer}\n")
            f.write(f"Caption: {user_caption}\n")
            f.write(f"Waktu: {datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S WIB')}\n")
    except Exception as e:
        log_error("save_proof_to_folder", e)


# FIX v15: AI CS Groq — Beneran Mikir, Bukan Template
AI_CS_SYSTEM_PROMPT = """Kamu adalah CS (Customer Service) dari Official Pakel MlbbStore.

KARAKTER KAMU:
- Ramah, santai, sopan, sedikit humoris
- Panggil user "Kak" atau "Bro" tergantung gaya user
- Pake emoji secukupnya (jangan lebay)
- Gaya bahasa: gaul tapi sopan (kayak CS profesional)

TUGAS UTAMA: Melayani pertanyaan seputar toko ini HANYA.

YANG BOLEH DIJAWAB:
1. Paket script MLBB & harganya
2. Cara order & pembayaran (Transfer/QRIS/Poin)
3. Keamanan script (anti-detect, anti-ban)
4. Proses verifikasi & pengiriman script
5. Kebijakan refund & garansi
6. Testimoni & trust toko
7. Fitur bonus (Server Lag Panel, Drone View)
8. Cara pakai script
9. Sistem poin loyalitas & tier
10. Promo & diskon yang aktif
11. Ngobrol santai / sapaan (halo, p, test, dll)

YANG HARUS DITOLAK (halus):
- Politik, agama, SARA, gosip
- Curhat pribadi user
- Pertanyaan soal toko lain
- Info internal toko (file, database, admin)
- Cara kerja bot / source code
- Chat_id atau identitas admin

ATURAN KETAT:
- Jawab natural kayak manusia, JANGAN pakai template kaku
- Kalau user nanya di luar topik toko -> tolak halus, arahin balik
- Kalau user kasar -> tetap sopan, jangan balas kasar
- Kalau user spam -> minta sabar
- Kalau user ngajak ngobrol -> boleh ngobrol santai, tapi arahin ke toko
- JANGAN bocorin info internal apapun
- JANGAN janjiin hal yang ga ada di toko
- JANGAN bilang "ketik /start" atau "ketik /katalog" -> arahin natural aja
- Kalau ga tau jawabannya -> bilang jujur + arahin ke admin
- Jawaban max 3-5 kalimat

INFO TOKO:
- Nama: Official Pakel MlbbStore
- Admin: @PakelMlbbOfficial
- Channel Testi: https://t.me/PakelMlbb/368
- Paket termurah: Rp 75.000 (Semi-Safe 14 Hari)
- Paket termahal: Rp 250.000 (Permanent Legend Lifetime)
- Bonus gratis: Server Lag Panel + Drone View X10
- Metode bayar: Transfer DANA/GoPay, QRIS, Poin Loyalitas
- Waktu verifikasi: max 5-10 menit
- Sistem poin: tiap transaksi dapet poin, bisa ditukar paket"""


def ai_cs_reply(chat_id, user_message, user_name="Kak"):
    """Panggil Groq API buat jawab natural, BUKAN template."""
    if not AI_ENABLED:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": AI_CS_SYSTEM_PROMPT},
                {"role": "user", "content": f"User ({user_name}): {user_message}"}
            ],
            temperature=0.8,
            max_tokens=400,
        )
        if completion and completion.choices:
            return completion.choices[0].message.content.strip()
        return None
    except Exception as e:
        log_error("ai_cs_reply", e)
        return None


def mark_proof_used(proof_unique_id):
    try:
        with open(F_PROOFS, "a") as f:
            f.write(f"{proof_unique_id}\n")
    except Exception as e:
        log_error("mark_proof_used", e)


# =====================================================================================
#  FIX v11: SECURITY LAYER — SUSPICIOUS LOG + AUTO BAN + CHECKSUM + AUTO BACKUP
# =====================================================================================

def log_suspicious(chat_id, username, tipe, detail):
    try:
        now_str = datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S')
        with open(F_SUSPICIOUS, "a") as f:
            f.write(f"{now_str} | {chat_id} | @{username or '-'} | {tipe} | {detail}\n")
    except Exception:
        pass
    try:
        counters = {}
        if os.path.exists(F_SUSPICIOUS_COUNT):
            with open(F_SUSPICIOUS_COUNT, "r") as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 2:
                        try:
                            counters[parts[0]] = int(parts[1])
                        except ValueError:
                            pass
        cid = str(chat_id)
        counters[cid] = counters.get(cid, 0) + 1
        with open(F_SUSPICIOUS_COUNT, "w") as f:
            for k, v in counters.items():
                f.write(f"{k}|{v}\n")
        if counters[cid] >= MAX_SUSPICIOUS_BEFORE_BAN:
            ban_user(cid)
            try:
                bot.send_message(
                    ADMIN_TELEGRAM_ID,
                    f"🚨 <b>AUTO-BAN AKTIVITAS MENCURIGAKAN</b>\n\n"
                    f"👤 User: @{username or '-'} (ID: <code>{chat_id}</code>)\n"
                    f"📌 Tipe: {tipe}\n"
                    f"📋 Detail: {detail}\n"
                    f"🔢 Total: {counters[cid]}\n\n"
                    f"⚠️ User otomatis di-BANNED.",
                    parse_mode="HTML"
                )
            except Exception:
                pass
    except Exception as e:
        log_error("log_suspicious", e)


def reset_suspicious(chat_id):
    try:
        counters = {}
        if os.path.exists(F_SUSPICIOUS_COUNT):
            with open(F_SUSPICIOUS_COUNT, "r") as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 2:
                        try:
                            counters[parts[0]] = int(parts[1])
                        except ValueError:
                            pass
        counters.pop(str(chat_id), None)
        with open(F_SUSPICIOUS_COUNT, "w") as f:
            for k, v in counters.items():
                f.write(f"{k}|{v}\n")
    except Exception as e:
        log_error("reset_suspicious", e)


def is_spam_voucher(chat_id):
    now = time.time()
    last = last_voucher_time.get(chat_id, 0)
    if now - last < ANTISPAM_VOUCHER_COOLDOWN:
        return True
    last_voucher_time[chat_id] = now
    return False


def compute_checksum(filepath):
    try:
        if not os.path.exists(filepath):
            return ""
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except Exception:
        return ""


def verify_checksums():
    critical_files = [F_ORDERS, F_POINTS, F_VOUCHERS, F_STOCKS]
    try:
        with open(F_CHECKSUM, "w") as f:
            for cf in critical_files:
                f.write(f"{cf}|{compute_checksum(cf)}\n")
    except Exception as e:
        log_error("verify_checksums", e)


def auto_backup_all_files():
    try:
        backup_dir = "backup_data"
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now(WIB).strftime('%Y%m%d_%H%M%S')
        files_to_backup = [F_ORDERS, F_USERS, F_POINTS, F_VOUCHERS, F_USER_VOUCHER, F_STOCKS, F_REFERRALS, F_COUPONS]
        for fname in files_to_backup:
            if os.path.exists(fname):
                shutil.copy2(fname, os.path.join(backup_dir, f"{timestamp}_{fname}"))
        all_backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.txt')])
        if len(all_backups) > 50:
            for old in all_backups[:-50]:
                try:
                    os.remove(os.path.join(backup_dir, old))
                except Exception:
                    pass
    except Exception as e:
        log_error("auto_backup_all_files", e)

# =====================================================================================
#  FITUR: ANTI-SPAM RATE LIMITER
# =====================================================================================

def is_spam_command(chat_id):
    now = time.time()
    last = last_command_time.get(chat_id, 0)
    if now - last < ANTISPAM_CMD_COOLDOWN:
        return True
    last_command_time[chat_id] = now
    return False

def is_spam_callback(chat_id):
    now = time.time()
    last = last_callback_time.get(chat_id, 0)
    if now - last < ANTISPAM_CALLBACK_COOLDOWN:
        return True
    last_callback_time[chat_id] = now
    return False

def is_spam_photo(chat_id):
    now = time.time()
    last = last_photo_time.get(chat_id, 0)
    if now - last < ANTISPAM_PHOTO_COOLDOWN:
        return True
    last_photo_time[chat_id] = now
    return False

# =====================================================================================
#  FITUR: SISTEM STOK FAKE + AUTO RESTOCK
# =====================================================================================

def init_stock_if_empty():
    if os.path.exists(F_STOCKS):
        return
    try:
        with open(F_STOCKS, "w") as f:
            for code in MASTER_PAKET.keys():
                harga = MASTER_PAKET[code][1]
                if harga < 100000:
                    stok_awal = random.randint(150, 250)
                elif harga < 180000:
                    stok_awal = random.randint(80, 150)
                else:
                    stok_awal = random.randint(30, 80)
                f.write(f"{code}|{stok_awal}|{int(time.time())}\n")
    except Exception as e:
        log_error("init_stock_if_empty", e)

def _read_all_stocks():
    stocks = {}
    try:
        with open(F_STOCKS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    try:
                        stocks[parts[0]] = int(parts[1])
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass
    return stocks

def _write_all_stocks(stocks):
    try:
        with open(F_STOCKS, "w") as f:
            now_ts = int(time.time())
            for code, stok in stocks.items():
                f.write(f"{code}|{stok}|{now_ts}\n")
    except Exception as e:
        log_error("_write_all_stocks", e)

def get_stock(paket_code):
    stocks = _read_all_stocks()
    return stocks.get(paket_code, 100)

def set_stock(paket_code, angka_baru):
    stocks = _read_all_stocks()
    stocks[paket_code] = max(0, int(angka_baru))
    _write_all_stocks(stocks)

def reduce_stock_specific(paket_code, jumlah=1):
    try:
        stocks = _read_all_stocks()
        if paket_code in stocks:
            stocks[paket_code] = max(0, stocks[paket_code] - jumlah)
            _write_all_stocks(stocks)
    except Exception as e:
        log_error("reduce_stock_specific", e)

def reduce_stock_random_all():
    try:
        stocks = _read_all_stocks()
        if not stocks:
            init_stock_if_empty()
            stocks = _read_all_stocks()
        for code in stocks.keys():
            turun = random.randint(STOCK_FAKE_REDUCE_MIN, STOCK_FAKE_REDUCE_MAX)
            stocks[code] = max(0, stocks[code] - turun)
        _write_all_stocks(stocks)
    except Exception as e:
        log_error("reduce_stock_random_all", e)

def auto_restock_if_low():
    try:
        stocks = _read_all_stocks()
        if not stocks:
            init_stock_if_empty()
            stocks = _read_all_stocks()
        changed = False
        for code, stok in stocks.items():
            if stok < STOCK_THRESHOLD_RESTOCK:
                restock_to = random.randint(STOCK_RESTOCK_MIN, STOCK_RESTOCK_MAX)
                stocks[code] = restock_to
                changed = True
        if changed:
            _write_all_stocks(stocks)
    except Exception as e:
        log_error("auto_restock_if_low", e)

def format_stock_label(stok):
    if stok <= 0:
        return "❌ <b>STOK HABIS</b> (Restock Segera)"
    elif stok < 20:
        return f"🔥 <b>SISA {stok} UNIT! GASKEUN!</b>"
    elif stok < 50:
        return f"⚠️ Stok: <b>{stok} unit</b> (Terbatas)"
    else:
        return f"📦 Stok: <b>{stok} unit</b>"

def get_paket_code_by_name(nama_paket):
    for code, data in MASTER_PAKET.items():
        if data[0] == nama_paket:
            return code
    return None

# =====================================================================================
#  FITUR: TIER MEMBERSHIP
# =====================================================================================

def get_user_tier(chat_id):
    total = count_user_success_orders(chat_id)
    if total >= TIER_PLATINUM[1]:
        return TIER_PLATINUM[0], TIER_PLATINUM[3], TIER_PLATINUM[4]
    elif total >= TIER_GOLD[1]:
        return TIER_GOLD[0], TIER_GOLD[3], TIER_GOLD[4]
    elif total >= TIER_SILVER[1]:
        return TIER_SILVER[0], TIER_SILVER[3], TIER_SILVER[4]
    else:
        return TIER_BRONZE[0], TIER_BRONZE[3], TIER_BRONZE[4]

def get_tier_progress(chat_id):
    total = count_user_success_orders(chat_id)
    if total < TIER_SILVER[1]:
        sisa = TIER_SILVER[1] - total
        return f"🥉 Bronze → 🥈 Silver ({sisa} transaksi lagi)"
    elif total < TIER_GOLD[1]:
        sisa = TIER_GOLD[1] - total
        return f"🥈 Silver → 🥇 Gold ({sisa} transaksi lagi)"
    elif total < TIER_PLATINUM[1]:
        sisa = TIER_PLATINUM[1] - total
        return f"🥇 Gold → 💎 Platinum ({sisa} transaksi lagi)"
    else:
        return "💎 Platinum (Tier Tertinggi!)"

# =====================================================================================
#  FITUR: LUCKY DRAW HARIAN
# =====================================================================================

def get_last_spin_time(chat_id):
    try:
        with open(F_SPINLOG, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2 and parts[0] == str(chat_id):
                    return int(parts[1])
    except FileNotFoundError:
        pass
    return 0

def can_spin_now(chat_id):
    last = get_last_spin_time(chat_id)
    return (time.time() - last) >= (LUCKY_DRAW_COOLDOWN_JAM * 3600)

def save_spin(chat_id):
    try:
        with open(F_SPINLOG, "a") as f:
            f.write(f"{chat_id}|{int(time.time())}\n")
    except Exception as e:
        log_error("save_spin", e)

def roll_lucky_draw():
    pilihan = random.choices(LUCKY_DRAW_HADIAH, weights=[h[3] for h in LUCKY_DRAW_HADIAH], k=1)[0]
    return pilihan

def get_remaining_spin_time(chat_id):
    last = get_last_spin_time(chat_id)
    sisa_detik = (LUCKY_DRAW_COOLDOWN_JAM * 3600) - (time.time() - last)
    if sisa_detik <= 0:
        return "Siap spin sekarang!"
    jam = int(sisa_detik // 3600)
    menit = int((sisa_detik % 3600) // 60)
    return f"{jam} jam {menit} menit lagi"

# =====================================================================================
#  FITUR: VOUCHER MANUAL + LUCKY DRAW DISKON
# =====================================================================================

def _read_all_vouchers():
    vouchers = {}
    try:
        with open(F_VOUCHERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 4:
                    kode = parts[0]
                    try:
                        vouchers[kode] = {
                            'diskon': int(parts[1]),
                            'max': int(parts[2]),
                            'terpakai': int(parts[3]),
                            'expired': int(parts[4]) if len(parts) > 4 else 0,
                        }
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass
    return vouchers

def _write_all_vouchers(vouchers):
    try:
        with open(F_VOUCHERS, "w") as f:
            for kode, data in vouchers.items():
                f.write(f"{kode}|{data['diskon']}|{data['max']}|{data['terpakai']}|{data['expired']}\n")
    except Exception as e:
        log_error("_write_all_vouchers", e)

def create_voucher(kode, diskon, max_pakai, durasi_jam=24):
    vouchers = _read_all_vouchers()
    expired_ts = int(time.time()) + (durasi_jam * 3600)
    vouchers[kode.upper()] = {
        'diskon': diskon,
        'max': max_pakai,
        'terpakai': 0,
        'expired': expired_ts,
    }
    _write_all_vouchers(vouchers)

def validate_voucher(kode):
    vouchers = _read_all_vouchers()
    kode_up = kode.upper().strip()
    if kode_up not in vouchers:
        return False, 0, "Kode voucher tidak ditemukan."
    v = vouchers[kode_up]
    if v['terpakai'] >= v['max']:
        return False, 0, "Voucher sudah habis kuota."
    if v['expired'] > 0 and time.time() > v['expired']:
        return False, 0, "Voucher sudah expired."
    return True, v['diskon'], "Voucher valid!"

def use_voucher(kode):
    vouchers = _read_all_vouchers()
    kode_up = kode.upper().strip()
    if kode_up in vouchers:
        v = vouchers[kode_up]
        # FIX v11: Cek kuota dulu sebelum increment
        if v['terpakai'] < v['max']:
            v['terpakai'] += 1
            _write_all_vouchers(vouchers)
            return True
    return False

def get_voucher_sisa(kode):
    vouchers = _read_all_vouchers()
    kode_up = kode.upper().strip()
    if kode_up in vouchers:
        v = vouchers[kode_up]
        return max(0, v['max'] - v['terpakai'])
    return 0

# =====================================================================================
#  VOUCHER USER
# =====================================================================================

def user_has_voucher(chat_id, kode):
    kode_up = kode.upper().strip()
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return False
        with open(F_USER_VOUCHER, "r") as f:
            for ln in f:
                parts = ln.strip().split('|')
                if len(parts) >= 3 and parts[0] == str(chat_id):
                    if parts[1].startswith("VOUCHER_"):
                        kode_tersimpan = parts[1].replace("VOUCHER_", "")
                        if kode_tersimpan == kode_up:
                            return True
    except Exception:
        pass
    return False

def save_user_voucher(chat_id, kode, diskon):
    try:
        kode_up = kode.upper().strip()
        rows = []
        if os.path.exists(F_USER_VOUCHER):
            with open(F_USER_VOUCHER, "r") as f:
                rows = [ln.strip() for ln in f if ln.strip()]
        # FIX v11: Cek duplikat - kalau voucher ini udah pernah di-redeem user, jangan simpan lagi
        for ln in rows:
            parts = ln.split('|')
            if len(parts) >= 2 and parts[0] == str(chat_id):
                if parts[1] == f"VOUCHER_{kode_up}":
                    return
        # FIX v11: Simpan voucher baru (JANGAN hapus voucher lama)
        rows.append(f"{chat_id}|VOUCHER_{kode_up}|{diskon}|{int(time.time())}")
        with open(F_USER_VOUCHER, "w") as f:
            f.write("\n".join(rows) + "\n")
    except Exception as e:
        log_error("save_user_voucher", e)

def get_user_voucher_diskon(chat_id):
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return None, 0
        with open(F_USER_VOUCHER, "r") as f:
            for ln in f:
                parts = ln.strip().split('|')
                if len(parts) >= 3 and parts[0] == str(chat_id):
                    if parts[1].startswith("VOUCHER_"):
                        kode = parts[1].replace("VOUCHER_", "")
                        try:
                            return kode, int(parts[2])
                        except ValueError:
                            return None, 0
    except Exception:
        pass
    return None, 0

def consume_user_voucher(chat_id):
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return
        with open(F_USER_VOUCHER, "r") as f:
            rows = [ln.strip() for ln in f if ln.strip()]
        new_rows = []
        consumed = False
        for ln in rows:
            parts = ln.split('|')
            if not consumed and len(parts) >= 2 and parts[0] == str(chat_id) and parts[1].startswith("VOUCHER_"):
                consumed = True
                continue
            new_rows.append(ln)
        with open(F_USER_VOUCHER, "w") as f:
            f.write("\n".join(new_rows) + ("\n" if new_rows else ""))
    except Exception as e:
        log_error("consume_user_voucher", e)

def get_user_lucky_diskon(chat_id):
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return 0
        with open(F_USER_VOUCHER, "r") as f:
            for ln in f:
                parts = ln.strip().split('|')
                if len(parts) >= 2 and parts[0] == str(chat_id):
                    if parts[1].startswith("DISKON"):
                        try:
                            return int(parts[1].replace("DISKON", ""))
                        except ValueError:
                            return 0
    except Exception:
        pass
    return 0

def consume_user_lucky_diskon(chat_id):
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return
        with open(F_USER_VOUCHER, "r") as f:
            rows = [ln.strip() for ln in f if ln.strip()]
        new_rows = []
        consumed = False
        for ln in rows:
            parts = ln.split('|')
            if not consumed and len(parts) >= 2 and parts[0] == str(chat_id) and parts[1].startswith("DISKON"):
                consumed = True
                continue
            new_rows.append(ln)
        with open(F_USER_VOUCHER, "w") as f:
            f.write("\n".join(new_rows) + ("\n" if new_rows else ""))
    except Exception as e:
        log_error("consume_user_lucky_diskon", e)

# =====================================================================================
#  BAGIAN 3: DATABASE & PERSISTENSI DATA
# =====================================================================================

def save_user(chat_id):
    try:
        chat_id_str = str(chat_id).strip()
        if not chat_id_str or chat_id_str.startswith('-'):
            return
        users = []
        try:
            with open(F_USERS, "r") as f:
                users = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            pass
        if chat_id_str not in users:
            with open(F_USERS, "a") as f:
                f.write(chat_id_str + "\n")
            # FIX v13: Notif user baru join (di thread biar ga blocking)
            try:
                user_info = bot.get_chat(int(chat_id_str))
                threading.Thread(
                    target=notify_admin_new_user,
                    args=(int(chat_id_str), user_info),
                    daemon=True
                ).start()
            except Exception:
                pass
        try:
            last_seen = {}
            if os.path.exists(F_LASTSEEN):
                with open(F_LASTSEEN, "r") as f:
                    for line in f:
                        p = line.strip().split('|')
                        if len(p) == 2:
                            last_seen[p[0]] = p[1]
            last_seen[chat_id_str] = str(int(time.time()))
            with open(F_LASTSEEN, "w") as f:
                for uid, ts in last_seen.items():
                    f.write(f"{uid}|{ts}\n")
        except Exception:
            pass
    except Exception as e:
        log_error("save_user", e)

def get_user_coupon_status(chat_id):
    # FIX v11: Cek file ada dulu, hindari crash kalau file hilang
    try:
        if not os.path.exists(F_COUPONS):
            return "AVAILABLE"
        with open(F_COUPONS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2 and parts[0] == str(chat_id):
                    return parts[1]
    except FileNotFoundError:
        pass
    return "AVAILABLE"

def set_user_coupon_status(chat_id, status_baru):
    try:
        chat_id_str = str(chat_id)
        rows = []
        updated = False
        if os.path.exists(F_COUPONS):
            with open(F_COUPONS, "r") as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 2:
                        c_id, status = parts
                        if c_id == chat_id_str:
                            status = status_baru
                            updated = True
                        rows.append(f"{c_id}|{status}\n")
        if not updated:
            rows.append(f"{chat_id_str}|{status_baru}\n")
        # FIX v11: Atomic write (anti reset promo)
        tmp = F_COUPONS + ".tmp"
        with open(tmp, "w") as f:
            f.writelines(rows)
        if os.path.exists(F_COUPONS):
            os.remove(F_COUPONS)
        os.rename(tmp, F_COUPONS)
    except Exception as e:
        log_error("set_user_coupon_status", e)

def get_user_points(chat_id):
    try:
        with open(F_POINTS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2 and parts[0] == str(chat_id):
                    return int(parts[1])
    except FileNotFoundError:
        pass
    return 0

def _write_point_log(chat_id, delta, alasan):
    try:
        now = datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S')
        with open(F_POINTLOG, "a") as f:
            f.write(f"{chat_id}|{now}|{delta}|{alasan}\n")
    except Exception as e:
        log_error("_write_point_log", e)

def add_user_points(chat_id, amount, alasan="Bonus/Penambahan"):
    try:
        current = get_user_points(chat_id)
        new_total = current + amount
        rows = []
        updated = False
        chat_id_str = str(chat_id)
        try:
            with open(F_POINTS, "r") as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 2:
                        c_id, pts = parts
                        if c_id == chat_id_str:
                            pts = str(new_total)
                            updated = True
                        rows.append(f"{c_id}|{pts}\n")
        except FileNotFoundError:
            pass
        if not updated:
            rows.append(f"{chat_id_str}|{new_total}\n")
        with open(F_POINTS, "w") as f:
            f.writelines(rows)
        _write_point_log(chat_id, f"+{amount}", alasan)
    except Exception as e:
        log_error("add_user_points", e)

def reduce_user_points(chat_id, amount, alasan="Penukaran/Pengurangan"):
    current = get_user_points(chat_id)
    new_total = max(0, current - amount)
    rows = []
    chat_id_str = str(chat_id)
    try:
        with open(F_POINTS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    c_id, pts = parts
                    if c_id == chat_id_str:
                        pts = str(new_total)
                    rows.append(f"{c_id}|{pts}\n")
    except FileNotFoundError:
        pass
    with open(F_POINTS, "w") as f:
        f.writelines(rows)
    _write_point_log(chat_id, f"-{amount}", alasan)

def save_user_review(chat_id, rating, text_review):
    try:
        now = datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S')
        review_line = f"{chat_id}|{now}|{rating}|{text_review.replace('|', '-')}\n"
        with open(F_REVIEWS, "a") as f:
            f.write(review_line)
    except Exception as e:
        log_error("save_user_review", e)

def save_order(chat_id, paket_nama, harga, resi, payment_method="TRANSFER", point_cost=0, admin_msg_id=0):
    try:
        now = datetime.now(WIB)
        tanggal_str = now.strftime('%d-%m-%Y')
        jam_str = now.strftime('%H:%M:%S WIB')
        timestamp_epoch = int(now.timestamp())
        days_indo = {'Mon': 'Senin', 'Tue': 'Selasa', 'Wed': 'Rabu', 'Thu': 'Kamis',
                     'Fri': 'Jumat', 'Sat': 'Sabtu', 'Sun': 'Minggu'}
        hari_str = days_indo.get(now.strftime('%a'), now.strftime('%a'))
        order_line = (f"{chat_id}|{tanggal_str}|{hari_str}|{jam_str}|{paket_nama}|{harga}|"
                      f"{resi}|PENDING|{timestamp_epoch}|{payment_method}|{point_cost}|{admin_msg_id}\n")
        with open(F_ORDERS, "a") as f:
            f.write(order_line)
    except Exception as e:
        log_error("save_order", e)

def _read_all_orders():
    rows = []
    try:
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8:
                    rows.append(parts)
    except FileNotFoundError:
        pass
    return rows

def update_order_status_by_resi(resi_target, status_baru):
    try:
        updated = False
        target_chat_id = None
        target_payment = "TRANSFER"
        target_paket_nama = ""
        current_status_db = ""
        rows = []
        for parts in _read_all_orders():
            chat_id, tanggal, hari, jam, paket, harga, resi = parts[0:7]
            status = parts[7]
            timestamp_epoch = parts[8] if len(parts) > 8 else "0"
            pay_method = parts[9] if len(parts) > 9 else "TRANSFER"
            p_cost = int(parts[10]) if len(parts) > 10 and parts[10].isdigit() else 0
            adm_msg_id = parts[11] if len(parts) > 11 else "0"

            if resi.strip() == resi_target.strip():
                target_chat_id = chat_id
                target_payment = pay_method
                target_paket_nama = paket
                current_status_db = status
                if status != "PENDING":
                    rows.append('|'.join(parts) + "\n")
                    continue
                status = status_baru
                updated = True
            rows.append(f"{chat_id}|{tanggal}|{hari}|{jam}|{paket}|{harga}|{resi}|{status}|"
                        f"{timestamp_epoch}|{pay_method}|{p_cost}|{adm_msg_id}\n")

        if updated:
            with open(F_ORDERS, "w") as f:
                f.writelines(rows)
            if target_chat_id and current_status_db == "PENDING":
                if status_baru == "BERHASIL":
                    set_user_coupon_status(target_chat_id, "USED")
                    if target_payment != "POIN":
                        _, multiplier, _ = get_user_tier(target_chat_id)
                        bonus = int(10 * multiplier)
                        add_user_points(target_chat_id, bonus, f"Bonus pembelian sukses (Tier x{multiplier})")
                    paket_code = get_paket_code_by_name(target_paket_nama)
                    if paket_code:
                        reduce_stock_specific(paket_code, 1)
                    try:
                        _apply_referral_bonus_if_eligible_helper(target_chat_id)
                    except Exception:
                        pass
                    # FIX v12: Cek Tier Upgrade
                    check_tier_upgrade(target_chat_id)

                elif status_baru in ["DITOLAK", "EXPIRED", "CANCELLED"]:
                    set_user_coupon_status(target_chat_id, "AVAILABLE")
            try:
                marker = f".reminded_{resi_target}"
                if os.path.exists(marker):
                    os.remove(marker)
            except Exception:
                pass
            return True
    except Exception as e:
        log_error("update_order_status_by_resi", e)
    return False

def get_user_orders(chat_id):
    orders = []
    for parts in _read_all_orders():
        if parts[0] == str(chat_id):
            orders.append({
                'tanggal': parts[1], 'hari': parts[2], 'jam': parts[3],
                'paket': parts[4], 'harga': parts[5], 'resi': parts[6],
                'status': parts[7], 'pay_method': parts[9] if len(parts) > 9 else "TRANSFER"
            })
    return orders

def get_latest_user_order_data(chat_id):
    try:
        current_time = int(datetime.now(WIB).timestamp())
        orders = [p for p in _read_all_orders() if p[0] == str(chat_id)]
        if orders:
            last_order = orders[-1]
            resi = last_order[6]
            status = last_order[7]
            timestamp_epoch = int(last_order[8]) if len(last_order) > 8 and last_order[8].isdigit() else current_time
            if status == "PENDING" and (current_time - timestamp_epoch > TRANSAKSI_TIMEOUT_DETIK):
                update_order_status_by_resi(resi, "EXPIRED")
                return resi, "EXPIRED"
            return resi, status
    except Exception as e:
        log_error("get_latest_user_order_data", e)
    return f"PKL-MLBB-{random.randint(10000, 99999)}", "PENDING"

def archive_old_orders():
    try:
        now_epoch = int(datetime.now(WIB).timestamp())
        keep_rows, archive_rows = [], []
        for parts in _read_all_orders():
            epoch = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else now_epoch
            line = '|'.join(parts) + "\n"
            if now_epoch - epoch > ARCHIVE_UMUR_HARI * 86400:
                archive_rows.append(line)
            else:
                keep_rows.append(line)
        if archive_rows:
            with open(F_ARCHIVE, "a") as f:
                f.writelines(archive_rows)
            with open(F_ORDERS, "w") as f:
                f.writelines(keep_rows)
    except Exception as e:
        log_error("archive_old_orders", e)

def count_user_success_orders(chat_id):
    total = 0
    for parts in _read_all_orders():
        if parts[0] == str(chat_id) and len(parts) > 7 and parts[7].strip() == "BERHASIL":
            total += 1
    return total

# =====================================================================================
#  BAGIAN 4: SISTEM REFERRAL + GACHA
# =====================================================================================

def register_referral(referrer_id, referred_id):
    referrer_id, referred_id = str(referrer_id), str(referred_id)
    if referrer_id == referred_id:
        return False
    try:
        with open(F_REFERRALS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2 and parts[1] == referred_id:
                    return False
    except FileNotFoundError:
        pass
    try:
        now = int(datetime.now(WIB).timestamp())
        with open(F_REFERRALS, "a") as f:
            f.write(f"{referrer_id}|{referred_id}|{now}|BELUM_BONUS\n")
        return True
    except Exception as e:
        log_error("register_referral", e)
        return False

def roll_gacha_referral_bonus():
    hasil = random.choices(population=[2, 3, 4, 5], weights=[45, 35, 15, 5], k=1)[0]
    return hasil

def _apply_referral_bonus_if_eligible_helper(new_buyer_chat_id):
    try:
        rows = []
        changed = False
        referrer_to_bonus = None
        with open(F_REFERRALS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 4:
                    referrer_id, referred_id, ts, status = parts
                    if referred_id == str(new_buyer_chat_id) and status == "BELUM_BONUS":
                        status = "SUDAH_BONUS"
                        referrer_to_bonus = referrer_id
                        changed = True
                    rows.append(f"{referrer_id}|{referred_id}|{ts}|{status}\n")
        if changed:
            with open(F_REFERRALS, "w") as f:
                f.writelines(rows)
        if referrer_to_bonus:
            bonus_poin = roll_gacha_referral_bonus()
            add_user_points(referrer_to_bonus, bonus_poin, f"Bonus referral gacha (+{bonus_poin} poin)")
            try:
                bot.send_message(
                    referrer_to_bonus,
                    f"🎉 <b>BONUS REFERRAL CAIR!</b>\n\n"
                    f"Temanmu berhasil belanja pertama kali.\n"
                    f"🎰 Hasil Gacha Bonus: <b>+{bonus_poin} Poin</b> masuk ke saldo loyalitasmu!",
                    parse_mode="HTML"
                )
            except Exception:
                pass
    except FileNotFoundError:
        pass
    except Exception as e:
        log_error("_apply_referral_bonus_if_eligible_helper", e)

def get_referral_stats(chat_id):
    total, bonus_cair = 0, 0
    try:
        with open(F_REFERRALS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 4 and parts[0] == str(chat_id):
                    total += 1
                    if parts[3] == "SUDAH_BONUS":
                        bonus_cair += 1
    except FileNotFoundError:
        pass
    return total, bonus_cair

def get_time_greeting():
    hour = datetime.now(WIB).hour
    if 4 <= hour < 11:
        return "Selamat Pagi 🌅"
    elif 11 <= hour < 15:
        return "Selamat Siang ☀️"
    elif 15 <= hour < 18:
        return "Selamat Sore 🌇"
    else:
        return "Selamat Malam 🌙"

def check_store_status():
    hour = datetime.now(WIB).hour
    if 0 <= hour < 7:
        return False, ("⚠️ <b>INFO OPERASIONAL TOKO:</b>\nHalo Kak! Toko sedang istirahat (Offline) "
                       "jam 00:00 - 07:00 WIB. Pesanan tetap bisa dibuat, pengiriman script "
                       "dilanjutkan jam 07:00 WIB! 🙏✨")
    return True, ""

def get_random_masked_name():
    # FIX v11: Tambah jadi 80+ nama biar variatif
    list_nama_tele = [
        "@R_Zky***", "@Alvinn_***", "@Dimas_99***", "@RezaPrat_***",
        "@Bayu_Official***", "@Farel_X***", "@Yoga_Mlg***", "@DickyGez_***",
        "@SuryaPratama***", "@RamaWicak***", "@Gilang_ID***", "@BagasKusn***",
        "@Arif_Wd***", "@DaniPratama***", "@Hendra_99***", "@Rian_Xyz***",
        "@Aldi_07***", "@Bintang_ID***", "@CandraPras***", "@DikaPrast_***",
        "@Fajar_01***", "@GalihGmr***", "@IqbalID***", "@JokoPrasetyo***",
        "@KevinWdj***", "@LukmanHkm***", "@MaulanaID***", "@NaufalXyz***",
        "@Pratama99***", "@RafliSultan***", "@SatriaGaming***", "@TegarGanz***",
        "@VianID***", "@WahyuPrat***", "@YudaDev***", "@ZakiMlf***",
        "@Amirul_My***", "@Haikal_Iskandar***", "@Farhan_Zul***", "@Aiman_Badri***",
        "@Aqil_Danial***", "@Syahmi_Zain***", "@Luqman_Hakim***", "@Zulhelmi_My***",
        "@Alex_Walker***", "@Liam_Smith***", "@Noah_Miller***", "@Oliver_Davis***",
        "@Sultan_Mlbb***", "@Anjay_Mabar***", "@Gacor_Gaming***", "@TopGlobal_1***",
        "@Zul_Ganz***", "@Rizky_Store***", "@Ibnu_Hkm***", "@Pandu_ID***",
        "@Fikri_Xp***", "@Aditya_Prat***", "@Eko_Cyber***", "@Bayu_Sena***",
        "@angga_99***", "@febri_nj***", "@putra_ml***", "@rendi_sultan***",
        "@agung_Gz***", "@bagus_ID***", "@deni_Xyz***", "@eko_prast***",
        "@gilang_store***", "@heru_mlbb***", "@ilham_ganz***", "@jeri_xpl***",
        "@kiki_pro***", "@lutfi_ID***", "@miko_sultan***", "@opan_gamer***",
        "@rama_cell***", "@rendra_ID***", "@septian_mz***", "@tegar_store***",
        "@rizal_mlbb***", "@yoga_sultan***", "@zidan_ID***", "@dika_store***",
    ]
    return random.choice(list_nama_tele)

def generate_single_testimonial():
    list_paket = [
        ("Natural Balance (30 Hari)", "Rp 120.000", "45 Poin"),
        ("Light VIP + Drone (30 Hari)", "Rp 95.000", "35 Poin"),
        ("Semi-Safe 14 Hari", "Rp 75.000", "25 Poin"),
        ("Lifetime Safe Permanent", "Rp 200.000", "75 Poin"),
        ("Sultan One Hit 100% (30 Hari)", "Rp 150.000", "55 Poin"),
        ("VIP Pro One Hit 80% (30 Hari)", "Rp 100.000", "40 Poin"),
        ("Semi-Private 14 Hari", "Rp 75.000", "25 Poin"),
        ("Permanent Legend (Lifetime)", "Rp 250.000", "90 Poin")
    ]
    nama = get_random_masked_name()
    paket, harga_rp, harga_poin = random.choice(list_paket)
    menit_lalu = random.randint(2, 45)
    current_hour = datetime.now(WIB).hour
    waktu_ket = "pagi ini" if 4 <= current_hour < 11 else (
        "siang ini" if 11 <= current_hour < 15 else (
            "sore ini" if 15 <= current_hour < 18 else "malam ini"))

    is_poin_pay = random.random() < 0.3
    if is_poin_pay:
        price_text = f"{harga_poin} (Klaim Saldo Poin Loyalitas ✨)"
        pay_method_label = "REDEEMED VIA LOYALTY POINTS"
    else:
        price_text = harga_rp
        pay_method_label = "SUCCESS & SCRIPT DELIVERED"

    reduce_stock_random_all()
    auto_restock_if_low()

    return (
        "🚨 REAL-TIME TRANSACTION REPORT 🚨\n\n"
        f"✅ Buyer ID: {nama}\n"
        f"📦 Item Purchased: {paket}\n"
        f"💵 Price / Method: {price_text}\n"
        f"⏱️ Time: {menit_lalu} menit yang lalu ({waktu_ket})\n"
        f"🔒 Status: {pay_method_label}\n\n"
        "🔥 Terima kasih telah berbelanja di Official Pakel MlbbStore! Aman, lancar, & anti-detect. Mau order juga? Langsung sikat ke bot ya! 👇\n"
        f"🤖 Bot Store: @{bot.get_me().username}"
    )

def generate_fake_testimonials_list():
    list_paket = [
        ("Natural Balance", "Rp 120.000"), ("Light VIP + Drone", "Rp 95.000"),
        ("Semi-Safe 14 Hari", "Rp 75.000"), ("Lifetime Safe Permanent", "Rp 200.000"),
        ("Sultan One Hit 100%", "Rp 150.000"), ("VIP Pro One Hit 80%", "Rp 100.000")
    ]
    testi_output = ""
    for i in range(1, 6):
        nama = get_random_masked_name()
        paket, harga = random.choice(list_paket)
        menit_lalu = random.randint(2, 45)
        testi_output += (f"✅ {i}. Buyer ID: {nama}\n   • Dibeli: {paket} ({harga})\n"
                         f"   • Status: LUNAS & SCRIPT TERKIRIM\n\n")
    return testi_output

# =====================================================================================
#  FITUR: AUTO BROADCAST VOUCHER BARU (di thread background)
# =====================================================================================

def broadcast_voucher_baru(kode, diskon, max_pakai, durasi_jam):
    """Kirim BC voucher baru ke semua user (dipanggil dari thread)."""
    try:
        with open(F_USERS, "r") as f:
            users = [line.strip() for line in f.read().splitlines() if line.strip()]
    except FileNotFoundError:
        return

    bc_text = (
        "🎫 <b>VOUCHER BARU DARI PAKEL MLBBSTORE!</b> 🎫\n\n"
        f"🎁 Kode Voucher: <code>{kode}</code>\n"
        f"💵 Diskon: <b>Rp {diskon:,}</b>\n"
        f"📊 Kuota Terbatas: <b>{max_pakai} user</b>\n"
        f"⏱️ Berlaku: <b>{durasi_jam} jam</b>\n\n"
        "📌 <b>CARA PAKAI:</b>\n"
        f"Ketik: <code>Voucher {kode}</code>\n"
        "Ke bot ini, langsung terkunci ke akunmu!\n\n"
        "⚡ <i>Buruan sebelum kuota habis! Yang cepat, yang dapat!</i>\n\n"
        f"🛒 Cek katalog & checkout di bot: @{bot.get_me().username}"
    )

    success = 0
    gagal = 0
    for chat_id in set(users):
        try:
            bot.send_message(chat_id, bc_text, parse_mode="HTML",
                             disable_web_page_preview=True)
            success += 1
            time.sleep(0.05)
        except Exception:
            gagal += 1

    # Notif admin hasil BC
    try:
        bot.send_message(
            ADMIN_TELEGRAM_ID,
            f"📢 <b>BROADCAST VOUCHER SELESAI</b>\n\n"
            f"🎫 Kode: <code>{kode}</code>\n"
            f"✅ Berhasil: <b>{success}</b> user\n"
            f"❌ Gagal: <b>{gagal}</b> user\n"
            f"👥 Total user: {len(set(users))}",
            parse_mode="HTML"
        )
    except Exception:
        pass

# =====================================================================================
#  BAGIAN 5: BACKGROUND THREADS
# =====================================================================================

def payment_reminder_loop():
    while True:
        try:
            # FIX v13: Notif admin order hampir expired
            notify_admin_order_will_expire()
            now_epoch = int(datetime.now(WIB).timestamp())
            for parts in _read_all_orders():
                chat_id = parts[0]
                resi = parts[6]
                status = parts[7]
                epoch = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else now_epoch
                if status == "PENDING":
                    sisa = TRANSAKSI_TIMEOUT_DETIK - (now_epoch - epoch)
                    if PAYMENT_REMINDER_SEBELUM_DETIK - 30 <= sisa <= PAYMENT_REMINDER_SEBELUM_DETIK:
                        marker_file = f".reminded_{resi}"
                        if not os.path.exists(marker_file):
                            try:
                                bot.send_message(
                                    chat_id,
                                    f"⏰ <b>REMINDER PEMBAYARAN!</b>\n\n"
                                    f"Kak, sisa waktu pembayaranmu tinggal <b>5 menit</b> lagi!\n\n"
                                    f"🔑 Resi: <code>{resi}</code>\n\n"
                                    "Buruan selesaikan pembayaran & kirim bukti transfer ke bot ini "
                                    "sebelum pesanan otomatis expired ya! 🙏",
                                    parse_mode="HTML"
                                )
                                open(marker_file, "w").close()
                            except Exception as e:
                                log_error("payment_reminder_send", e)
        except Exception as e:
            log_error("payment_reminder_loop", e)
        time.sleep(30)

threading.Thread(target=payment_reminder_loop, daemon=True).start()

def timeout_dan_reminder_loop():
    while True:
        try:
            now_epoch = int(datetime.now(WIB).timestamp())
            for parts in _read_all_orders():
                chat_id, resi, status = parts[0], parts[6], parts[7]
                epoch = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else now_epoch
                if status == "PENDING" and (now_epoch - epoch > TRANSAKSI_TIMEOUT_DETIK):
                    update_order_status_by_resi(resi, "EXPIRED")
                    try:
                        bot.send_message(chat_id,
                                         f"❌ <b>PESANAN EXPIRED</b> (Resi <code>{resi}</code>)\nWaktu 15 menit habis.",
                                         parse_mode="HTML")
                    except Exception:
                        pass
        except Exception as e:
            log_error("timeout_dan_reminder_loop", e)
        time.sleep(30)

threading.Thread(target=timeout_dan_reminder_loop, daemon=True).start()

def archive_loop():
    while True:
        time.sleep(24 * 3600)
        archive_old_orders()

threading.Thread(target=archive_loop, daemon=True).start()

def background_auto_poster():
    time.sleep(60)
    while True:
        try:
            time.sleep(random.choice([1500, 3600, 7200, 10800]))
            bot.send_message(chat_id=GROUP_CHAT_ID, text=generate_single_testimonial(),
                             message_thread_id=GROUP_TOPIC_ID, disable_web_page_preview=True)
        except Exception as e:
            log_error("background_auto_poster", e)
            time.sleep(60)

threading.Thread(target=background_auto_poster, daemon=True).start()

def background_auto_broadcast():
    time.sleep(300)
    broadcast_templates = [
        "📢 <b>INFO PROMO SPESIAL HARI INI!</b> 🔥\n\nBuat Kakak yang mau ngebut <i>push rank</i> tanpa takut kena ban, buruan sikat script VIP kita sekarang!\n🎁 Spesial hari ini, ada potongan harga spesial + bonus <i>Server Lag Panel</i> dan <i>Drone View X10</i> gratis tanpa biaya tambahan.\n\n🛒 Langsung cek katalog lengkapnya di bot: @{bot_username}",
        "🛡️ <b>KENAPA HARUS PAKAI SCRIPT PAKEL MLBBSTORE?</b> ⚡\n\nJangan pertaruhkan akun sultan Kakak pakai script sembarangan yang gampang terdeteksi sistem Moonton!\nDi sini kita pakai enkripsi <i>high-tier anti-detect</i> paling stabil se-Indonesia, aman buat main di mode <i>Ranked</i> Mythic sekalipun.\n\n📦 Pilih paket andalan Kakak sekarang sebelum kehabisan slot: @{bot_username}",
        "⚡ <b>BONUS FREE ALL PACKAGES TANPA SYARAT!</b> 🎁\n\nSetiap pembelian paket apa saja di Official Pakel MlbbStore, Kakak bakal otomatis dapet:\n• Panel Server Lag Musuh (<i>Global Ping Spikes</i>) 🌐\n• Drone View Eksklusif Ultra Wide X1 - X10 🦅\n\n🚀 Yuk dominasi permainan sekarang juga! Order gampang via bot: @{bot_username}",
        "🏆 <b>MAU JADI TOP GLOBAL ATAU NYAMPE MYTHIC GLORY DENGAN CEPAT?</b> 🔥\n\nWaktunya buktikan kemampuan terbaikmu di Land of Dawn! Gunakan <i>Custom Damage</i> dan <i>Light VIP</i> dari Pakel MlbbStore biar gameplay makin gampang dan mulus.\n\n💬 Cek riwayat pesanan, klaim kupon, atau pilih paket langsung di: @{bot_username}",
        "🌟 <b>PEMBERITAHUAN UPDATE STOK & TESTIMONI HARIAN</b> 🚀\n\nRatusan player sudah membuktikan sendiri kestabilan script kita hari ini tanpa kendala. Giliran Kakak buat rasain bedanya pas war!\n💎 Proses cepat, amanah, dan dibimbing sampai beres.\n\n👇 Yuk amankan paket pilihanmu langsung di bot: @{bot_username}",
        "💥 <b>SPECIAL EDITION: SULTAN ONE HIT & INSTANT KILL</b> ⚡\n\nMau ngerasain dominasi mutlak di setiap pertandingan? Paket <i>Sultan One Hit</i> siap bikin musuh kewalahan dan rata dalam sekejap!\n🛡️ Dilengkapi sistem pengaman kelas atas agar akun tetap aman sentosa.\n\n🛒 Sikat promonya sekarang lewat bot: @{bot_username}",
        "🎁 <b>CEK SALDO POIN & KUPON MEMBER KAMU!</b> 💳\n\nTahukah Kakak? Setiap transaksi sukses di Official Pakel MlbbStore, Kakak bakal otomatis dapet tambahan Poin Loyalitas lho!\n🪙 Poinnya bisa ditukar buat bayar paket script gratis tanpa perlu transfer rupiah lagi. Mantap kan?\n\n✨ Yuk cek poinmu sekarang di bot: @{bot_username}",
        "🌐 <b>BASMI LAG & FPS DROP SAAT WAR BERSAMA KITA!</b> 📉➡️📈\n\nKesel banget kan pas lagi momen penting malah patah-patah atau sinyal mendadak merah? Tenang, script kita sudah include fitur *Server Lag Panel* buat stabilin permainan.\n🎯 Main jadi lebih PeDe, mulus, dan bebas hambatan!\n\n📦 Langsung pilih paketnya di sini: @{bot_username}",
        "⏰ <b>WAKTU TERBATAS: GASPOL PUSH RANK AKHIR SEASON!</b> ⏳\n\nJangan biarkan bintangmu turun atau stuck di satu tier terus! Maksimalkan performa permainanmu dengan script premium anti-detect terpercaya se-Indonesia.\n⚡ Dijamin ampuh buat bantu naik tier dengan mulus.\n\n🚀 Amankan paketmu sekarang juga via bot: @{bot_username}",
        "👋 <b>HALO KAKAK-KAKAK PLAYER MLBB INDONESIA!</b> 🎮✨\n\nMau mabar bareng squad tapi minder sama performa hero? Jangan khawatir, Official Pakel MlbbStore selalu siap jadi solusi terbaik buat naikin performa game kamu hari ini.\n💎 Aman, stabil, dan bergaransi.\n\n👇 Yuk langsung mampir ke katalog bot: @{bot_username}"
    ]
    while True:
        try:
            time.sleep(random.randint(14400, 28800))
            try:
                with open(F_USERS, "r") as f:
                    users = [line.strip() for line in f.read().splitlines() if line.strip()]
            except FileNotFoundError:
                continue
            if not users:
                continue
            template_pilihan = random.choice(broadcast_templates)
            pesan_final = template_pilihan.format(bot_username=bot.get_me().username)
            for chat_id in set(users):
                try:
                    bot.send_message(chat_id=chat_id,
                                     text=f"📢 <b>PENGUMUMAN OTOMATIS</b>\n\n{pesan_final}",
                                     parse_mode="HTML", disable_web_page_preview=True)
                    time.sleep(0.05)
                except Exception:
                    pass
        except Exception as e:
            print(f"[AUTO-BROADCAST ERROR]: {e}")
            time.sleep(300)

threading.Thread(target=background_auto_broadcast, daemon=True).start()

def auto_refresh_stock_loop():
    """Restock semua paket tiap 6 jam biar keliatan fresh."""
    while True:
        time.sleep(21600)  # 6 jam
        try:
            stocks = _read_all_stocks()
            if not stocks:
                init_stock_if_empty()
                continue
            changed = False
            for code in list(stocks.keys()):
                if code not in MASTER_PAKET:
                    continue
                harga = MASTER_PAKET[code][1]
                # Set range restock sesuai harga
                if harga < 100000:
                    stok_baru = random.randint(150, 250)
                elif harga < 180000:
                    stok_baru = random.randint(80, 150)
                else:
                    stok_baru = random.randint(30, 80)
                stocks[code] = stok_baru
                changed = True
            if changed:
                _write_all_stocks(stocks)
        except Exception as e:
            log_error("auto_refresh_stock_loop", e)


threading.Thread(target=auto_refresh_stock_loop, daemon=True).start()


def income_update_loop():
    """Kirim update pendapatan ke admin tiap 4 jam."""
    time.sleep(600)  # Delay awal 10 menit biar bot stabil
    while True:
        try:
            notify_admin_income_update()
        except Exception as e:
            log_error("income_update_loop", e)
        time.sleep(14400)  # 4 jam


threading.Thread(target=income_update_loop, daemon=True).start()


def voucher_reminder_loop():
    """Cek voucher hampir expired tiap 10 menit."""
    while True:
        try:
            remind_expiring_user_vouchers()
        except Exception as e:
            log_error("voucher_reminder_loop", e)
        time.sleep(600)  # 10 menit


threading.Thread(target=voucher_reminder_loop, daemon=True).start()


def auto_backup_loop():
    while True:
        time.sleep(AUTO_BACKUP_INTERVAL_DETIK)
        # FIX v11: Backup ke folder lokal + kirim ke admin
        auto_backup_all_files()
        for fname in [F_ORDERS, F_USERS, F_POINTS]:
            try:
                if os.path.exists(fname):
                    with open(fname, "rb") as f:
                        bot.send_document(ADMIN_TELEGRAM_ID, f, caption=f"🗄️ Auto-backup: {fname}")
            except Exception as e:
                log_error("auto_backup_loop", e)
        # FIX v12: Cleanup file lama
        cleanup_old_logs()

threading.Thread(target=auto_backup_loop, daemon=True).start()

init_stock_if_empty()
verify_checksums()  # FIX v11: Generate baseline checksum

print("[SECURITY] v11 Cyber Security Layer Aktif")
print("[SECURITY] ✓ Thread Locks")
print("[SECURITY] ✓ Anti Curang Voucher")
print("[SECURITY] ✓ Anti Kupon Reset")
print("[SECURITY] ✓ Auto Backup 1 Jam")
print("[SECURITY] ✓ Suspicious Log + Auto Ban")
print("[SECURITY] ✓ Checksum Verify")

# =====================================================================================
#  BAGIAN 6: TRANSLATIONS & UI HELPERS
# =====================================================================================

TRANSLATIONS = {
    'id': {
        'btn_katalog': "💎 Katalog VIP & Harga Paket",
        'btn_testi': "🌟 Testimoni & Real-Time Bukti Order",
        'btn_riwayat': "📦 Cek Riwayat & Status Pesanan Saya",
        'btn_promo': "🎁 Klaim Kupon & Poin Loyalitas",
        'btn_referral': "🎯 Poin & Link Referral Saya",
        'btn_profil': "👤 Profil Akun Saya",
        'btn_lucky': "🎰 Lucky Draw Harian",
        'btn_cara_order': "❓ Panduan Cara Order",
        'btn_bayar': "💳 Metode Pembayaran Lengkap",
        'btn_faq': "💡 FAQ / Pertanyaan Umum",
        'btn_konfirmasi': "✅ Cek Status & Konfirmasi Resi",
        'btn_admin': "💬 Hubungi Admin Resmi",
        'back': "⬅️ Kembali ke Menu Utama",
        'cat_title_1': "🔥 VIP EXCLUSIVE CATALOGUE - BAGIAN 1 (Kak {name}) 🔥\n<i>(Kategori: Custom Damage High-Tier & Fair Play Anti-Detect)</i>",
        'cat_title_2': "🔥 VIP EXCLUSIVE CATALOGUE - BAGIAN 2 (Kak {name}) 🔥\n<i>(Kategori: Sultan One Hit Instan & Dominasi Mutlak)</i>",
        'bonus_txt': ("⚡ <b>BONUS SPESIAL FREE ALL PACKAGES (TANPA BIAYA TAMBAHAN):</b>\n"
                      "🎁 Setiap pembelian paket apa saja, otomatis mendapatkan:\n"
                      "  • Panel Server Lag Musuh (Global Ping Spikes)\n"
                      "  • Drone View Eksklusif X1 sampai X10 (Ultra Wide View)\n\n"
                      "📂 <b>SILAKAN PILIH SCRIPT & PELAJARI DETAIL FITUR DI BAWAH INI:</b>"),
        'next_1': "▶️ Lanjut Katalog Bagian 2",
        'prev_2': "◀️ Kembali Katalog Bagian 1",
        'inv_title': "🛒 INVOICE PEMESANAN RESMI VIP (Kak {name}) 🧾",
        'confirm_instr': ("🛡️ INSTRUKSI KONFIRMASI PEMBAYARAN:\n"
                          "Setelah sukses membayar, silakan kirim Screenshot Bukti Transfer ke bot ini "
                          "untuk mendapatkan Resi Unik."),
    },
    'en': {
        'btn_katalog': "💎 VIP Catalogue & Pricing", 'btn_testi': "🌟 Live Testimonials",
        'btn_riwayat': "📦 My Order History", 'btn_promo': "🎁 Claim Promo & Points",
        'btn_referral': "🎯 My Points & Referral Link",
        'btn_profil': "👤 My Account Profile",
        'btn_lucky': "🎰 Daily Lucky Draw",
        'btn_cara_order': "❓ How to Order", 'btn_bayar': "💳 Payments",
        'btn_faq': "💡 FAQ", 'btn_konfirmasi': "✅ Check Status",
        'btn_admin': "💬 Contact Admin", 'back': "⬅️ Kembali ke Menu Utama",
        'cat_title_1': "🔥 VIP EXCLUSIVE CATALOGUE - PART 1 ({name}) 🔥",
        'cat_title_2': "🔥 VIP EXCLUSIVE CATALOGUE - PART 2 ({name}) 🔥",
        'bonus_txt': "⚡ SPECIAL BONUS:",
        'next_1': "▶️ Next", 'prev_2': "◀️ Back", 'inv_title': "🛒 INVOICE",
        'confirm_instr': "🛡️ Send screenshot.",
    }
}

def get_lang(user):
    code = getattr(user, 'language_code', 'en')
    if code and code.lower().startswith('id'):
        return 'id'
    return 'en'

def get_back_markup(l):
    markup = types.InlineKeyboardMarkup()
    text = TRANSLATIONS.get(l, TRANSLATIONS['en'])['back']
    markup.add(types.InlineKeyboardButton(text, callback_data='menu_utama'))
    return markup

def build_welcome_text(user, user_points, l='id'):
    greeting = get_time_greeting()
    tier_label, _, _ = get_user_tier(user.id)
    if l == 'id':
        return (
            f"🔥 {greeting}, Kak {user.first_name}! Selamat datang di Official Pakel MlbbStore 🙏✨\n\n"
            f"🪙 Saldo Poin Loyalitas Anda: <b>{user_points} Poin</b>\n"
            f"🏅 Tier Anda: <b>{tier_label}</b>\n\n"
            "Pusat layanan script cheat Mobile Legends premium terpercaya, anti-detect kelas atas, "
            "server lag panel, & drone view paling stabil se-Indonesia.\n\n"
            "👇 Silakan pilih menu di bawah ini untuk mulai berbelanja:"
        )
    else:
        return (
            f"🔥 {greeting}, {user.first_name}! Welcome to Official Pakel MlbbStore 🙏✨\n\n"
            f"🪙 Your Loyalty Points: <b>{user_points} Poin</b>\n"
            f"🏅 Your Tier: <b>{tier_label}</b>\n\n"
            "Trusted premium Mobile Legends script service.\n\n"
            "👇 Please select a menu below to start shopping:"
        )

def build_main_menu_markup(l='id'):
    t = TRANSLATIONS.get(l, TRANSLATIONS['id'])
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(t['btn_katalog'], callback_data='menu_katalog'),
        types.InlineKeyboardButton(t['btn_testi'], callback_data='menu_testi'),
        types.InlineKeyboardButton(t['btn_riwayat'], callback_data='menu_riwayat'),
        types.InlineKeyboardButton(t['btn_promo'], callback_data='menu_promo'),
        types.InlineKeyboardButton(t['btn_referral'], callback_data='menu_referral'),
        types.InlineKeyboardButton(t['btn_profil'], callback_data='menu_profil'),
        types.InlineKeyboardButton(t['btn_lucky'], callback_data='menu_lucky'),
        types.InlineKeyboardButton(t['btn_cara_order'], callback_data='menu_cara_order'),
        types.InlineKeyboardButton(t['btn_bayar'], callback_data='menu_bayar'),
        types.InlineKeyboardButton(t['btn_faq'], callback_data='menu_faq'),
        types.InlineKeyboardButton(t['btn_konfirmasi'], callback_data='menu_konfirmasi'),
        types.InlineKeyboardButton("🏆 Leaderboard Top Buyer", callback_data='refresh_leaderboard'),
    )
    markup.add(types.InlineKeyboardButton(t['btn_admin'], url=ADMIN_LINK))
    return markup

def _kirim_poin_referral(chat_id, message_id, l='id'):
    points = get_user_points(chat_id)
    total_ref, bonus_cair = get_referral_stats(chat_id)
    bot_username = bot.get_me().username
    link = f"https://t.me/{bot_username}?start=ref_{chat_id}"

    share_text = "Gabung & belanja script VIP MLBB terpercaya di Pakel MlbbStore! Pakai link referral saya ya"
    share_text_encoded = urllib.parse.quote(share_text)
    share_url = f"https://t.me/share/url?url={link}&text={share_text_encoded}"

    text = (
        f"🎯 <b>POIN & REFERRAL KAMU</b>\n\n"
        f"🪙 Saldo Poin: <b>{points} Poin</b>\n"
        f"👥 Total teman diundang: <b>{total_ref}</b>\n"
        f"✅ Bonus referral sudah cair: <b>{bonus_cair}</b>\n\n"
        f"🔗 <b>Link Referral Pribadimu:</b>\n<code>{link}</code>\n\n"
        "🎰 <b>Sistem Gacha Bonus Referral:</b>\n"
        "• +2 Poin (45%)\n• +3 Poin (35%)\n• +4 Poin (15%)\n• +5 Poin (5%)\n\n"
        "💡 <i>Ajak teman pakai link ini, makin banyak yang belanja makin besar peluang gacha bonusnya!</i>"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📤 Bagikan ke Teman / Grup", url=share_url),
        types.InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data='menu_utama')
    )
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                              parse_mode="HTML", reply_markup=markup,
                              disable_web_page_preview=True)
    except Exception:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup,
                         disable_web_page_preview=True)

def _kirim_profil_akun(chat_id, message_id, user, l='id'):
    points = get_user_points(chat_id)
    coupon_status = get_user_coupon_status(chat_id)
    total_sukses = count_user_success_orders(chat_id)
    total_ref, bonus_cair = get_referral_stats(chat_id)
    tier_label, multiplier, diskon = get_user_tier(chat_id)
    tier_progress = get_tier_progress(chat_id)

    if coupon_status == "AVAILABLE":
        status_kupon = "🎁 Tersedia (Belum Dipakai)"
    elif coupon_status == "PENDING":
        status_kupon = "⏳ Pending (Menunggu Verifikasi)"
    else:
        status_kupon = "✅ Sudah Digunakan"

    username_display = f"@{user.username}" if user.username else "-"
    nama_tampil = user.first_name + (f" {user.last_name}" if user.last_name else "")

    text = (
        "👤 <b>PROFIL AKUN SAYA</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"📝 Nama Tampil : <b>{nama_tampil}</b>\n"
        f"🔗 Username     : {username_display}\n"
        f"🆔 ID Telegram  : <code>{chat_id}</code>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"🏅 Tier Membership : <b>{tier_label}</b>\n"
        f"   ├ Poin Bonus: <b>x{multiplier}</b>\n"
        f"   ├ Diskon    : <b>{diskon}%</b>\n"
        f"   └ Progress  : {tier_progress}\n\n"
        f"🪙 Saldo Poin    : <b>{points} Poin</b>\n"
        f"🎫 Status Kupon  : {status_kupon}\n"
        f"📦 Total Transaksi Sukses : <b>{total_sukses}</b>\n"
        f"👥 Total Referral          : <b>{total_ref}</b>\n"
        f"✅ Bonus Referral Cair     : <b>{bonus_cair}</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 <i>Semakin banyak transaksi sukses, tier kamu naik & poin makin gacor!</i>"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📦 Lihat Riwayat Pesanan", callback_data='menu_riwayat'),
        types.InlineKeyboardButton("🎁 Klaim Poin & Kupon", callback_data='menu_promo'),
        types.InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data='menu_utama')
    )
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                              parse_mode="HTML", reply_markup=markup,
                              disable_web_page_preview=True)
    except Exception:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup,
                         disable_web_page_preview=True)

def build_katalog_markup(part, l='id'):
    t = TRANSLATIONS.get(l, TRANSLATIONS['id'])
    markup = types.InlineKeyboardMarkup(row_width=2)

    if part == 1:
        paket_urutan = ['buy_natural', 'buy_light', 'buy_semisafe', 'buy_lifetimesafe']
        next_btn_text = t['next_1']
        nav_cb = 'katalog_part2'
    else:
        paket_urutan = ['buy_sultan', 'buy_pro', 'buy_semiprivate', 'buy_permanent']
        next_btn_text = t['prev_2']
        nav_cb = 'katalog_part1'

    for code in paket_urutan:
        nama, harga_angka, harga_str, poin, _ = MASTER_PAKET[code]
        stok = get_stock(code)
        if stok <= 0:
            stok_emoji = "❌"
        elif stok < 20:
            stok_emoji = "🔥"
        elif stok < 50:
            stok_emoji = "⚠️"
        else:
            stok_emoji = "📦"
        btn_label = f"🛒 {nama.split('(')[0].strip()}\n💰 {harga_str} | {stok_emoji} {stok}"
        markup.add(types.InlineKeyboardButton(btn_label, callback_data=code))

    markup.add(types.InlineKeyboardButton(next_btn_text, callback_data=nav_cb))
    markup.add(types.InlineKeyboardButton(t['back'], callback_data='menu_utama'))
    return markup

def build_katalog_text(part, user, l='id', coupon_status="AVAILABLE"):
    t = TRANSLATIONS.get(l, TRANSLATIONS['id'])
    if part == 1:
        paket_urutan = ['buy_natural', 'buy_light', 'buy_semisafe', 'buy_lifetimesafe']
        title = t['cat_title_1'].format(name=user.first_name)
    else:
        paket_urutan = ['buy_sultan', 'buy_pro', 'buy_semiprivate', 'buy_permanent']
        title = t['cat_title_2'].format(name=user.first_name)

    text = f"{title}\n\n{t['bonus_txt']}\n\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"

    for code in paket_urutan:
        nama, harga_angka, harga_str, poin, deskripsi = MASTER_PAKET[code]
        stok = get_stock(code)
        stok_label = format_stock_label(stok)
        # FIX v12: Flash Sale prioritas
        fs_diskon, _fs_sisa = get_active_flashsale()
        if fs_diskon > 0:
            harga_flashsale = int(harga_angka * (100 - fs_diskon) / 100)
            text += (
                f"👑 <b>{nama}</b>\n"
                f"   ⚡ <b>FLASH SALE {fs_diskon}%!</b>\n"
                f"   💵 Harga: <s>{harga_str}</s> <b>Rp {harga_flashsale:,}</b>\n"
                f"   🪙 Atau Tukar: <b>{poin} Poin</b>\n"
                f"   {stok_label}\n"
                f"   {deskripsi}\n\n"
            )
        elif coupon_status == "AVAILABLE":
            harga_promo = harga_angka - 10000
            text += (
                f"👑 <b>{nama}</b>\n"
                f"   💵 Harga: <s>{harga_str}</s> <b>Rp {harga_promo:,}</b> <i>(Hemat Rp 10.000)</i>\n"
                f"   🪙 Atau Tukar: <b>{poin} Poin</b>\n"
                f"   {stok_label}\n"
                f"   {deskripsi}\n\n"
            )
        else:
            text += (
                f"👑 <b>{nama}</b>\n"
                f"   💵 Harga: <b>{harga_str}</b>\n"
                f"   🪙 Atau Tukar: <b>{poin} Poin</b>\n"
                f"   {stok_label}\n"
                f"   {deskripsi}\n\n"
            )

    text += f"🪙 Saldo Poin Anda: <b>{get_user_points(user.id)} Poin</b>"
    if coupon_status == "AVAILABLE":
        text += "\n🎁 <b>INFO PROMO:</b> Anda punya hak potong harga spesial member baru otomatis!"
    return text

# =====================================================================================
#  BAGIAN 7: COMMAND HANDLERS
# =====================================================================================

@bot.message_handler(commands=['resetorders'])
def cmd_reset_orders(message):
    if not is_super_admin(message.chat.id):
        bot.reply_to(message, "⚠️ Perintah khusus admin utama!")
        return
    try:
        open(F_ORDERS, "w").close()
        bot.reply_to(message, "✅ Berhasil dikosongkan.")
    except Exception as e:
        bot.reply_to(message, f"Gagal: {e}")

@bot.message_handler(commands=['laporan', 'report'])
def cmd_laporan(message):
    if not is_any_admin(message.from_user.id):
        return
    try:
        today_str = datetime.now(WIB).strftime('%d-%m-%Y')
        sukses = 0
        ditolak = 0
        expired = 0
        pending = 0
        total_pendapatan = 0
        poin_ditukar = 0
        user_order_hari_ini = set()

        for parts in _read_all_orders():
            if len(parts) < 8:
                continue
            tanggal = parts[1]
            if tanggal != today_str:
                continue
            status = parts[7]
            user_order_hari_ini.add(parts[0])
            if status == "BERHASIL":
                sukses += 1
                pay = parts[9] if len(parts) > 9 else "TRANSFER"
                if pay == "POIN":
                    poin_ditukar += int(parts[10]) if len(parts) > 10 and parts[10].isdigit() else 0
                else:
                    total_pendapatan += int(''.join(ch for ch in parts[5] if ch.isdigit()) or 0)
            elif status == "DITOLAK":
                ditolak += 1
            elif status == "EXPIRED":
                expired += 1
            elif status == "PENDING":
                pending += 1

        text = (
            f"📊 <b>LAPORAN HARIAN</b>\n"
            f"🗓️ Tanggal: <b>{today_str}</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Transaksi Sukses : <b>{sukses}</b>\n"
            f"❌ Ditolak          : <b>{ditolak}</b>\n"
            f"⌛ Expired          : <b>{expired}</b>\n"
            f"⏳ Masih Pending    : <b>{pending}</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>Total Pendapatan</b>: Rp {total_pendapatan:,}\n"
            f"🪙 Poin Ditukar     : {poin_ditukar} Poin\n"
            f"👥 User Order Hari Ini: <b>{len(user_order_hari_ini)}</b>\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        bot.reply_to(message, text, parse_mode="HTML")
    except Exception as e:
        log_error("cmd_laporan", e)
        bot.reply_to(message, f"Gagal: {e}")

@bot.message_handler(commands=['stok', 'stock'])
def cmd_stok(message):
    if not is_any_admin(message.from_user.id):
        return
    try:
        stocks = _read_all_stocks()
        text = "📦 <b>STOK SEMUA PAKET</b>\n\n"
        for code, data in MASTER_PAKET.items():
            nama = data[0]
            stok = stocks.get(code, 0)
            text += f"• <b>{nama}</b>\n   Stok: <b>{stok}</b> unit\n\n"
        text += "💡 Command:\n/setstok [code] [angka]\n/restock\n/offstok [code]"
        bot.reply_to(message, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"Gagal: {e}")

@bot.message_handler(commands=['setstok'])
def cmd_setstok(message):
    if not is_super_admin(message.chat.id):
        return
    args = message.text.replace('/setstok', '').strip().split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ Format: /setstok buy_sultan 100")
        return
    code = args[0].strip()
    try:
        angka = int(args[1])
    except ValueError:
        bot.reply_to(message, "⚠️ Angka stok harus integer.")
        return
    if code not in MASTER_PAKET:
        bot.reply_to(message, f"⚠️ Kode paket tidak valid. Pakai salah satu: {', '.join(MASTER_PAKET.keys())}")
        return
    set_stock(code, angka)
    bot.reply_to(message, f"✅ Stok {MASTER_PAKET[code][0]} di-set ke {angka}.")

@bot.message_handler(commands=['restock'])
def cmd_restock(message):
    if not is_super_admin(message.chat.id):
        return
    try:
        stocks = _read_all_stocks()
        for code in stocks.keys():
            if code in MASTER_PAKET:
                stocks[code] = random.randint(STOCK_RESTOCK_MIN, STOCK_RESTOCK_MAX)
        _write_all_stocks(stocks)
        bot.reply_to(message, "✅ Semua stok berhasil di-restock ke range 150-250.")
    except Exception as e:
        bot.reply_to(message, f"Gagal: {e}")

@bot.message_handler(commands=['offstok'])
def cmd_offstok(message):
    if not is_super_admin(message.chat.id):
        return
    args = message.text.replace('/offstok', '').strip().split()
    if not args:
        bot.reply_to(message, "⚠️ Format: /offstok buy_sultan")
        return
    code = args[0].strip()
    if code not in MASTER_PAKET:
        bot.reply_to(message, "⚠️ Kode paket tidak valid.")
        return
    set_stock(code, 0)
    bot.reply_to(message, f"✅ Stok {MASTER_PAKET[code][0]} di-set 0 (HABIS).")

@bot.message_handler(commands=['stats', 'statistik'])
def cmd_stats(message):
    if not is_any_admin(message.from_user.id):
        bot.reply_to(message, "⚠️ Perintah khusus admin!")
        return
    try:
        # 1. Data user
        total_users = 0
        try:
            with open(F_USERS, "r") as f:
                total_users = len([ln for ln in f if ln.strip()])
        except FileNotFoundError:
            pass

        # 2. Data order
        today_str = datetime.now(WIB).strftime('%d-%m-%Y')
        total_order_all = 0
        total_order_hari = 0
        sukses = 0
        pending = 0
        ditolak = 0
        expired = 0
        total_pendapatan = 0
        paket_counter = {}

        for parts in _read_all_orders():
            if len(parts) < 8:
                continue
            total_order_all += 1
            tanggal = parts[1]
            status = parts[7]
            paket = parts[4]
            harga = parts[5]
            pay = parts[9] if len(parts) > 9 else "TRANSFER"

            if tanggal == today_str:
                total_order_hari += 1
                if status == "BERHASIL":
                    sukses += 1
                    if pay != "POIN":
                        total_pendapatan += int(''.join(ch for ch in harga if ch.isdigit()) or 0)
                    paket_counter[paket] = paket_counter.get(paket, 0) + 1
                elif status == "PENDING":
                    pending += 1
                elif status == "DITOLAK":
                    ditolak += 1
                elif status == "EXPIRED":
                    expired += 1

        # 3. Top 3 paket terlaris
        top_paket = sorted(paket_counter.items(), key=lambda x: x[1], reverse=True)[:3]
        top_paket_text = ""
        if top_paket:
            for idx, (nama, jml) in enumerate(top_paket, 1):
                top_paket_text += f"   {idx}. {nama} — <b>{jml}x</b>\n"
        else:
            top_paket_text = "   <i>Belum ada</i>\n"

        # 4. Total poin beredar
        total_poin = 0
        try:
            with open(F_POINTS, "r") as f:
                for line in f:
                    parts_p = line.strip().split('|')
                    if len(parts_p) == 2 and parts_p[1].isdigit():
                        total_poin += int(parts_p[1])
        except FileNotFoundError:
            pass

        # 5. Total voucher aktif
        vouchers = _read_all_vouchers()
        total_voucher_aktif = 0
        now_ts = int(time.time())
        for kode, v in vouchers.items():
            if v['terpakai'] < v['max'] and (v['expired'] == 0 or now_ts < v['expired']):
                total_voucher_aktif += 1

        # 6. Flash sale aktif
        fs_diskon, fs_sisa = get_active_flashsale()
        if fs_diskon > 0:
            jam_sisa = int(fs_sisa // 3600)
            menit_sisa = int((fs_sisa % 3600) // 60)
            fs_info = f"⚡ <b>AKTIF</b> — Diskon {fs_diskon}% ({jam_sisa}j {menit_sisa}m lagi)"
        else:
            fs_info = "❌ Tidak aktif"

        text = (
            f"📊 <b>DASHBOARD STATISTIK</b>\n"
            f"🗓️ {datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S WIB')}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👥 <b>Total User</b>          : <b>{total_users}</b>\n"
            f"📦 <b>Total Order All-Time</b> : <b>{total_order_all}</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>HARI INI</b>\n"
            f"   • Order Masuk      : <b>{total_order_hari}</b>\n"
            f"   ✅ Sukses           : <b>{sukses}</b>\n"
            f"   ⏳ Pending          : <b>{pending}</b>\n"
            f"   ❌ Ditolak          : <b>{ditolak}</b>\n"
            f"   ⌛ Expired          : <b>{expired}</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>Pendapatan Hari Ini</b> : <b>Rp {total_pendapatan:,}</b>\n"
            f"🪙 <b>Total Poin Beredar</b>  : <b>{total_poin:,} Poin</b>\n"
            f"🎫 <b>Voucher Aktif</b>        : <b>{total_voucher_aktif}</b>\n"
            f"⚡ <b>Flash Sale</b>           : {fs_info}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 <b>TOP 3 PAKET HARI INI:</b>\n"
            f"{top_paket_text}"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"💡 Admin: {ADMIN_USERNAME}"
        )
        bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        log_error("cmd_stats", e)
        bot.reply_to(message, f"❌ Gagal load stats: {e}")


@bot.message_handler(commands=['leaderboard', 'topbuyer', 'top'])
def cmd_leaderboard(message):
    if is_spam_command(message.chat.id):
        return
    save_user(message.chat.id)
    user = message.from_user
    try:
        # Hitung total transaksi sukses per user
        user_stats = {}
        for parts in _read_all_orders():
            if len(parts) < 8:
                continue
            if parts[7].strip() != "BERHASIL":
                continue
            chat_id_order = parts[0]
            harga = parts[5]
            # Skip kalau bayar poin (hitung nilai Rp aja)
            pay = parts[9] if len(parts) > 9 else "TRANSFER"
            if pay == "POIN":
                nilai = 0
            else:
                nilai = int(''.join(ch for ch in harga if ch.isdigit()) or 0)

            if chat_id_order not in user_stats:
                user_stats[chat_id_order] = {'total_order': 0, 'total_belanja': 0}
            user_stats[chat_id_order]['total_order'] += 1
            user_stats[chat_id_order]['total_belanja'] += nilai

        if not user_stats:
            bot.reply_to(message,
                         "🏆 <b>LEADERBOARD TOP BUYER</b>\n\n"
                         "❌ Belum ada transaksi sukses.\n\n"
                         "💡 Jadi yang pertama order di Pakel MlbbStore!",
                         parse_mode="HTML")
            return

        # Sort by total_order (bisa diganti total_belanja)
        sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['total_order'], reverse=True)[:10]

        text = "🏆 <b>LEADERBOARD TOP BUYER</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━\n\n"

        medals = ["🥇", "🥈", "🥉"]
        for idx, (cid, stat) in enumerate(sorted_users, 1):
            # Sensor username
            try:
                cid_int = int(cid)
                info = bot.get_chat(cid_int)
                if info.username:
                    uname = f"@{info.username}"
                    # Mask
                    if len(uname) > 6:
                        masked = uname[:4] + "***" + uname[-2:]
                    else:
                        masked = uname[:3] + "***"
                else:
                    nama = info.first_name or "User"
                    masked = nama[:3] + "***"
            except Exception:
                masked = f"User***{cid[-3:]}"

            # Highlight user sendiri
            marker = " 👈 (KAMU)" if cid == str(message.chat.id) else ""

            # Medali atau angka
            if idx <= 3:
                rank_icon = medals[idx - 1]
            else:
                rank_icon = f"<b>{idx}.</b>"

            text += (
                f"{rank_icon} {masked}{marker}\n"
                f"   📦 {stat['total_order']}x transaksi\n"
                f"   💰 Rp {stat['total_belanja']:,}\n\n"
            )

        # Cek rank user ini
        my_rank = None
        my_stat = user_stats.get(str(message.chat.id))
        all_sorted = sorted(user_stats.items(), key=lambda x: x[1]['total_order'], reverse=True)
        for idx, (cid, _) in enumerate(all_sorted, 1):
            if cid == str(message.chat.id):
                my_rank = idx
                break

        text += "━━━━━━━━━━━━━━━━━━━\n"
        if my_rank and my_stat:
            text += (
                f"📊 <b>Posisi Kamu:</b> #{my_rank}\n"
                f"   • Total Order: {my_stat['total_order']}x\n"
                f"   • Total Belanja: Rp {my_stat['total_belanja']:,}\n\n"
            )
        else:
            text += "💡 <i>Kamu belum pernah order. Yuk mulai sekarang biar masuk leaderboard!</i>\n\n"

        text += f"🔥 Terus belanja & jadi Top #1 di Pakel MlbbStore!"

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔄 Refresh", callback_data='refresh_leaderboard'),
            types.InlineKeyboardButton("💎 Lihat Katalog", callback_data='menu_katalog'),
            types.InlineKeyboardButton("⬅️ Menu Utama", callback_data='menu_utama')
        )
        bot.reply_to(message, text, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)
    except Exception as e:
        log_error("cmd_leaderboard", e)
        bot.reply_to(message, f"❌ Gagal load leaderboard: {e}")


@bot.message_handler(commands=['voucheruser', 'pvoucher'])
def cmd_voucher_user(message):
    if not is_super_admin(message.chat.id):
        bot.reply_to(message, "⚠️ Perintah khusus admin utama!")
        return

    args = message.text.replace('/voucheruser', '').replace('/pvoucher', '').strip().split()
    if len(args) < 2:
        bot.reply_to(message,
                     "⚠️ <b>Format:</b>\n"
                     "<code>/voucheruser [chat_id] [diskon] [durasi_jam]</code>\n\n"
                     "Contoh:\n"
                     "<code>/voucheruser 123456789 10000 24</code>\n\n"
                     "→ Diskon Rp 10.000, berlaku 24 jam, cuma buat user 123456789",
                     parse_mode="HTML")
        return

    try:
        target_chat_id = int(args[0].strip())
        diskon = int(args[1])
        durasi_jam = int(args[2]) if len(args) > 2 else 24
    except ValueError:
        bot.reply_to(message, "⚠️ Chat ID, diskon, & durasi harus angka!")
        return

    if diskon <= 0:
        bot.reply_to(message, "⚠️ Diskon harus > 0!")
        return
    if durasi_jam <= 0 or durasi_jam > 168:
        bot.reply_to(message, "⚠️ Durasi 1-168 jam!")
        return

    # Cek user exist
    try:
        target_info = bot.get_chat(target_chat_id)
    except Exception:
        bot.reply_to(message, f"❌ User <code>{target_chat_id}</code> ga ditemukan!", parse_mode="HTML")
        return

    # Buat kode voucher unik
    kode = f"PERSONAL{target_chat_id}_{random.randint(1000, 9999)}"

    # Simpan sebagai voucher publik juga (biar bisa divalidasi sistem)
    try:
        create_voucher(kode, diskon, 1, durasi_jam)  # max 1x pakai
    except Exception as e:
        bot.reply_to(message, f"❌ Gagal buat voucher: {e}")
        return

    # Save langsung ke user
    try:
        save_user_voucher(target_chat_id, kode, diskon)
    except Exception as e:
        bot.reply_to(message, f"❌ Gagal simpan ke user: {e}")
        return

    # Kirim notif ke user
    try:
        nama_user = target_info.first_name or "Kak"
        bot.send_message(
            target_chat_id,
            f"🎁 <b>VOUCHER SPESIAL UNTUKMU!</b> 🎁\n\n"
            f"Halo Kak {nama_user}!\n\n"
            f"Kamu dapet voucher eksklusif dari admin:\n\n"
            f"🎫 Kode: <code>{kode}</code>\n"
            f"💵 Diskon: <b>Rp {diskon:,}</b>\n"
            f"⏱️ Berlaku: <b>{durasi_jam} jam</b>\n\n"
            f"💡 Voucher udah otomatis aktif di akunmu!\n"
            f"🛒 Tinggal checkout paket & diskon kepakai otomatis.\n\n"
            f"📌 Buruan pakai sebelum expired ya!",
            parse_mode="HTML"
        )
        status = "✅ Terkirim ke user"
    except Exception as e:
        status = f"⚠️ User ga bisa di-DM: {e}"

    bot.reply_to(message,
                 f"✅ <b>VOUCHER PERSONAL DIBUAT!</b>\n\n"
                 f"👤 Target: {target_info.first_name} (<code>{target_chat_id}</code>)\n"
                 f"🎫 Kode: <code>{kode}</code>\n"
                 f"💵 Diskon: Rp {diskon:,}\n"
                 f"⏱️ Durasi: {durasi_jam} jam\n"
                 f"📌 Max Pakai: 1x (cuma buat user ini)\n\n"
                 f"📤 Status DM: {status}",
                 parse_mode="HTML")


@bot.message_handler(commands=['flashsale'])
def cmd_flashsale(message):
    if not is_super_admin(message.chat.id):
        return
    args = message.text.replace('/flashsale', '').strip().split()

    if len(args) < 1:
        bot.reply_to(message, "⚠️ Format: /flashsale [DISKON%] [DURASI_JAM]\nContoh: /flashsale 20 2\n\nAtau /flashsale stop buat matiin flash sale")
        return

    if args[0].lower() == 'stop':
        clear_flashsale()
        bot.reply_to(message, "✅ Flash sale dimatikan.")
        return

    if len(args) < 2:
        bot.reply_to(message, "⚠️ Format: /flashsale [DISKON%] [DURASI_JAM]\nContoh: /flashsale 20 2")
        return

    try:
        diskon = int(args[0])
        durasi_jam = int(args[1])
        if diskon <= 0 or diskon > 50:
            bot.reply_to(message, "⚠️ Diskon harus antara 1-50%!")
            return
        if durasi_jam <= 0 or durasi_jam > 24:
            bot.reply_to(message, "⚠️ Durasi harus antara 1-24 jam!")
            return
    except ValueError:
        bot.reply_to(message, "⚠️ Diskon & durasi harus angka!")
        return

    set_flashsale(diskon, durasi_jam)

    bot.reply_to(message, f"✅ <b>FLASH SALE AKTIF!</b>\n\n🔥 Diskon: <b>{diskon}%</b>\n⏱️ Durasi: <b>{durasi_jam} jam</b>\n\n📢 Sedang broadcast ke semua user...", parse_mode="HTML")

    threading.Thread(
        target=broadcast_flashsale,
        args=(diskon, durasi_jam),
        daemon=True
    ).start()


@bot.message_handler(commands=['buatvoucher'])
def cmd_buatvoucher(message):
    if not is_super_admin(message.chat.id):
        return
    args = message.text.replace('/buatvoucher', '').strip().split()
    if len(args) < 3:
        bot.reply_to(message, "⚠️ Format: /buatvoucher KODE DISKON MAX_PAKAI [DURASI_JAM]\nContoh: /buatvoucher PROMO10 10000 50 24")
        return
    kode = args[0].strip().upper()
    try:
        diskon = int(args[1])
        max_pakai = int(args[2])
        durasi_jam = int(args[3]) if len(args) > 3 else 24
    except ValueError:
        bot.reply_to(message, "⚠️ Diskon, max_pakai, dan durasi harus angka.")
        return

    # FIX v11: Validasi input
    if diskon <= 0:
        bot.reply_to(message, "⚠️ Diskon harus > 0!")
        return
    if max_pakai <= 0:
        bot.reply_to(message, "⚠️ Max Pakai harus > 0!")
        return
    if durasi_jam <= 0:
        bot.reply_to(message, "⚠️ Durasi harus > 0 jam!")
        return

    create_voucher(kode, diskon, max_pakai, durasi_jam)

    bot.reply_to(message,
                 f"✅ Voucher dibuat!\n\n"
                 f"🎫 Kode: <code>{kode}</code>\n"
                 f"💵 Diskon: Rp {diskon:,}\n"
                 f"📊 Max Pakai: {max_pakai} kali\n"
                 f"⏱️ Expired: {durasi_jam} jam\n\n"
                 f"📢 Sedang broadcast ke semua user...",
                 parse_mode="HTML")

    # Auto broadcast voucher baru (di thread background biar ga blocking)
    threading.Thread(
        target=broadcast_voucher_baru,
        args=(kode, diskon, max_pakai, durasi_jam),
        daemon=True
    ).start()

@bot.message_handler(commands=['listvoucher'])
def cmd_listvoucher(message):
    if not is_any_admin(message.from_user.id):
        return
    vouchers = _read_all_vouchers()
    if not vouchers:
        bot.reply_to(message, "Belum ada voucher.")
        return
    text = "🎫 <b>DAFTAR VOUCHER</b>\n\n"
    for kode, v in vouchers.items():
        sisa = v['max'] - v['terpakai']
        exp = datetime.fromtimestamp(v['expired'], WIB).strftime('%d-%m-%Y %H:%M') if v['expired'] > 0 else "-"
        text += (f"• <code>{kode}</code>\n"
                 f"  Diskon: Rp {v['diskon']:,}\n"
                 f"  Sisa: {sisa}/{v['max']}\n"
                 f"  Expired: {exp}\n\n")
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(commands=['hapusvoucher'])
def cmd_hapusvoucher(message):
    if not is_super_admin(message.chat.id):
        bot.reply_to(message, "⚠️ Perintah khusus admin utama!")
        return
    args = message.text.replace('/hapusvoucher', '').strip().split()
    if not args:
        bot.reply_to(message, "⚠️ Format: /hapusvoucher [KODE]\nContoh: /hapusvoucher PROMO10")
        return
    kode = args[0].strip().upper()
    try:
        vouchers = _read_all_vouchers()
        if kode not in vouchers:
            bot.reply_to(message, f"❌ Voucher <code>{kode}</code> tidak ditemukan.", parse_mode="HTML")
            return
        v = vouchers[kode]
        sisa = v['max'] - v['terpakai']
        del vouchers[kode]
        _write_all_vouchers(vouchers)
        bot.reply_to(message,
                     f"✅ <b>Voucher berhasil dihapus!</b>\n\n"
                     f"🎫 Kode: <code>{kode}</code>\n"
                     f"💵 Diskon: Rp {v['diskon']:,}\n"
                     f"📊 Sisa Kuota Sebelum Hapus: {sisa}/{v['max']}\n"
                     f"⚠️ <i>Voucher yang sudah di-redeem user tetap bisa dipakai (tersimpan di akun user masing-masing).</i>",
                     parse_mode="HTML")
    except Exception as e:
        log_error("cmd_hapusvoucher", e)
        bot.reply_to(message, f"❌ Gagal: {e}")

@bot.message_handler(commands=['hapusvoucherall'])
def cmd_hapusvoucherall(message):
    if not is_super_admin(message.chat.id):
        bot.reply_to(message, "⚠️ Perintah khusus admin utama!")
        return
    vouchers = _read_all_vouchers()
    if not vouchers:
        bot.reply_to(message, "Belum ada voucher untuk dihapus.")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Ya, Hapus Semua", callback_data="confirm_hapus_all_voucher"),
        types.InlineKeyboardButton("❌ Batal", callback_data="cancel_hapus_all_voucher")
    )
    daftar_kode = ", ".join([f"<code>{k}</code>" for k in vouchers.keys()])
    bot.reply_to(message,
                 f"⚠️ <b>KONFIRMASI HAPUS SEMUA VOUCHER</b>\n\n"
                 f"📋 Total voucher: <b>{len(vouchers)}</b>\n"
                 f"🎫 Daftar: {daftar_kode}\n\n"
                 "Apakah kamu yakin mau hapus <b>SEMUA</b> voucher?\n"
                 "Tindakan ini tidak bisa dibatalkan!",
                 reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=['expiredvoucher'])
def cmd_expiredvoucher(message):
    if not is_super_admin(message.chat.id):
        return
    try:
        vouchers = _read_all_vouchers()
        if not vouchers:
            bot.reply_to(message, "Belum ada voucher.")
            return
        now_ts = time.time()
        hapus = []
        for kode, v in vouchers.items():
            if v['expired'] > 0 and now_ts > v['expired']:
                hapus.append(kode)
        if not hapus:
            bot.reply_to(message, "✅ Tidak ada voucher expired.")
            return
        for kode in hapus:
            del vouchers[kode]
        _write_all_vouchers(vouchers)
        daftar = ", ".join([f"<code>{k}</code>" for k in hapus])
        bot.reply_to(message,
                     f"✅ <b>Berhasil hapus {len(hapus)} voucher expired!</b>\n\n"
                     f"🎫 Daftar: {daftar}",
                     parse_mode="HTML")
    except Exception as e:
        log_error("cmd_expiredvoucher", e)
        bot.reply_to(message, f"❌ Gagal: {e}")

@bot.message_handler(commands=['cekvoceruser'])
def cmd_cek_voucher_user(message):
    if not is_super_admin(message.chat.id):
        return
    args = message.text.replace('/cekvoceruser', '').strip().split()
    if not args:
        bot.reply_to(message, "⚠️ Format: /cekvoceruser [chat_id]")
        return
    target_id = args[0].strip()
    try:
        if not os.path.exists(F_USER_VOUCHER):
            bot.reply_to(message, "File user_voucher.txt belum ada.")
            return
        rows = []
        with open(F_USER_VOUCHER, "r") as f:
            for ln in f:
                parts = ln.strip().split('|')
                if len(parts) >= 3 and parts[0] == target_id:
                    rows.append(parts)
        if not rows:
            bot.reply_to(message, f"User {target_id} tidak punya voucher aktif.")
            return
        text = f"🎫 <b>VOUCHER USER {target_id}</b>\n\n"
        for p in rows:
            tag = p[1]
            if tag.startswith("VOUCHER_"):
                kode = tag.replace("VOUCHER_", "")
                text += f"• Voucher: <code>{kode}</code>\n  Diskon: Rp {int(p[2]):,}\n\n"
            elif tag.startswith("DISKON"):
                text += f"• Lucky Draw Diskon: {tag.replace('DISKON', '')}%\n\n"
        bot.reply_to(message, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")
# FIX v11: Command admin baru — cek suspicious & reset warning
@bot.message_handler(commands=['ceksuspicious'])
def cmd_cek_suspicious(message):
    if not is_super_admin(message.chat.id):
        return
    if not os.path.exists(F_SUSPICIOUS):
        bot.reply_to(message, "✅ Belum ada aktivitas mencurigakan.")
        return
    with open(F_SUSPICIOUS, "r") as f:
        lines = [ln for ln in f.read().strip().split("\n") if ln]
    if not lines:
        bot.reply_to(message, "✅ Kosong.")
        return
    text = "🚨 <b>LOG MENCURIGAKAN (20 terakhir)</b>\n\n"
    for ln in lines[-20:]:
        text += f"• {ln}\n"
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(commands=['resetwarning'])
def cmd_reset_warning(message):
    if not is_super_admin(message.chat.id):
        return
    args = message.text.replace('/resetwarning', '').strip().split()
    if not args:
        bot.reply_to(message, "⚠️ Format: /resetwarning [chat_id]")
        return
    reset_suspicious(args[0])
    bot.reply_to(message, f"✅ Warning user {args[0]} direset.")
@bot.message_handler(commands=['grafikpaket', 'toppaket'])
def cmd_grafik_paket(message):
    if not is_any_admin(message.from_user.id):
        bot.reply_to(message, "⚠️ Perintah khusus admin!")
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        args = message.text.replace('/grafikpaket', '').replace('/toppaket', '').strip().lower()
        filter_mode = args if args in ['semua', 'bulan', 'minggu'] else 'semua'

        paket_counter = {}
        total_order = 0
        now = datetime.now(WIB)

        for parts in _read_all_orders():
            if len(parts) < 8:
                continue
            if parts[7].strip() != "BERHASIL":
                continue
            if filter_mode != 'semua':
                try:
                    order_time = datetime.strptime(parts[1], '%d-%m-%Y')
                    selisih = (now - order_time.replace(tzinfo=WIB)).days
                    if filter_mode == 'bulan' and selisih > 30:
                        continue
                    if filter_mode == 'minggu' and selisih > 7:
                        continue
                except Exception:
                    continue

            paket = parts[4]
            paket_counter[paket] = paket_counter.get(paket, 0) + 1
            total_order += 1

        if not paket_counter:
            bot.reply_to(message,
                         "📊 <b>GRAFIK PAKET TERLARIS</b>\n\n"
                         "❌ Belum ada transaksi sukses.",
                         parse_mode="HTML")
            return

        sorted_paket = sorted(paket_counter.items(), key=lambda x: x[1], reverse=True)
        top_paket = sorted_paket[:10]

        nama_labels = []
        jumlah_data = []
        for nama, jml in top_paket:
            nama_singkat = nama.split('(')[0].strip()
            if len(nama_singkat) > 18:
                nama_singkat = nama_singkat[:15] + "..."
            nama_labels.append(nama_singkat)
            jumlah_data.append(jml)

        fig, ax = plt.subplots(figsize=(10, 5.5))
        colors = plt.cm.viridis([i / max(len(nama_labels), 1) for i in range(len(nama_labels))])
        bars = ax.bar(range(len(nama_labels)), jumlah_data, color=colors)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}x', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')

        ax.set_xlabel('Paket', fontsize=11, fontweight='bold')
        ax.set_ylabel('Jumlah Penjualan', fontsize=11, fontweight='bold')
        ax.set_title(f'📊 Top Paket Terlaris (Filter: {filter_mode.title()})',
                     fontsize=13, fontweight='bold', pad=15)
        ax.set_xticks(range(len(nama_labels)))
        ax.set_xticklabels(nama_labels, rotation=30, ha='right', fontsize=9)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)

        caption = (
            f"📊 <b>GRAFIK PAKET TERLARIS</b>\n"
            f"🗓️ Filter: <b>{filter_mode.title()}</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🏆 <b>TOP 5 PAKET:</b>\n"
        )
        for idx, (nama, jml) in enumerate(top_paket[:5], 1):
            medal = ["🥇", "🥈", "🥉"][idx-1] if idx <= 3 else f"<b>{idx}.</b>"
            caption += f"{medal} {nama} — <b>{jml}x</b>\n"

        caption += (
            "━━━━━━━━━━━━━━━━━━━\n"
            f"📦 Total Order Sukses: <b>{total_order}</b>\n"
            f"💡 Kirim <code>/grafikpaket bulan</code> buat filter bulanan"
        )

        bot.send_photo(message.chat.id, buf, caption=caption, parse_mode="HTML")
    except Exception as e:
        log_error("cmd_grafik_paket", e)
        bot.reply_to(message, f"❌ Gagal bikin grafik: {e}\n\n⚠️ Pastikan <code>matplotlib</code> terinstall:\n<code>pip install matplotlib</code>", parse_mode="HTML")


@bot.message_handler(commands=['grafik'])
def cmd_grafik_bulanan(message):
    if not is_any_admin(message.from_user.id):
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        daily_total = {}
        for o in _read_all_orders():
            if o[7] != "BERHASIL":
                continue
            daily_total[o[1]] = daily_total.get(o[1], 0) + int(''.join(ch for ch in o[5] if ch.isdigit()) or 0)
        if not daily_total:
            bot.reply_to(message, "Belum ada transaksi sukses.")
            return
        plt.figure(figsize=(8, 4))
        plt.plot(sorted(daily_total.keys()),
                 [daily_total[t] for t in sorted(daily_total.keys())], marker='o')
        plt.title("Tren Penjualan")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption="📈 Grafik Penjualan.")
    except Exception as e:
        bot.reply_to(message, f"Gagal (pastikan matplotlib terinstall): {e}")

@bot.message_handler(commands=['poin'])
def admin_add_points(message):
    if message.chat.id != ADMIN_TELEGRAM_ID:
        bot.reply_to(message, "⚠️ Perintah khusus admin utama!")
        return
    args = message.text.replace('/poin', '').strip().split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ Format: /poin @user 1000")
        return
    target_username = args[0].strip()
    try:
        jumlah_tambah = int(args[1])
    except ValueError:
        bot.reply_to(message, "⚠️ Jumlah poin harus angka.")
        return
    if not target_username.startswith('@'):
        bot.reply_to(message, "⚠️ Format harus @username")
        return
    target_chat_id = None
    try:
        with open(F_USERS, "r") as f:
            for line in f:
                uid = line.strip()
                if uid and not uid.startswith('-'):
                    try:
                        chat_info = bot.get_chat(int(uid))
                        uname = f"@{chat_info.username}" if chat_info.username else ""
                        if uname.lower() == target_username.lower():
                            target_chat_id = int(uid)
                            break
                    except Exception:
                        pass
    except FileNotFoundError:
        pass
    if not target_chat_id:
        bot.reply_to(message, "User tidak ditemukan.")
        return
    try:
        chat_info = bot.get_chat(target_chat_id)
        add_user_points(target_chat_id, jumlah_tambah, "Penambahan manual admin")
        total_pasti = get_user_points(target_chat_id)
        bot.reply_to(message, f"✅ +{jumlah_tambah} poin ke @{chat_info.username or target_username}. Total: {total_pasti} poin.")
        try:
            bot.send_message(target_chat_id,
                             f"🎁 <b>ADMIN MENAMBAHKAN POIN!</b>\n\n+{jumlah_tambah} Poin\nTotal: <b>{total_pasti} Poin</b>",
                             parse_mode="HTML")
        except Exception:
            pass
    except Exception:
        bot.reply_to(message, "Gagal menambahkan poin.")

@bot.message_handler(commands=['bc', 'broadcast'])
def broadcast_message(message):
    if not is_super_admin(message.chat.id):
        return
    pesan_bc = message.text.replace('/bc', '').replace('/broadcast', '').strip()
    if not pesan_bc:
        bot.reply_to(message, "⚠️ Format: /bc pesan...")
        return
    try:
        with open(F_USERS, "r") as f:
            users = [line.strip() for line in f.read().splitlines() if line.strip()]
    except FileNotFoundError:
        bot.reply_to(message, "Belum ada user.")
        return
    success = 0
    for chat_id in set(users):
        try:
            bot.send_message(chat_id, f"📢 <b>PENGUMUMAN RESMI</b>\n\n{pesan_bc}", parse_mode="HTML")
            success += 1
            time.sleep(0.05)
        except Exception:
            pass
    bot.send_message(message.chat.id, f"✅ Broadcast selesai. Berhasil: {success}")

@bot.message_handler(commands=['bcs'])
def broadcast_buyers_only(message):
    if not is_super_admin(message.chat.id):
        return
    pesan_bcs = message.text.replace('/bcs', '').strip()
    if not pesan_bcs:
        bot.reply_to(message, "⚠️ Format: /bcs pesan...")
        return
    buyer_ids = set()
    try:
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[7].strip() == "BERHASIL":
                    buyer_ids.add(parts[0].strip())
    except FileNotFoundError:
        pass
    success = 0
    for chat_id in buyer_ids:
        try:
            bot.send_message(chat_id, f"💎 <b>INFO KHUSUS VIP</b>\n\n{pesan_bcs}", parse_mode="HTML")
            success += 1
            time.sleep(0.05)
        except Exception:
            pass
    bot.send_message(message.chat.id, f"✅ Broadcast VIP selesai. Berhasil: {success}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if is_spam_command(message.chat.id):
        return
    chat_id = message.chat.id
    if is_banned(chat_id):
        return
    save_user(chat_id)
    user = message.from_user
    l = get_lang(user)

    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        ref_id = args[1].replace("ref_", "").strip()
        if ref_id.isdigit():
            register_referral(ref_id, chat_id)

    user_points = get_user_points(chat_id)
    welcome_text = build_welcome_text(user, user_points, l)
    markup = build_main_menu_markup(l)
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=['riwayat', 'history'])
def cmd_riwayat(message):
    if is_spam_command(message.chat.id):
        return
    save_user(message.chat.id)
    user = message.from_user
    l = get_lang(user)
    get_latest_user_order_data(message.chat.id)
    orders = get_user_orders(message.chat.id)
    if not orders:
        text = (f"📋 RIWAYAT PESANAN SAYA (Kak {user.first_name})\n\n"
                "❌ Belum ada riwayat pesanan tercatat.")
    else:
        text = f"📋 <b>RIWAYAT PESANAN SAYA (Kak {user.first_name})</b>\n\n"
        for idx, o in enumerate(orders[-5:], 1):
            st = {"BERHASIL": "✅ BERHASIL", "DITOLAK": "❌ DITOLAK",
                  "CANCELLED": "❌ DIBATALKAN", "EXPIRED": "⌛ EXPIRED"}.get(o['status'], "⏳ PENDING")
            text += (f"<b>{idx}. {o['paket']}</b>\n   • Harga: {o['harga']}\n"
                     f"   • Resi: <code>{o['resi']}</code>\n   • Status: {st}\n\n")
    bot.reply_to(message, text, reply_markup=get_back_markup(l), parse_mode="HTML",
                 disable_web_page_preview=True)

@bot.message_handler(commands=['cekresi', 'resi'])
def cmd_cekresi(message):
    if is_spam_command(message.chat.id):
        return
    save_user(message.chat.id)
    user = message.from_user
    chat_id = message.chat.id
    l = get_lang(user)

    # FIX v13: Cek kalau ada argumen resi
    args = message.text.replace('/cekresi', '').replace('/resi', '').strip()
    # Kalau ga ada argumen, kasih instruksi
    if not args:
        text = (f"🔍 <b>CEK STATUS RESI</b> (Kak {user.first_name})\n\n"
                f"Cara pakai:\n"
                f"<code>/cekresi PKL-MLBB-12345</code>\n\n"
                f"Atau kirim screenshot bukti transfer ke bot ini.\n\n"
                f"💬 Admin: {ADMIN_USERNAME}")
        bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)
        return

    # Cari order berdasarkan resi
    resi_target = args.strip().upper()
    found = None
    for parts in _read_all_orders():
        if len(parts) >= 8 and parts[6].strip().upper() == resi_target:
            found = parts
            break

    # Cek kalau order milik user lain
    if found and found[0] != str(chat_id):
        # Admin bisa cek punya orang
        if not is_any_admin(chat_id):
            bot.reply_to(message,
                         f"❌ <b>Resi Tidak Ditemukan!</b>\n\n"
                         f"🔑 Resi: <code>{resi_target}</code>\n\n"
                         f"Pastikan resi benar & milik akunmu ya Kak.",
                         parse_mode="HTML")
            return

    if not found:
        bot.reply_to(message,
                     f"❌ <b>Resi Tidak Ditemukan!</b>\n\n"
                     f"🔑 Resi: <code>{resi_target}</code>\n\n"
                     f"Pastikan resi benar. Cek /riwayat buat liat resi kamu.",
                     parse_mode="HTML")
        return

    # Parse data order
    chat_id_order = found[0]
    tanggal = found[1]
    hari = found[2]
    jam = found[3]
    paket = found[4]
    harga = found[5]
    resi = found[6]
    status_db = found[7]
    pay_method = found[9] if len(found) > 9 else "TRANSFER"

    # Mapping status ke emoji
    status_emoji = {
        "BERHASIL": "✅ BERHASIL",
        "PENDING": "⏳ PENDING (Menunggu ACC)",
        "DITOLAK": "❌ DITOLAK",
        "EXPIRED": "⌛ EXPIRED",
        "CANCELLED": "🚫 DIBATALKAN",
    }.get(status_db, f"❓ {status_db}")

    text = (
        f"🔍 <b>DETAIL RESI</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🔑 Resi: <code>{resi}</code>\n"
        f"📦 Paket: <b>{paket}</b>\n"
        f"💵 Harga: <b>{harga}</b>\n"
        f"💳 Metode: <b>{pay_method}</b>\n"
        f"📅 Tanggal: <b>{hari}, {tanggal}</b>\n"
        f"⏱️ Jam: <b>{jam}</b>\n"
        f"📊 Status: <b>{status_emoji}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
    )

    if status_db == "PENDING":
        text += "💡 <i>Pesananmu masih menunggu ACC admin. Kirim bukti transfer ke bot ini kalau belum!</i>"
    elif status_db == "BERHASIL":
        text += "🎉 <i>Pesanan sukses! Cek DM admin buat klaim script-nya ya.</i>"
    elif status_db == "DITOLAK":
        text += "❌ <i>Pesanan ditolak. Hubungi admin buat info lebih lanjut.</i>"
    elif status_db == "EXPIRED":
        text += "⌛ <i>Pesanan expired karena lewat batas waktu. Silakan order ulang ya Kak!</i>"
    elif status_db == "CANCELLED":
        text += "🚫 <i>Pesanan dibatalkan. Poinmu tetap aman!</i>"

    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)

@bot.message_handler(commands=['katalog'])
def cmd_katalog(message):
    if is_spam_command(message.chat.id):
        return
    try:
        save_user(message.chat.id)
        user = message.from_user
        l = get_lang(user)
        coupon_status = get_user_coupon_status(message.chat.id)
        markup = build_katalog_markup(1, l)
        katalog_text = build_katalog_text(1, user, l, coupon_status)
        bot.send_message(message.chat.id, katalog_text, reply_markup=markup, parse_mode="HTML",
                         disable_web_page_preview=True)
    except Exception as e:
        log_error("cmd_katalog", e)
        bot.reply_to(message, "Terjadi kesalahan saat memuat katalog.")

@bot.message_handler(commands=['sc'])
def cmd_sc_interactive(message):
    if not is_super_admin(message.chat.id):
        return
    save_user(message.chat.id)
    args = message.text.replace('/sc', '').strip()
    if not args:
        bot.reply_to(message, "⚠️ Format: /sc @UsernamePembeli")
        return
    target_buyer = args if args.startswith('@') else f"@{args}"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for code, data_paket in MASTER_PAKET.items():
        nama, harga_angka, harga_str, poin, _ = data_paket
        markup.add(types.InlineKeyboardButton(f"💎 {nama} — {harga_str}", callback_data=f"sc_{code}|{target_buyer}"))
    bot.reply_to(message, f"🎯 Target: <b>{target_buyer}</b>\n👇 Pilih paket:",
                 reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=['scp'])
def cmd_scp_interactive(message):
    if message.chat.id != ADMIN_TELEGRAM_ID:
        return
    save_user(message.chat.id)
    args = message.text.replace('/scp', '').strip()
    if not args:
        bot.reply_to(message, "⚠️ Format: /scp @UsernamePembeli")
        return
    target_buyer = args if args.startswith('@') else f"@{args}"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for code, data_paket in MASTER_PAKET.items():
        nama, harga_angka, harga_str, poin, _ = data_paket
        markup.add(types.InlineKeyboardButton(f"🪙 {nama} — {poin} Poin", callback_data=f"scp_{code}|{target_buyer}"))
    bot.reply_to(message, f"🎯 Target: <b>{target_buyer}</b>\n👇 Pilih paket (poin):",
                 reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=['testi', 'push'])
def admin_push_testi(message):
    if not is_any_admin(message.from_user.id):
        return
    try:
        bot.send_message(chat_id=GROUP_CHAT_ID, text=generate_single_testimonial(),
                         message_thread_id=GROUP_TOPIC_ID, disable_web_page_preview=True)
        bot.reply_to(message, "✅ Testimoni terkirim ke grup. (Stok otomatis turun!)")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Gagal: {e}")

# =====================================================================================
#  BAGIAN 8: CALLBACK HANDLERS
# =====================================================================================

def mask_username(username):
    if not username:
        return "@Buyer***"
    clean_uname = username.strip()
    if not clean_uname.startswith('@'):
        clean_uname = f"@{clean_uname}"
    name_part = clean_uname[1:]
    if len(name_part) <= 4:
        masked = name_part[:2] + "***"
    else:
        keep_len = max(3, len(name_part) // 2)
        masked = name_part[:keep_len] + "***"
    return f"@{masked}"

def generate_real_testimonial(chat_id, resi_target):
    now = datetime.now(WIB)
    current_hour = now.hour
    if 4 <= current_hour < 11:
        waktu_ket = "pagi ini"
    elif 11 <= current_hour < 15:
        waktu_ket = "siang ini"
    elif 15 <= current_hour < 18:
        waktu_ket = "sore ini"
    else:
        waktu_ket = "malam ini"
    jam_str = now.strftime('%H:%M WIB')
    try:
        chat_info = bot.get_chat(int(chat_id))
        raw_username = f"@{chat_info.username}" if chat_info.username else chat_info.first_name
    except Exception:
        raw_username = "@BuyerMlbb"
    masked_name = mask_username(raw_username)
    detail_paket = "VIP Package"
    detail_harga = "Rp 100.000"
    pay_method_label = "TRANSFER MANUAL"
    try:
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 11 and parts[6].strip() == resi_target.strip():
                    detail_paket = parts[4]
                    detail_harga = parts[5]
                    pay_method = parts[9] if len(parts) > 9 else "TRANSFER"
                    pay_method_label = "REDEEMED VIA LOYALTY POINTS 🪙" if pay_method == "POIN" else "SUCCESS & SCRIPT DELIVERED 💳"
                    break
    except Exception as e:
        log_error("generate_real_testimonial", e)
    return (
        "🚨 <b>REAL-TIME TRANSACTION REPORT</b> 🚨\n\n"
        f"✅ Buyer ID: {masked_name}\n"
        f"📦 Item Purchased: {detail_paket}\n"
        f"💵 Price / Method: {detail_harga} ({pay_method_label})\n"
        f"⏱️ Time: {jam_str} ({waktu_ket})\n"
        f"🔒 Status: BERHASIL & TERKIRIM\n\n"
        "🔥 Terima kasih telah berbelanja di Official Pakel MlbbStore! Aman, lancar, & anti-detect. Mau order juga? Langsung sikat ke bot ya! 👇\n"
        f"🤖 Bot Store: @{bot.get_me().username}"
    )

def loading_toast(call_id, text="⏳ Mohon tunggu sebentar, sistem sedang memproses permintaanmu..."):
    try:
        bot.answer_callback_query(call_id, text=text, show_alert=False)
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: True)
def callback_handler_master(call):
    save_user(call.message.chat.id)
    user = call.from_user
    l = get_lang(user)
    t = TRANSLATIONS.get(l, TRANSLATIONS['id'])
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    if is_banned(chat_id):
        return

    if is_spam_callback(chat_id):
        bot.answer_callback_query(call.id, "⚠️ Santai kak, jangan spam 🙏")
        return

    lock_key = f"{chat_id}_{data}"
    if lock_key in processing_lock:
        bot.answer_callback_query(call.id, "⏳ Diproses...")
        return
    processing_lock.add(lock_key)

    try:
        # --- KONFIRMASI HAPUS VOUCHER ALL ---
        if data == 'confirm_hapus_all_voucher':
            if not is_super_admin(chat_id):
                bot.answer_callback_query(call.id, text="⚠️ Khusus admin!", show_alert=True)
                return
            try:
                vouchers = _read_all_vouchers()
                jumlah = len(vouchers)
                if os.path.exists(F_VOUCHERS):
                    with open(F_VOUCHERS, "w") as f:
                        f.write("")
                bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                      text=f"✅ <b>{jumlah} voucher berhasil dihapus semua!</b>",
                                      parse_mode="HTML")
                bot.answer_callback_query(call.id, text="Semua voucher dihapus!")
            except Exception as e:
                log_error("confirm_hapus_all_voucher", e)
                bot.answer_callback_query(call.id, text=f"Error: {e}", show_alert=True)
            return

        elif data == 'cancel_hapus_all_voucher':
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                  text="❌ <b>Hapus voucher dibatalkan.</b>",
                                  parse_mode="HTML")
            bot.answer_callback_query(call.id, text="Dibatalkan")
            return

        # --- ADMIN ACTIONS ---
        if data.startswith(('acc_', 'tolak_', 'acc|', 'tolak|', 'apoin|', 'tpoin|')):
            loading_toast(call.id, "⏳ Memverifikasi transaksi...")
            try:
                sep = '|' if '|' in data else '_'
                parts = data.split(sep)
                if len(parts) < 2:
                    bot.answer_callback_query(call.id, text="Format tombol tidak valid.", show_alert=True)
                    return
                action = parts[0].replace('_', '')
                resi_code = parts[1] if action in ['apoin', 'tpoin'] else (parts[2] if len(parts) > 2 else parts[1])
                target_user_id = parts[1] if action not in ['apoin', 'tpoin'] and len(parts) > 2 else None
                current_db_status = ""
                try:
                    with open(F_ORDERS, "r") as f:
                        for line in f:
                            p = line.strip().split('|')
                            if len(p) >= 8 and p[6].strip() == resi_code.strip():
                                target_user_id = p[0]
                                current_db_status = p[7].strip()
                                break
                except Exception:
                    pass
                if not target_user_id:
                    bot.answer_callback_query(call.id, text="Resi tidak ditemukan!", show_alert=True)
                    return
                if current_db_status != "PENDING":
                    bot.answer_callback_query(call.id, text=f"⚠️ Sudah diproses: {current_db_status}!", show_alert=True)
                    return
                original_text = call.message.caption or call.message.text or ""
                if action in ('acc', 'apoin'):
                    p_points_val = 0
                    if action == 'apoin':
                        try:
                            with open(F_ORDERS, "r") as f:
                                for line in f:
                                    p = line.strip().split('|')
                                    if len(p) >= 11 and p[6].strip() == resi_code.strip():
                                        p_points_val = int(p[10]) if p[10].isdigit() else 0
                                        break
                        except Exception:
                            pass
                        current_user_pts = get_user_points(target_user_id)
                        if current_user_pts >= p_points_val:
                            reduce_user_points(target_user_id, p_points_val, "Penukaran poin paket VIP")
                        else:
                            bot.answer_callback_query(call.id, text="Poin pembeli tidak cukup!", show_alert=True)
                            return
                    update_order_status_by_resi(resi_code, "BERHASIL")
                    try:
                        auto_testi_message = generate_real_testimonial(target_user_id, resi_code)
                        bot.send_message(chat_id=GROUP_CHAT_ID, text=auto_testi_message,
                                         message_thread_id=GROUP_TOPIC_ID,
                                         parse_mode="HTML", disable_web_page_preview=True)
                    except Exception as e:
                        log_error("auto_send_testi", e)
                    # FIX v13: Auto-forward ke channel testi
                    # (DIHAPUS: bentrok dengan generate_real_testimonial yang udah kirim ke grup yang sama)
                    # threading.Thread(
                    #     target=forward_proof_to_channel,
                    #     args=(target_user_id, resi_code),
                    #     daemon=True
                    # ).start()
                    status_label = (f"✅ DI-ACC ADMIN (Poin Dipotong {p_points_val})"
                                    if action == 'apoin' else
                                    "✅ TELAH DI-ACC ADMIN")
                    new_admin_text = original_text + f"\n\n<b>STATUS: {status_label}</b>"
                    if call.message.content_type == 'photo':
                        bot.edit_message_caption(chat_id=chat_id, message_id=message_id,
                                                 caption=new_admin_text, parse_mode="HTML", reply_markup=None)
                    else:
                        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                              text=new_admin_text, parse_mode="HTML", reply_markup=None)
                    detail_paket, detail_harga, waktu_beli = "VIP Package", "Rp 100.000", datetime.now(WIB).strftime('%d-%m-%Y, %H:%M:%S WIB')
                    try:
                        with open(F_ORDERS, "r") as f:
                            for line in f:
                                p = line.strip().split('|')
                                if len(p) >= 8 and p[6].strip() == resi_code.strip():
                                    detail_paket, detail_harga = p[4], p[5]
                                    waktu_beli = f"{p[1]}, {p[3]}"
                                    break
                    except Exception:
                        pass
                    bot.send_message(target_user_id,
                                     "🛒 <b>PakelMlbbStore:</b>\n"
                                     "🎉 <b>PEMBAYARAN ANDA TELAH DI-ACC ADMIN!</b> 🎉\n\n"
                                     f"🔑 No Resi: <code>{resi_code}</code>\n"
                                     "Status: <b>BERHASIL</b>. Selamat menikmati script-nya!\n\n"
                                     "📋 <b>SALIN FORMAT DI BAWAH & KIRIM KE ADMIN:</b>",
                                     parse_mode="HTML")
                    template_chat_admin = (
                        "🔥 KONFIRMASI KLAIM SCRIPT VIP 🔥\n"
                        f"📦 Paket: {detail_paket}\n"
                        f"💵 Harga: {detail_harga}\n"
                        f"🔑 No Resi: {resi_code}\n"
                        f"⏱️ Waktu Order: {waktu_beli}\n"
                        "Status: Lunas & Sudah di-ACC Bot.\n"
                        "Mohon kirimkan link/file script-nya ya Kak. Terima kasih! 🙏"
                    )
                    bot.send_message(target_user_id, f"<code>{template_chat_admin}</code>", parse_mode="HTML")
                    markup_rating = types.InlineKeyboardMarkup(row_width=5)
                    markup_rating.add(
                        types.InlineKeyboardButton("⭐ 1", callback_data=f"rate|1|{resi_code}"),
                        types.InlineKeyboardButton("⭐ 2", callback_data=f"rate|2|{resi_code}"),
                        types.InlineKeyboardButton("⭐ 3", callback_data=f"rate|3|{resi_code}"),
                        types.InlineKeyboardButton("⭐ 4", callback_data=f"rate|4|{resi_code}"),
                        types.InlineKeyboardButton("⭐ 5", callback_data=f"rate|5|{resi_code}")
                    )
                    bot.send_message(target_user_id,
                                     f"⭐ <b>BAGAIMANA PELAYANAN KAMI?</b>\n\nResi: <code>{resi_code}</code>\nBerikan penilaian:",
                                     reply_markup=markup_rating, parse_mode="HTML")
                elif action in ('tolak', 'tpoin'):
                    update_order_status_by_resi(resi_code, "DITOLAK")
                    new_admin_text = original_text + "\n\n<b>STATUS: ❌ DITOLAK</b>"
                    if call.message.content_type == 'photo':
                        bot.edit_message_caption(chat_id=chat_id, message_id=message_id,
                                                 caption=new_admin_text, parse_mode="HTML", reply_markup=None)
                    else:
                        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                              text=new_admin_text, parse_mode="HTML", reply_markup=None)
                    bot.send_message(target_user_id,
                                     f"❌ <b>PEMBAYARAN DITOLAK</b>\n\nResi: <code>{resi_code}</code>\nKupon dikembalikan. Hubungi: {ADMIN_USERNAME}",
                                     parse_mode="HTML")
            except Exception as e:
                log_error("callback_admin", e)
                bot.answer_callback_query(call.id, text=f"Error: {e}", show_alert=True)
            return

        # --- MENU UTAMA ---
        if data == 'menu_utama':
            loading_toast(call.id, "⏳ Mengembalikan ke menu...")
            user_points = get_user_points(chat_id)
            markup = build_main_menu_markup(l)
            text = build_welcome_text(user, user_points, l)
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                      reply_markup=markup, parse_mode="HTML",
                                      disable_web_page_preview=True)
            except Exception:
                bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode="HTML")
            return

        elif data == 'menu_referral':
            loading_toast(call.id, "⏳ Memuat data referral...")
            _kirim_poin_referral(chat_id, message_id, l)
            return

        elif data == 'menu_profil':
            loading_toast(call.id, "⏳ Memuat profil...")
            _kirim_profil_akun(chat_id, message_id, user, l)
            return

        elif data == 'menu_lucky':
            loading_toast(call.id, "⏳ Memuat Lucky Draw...")
            can_spin = can_spin_now(chat_id)
            if can_spin:
                text = (
                    "🎰 <b>LUCKY DRAW HARIAN</b> 🎰\n\n"
                    "Kamu punya <b>1 kesempatan spin</b> hari ini!\n\n"
                    "🎁 Hadiah yang bisa didapat:\n"
                    "• 🪙 Poin 5 – 50\n"
                    "• 🎁 Diskon 5% – 10%\n"
                    "• 💎 Paket Semi-Safe GRATIS (rare!)\n\n"
                    "Klik tombol di bawah untuk spin!"
                )
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("🎰 SPIN SEKARANG!", callback_data='spin_now'),
                    types.InlineKeyboardButton(t['back'], callback_data='menu_utama')
                )
            else:
                sisa = get_remaining_spin_time(chat_id)
                text = (
                    "🎰 <b>LUCKY DRAW HARIAN</b> 🎰\n\n"
                    "❌ Kamu sudah spin hari ini.\n\n"
                    f"⏰ Spin berikutnya: <b>{sisa}</b>\n\n"
                    "💡 Balik lagi besok buat spin gratis!"
                )
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(types.InlineKeyboardButton(t['back'], callback_data='menu_utama'))
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                      parse_mode="HTML", reply_markup=markup)
            except Exception:
                bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
            return

        elif data == 'spin_now':
            loading_toast(call.id, "🎰 Spin berputar...")
            if not can_spin_now(chat_id):
                bot.answer_callback_query(call.id, text="❌ Kamu sudah spin hari ini!", show_alert=True)
                return
            hadiah = roll_lucky_draw()
            label, tipe, nilai, _ = hadiah
            save_spin(chat_id)
            if tipe == "poin":
                add_user_points(chat_id, nilai, "Hadiah Lucky Draw Harian")
                result_text = (
                    f"🎉 <b>SELAMAT!</b> 🎉\n\n"
                    f"🎰 Hasil Spin: <b>{label}</b>\n\n"
                    f"✅ +{nilai} poin sudah masuk ke saldo kamu!\n"
                    f"🪙 Total Poin Sekarang: <b>{get_user_points(chat_id)} Poin</b>\n\n"
                    "Balik lagi besok buat spin gratis!"
                )
            elif tipe == "diskon":
                try:
                    with open(F_USER_VOUCHER, "a") as f:
                        f.write(f"{chat_id}|DISKON{nilai}|{int(time.time())}\n")
                except Exception:
                    pass
                result_text = (
                    f"🎉 <b>SELAMAT!</b> 🎉\n\n"
                    f"🎰 Hasil Spin: <b>{label}</b>\n\n"
                    f"✅ Voucher diskon {nilai}% aktif otomatis di akun kamu!\n"
                    "Tinggal checkout paket & diskon akan diapply.\n\n"
                    "Balik lagi besok buat spin gratis!"
                )
            else:
                result_text = (
                    f"💎 <b>JACKPOT!!!</b> 💎\n\n"
                    f"🎰 Hasil Spin: <b>{label}</b>\n\n"
                    "🎉 Kamu menang PAKET SEMI-SAFE GRATIS!\n\n"
                    f"📩 Silakan hubungi admin {ADMIN_USERNAME} dengan screenshot pesan ini buat klaim hadiah!"
                )
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result_text,
                                      parse_mode="HTML",
                                      reply_markup=get_back_markup(l))
            except Exception:
                bot.send_message(chat_id, result_text, parse_mode="HTML",
                                 reply_markup=get_back_markup(l))
            return

        elif data == 'menu_testi':
            loading_toast(call.id, "⏳ Memuat testimoni...")
            fake_data = generate_fake_testimonials_list()
            testi_text = (f"🌟 LIVE TESTIMONI (Kak {user.first_name})\n\n"
                          f"{fake_data}💡 Toko 100% amanah! 🚀")
            markup_testi = types.InlineKeyboardMarkup(row_width=1)
            markup_testi.add(
                types.InlineKeyboardButton("🔄 Refresh", callback_data='menu_testi'),
                types.InlineKeyboardButton("🌟 Testi Lengkap", url=CHANNEL_TESTI_LINK),
                types.InlineKeyboardButton(t['back'], callback_data='menu_utama')
            )
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=testi_text,
                                  reply_markup=markup_testi, disable_web_page_preview=True)
            return

        elif data == 'refresh_leaderboard':
            loading_toast(call.id, "⏳ Refresh leaderboard...")
            try:
                # Hitung ulang
                user_stats = {}
                for parts in _read_all_orders():
                    if len(parts) < 8:
                        continue
                    if parts[7].strip() != "BERHASIL":
                        continue
                    cid_order = parts[0]
                    harga = parts[5]
                    pay = parts[9] if len(parts) > 9 else "TRANSFER"
                    nilai = 0 if pay == "POIN" else int(''.join(ch for ch in harga if ch.isdigit()) or 0)
                    if cid_order not in user_stats:
                        user_stats[cid_order] = {'total_order': 0, 'total_belanja': 0}
                    user_stats[cid_order]['total_order'] += 1
                    user_stats[cid_order]['total_belanja'] += nilai

                if not user_stats:
                    bot.answer_callback_query(call.id, text="Belum ada transaksi", show_alert=True)
                    return

                sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['total_order'], reverse=True)[:10]
                text = "🏆 <b>LEADERBOARD TOP BUYER</b>\n━━━━━━━━━━━━━━━━━━━\n\n"
                medals = ["🥇", "🥈", "🥉"]
                for idx, (cid, stat) in enumerate(sorted_users, 1):
                    try:
                        info = bot.get_chat(int(cid))
                        if info.username:
                            uname = f"@{info.username}"
                            masked = uname[:4] + "***" + uname[-2:] if len(uname) > 6 else uname[:3] + "***"
                        else:
                            masked = (info.first_name or "User")[:3] + "***"
                    except Exception:
                        masked = f"User***{cid[-3:]}"
                    marker = " 👈 (KAMU)" if cid == str(chat_id) else ""
                    rank_icon = medals[idx - 1] if idx <= 3 else f"<b>{idx}.</b>"
                    text += (f"{rank_icon} {masked}{marker}\n"
                             f"   📦 {stat['total_order']}x transaksi\n"
                             f"   💰 Rp {stat['total_belanja']:,}\n\n")
                text += "━━━━━━━━━━━━━━━━━━━\n🔥 Terus belanja!"

                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("🔄 Refresh", callback_data='refresh_leaderboard'),
                    types.InlineKeyboardButton("💎 Lihat Katalog", callback_data='menu_katalog'),
                    types.InlineKeyboardButton("⬅️ Menu Utama", callback_data='menu_utama')
                )
                try:
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                          parse_mode="HTML", reply_markup=markup,
                                          disable_web_page_preview=True)
                except Exception:
                    pass
                bot.answer_callback_query(call.id, text="✅ Refreshed!")
            except Exception as e:
                bot.answer_callback_query(call.id, text=f"Error: {e}", show_alert=True)
            return

        elif data == 'menu_riwayat':
            loading_toast(call.id, "⏳ Memuat riwayat...")
            get_latest_user_order_data(chat_id)
            orders = get_user_orders(chat_id)
            if not orders:
                riw_text = f"📋 RIWAYAT (Kak {user.first_name})\n\n❌ Belum ada riwayat."
            else:
                riw_text = f"📋 <b>RIWAYAT PESANAN (Kak {user.first_name})</b>\n\n"
                for idx, o in enumerate(orders[-5:], 1):
                    st = {"BERHASIL": "✅ BERHASIL", "DITOLAK": "❌ DITOLAK",
                          "CANCELLED": "❌ DIBATALKAN", "EXPIRED": "⌛ EXPIRED"}.get(o['status'], "⏳ PENDING")
                    riw_text += (f"<b>{idx}. {o['paket']}</b>\n   • Harga: {o['harga']}\n"
                                 f"   • Resi: <code>{o['resi']}</code>\n   • Status: {st}\n\n")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=riw_text,
                                  reply_markup=get_back_markup(l), parse_mode="HTML",
                                  disable_web_page_preview=True)
            return

        elif data == 'menu_promo':
            loading_toast(call.id, "⏳ Memuat promo...")
            status_c = get_user_coupon_status(chat_id)
            user_pts = get_user_points(chat_id)
            tier_label, multiplier, diskon = get_user_tier(chat_id)
            if status_c == "AVAILABLE":
                kupon_info = "🎁 Kupon Member Baru: <b>TERSEDIA</b>"
            elif status_c == "PENDING":
                kupon_info = "🎁 Kupon Member Baru: <b>PENDING</b>"
            else:
                kupon_info = "🎁 Kupon Member Baru: <b>SUDAH DIGUNAKAN</b>"
            promo_text = (
                f"🎁 <b>PROMO & POIN (Kak {user.first_name})</b>\n\n"
                f"🪙 Saldo Poin: <b>{user_pts} Poin</b>\n"
                f"🏅 Tier: <b>{tier_label}</b>\n"
                f"   ├ Bonus Poin: <b>x{multiplier}</b>\n"
                f"   └ Diskon    : <b>{diskon}%</b>\n\n"
                f"{kupon_info}\n\n"
                "💡 <i>Kumpulkan poin & naikin tier buat dapet bonus lebih gede!</i>"
            )
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=promo_text,
                                  reply_markup=get_back_markup(l), parse_mode="HTML")
            return

        elif data == 'menu_faq':
            loading_toast(call.id, "⏳ Memuat FAQ...")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                  text="💡 FAQ\n\n❓ Aman dari banned?\n💬 A: Sangat aman.",
                                  reply_markup=get_back_markup(l))
            return

        elif data in ('menu_katalog', 'katalog_part1'):
            loading_toast(call.id, "⏳ Memuat katalog 1...")
            try:
                coupon_status = get_user_coupon_status(chat_id)
                markup = build_katalog_markup(1, l)
                katalog_text = build_katalog_text(1, user, l, coupon_status)
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=katalog_text,
                                      reply_markup=markup, parse_mode="HTML",
                                      disable_web_page_preview=True)
            except Exception as e:
                log_error("katalog_part1", e)
            return

        elif data == 'katalog_part2':
            loading_toast(call.id, "⏳ Memuat katalog 2...")
            try:
                coupon_status = get_user_coupon_status(chat_id)
                markup = build_katalog_markup(2, l)
                katalog_text = build_katalog_text(2, user, l, coupon_status)
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=katalog_text,
                                      reply_markup=markup, parse_mode="HTML",
                                      disable_web_page_preview=True)
            except Exception as e:
                log_error("katalog_part2", e)
            return

        elif data in MASTER_PAKET:
            loading_toast(call.id, "⏳ Menyiapkan opsi...")
            p_name, p_price_angka, p_price_str, p_points, _ = MASTER_PAKET[data]
            stok = get_stock(data)
            if stok <= 0:
                bot.answer_callback_query(call.id, text="❌ Maaf, stok paket ini habis! Tunggu restock ya 🙏", show_alert=True)
                return
            choice_text = (f"🛒 <b>PILIH METODE PEMBAYARAN</b>\n\n"
                           f"📦 Paket: <b>{p_name}</b>\n"
                           f"💵 Harga: <b>{p_price_str}</b>\n"
                           f"🪙 Atau Tukar: <b>{p_points} Poin</b>\n"
                           f"📦 Stok: <b>{stok} unit</b>")
            markup_choice = types.InlineKeyboardMarkup(row_width=1)
            markup_choice.add(
                types.InlineKeyboardButton(f"🪙 Bayar Pakai Saldo Poin ({p_points} Poin)", callback_data=f"paymode_|poin|{data}"),
                types.InlineKeyboardButton(f"💳 Transfer Manual DANA/GoPay ({p_price_str})", callback_data=f"paymode_|transfer|{data}"),
                types.InlineKeyboardButton("📱 QRIS (Otomatis Kirim Foto)", callback_data=f"paymode_|qris|{data}"),
                types.InlineKeyboardButton(t['back'], callback_data='menu_katalog')
            )
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=choice_text,
                                  reply_markup=markup_choice, parse_mode="HTML")
            return

        elif data == 'menu_cara_order':
            loading_toast(call.id, "⏳ Memuat panduan...")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                  text="❓ CARA ORDER\n1. Pilih paket.\n2. Pilih metode bayar.\n3. Bayar.\n4. Kirim bukti.\n5. Tunggu ACC.",
                                  reply_markup=get_back_markup(l), disable_web_page_preview=True)
            return

        elif data == 'menu_bayar':
            loading_toast(call.id, "⏳ Memuat metode bayar...")
            markup_bayar = types.InlineKeyboardMarkup(row_width=1)
            markup_bayar.add(types.InlineKeyboardButton(t['back'], callback_data='menu_utama'))
            pay_text = (
                "💳 <b>METODE PEMBAYARAN</b>\n\n"
                "1️⃣ <b>QRIS (All E-Wallet):</b>\n   Bot kirim gambar QRIS otomatis saat checkout\n\n"
                f"2️⃣ <b>Transfer Manual:</b>\n   • DANA/GoPay: <code>{INFO_DANA}</code>\n   • A/N: PakelMlbb\n\n"
                f"3️⃣ <b>Saweria:</b>\n   {INFO_SAWERIA}"
            )
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=pay_text,
                                  reply_markup=markup_bayar, parse_mode="HTML",
                                  disable_web_page_preview=True)
            return

        elif data == 'menu_konfirmasi':
            loading_toast(call.id, "⏳ Memuat instruksi...")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                  text="✅ Kirim screenshot bukti transfer ke bot ini.",
                                  reply_markup=get_back_markup(l), disable_web_page_preview=True)
            return

        elif data.startswith('cancel_'):
            loading_toast(call.id, "⏳ Membatalkan pesanan...")
            resi_target = data.replace('cancel_', '')
            admin_msg_id = None
            try:
                with open(F_ORDERS, "r") as f:
                    for line in f:
                        p = line.strip().split('|')
                        if len(p) >= 12 and p[6].strip() == resi_target.strip():
                            if p[7].strip() != "PENDING":
                                bot.answer_callback_query(call.id, text="Pesanan sudah diproses sebelumnya.", show_alert=True)
                                return
                            admin_msg_id = int(p[11]) if p[11].isdigit() and int(p[11]) > 0 else None
                            break
            except Exception:
                pass
            success = update_order_status_by_resi(resi_target, "CANCELLED")
            if success:
                if admin_msg_id:
                    try:
                        new_admin_caption = call.message.caption or call.message.text or "KLAIM MASUK"
                        new_admin_caption += "\n\n<b>STATUS: ❌ DIBATALKAN PEMBELI</b>"
                        if call.message.content_type == 'photo':
                            bot.edit_message_caption(chat_id=GROUP_PAY_ID, message_id=admin_msg_id,
                                                     caption=new_admin_caption, parse_mode="HTML", reply_markup=None)
                        else:
                            bot.edit_message_text(chat_id=GROUP_PAY_ID, message_id=admin_msg_id,
                                                  text=new_admin_caption, parse_mode="HTML", reply_markup=None)
                    except Exception as e:
                        log_error("edit_admin_msg_cancel", e)
                cancel_text = (
                    f"❌ <b>PESANAN DIBATALKAN</b>\n\nResi: <code>{resi_target}</code>\nPoin kamu tetap utuh."
                )
                try:
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=cancel_text,
                                          parse_mode="HTML", reply_markup=get_back_markup(l))
                except Exception:
                    bot.send_message(chat_id, cancel_text, parse_mode="HTML", reply_markup=get_back_markup(l))
                bot.answer_callback_query(call.id, text="Pesanan dibatalkan!")
            else:
                bot.answer_callback_query(call.id, text="Pesanan sudah diproses.", show_alert=True)
            return

        elif data.startswith('paymode_'):
            parts = data.split('|')
            if len(parts) < 3:
                bot.answer_callback_query(call.id, text="Data tidak valid.", show_alert=True)
                return
            action_type, paket_code = parts[1], parts[2]
            if paket_code not in MASTER_PAKET:
                bot.answer_callback_query(call.id, text="Paket tidak ditemukan.", show_alert=True)
                return
            p_name, p_price_angka, p_price_str, p_points, _ = MASTER_PAKET[paket_code]
            tier_label, multiplier, diskon_tier = get_user_tier(chat_id)
            resi_unik = f"PKL-MLBB-{random.randint(10000, 99999)}"

            # ==== POIN ====
            if action_type == 'poin':
                loading_toast(call.id, "⏳ Cek saldo poin...")
                user_pts = get_user_points(chat_id)
                if user_pts >= p_points:
                    coupon_status = get_user_coupon_status(chat_id)
                    if coupon_status == "AVAILABLE":
                        set_user_coupon_status(chat_id, "PENDING")
                    pending_poin_text = (
                        f"🪙 <b>INVOICE VIA POIN (PENDING)</b>\n\n"
                        f"📦 Paket: {p_name}\n"
                        f"🪙 Poin: <b>{p_points} Poin</b> (Sisa: {user_pts})\n"
                        f"🔑 Resi: <code>{resi_unik}</code>\n\n"
                        "⏳ Menunggu ACC admin."
                    )
                    markup_poin_inv = types.InlineKeyboardMarkup(row_width=1)
                    markup_poin_inv.add(
                        types.InlineKeyboardButton("❌ Batalkan", callback_data=f"cancel_{resi_unik}"),
                        types.InlineKeyboardButton("📦 Riwayat", callback_data='menu_riwayat'),
                        types.InlineKeyboardButton(t['back'], callback_data='menu_utama')
                    )
                    try:
                        bot.delete_message(chat_id=chat_id, message_id=message_id)
                    except Exception:
                        pass
                    bot.send_message(chat_id, pending_poin_text, reply_markup=markup_poin_inv, parse_mode="HTML")
                    # FIX v12: Notif ke Admin
                    notify_admin_new_order(chat_id, user, p_name, f"{p_points} Poin", resi_unik, "POIN")
                    try:
                        waktu_str = datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S WIB')
                        report_admin_poin = (
                            "🪙 <b>KLAIM POIN MASUK!</b>\n\n"
                            f"👤 @{user.username or user.first_name} (ID: <code>{chat_id}</code>)\n"
                            f"📦 {p_name}\n"
                            f"🪙 {p_points} Poin\n"
                            f"⏱️ {waktu_str}\n"
                            f"🔑 Resi: <code>{resi_unik}</code>"
                        )
                        markup_admin_poin = types.InlineKeyboardMarkup(row_width=2)
                        markup_admin_poin.add(
                            types.InlineKeyboardButton("✅ ACC", callback_data=f"apoin|{resi_unik}"),
                            types.InlineKeyboardButton("❌ TOLAK", callback_data=f"tpoin|{resi_unik}")
                        )
                        admin_sent = bot.send_message(GROUP_PAY_ID, report_admin_poin,
                                                      message_thread_id=GROUP_PAY_TOPIC_ID,
                                                      parse_mode="HTML", reply_markup=markup_admin_poin)
                        save_order(chat_id, p_name, f"{p_points} Poin", resi_unik,
                                   payment_method="POIN", point_cost=p_points,
                                   admin_msg_id=admin_sent.message_id)
                    except Exception as e:
                        log_error("report_admin_poin", e)
                        save_order(chat_id, p_name, f"{p_points} Poin", resi_unik,
                                   payment_method="POIN", point_cost=p_points, admin_msg_id=0)
                    bot.answer_callback_query(call.id, text="Menunggu ACC admin!")
                    return
                else:
                    markup_fallback = types.InlineKeyboardMarkup(row_width=1)
                    markup_fallback.add(
                        types.InlineKeyboardButton(f"💳 Bayar Transfer ({p_price_str})", callback_data=f"paymode_|transfer|{paket_code}"),
                        types.InlineKeyboardButton(t['back'], callback_data='menu_utama')
                    )
                    fail_text = f"❌ <b>POIN BELUM CUKUP!</b>\nPoin: {user_pts} | Butuh: {p_points}"
                    try:
                        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=fail_text,
                                              parse_mode="HTML", reply_markup=markup_fallback)
                    except Exception:
                        bot.send_message(chat_id, fail_text, parse_mode="HTML", reply_markup=markup_fallback)
                    bot.answer_callback_query(call.id, text="Poin kurang!", show_alert=True)
                    return

            # ==== TRANSFER ====
            elif action_type == 'transfer':
                loading_toast(call.id, "⏳ Menerbitkan invoice...")
                coupon_status = get_user_coupon_status(chat_id)
                is_promo_used = (coupon_status == "AVAILABLE")
                harga_final = p_price_angka
                # FIX v12: Flash Sale prioritas
                fs_diskon, _ = get_active_flashsale()
                if fs_diskon > 0:
                    harga_final = int(p_price_angka * (100 - fs_diskon) / 100)
                else:
                    if diskon_tier > 0:
                        harga_final = int(p_price_angka * (100 - diskon_tier) / 100)
                    if is_promo_used:
                        harga_final -= 10000
                lucky_diskon = get_user_lucky_diskon(chat_id)
                if lucky_diskon > 0:
                    harga_final = int(harga_final * (100 - lucky_diskon) / 100)
                voucher_kode, voucher_diskon = get_user_voucher_diskon(chat_id)
                if voucher_diskon > 0:
                    harga_final -= voucher_diskon
                harga_final = max(0, harga_final)
                harga_final_str = f"Rp {harga_final:,}"
                save_order(chat_id, p_name, harga_final_str, resi_unik, payment_method="TRANSFER",
                           point_cost=0, admin_msg_id=0)
                # FIX v12: Notif ke Admin
                notify_admin_new_order(chat_id, user, p_name, harga_final_str, resi_unik, "TRANSFER")
                if is_promo_used:
                    set_user_coupon_status(chat_id, "PENDING")
                invoice_text = (
                    f"{t['inv_title'].format(name=user.first_name)}\n\n"
                    f"📦 <b>Nama Paket</b>       : {p_name}\n"
                    f"💵 <b>Harga Dasar</b>      : {p_price_str}\n"
                )
                if fs_diskon > 0:
                    invoice_text += f"⚡ <b>FLASH SALE</b>        : -{fs_diskon}%\n"
                if diskon_tier > 0:
                    invoice_text += f"🏅 <b>Diskon Tier ({tier_label})</b>  : -{diskon_tier}%\n"
                if is_promo_used:
                    invoice_text += "🎁 <b>Promo Member Baru</b>  : -Rp 10.000\n"
                if lucky_diskon > 0:
                    invoice_text += f"🎰 <b>Diskon Lucky Draw</b>    : -{lucky_diskon}%\n"
                if voucher_diskon > 0:
                    invoice_text += f"🎫 <b>Voucher ({voucher_kode})</b>   : -Rp {voucher_diskon:,}\n"
                invoice_text += (
                    f"💰 <b>Total Bayar Transfer</b> : <b>{harga_final_str}</b>\n"
                    f"🔑 <b>Nomor Resi Unik</b>  : <code>{resi_unik}</code>\n"
                    f"⏱️ <b>Batas Waktu</b>      : 15 Menit\n\n"
                    "💳 <b>PEMBAYARAN VIA TRANSFER MANUAL</b>\n"
                    "Silakan transfer ke salah satu rekening di bawah:\n\n"
                    f"• <b>DANA / GoPay:</b> <code>{INFO_DANA}</code>\n"
                    "• <b>Atas Nama:</b> PakelMlbb\n\n"
                    "⚠️ <b>PENTING — WAJIB DIBACA!</b>\n"
                    f"Masukkan nominal transfer <b>PERSIS</b> sebesar:\n"
                    f"👉 <b>{harga_final_str}</b>\n\n"
                    "Jangan dilebihkan atau dikurangi ya Kak, biar admin gampang verifikasi "
                    "dan pesananmu cepet diproses! 🙏\n\n"
                    "🛡️ <b>INSTRUKSI KONFIRMASI:</b>\n"
                    "Setelah sukses transfer, kirim <b>Screenshot Bukti Transfer</b> ke bot ini untuk "
                    f"mendapatkan script VIP.\n\n👉 Admin: {ADMIN_USERNAME}"
                )
                markup_inv = types.InlineKeyboardMarkup(row_width=1)
                markup_inv.add(
                    types.InlineKeyboardButton("❌ Batalkan Pesanan Ini", callback_data=f"cancel_{resi_unik}"),
                    types.InlineKeyboardButton("📦 Cek Riwayat Pesanan Saya", callback_data='menu_riwayat'),
                    types.InlineKeyboardButton(t['back'], callback_data='menu_utama')
                )
                if lucky_diskon > 0:
                    consume_user_lucky_diskon(chat_id)
                if voucher_diskon > 0:
                    consume_user_voucher(chat_id)
                try:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception:
                    pass
                bot.send_message(chat_id, invoice_text, reply_markup=markup_inv,
                                 parse_mode="HTML", disable_web_page_preview=True)
                return

            # ==== QRIS ====
            elif action_type == 'qris':
                loading_toast(call.id, "⏳ Menyiapkan gambar QRIS...")
                coupon_status = get_user_coupon_status(chat_id)
                is_promo_used = (coupon_status == "AVAILABLE")

                harga_final_qris = p_price_angka
                # FIX v12: Flash Sale prioritas
                fs_diskon, _ = get_active_flashsale()
                if fs_diskon > 0:
                    harga_final_qris = int(p_price_angka * (100 - fs_diskon) / 100)
                else:
                    if diskon_tier > 0:
                        harga_final_qris = int(p_price_angka * (100 - diskon_tier) / 100)
                    if is_promo_used:
                        harga_final_qris -= 10000
                lucky_diskon = get_user_lucky_diskon(chat_id)
                if lucky_diskon > 0:
                    harga_final_qris = int(harga_final_qris * (100 - lucky_diskon) / 100)
                voucher_kode, voucher_diskon = get_user_voucher_diskon(chat_id)
                if voucher_diskon > 0:
                    harga_final_qris -= voucher_diskon
                harga_final_qris = max(0, harga_final_qris)

                save_order(chat_id, p_name, f"Rp {harga_final_qris:,}", resi_unik,
                           payment_method="QRIS", point_cost=0, admin_msg_id=0)
                # FIX v12: Notif ke Admin
                notify_admin_new_order(chat_id, user, p_name, f"Rp {harga_final_qris:,}", resi_unik, "QRIS")
                if is_promo_used:
                    set_user_coupon_status(chat_id, "PENDING")

                invoice_caption = (
                    f"{t['inv_title'].format(name=user.first_name)}\n\n"
                    f"📦 <b>Nama Paket</b>       : {p_name}\n"
                    f"💵 <b>Harga Dasar</b>      : {p_price_str}\n"
                )
                if fs_diskon > 0:
                    invoice_caption += f"⚡ <b>FLASH SALE</b>        : -{fs_diskon}%\n"
                if diskon_tier > 0:
                    invoice_caption += f"🏅 <b>Diskon Tier ({tier_label})</b>  : -{diskon_tier}%\n"
                if is_promo_used:
                    invoice_caption += "🎁 <b>Promo Member Baru</b>  : -Rp 10.000\n"
                if lucky_diskon > 0:
                    invoice_caption += f"🎰 <b>Diskon Lucky Draw</b>    : -{lucky_diskon}%\n"
                if voucher_diskon > 0:
                    invoice_caption += f"🎫 <b>Voucher ({voucher_kode})</b>   : -Rp {voucher_diskon:,}\n"
                invoice_caption += (
                    f"💰 <b>Total Bayar QRIS</b> : <b>Rp {harga_final_qris:,}</b>\n"
                    f"🔑 <b>Nomor Resi Unik</b>  : <code>{resi_unik}</code>\n"
                    f"⏱️ <b>Batas Waktu</b>      : 15 Menit\n\n"
                    "📱 <b>PEMBAYARAN VIA QRIS</b>\n"
                    "Silakan scan gambar QRIS di atas menggunakan aplikasi e-wallet / m-banking Anda "
                    "(DANA, OVO, GoPay, ShopeePay, LinkAja, Mobile Banking, dll).\n\n"
                    "⚠️ <b>PENTING — WAJIB DIBACA!</b>\n"
                    f"Masukkan nominal transfer <b>PERSIS</b> sebesar:\n"
                    f"👉 <b>Rp {harga_final_qris:,}</b>\n\n"
                    "Jangan dilebihkan atau dikurangi ya Kak, biar admin gampang verifikasi "
                    "dan pesananmu cepet diproses! 🙏\n\n"
                    "🛡️ <b>INSTRUKSI KONFIRMASI:</b>\n"
                    "Setelah sukses membayar, kirim <b>Screenshot Bukti Transfer</b> ke bot ini untuk "
                    f"mendapatkan script VIP.\n\n👉 Admin: {ADMIN_USERNAME}"
                )

                markup_qris = types.InlineKeyboardMarkup(row_width=1)
                markup_qris.add(
                    types.InlineKeyboardButton("❌ Batalkan Pesanan Ini", callback_data=f"cancel_{resi_unik}"),
                    types.InlineKeyboardButton("📦 Cek Riwayat Pesanan Saya", callback_data='menu_riwayat'),
                    types.InlineKeyboardButton(t['back'], callback_data='menu_utama')
                )

                if lucky_diskon > 0:
                    consume_user_lucky_diskon(chat_id)
                if voucher_diskon > 0:
                    consume_user_voucher(chat_id)

                try:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception:
                    pass

                try:
                    bot.send_photo(
                        chat_id=chat_id,
                        photo=QRIS_IMAGE_URL,
                        caption=invoice_caption,
                        parse_mode="HTML",
                        reply_markup=markup_qris
                    )
                except Exception as e:
                    log_error("send_photo_qris", e)
                    try:
                        bot.send_message(
                            ADMIN_TELEGRAM_ID,
                            f"⚠️ <b>GAGAL KIRIM QRIS!</b>\n\n"
                            f"Error: <code>{e}</code>\n\n"
                            f"Cek <code>QRIS_IMAGE_URL</code> — mungkin link invalid.",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                    bot.send_message(
                        chat_id=chat_id,
                        text=invoice_caption,
                        parse_mode="HTML",
                        reply_markup=markup_qris,
                        disable_web_page_preview=True
                    )
                return

        elif data.startswith('rate|'):
            loading_toast(call.id, "⏳ Memuat ulasan...")
            parts = data.split('|')
            if len(parts) < 3:
                return
            rating_val, resi_code = parts[1], parts[2]
            markup_ulasan = types.InlineKeyboardMarkup(row_width=1)
            if int(rating_val) <= 2:
                markup_ulasan.add(
                    types.InlineKeyboardButton("⚠️ Kurang Memuaskan", callback_data=f"textrev|{resi_code}|{rating_val}|Kurang memuaskan"),
                    types.InlineKeyboardButton("❌ Kecewa", callback_data=f"textrev|{resi_code}|{rating_val}|Sangat buruk")
                )
            elif int(rating_val) == 3:
                markup_ulasan.add(
                    types.InlineKeyboardButton("⭐ Cukup", callback_data=f"textrev|{resi_code}|{rating_val}|Cukup standar"),
                    types.InlineKeyboardButton("👍 Lumayan", callback_data=f"textrev|{resi_code}|{rating_val}|Lumayan bagus")
                )
            else:
                markup_ulasan.add(
                    types.InlineKeyboardButton("🔥 Super Bagus!", callback_data=f"textrev|{resi_code}|{rating_val}|Super bagus"),
                    types.InlineKeyboardButton("🚀 Gercep Banget!", callback_data=f"textrev|{resi_code}|{rating_val}|Sangat puas gercep"),
                    types.InlineKeyboardButton("💯 The Best!", callback_data=f"textrev|{resi_code}|{rating_val}|The best")
                )
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                  text=f"⭐ <b>Terima kasih rating {rating_val} bintang!</b>\nPilih ulasan:",
                                  parse_mode="HTML", reply_markup=markup_ulasan)
            with open(f"pending_review_{chat_id}.txt", "w") as f:
                f.write(f"{resi_code}|{rating_val}")
            return

        elif data.startswith('textrev|'):
            loading_toast(call.id, "⏳ Menyimpan ulasan...")
            parts = data.split('|', 3)
            if len(parts) < 4:
                return
            resi_c, rating_c, quick_text = parts[1], parts[2], parts[3]
            save_user_review(chat_id, rating_c, quick_text)
            try:
                if os.path.exists(f"pending_review_{chat_id}.txt"):
                    os.remove(f"pending_review_{chat_id}.txt")
            except Exception:
                pass
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                  text="🎉 <b>TERIMA KASIH ATAS ULASANNYA!</b>",
                                  parse_mode="HTML")
            return

        elif data.startswith('sc_'):
            loading_toast(call.id, "⏳ Mengirim testi...")
            try:
                data_split = data.split('|')
                if len(data_split) < 2:
                    return
                action, buyer_name = data_split[0], data_split[1]
                paket_code = action.replace('sc_', '')
                if paket_code in MASTER_PAKET:
                    p_nama, _, p_hrg, _, _ = MASTER_PAKET[paket_code]
                else:
                    p_nama, p_hrg = "VIP Package", "Rp 100.000"
                current_hour = datetime.now(WIB).hour
                waktu_ket = "pagi ini" if 4 <= current_hour < 11 else (
                    "siang ini" if 11 <= current_hour < 15 else (
                        "sore ini" if 15 <= current_hour < 18 else "malam ini"))
                post_text = (
                    "🚨 REAL-TIME TRANSACTION REPORT 🚨\n\n"
                    f"✅ Buyer ID: {buyer_name}\n"
                    f"📦 Item Purchased: {p_nama}\n"
                    f"💵 Price: {p_hrg}\n"
                    f"⏱️ Time: {random.randint(1, 15)} menit lalu ({waktu_ket})\n"
                    f"🔒 Status: SUCCESS & SCRIPT DELIVERED\n\n"
                    "🔥 Terima kasih telah berbelanja! Order juga di bot ya! 👇\n"
                    f"🤖 Bot: @{bot.get_me().username}"
                )
                bot.send_message(chat_id=GROUP_CHAT_ID, text=post_text,
                                 message_thread_id=GROUP_TOPIC_ID, disable_web_page_preview=True)
                reduce_stock_random_all()
                auto_restock_if_low()
                bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                      text=f"✅ <b>TESTI TERKIRIM!</b>\n• {buyer_name}\n• {p_nama}",
                                      parse_mode="HTML")
            except Exception as e:
                bot.answer_callback_query(call.id, text=f"Gagal: {e}", show_alert=True)
            return

        elif data.startswith('scp_'):
            loading_toast(call.id, "⏳ Mengirim testi poin...")
            try:
                data_split = data.split('|')
                if len(data_split) < 2:
                    return
                action, buyer_name = data_split[0], data_split[1]
                paket_code = action.replace('scp_', '')
                if paket_code in MASTER_PAKET:
                    p_nama, _, _, p_poin, _ = MASTER_PAKET[paket_code]
                    p_hrg_poin = f"{p_poin} Poin (Tukar Poin Loyalitas)"
                else:
                    p_nama, p_hrg_poin = "VIP Package", "30 Poin"
                current_hour = datetime.now(WIB).hour
                waktu_ket = "pagi ini" if 4 <= current_hour < 11 else (
                    "siang ini" if 11 <= current_hour < 15 else (
                        "sore ini" if 15 <= current_hour < 18 else "malam ini"))
                post_text = (
                    "🚨 REAL-TIME TRANSACTION REPORT 🚨\n\n"
                    f"✅ Buyer ID: {buyer_name}\n"
                    f"📦 Item Purchased: {p_nama}\n"
                    f"💵 Price / Method: {p_hrg_poin}\n"
                    f"⏱️ Time: {random.randint(1, 15)} menit lalu ({waktu_ket})\n"
                    f"🔒 Status: REDEEMED VIA LOYALTY POINTS\n\n"
                    "🔥 Kumpulin poin, sikat script gratisannya! 👇\n"
                    f"🤖 Bot: @{bot.get_me().username}"
                )
                bot.send_message(chat_id=GROUP_CHAT_ID, text=post_text,
                                 message_thread_id=GROUP_TOPIC_ID, disable_web_page_preview=True)
                reduce_stock_random_all()
                auto_restock_if_low()
                bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                      text=f"✅ <b>TESTI POIN TERKIRIM!</b>\n• {buyer_name}\n• {p_nama}",
                                      parse_mode="HTML")
            except Exception as e:
                bot.answer_callback_query(call.id, text=f"Gagal: {e}", show_alert=True)
            return
    except Exception as e:
        log_error("callback_handler_master", e)
    finally:
        threading.Timer(2.0, lambda: processing_lock.discard(lock_key)).start()

def check_bot_status_health():
    try:
        me = bot.get_me()
        print(f"[HEALTH CHECK] Bot @{me.username} (ID: {me.id}) berjalan normal.")
    except Exception as e:
        print(f"[HEALTH CHECK ERROR]: {e}")

threading.Thread(target=check_bot_status_health, daemon=True).start()

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_and_reviews(message):
    chat_id = message.chat.id
    if message.chat.type != 'private':
        return
    save_user(chat_id)
    user = message.from_user
    l = get_lang(user)
    txt = message.text.strip()

    upper_txt = txt.upper().strip()
    if upper_txt.startswith("VOUCHER "):
        kode = upper_txt.replace("VOUCHER ", "").strip().upper()

        # FIX v11: Cek duplikat DULU sebelum validasi
        if user_has_voucher(chat_id, kode):
            bot.reply_to(
                message,
                f"🚫 <b>SUDAH PERNAH REDEEM!</b>\n\n"
                f"🎫 Kode: <code>{kode}</code>\n"
                "💡 1 akun hanya bisa redeem 1x per kode voucher.\n\n"
                "📌 <i>Anti-curang aktif. Abuse = auto-ban.</i>",
                parse_mode="HTML"
            )
            try:
                log_suspicious(chat_id, user.username or user.first_name, "REDEEM_DUPLIKAT", kode)
            except Exception:
                pass
            return

        # FIX v11: Cek spam cooldown
        if is_spam_voucher(chat_id):
            bot.reply_to(message, "⚠️ Santai kak, tunggu 30 detik dulu ya 🙏")
            return

        valid, diskon, pesan = validate_voucher(kode)
        if not valid:
            bot.reply_to(message, f"❌ <b>Voucher tidak valid:</b> {pesan}", parse_mode="HTML")
            return

        save_user_voucher(chat_id, kode, diskon)
        use_voucher(kode)
        sisa = get_voucher_sisa(kode)

        bot.reply_to(
            message,
            f"✅ <b>VOUCHER BERHASIL DI-REDEEM!</b>\n\n"
            f"🎫 Kode: <code>{kode}</code>\n"
            f"💵 Diskon: Rp {diskon:,}\n"
            f"📊 Sisa Kuota Voucher: <b>{sisa}</b>\n\n"
            "💡 Voucher akan otomatis terpakai saat checkout paket berikutnya.\n"
            "⚠️ <i>Voucher sudah terkunci untuk akunmu — tidak bisa dipindah atau dipakai 2x.</i>",
            parse_mode="HTML"
        )
        return

    review_flag_file = f"pending_review_{chat_id}.txt"
    try:
        if os.path.exists(review_flag_file):
            with open(review_flag_file, "r") as f:
                data_rev = f.read().strip().split('|')
            if len(data_rev) == 2:
                resi_c, rating_c = data_rev
                save_user_review(chat_id, rating_c, txt)
                try:
                    os.remove(review_flag_file)
                except Exception:
                    pass
                bot.reply_to(message, "🎉 <b>TERIMA KASIH ATAS ULASANNYA!</b>",
                             reply_markup=get_back_markup(l), parse_mode="HTML")
                return
    except Exception:
        pass

    # FIX v15: FULL AI GROQ — Beneran mikir, bukan template
    if AI_ENABLED:
        try:
            # Kirim indikator "typing" biar user tau bot lagi mikir
            bot.send_chat_action(chat_id, 'typing')
            # Panggil AI Groq
            ai_reply = ai_cs_reply(chat_id, txt, user.first_name)
            if ai_reply:
                bot.reply_to(message, ai_reply, parse_mode="HTML",
                             disable_web_page_preview=True)
                return
        except Exception as e:
            log_error("ai_cs_handler", e)

    # Fallback CUMA kalau AI mati total
    bot.reply_to(message, "Maaf Kak, CS sedang sibuk. Coba lagi sebentar ya 🙏",
                 disable_web_page_preview=True)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if is_banned(message.chat.id):
        return
    if is_spam_photo(message.chat.id):
        bot.reply_to(message, "⚠️ Santai kak, tunggu sebentar ya 🙏")
        return
    save_user(message.chat.id)
    user = message.from_user
    resi_unik, order_status = get_latest_user_order_data(message.chat.id)
    if order_status == "EXPIRED":
        bot.reply_to(message, "❌ <b>WAKTU KONFIRMASI HABIS!</b>", parse_mode="HTML")
        return
    proof_id = message.photo[-1].file_unique_id
    if is_proof_used(proof_id):
        bot.reply_to(message, "⚠️ Bukti transfer ini sudah pernah digunakan!")
        return
    mark_proof_used(proof_id)
    user_caption = message.caption if message.caption else "Tidak ada pesan"
    now = datetime.now(WIB)
    # FIX v14: Auto-save bukti ke folder (di thread biar ga blocking)
    try:
        threading.Thread(
            target=save_proof_to_folder,
            args=(message.chat.id, resi_unik, message.photo[-1].file_id, user_caption),
            daemon=True
        ).start()
    except Exception:
        pass
    bot.reply_to(message,
                 f"✅ BUKTI DIUNGGAH!\nKak {user.first_name}\n"
                 f"Resi: {resi_unik}\n"
                 f"⏱️ {now.strftime('%d-%m-%Y %H:%M:%S WIB')}\n\n"
                 f"📋 Tunggu verifikasi {ADMIN_USERNAME}",
                 disable_web_page_preview=True)
    try:
        caption_admin = (
            "🚨 <b>BUKTI TRANSFER MASUK!</b>\n\n"
            f"👤 @{user.username or user.first_name} (ID: <code>{user.id}</code>)\n"
            f"✉️ Pesan: \"{user_caption}\"\n"
            f"⏱️ {now.strftime('%d-%m-%Y %H:%M:%S WIB')}\n"
            f"🔑 Resi: {resi_unik}\n\n"
            "👇 Cek mutasi, klik ACC atau TOLAK!"
        )
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ ACC", callback_data=f"acc|{user.id}|{resi_unik}"),
            types.InlineKeyboardButton("❌ TOLAK", callback_data=f"tolak|{user.id}|{resi_unik}")
        )
        bot.send_photo(chat_id=GROUP_PAY_ID, photo=message.photo[-1].file_id,
                       caption=caption_admin, message_thread_id=GROUP_PAY_TOPIC_ID,
                       parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        log_error("handle_photo_forward", e)

# =====================================================================================
#  COMMAND ADMIN KHUSUS APK
# =====================================================================================

@bot.message_handler(commands=['apkorder'])
def cmd_apk_order(message):
    """Lihat order pending dari APK."""
    if not is_super_admin(message.chat.id):
        return
    try:
        orders = []
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[7].strip() == "PENDING":
                    orders.append(parts)
        
        if not orders:
            bot.reply_to(message, "✅ Tidak ada order pending.")
            return
        
        text = "📦 <b>ORDER PENDING</b>\n\n"
        for o in orders[-10:]:
            text += (
                f"🔑 Resi: <code>{o[6]}</code>\n"
                f"📦 Paket: {o[4]}\n"
                f"💰 Harga: {o[5]}\n"
                f"📅 {o[1]} {o[3]}\n\n"
            )
        bot.reply_to(message, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['apkacc'])
def cmd_apk_acc(message):
    """ACC order dari APK."""
    if not is_super_admin(message.chat.id):
        return
    args = message.text.replace('/apkacc', '').strip().split()
    if not args:
        bot.reply_to(message, "⚠️ Format: /apkacc [RESI]")
        return
    resi = args[0].strip().upper()
    success = update_order_status_by_resi(resi, "BERHASIL")
    if success:
        bot.reply_to(message, f"✅ Order <code>{resi}</code> di-ACC!", parse_mode="HTML")
    else:
        bot.reply_to(message, f"❌ Resi <code>{resi}</code> tidak ditemukan atau sudah diproses.", parse_mode="HTML")

@bot.message_handler(commands=['apkreject'])
def cmd_apk_reject(message):
    """Tolak order dari APK."""
    if not is_super_admin(message.chat.id):
        return
    args = message.text.replace('/apkreject', '').strip().split()
    if not args:
        bot.reply_to(message, "⚠️ Format: /apkreject [RESI]")
        return
    resi = args[0].strip().upper()
    success = update_order_status_by_resi(resi, "DITOLAK")
    if success:
        bot.reply_to(message, f"✅ Order <code>{resi}</code> ditolak.", parse_mode="HTML")
    else:
        bot.reply_to(message, f"❌ Resi <code>{resi}</code> tidak ditemukan.", parse_mode="HTML")

@bot.message_handler(commands=['apkstats'])
def cmd_apk_stats(message):
    """Statistik order dari APK."""
    if not is_super_admin(message.chat.id):
        return
    try:
        today = datetime.now(WIB).strftime('%d-%m-%Y')
        total_hari = 0
        pending = 0
        sukses = 0
        total_pendapatan = 0
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[1] == today:
                    total_hari += 1
                    if parts[7].strip() == "PENDING":
                        pending += 1
                    elif parts[7].strip() == "BERHASIL":
                        sukses += 1
                        total_pendapatan += int(''.join(ch for ch in parts[5] if ch.isdigit()) or 0)
        text = (
            f"📊 <b>STATISTIK HARI INI</b>\n"
            f"📅 {today}\n\n"
            f"📦 Total Order: <b>{total_hari}</b>\n"
            f"⏳ Pending: <b>{pending}</b>\n"
            f"✅ Sukses: <b>{sukses}</b>\n"
            f"💰 Pendapatan: <b>Rp {total_pendapatan:,}</b>\n"
        )
        bot.reply_to(message, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")


print("[INFO] Pakel MlbbStore v10 VOUCHER-MGMT + AUTO-BC Edition Berhasil Dijalankan...")

# FIX: Pindah polling ke dalam if __name__ biar gak auto-run saat di-import
if __name__ == '__main__':
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"[FATAL ERROR] Bot berhenti: {e}")