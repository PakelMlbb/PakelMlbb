# =====================================================================================
#  PAKEL MLBBSTORE — APK API SERVER (v7 — FULL FITUR + POIN + CUSTOM PAKET + RESTOCK)
# =====================================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import random
import time
import requests as req
import threading
from datetime import datetime, timezone, timedelta

# LOCK GLOBAL untuk file operations
orders_lock = threading.Lock()
vouchers_lock = threading.Lock()
points_lock = threading.Lock()
stocks_lock = threading.Lock()

# =====================================================================================
#  KONFIGURASI
# =====================================================================================
WIB = timezone(timedelta(hours=7))
DATA_DIR = os.environ.get('DATA_DIR', '.')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')

F_USERS = os.path.join(DATA_DIR, "users.txt")
F_ORDERS = os.path.join(DATA_DIR, "orders.txt")
F_POINTS = os.path.join(DATA_DIR, "points.txt")
F_POINTLOG = os.path.join(DATA_DIR, "point_log.txt")
F_VOUCHERS = os.path.join(DATA_DIR, "vouchers.txt")
F_USER_VOUCHER = os.path.join(DATA_DIR, "user_voucher.txt")
F_STOCKS = os.path.join(DATA_DIR, "stocks.txt")
F_FLASHSALE = os.path.join(DATA_DIR, "flashsale.txt")
F_COUPONS = os.path.join(DATA_DIR, "coupons.txt")
F_REFERRALS = os.path.join(DATA_DIR, "referrals.txt")
F_SPINLOG = os.path.join(DATA_DIR, "spin_log.txt")
F_PROOFS = os.path.join(DATA_DIR, "proofs")
F_LASTTIER = os.path.join(DATA_DIR, "last_tier.txt")
# ---- FILE BARU v7 ----
F_CUSTOM_PAKET = os.path.join(DATA_DIR, "custom_paket.txt")
F_PAKET_OVERRIDE = os.path.join(DATA_DIR, "paket_override.txt")
F_BLACKLIST = os.path.join(DATA_DIR, "blacklist_paket.txt")
F_RESTOCK_LOG = os.path.join(DATA_DIR, "restock_log.txt")
F_TESTIMONI = os.path.join(DATA_DIR, "testimoni.txt")
F_INBOX = os.path.join(DATA_DIR, "inbox.txt")
F_ERROR_LOG_API = os.path.join(DATA_DIR, "client_errors.txt")
F_SPAM_LOG = os.path.join(DATA_DIR, "spam_log.txt")

ADMIN_TELEGRAM_ID = 8772023108
GROUP_PAY_ID = "@Paysukses"
GROUP_PAY_TOPIC_ID = 5

# =====================================================================================
#  KONFIGURASI LUCKY DRAW
# =====================================================================================
LUCKY_DRAW_COOLDOWN_JAM = 24
LUCKY_DRAW_HADIAH = [
    ("🪙 +2 Poin",      "poin",  2,  40),
    ("🪙 +5 Poin",      "poin",  5,  30),
    ("🪙 +10 Poin",     "poin",  10, 15),
    ("🪙 +15 Poin",     "poin",  15, 8),
    ("🪙 +25 Poin",     "poin",  25, 4),
    ("🎁 Diskon 5%",    "diskon", 5,  2),
    ("🎁 Diskon 10%",   "diskon", 10, 0.8),
    ("💎 Paket Semi-Safe GRATIS", "paket_gratis", 0, 0.2),
]

# =====================================================================================
#  DATA PAKET DEFAULT
# =====================================================================================
MASTER_PAKET = {
    'buy_natural': ("Natural Balance (30 Hari)", 120000, "Rp 120.000", 60, "🎯 Damage disesuaikan, aman & senyap."),
    'buy_light': ("Light VIP + Drone (30 Hari)", 95000, "Rp 95.000", 45, "🎯 Damage wajar + pandangan luas."),
    'buy_semisafe': ("Semi-Safe 14 Hari", 75000, "Rp 75.000", 35, "🎯 Paket harian terjangkau."),
    'buy_lifetimesafe': ("Lifetime Safe Permanent", 200000, "Rp 200.000", 95, "🎯 Solusi hemat jangka panjang."),
    'buy_sultan': ("Sultan One Hit 100% (30 Hari)", 150000, "Rp 150.000", 75, "🎯 Damage tembus batas, instant kill."),
    'buy_pro': ("VIP Pro One Hit 80% (30 Hari)", 100000, "Rp 100.000", 55, "🎯 Damage sakit, skin kebuka."),
    'buy_semiprivate': ("Semi-Private 14 Hari", 75000, "Rp 75.000", 35, "🎯 Performa stabil, anti patah-patah."),
    'buy_permanent': ("Permanent Legend (Lifetime)", 250000, "Rp 250.000", 120, "🎯 Sekali bayar, update seumur hidup."),
}

DEFAULT_STOK = {
    'buy_sultan': 8, 'buy_pro': 45, 'buy_permanent': 12, 'buy_natural': 35,
    'buy_lifetimesafe': 20, 'buy_light': 60, 'buy_semisafe': 75, 'buy_semiprivate': 70,
}

KATEGORI_MAP = {
    'buy_sultan': 'sultan', 'buy_pro': 'pro', 'buy_permanent': 'sultan',
    'buy_natural': 'safe', 'buy_lifetimesafe': 'safe',
    'buy_light': 'murah', 'buy_semisafe': 'murah', 'buy_semiprivate': 'murah'
}

app = Flask(__name__)
CORS(app)

# =====================================================================================
#  HELPER — BACA FILE
# =====================================================================================
def read_points(chat_id):
    try:
        with open(F_POINTS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2 and parts[0] == str(chat_id):
                    return int(parts[1])
    except FileNotFoundError:
        pass
    return 0

def read_stocks():
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
    except Exception as e:
        print(f"[API] read_stocks error: {e}")
    return stocks

def get_stok(paket_kode):
    stocks = read_stocks()
    stok = stocks.get(paket_kode)
    if stok is None:
        return DEFAULT_STOK.get(paket_kode, 10)
    return stok

def read_flashsale():
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

def read_vouchers():
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

def get_user_tier(chat_id):
    total = count_user_success_orders(chat_id)
    if total >= 30:
        return "💎 Platinum", 2.0, 15
    elif total >= 15:
        return "🥇 Gold", 1.5, 10
    elif total >= 5:
        return "🥈 Silver", 1.2, 5
    else:
        return "🥉 Bronze", 1.0, 0

def count_user_success_orders(chat_id):
    total = 0
    try:
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[0] == str(chat_id) and parts[7].strip() == "BERHASIL":
                    total += 1
    except FileNotFoundError:
        pass
    return total

def set_coupon_status_api(chat_id, status_baru):
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
        tmp = F_COUPONS + ".tmp"
        with open(tmp, "w") as f:
            f.writelines(rows)
        if os.path.exists(F_COUPONS):
            os.remove(F_COUPONS)
        os.rename(tmp, F_COUPONS)
        print(f"[API] ✅ Coupon status {chat_id} → {status_baru}")
    except Exception as e:
        print(f"[API] set_coupon_status_api error: {e}")

def consume_user_lucky_diskon_api(chat_id):
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
        print(f"[API] ✅ Lucky draw diskon {chat_id} consumed")
    except Exception as e:
        print(f"[API] consume_user_lucky_diskon_api error: {e}")

def get_coupon_status(chat_id):
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

def get_user_voucher_rupiah(chat_id):
    total = 0
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return 0
        with open(F_USER_VOUCHER, "r") as f:
            for ln in f:
                parts = ln.strip().split('|')
                if len(parts) >= 3 and parts[0] == str(chat_id):
                    if parts[1].startswith("VOUCHER_"):
                        try:
                            total += int(parts[2])
                        except ValueError:
                            pass
    except Exception as e:
        print(f"[API] get_user_voucher_rupiah error: {e}")
    return total

def get_user_lucky_diskon_persen(chat_id):
    total_persen = 0
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return 0
        with open(F_USER_VOUCHER, "r") as f:
            for ln in f:
                parts = ln.strip().split('|')
                if len(parts) >= 2 and parts[0] == str(chat_id):
                    if parts[1].startswith("DISKON"):
                        try:
                            persen = int(parts[1].replace("DISKON", ""))
                            total_persen += persen
                        except ValueError:
                            pass
    except Exception as e:
        print(f"[API] get_user_lucky_diskon_persen error: {e}")
    return total_persen

def get_user_voucher_list(chat_id):
    vouchers = []
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return vouchers
        with open(F_USER_VOUCHER, "r") as f:
            for ln in f:
                parts = ln.strip().split('|')
                if len(parts) >= 3 and parts[0] == str(chat_id):
                    if parts[1].startswith("VOUCHER_"):
                        kode = parts[1].replace("VOUCHER_", "")
                        try:
                            diskon = int(parts[2])
                        except ValueError:
                            diskon = 0
                        vouchers.append({"kode": kode, "diskon": diskon})
    except Exception as e:
        print(f"[API] get_user_voucher_list error: {e}")
    return vouchers

def consume_user_voucher_api(chat_id):
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
        print(f"[API] ✅ Voucher user {chat_id} consumed")
    except Exception as e:
        print(f"[API] consume_user_voucher_api error: {e}")

def user_has_voucher(chat_id, kode):
    kode_up = kode.upper().strip()
    try:
        if not os.path.exists(F_USER_VOUCHER):
            return False
        with open(F_USER_VOUCHER, "r") as f:
            for ln in f:
                parts = ln.strip().split('|')
                if len(parts) >= 3 and parts[0] == str(chat_id):
                    if parts[1] == f"VOUCHER_{kode_up}":
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
        for ln in rows:
            parts = ln.split('|')
            if len(parts) >= 2 and parts[0] == str(chat_id) and parts[1] == f"VOUCHER_{kode_up}":
                return
        rows.append(f"{chat_id}|VOUCHER_{kode_up}|{diskon}|{int(time.time())}")
        with open(F_USER_VOUCHER, "w") as f:
            f.write("\n".join(rows) + "\n")
    except Exception:
        pass

def get_order_by_resi(resi):
    try:
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[6].strip().upper() == resi.upper():
                    return {
                        'chat_id': parts[0], 'tanggal': parts[1], 'hari': parts[2],
                        'jam': parts[3], 'paket': parts[4], 'harga': parts[5],
                        'resi': parts[6], 'status': parts[7],
                        'metode': parts[9] if len(parts) > 9 else "TRANSFER"
                    }
    except FileNotFoundError:
        pass
    return None

def get_user_orders_list(chat_id, limit=15):
    orders = []
    try:
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[0] == str(chat_id):
                    orders.append({
                        'tanggal': parts[1], 'hari': parts[2], 'jam': parts[3],
                        'paket': parts[4], 'harga': parts[5], 'resi': parts[6],
                        'status': parts[7],
                        'metode': parts[9] if len(parts) > 9 else "TRANSFER"
                    })
    except FileNotFoundError:
        pass
    return orders[-limit:]

def get_leaderboard(limit=10):
    stats = {}
    try:
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[7].strip() == "BERHASIL":
                    cid = parts[0]
                    harga = parts[5]
                    pay = parts[9] if len(parts) > 9 else "TRANSFER"
                    nilai = 0 if pay == "POIN" else int(''.join(ch for ch in harga if ch.isdigit()) or 0)
                    if cid not in stats:
                        stats[cid] = {'total_order': 0, 'total_belanja': 0}
                    stats[cid]['total_order'] += 1
                    stats[cid]['total_belanja'] += nilai
    except FileNotFoundError:
        pass
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['total_order'], reverse=True)[:limit]
    result = []
    for cid, st in sorted_stats:
        if len(cid) > 4:
            masked = f"User***{cid[-4:]}"
        else:
            masked = "User***"
        result.append({
            'chat_id': cid,
            'chat_id_masked': masked,
            'total_order': st['total_order'],
            'total_belanja': st['total_belanja']
        })
    return result

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
        print(f"[API] register_referral error: {e}")
        return False

def get_last_spin_time(chat_id):
    last_time = 0
    try:
        with open(F_SPINLOG, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2 and parts[0] == str(chat_id):
                    try:
                        t = int(parts[1])
                        if t > last_time:
                            last_time = t
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass
    return last_time


def can_spin_now(chat_id):
    last = get_last_spin_time(chat_id)
    return (time.time() - last) >= (LUCKY_DRAW_COOLDOWN_JAM * 3600)

def save_spin(chat_id):
    try:
        with open(F_SPINLOG, "a") as f:
            f.write(f"{chat_id}|{int(time.time())}\n")
    except Exception as e:
        print(f"[API] save_spin error: {e}")

def roll_lucky_draw():
    pilihan = random.choices(LUCKY_DRAW_HADIAH, weights=[h[3] for h in LUCKY_DRAW_HADIAH], k=1)[0]
    return pilihan

def add_user_points(chat_id, amount, alasan="Bonus"):
    try:
        current = read_points(chat_id)
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
        try:
            now = datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S')
            with open(F_POINTLOG, "a") as f:
                f.write(f"{chat_id}|{now}|{amount}|{alasan}\n")
        except Exception:
            pass
        return new_total
    except Exception as e:
        print(f"[API] add_user_points error: {e}")
        return None

# =====================================================================================
#  HELPER BARU v7 — CUSTOM PAKET + BLACKLIST
# =====================================================================================
def read_custom_paket_api():
    paket = {}
    try:
        if not os.path.exists(F_CUSTOM_PAKET):
            return paket
        with open(F_CUSTOM_PAKET, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 7:
                    kode = parts[0]
                    try:
                        paket[kode] = {
                            'nama': parts[1],
                            'harga': int(parts[2]),
                            'poin': int(parts[3]),
                            'deskripsi': parts[4],
                            'kategori': parts[5],
                            'stok_default': int(parts[6]),
                        }
                    except ValueError:
                        pass
    except Exception as e:
        print(f"[API] read_custom_paket_api error: {e}")
    return paket

def read_blacklist_api():
    bl = set()
    try:
        if not os.path.exists(F_BLACKLIST):
            return bl
        with open(F_BLACKLIST, "r") as f:
            for line in f:
                kode = line.strip()
                if kode:
                    bl.add(kode)
    except Exception as e:
        print(f"[API] read_blacklist_api error: {e}")
    return bl



def read_paket_override_api():
    ov = {}
    try:
        if not os.path.exists(F_PAKET_OVERRIDE):
            return ov
        with open(F_PAKET_OVERRIDE, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    try:
                        ov[parts[0]] = {'harga': int(parts[1]), 'poin': int(parts[2])}
                    except ValueError:
                        pass
    except Exception as e:
        print("[API] read_paket_override_api error: " + str(e))
    return ov


def get_all_paket_combined_api():
    """Gabung default + custom, minus blacklist. Apply override harga/poin."""
    bl = read_blacklist_api()
    ov = read_paket_override_api()
    hasil = {}
    for kode, data in MASTER_PAKET.items():
        if kode in bl:
            continue
        nama, harga, harga_str, poin, deskripsi = data
        if kode in ov:
            harga = ov[kode]['harga']
            poin = ov[kode]['poin']
            harga_str = "Rp " + format(harga, ",").replace(",", ".")
        hasil[kode] = {
            'nama': nama, 'harga': harga, 'harga_str': harga_str,
            'poin': poin, 'deskripsi': deskripsi,
            'kategori': KATEGORI_MAP.get(kode, 'all'),
            'is_custom': False,
        }
    custom = read_custom_paket_api()
    for kode, p in custom.items():
        if kode in bl:
            continue
        harga = p['harga']
        poin = p['poin']
        if kode in ov:
            harga = ov[kode]['harga']
            poin = ov[kode]['poin']
        harga_str = "Rp " + format(harga, ",").replace(",", ".")
        hasil[kode] = {
            'nama': p['nama'], 'harga': harga, 'harga_str': harga_str,
            'poin': poin, 'deskripsi': p['deskripsi'],
            'kategori': p['kategori'],
            'is_custom': True,
        }
    return hasil

# =====================================================================================
#  AUTO-CREATE FILES & FOLDER
# =====================================================================================
def ensure_stocks_file():
    try:
        print(f"[API] DATA_DIR = {DATA_DIR}")
        print(f"[API] F_STOCKS = {F_STOCKS}")

        if DATA_DIR and DATA_DIR != '.':
            try:
                os.makedirs(DATA_DIR, exist_ok=True)
                print(f"[API] ✅ Folder {DATA_DIR} ready")
            except Exception as e:
                print(f"[API] ⚠️ Cannot create {DATA_DIR}: {e}")

        existing = {}
        if os.path.exists(F_STOCKS):
            try:
                with open(F_STOCKS, "r") as f:
                    for line in f:
                        parts = line.strip().split('|')
                        if len(parts) >= 2:
                            try:
                                existing[parts[0]] = int(parts[1])
                            except ValueError:
                                pass
                print(f"[API] 📖 Existing stocks: {existing}")
            except Exception as e:
                print(f"[API] ⚠️ Read error: {e}")

        changed = False
        # Paket default
        for code, default_val in DEFAULT_STOK.items():
            if code not in existing or existing[code] <= 0:
                existing[code] = default_val
                changed = True
        # Paket custom
        custom = read_custom_paket_api()
        for code, p in custom.items():
            if code not in existing or existing[code] <= 0:
                existing[code] = p.get('stok_default', 50)
                changed = True

        if changed or not os.path.exists(F_STOCKS):
            with open(F_STOCKS, "w") as f:
                now_ts = int(time.time())
                all_codes = set(list(MASTER_PAKET.keys()) + list(custom.keys()))
                for code in all_codes:
                    stok = existing.get(code, DEFAULT_STOK.get(code, 50))
                    f.write(f"{code}|{stok}|{now_ts}\n")
            print(f"[API] ✅ WROTE stocks.txt at {F_STOCKS}")
        else:
            print(f"[API] ✅ stocks.txt OK")
    except Exception as e:
        print(f"[API] ❌ Failed ensure_stocks_file: {e}")
        import traceback
        traceback.print_exc()

def ensure_proofs_folder():
    try:
        os.makedirs(F_PROOFS, exist_ok=True)
        return True
    except Exception as e:
        print(f"[API] ⚠️ Cannot create proofs folder: {e}")
        return False

# =====================================================================================
#  TELEGRAM SEND
# =====================================================================================
def send_photo_to_telegram(filepath, caption, reply_markup=None, chat_id=GROUP_PAY_ID, thread_id=GROUP_PAY_TOPIC_ID):
    try:
        if not TELEGRAM_TOKEN:
            print("[API] ❌ TELEGRAM_TOKEN kosong!")
            return False, "Token bot tidak tersedia"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'HTML'}
        if thread_id:
            data['message_thread_id'] = thread_id
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        with open(filepath, 'rb') as f:
            files = {'photo': f}
            r = req.post(url, files=files, data=data, timeout=30)
        if r.status_code == 200:
            print(f"[API] ✅ Photo sent to Telegram")
            return True, r.json()
        else:
            print(f"[API] ❌ Telegram error: {r.status_code} {r.text}")
            return False, r.text
    except Exception as e:
        print(f"[API] ❌ send_photo error: {e}")
        return False, str(e)

def send_message_to_telegram(chat_id, text):
    try:
        if not TELEGRAM_TOKEN:
            return False
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = req.post(url, data={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[API] send_message error: {e}")
        return False

# =====================================================================================
#  API ENDPOINTS
# =====================================================================================
@app.route('/', methods=['GET'])
def home():
    ensure_stocks_file()
    return jsonify({
        "status": "OK",
        "message": "Pakel MlbbStore APK API",
        "version": "7.0",
        "time": datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S WIB')
    })

@app.route('/api/paket', methods=['GET'])
def get_paket():
    flashsale_diskon, flashsale_sisa = read_flashsale()
    paket_list = []
    all_paket = get_all_paket_combined_api()

    for kode, data in all_paket.items():
        stok = get_stok(kode)
        harga_final = data['harga']
        if flashsale_diskon > 0:
            harga_final = int(harga_final * (100 - flashsale_diskon) / 100)
        paket_list.append({
            "kode": kode,
            "nama": data['nama'],
            "harga": data['harga'],
            "harga_str": data['harga_str'],
            "harga_final": harga_final,
            "harga_final_str": f"Rp {harga_final:,}".replace(",", "."),
            "poin": data['poin'],
            "stok": stok,
            "deskripsi": data['deskripsi'],
            "kategori": data['kategori'],
            "is_custom": data['is_custom'],
            "flashsale": flashsale_diskon > 0,
            "flashsale_diskon": flashsale_diskon
        })
    return jsonify({"status": "OK", "paket": paket_list,
                    "flashsale_diskon": flashsale_diskon,
                    "flashsale_sisa": flashsale_sisa})

@app.route('/api/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        chat_id = str(data.get('chat_id', '')).strip()
        paket_kode = data.get('paket_kode')
        payment_method = data.get('payment_method', 'TRANSFER')

        if not chat_id or not chat_id.isdigit():
            return jsonify({"status": "ERROR", "message": "Chat ID tidak valid"}), 400
        if len(chat_id) < 8 or len(chat_id) > 15:
            return jsonify({"status": "ERROR", "message": "Chat ID harus 8-15 digit"}), 400
        if len(set(chat_id)) < 4:
            return jsonify({"status": "ERROR", "message": "Chat ID terdeteksi palsu"}), 400
        if chat_id in ['12345678', '123456789', '1234567890', '11111111', '00000000']:
            return jsonify({"status": "ERROR", "message": "Chat ID terdeteksi palsu"}), 400

        all_paket = get_all_paket_combined_api()
        if paket_kode not in all_paket:
            return jsonify({"status": "ERROR", "message": "Paket tidak ditemukan"}), 400

        paket_data = all_paket[paket_kode]
        nama = paket_data['nama']
        harga = paket_data['harga']
        poin = paket_data['poin']

        stok = get_stok(paket_kode)
        if stok <= 0:
            return jsonify({"status": "ERROR", "message": "Stok habis"}), 400

        with orders_lock:
            try:
                with open(F_ORDERS, "r") as f:
                    for line in f:
                        parts = line.strip().split('|')
                        if len(parts) >= 8 and parts[0] == chat_id and parts[7].strip() == "PENDING":
                            return jsonify({
                                "status": "ERROR",
                                "message": "Kamu masih punya pesanan PENDING (Resi: " + parts[6] + "). Selesaikan atau batalkan dulu!"
                            }), 400
            except FileNotFoundError:
                pass

            if payment_method == "POIN":
                poin_dibutuhkan = poin
                saldo_poin = read_points(chat_id)
                if saldo_poin < poin_dibutuhkan:
                    return jsonify({
                        "status": "ERROR",
                        "message": "Poin tidak cukup! Butuh " + str(poin_dibutuhkan) + " poin, saldo kamu " + str(saldo_poin) + " poin."
                    }), 400

                add_user_points(chat_id, -poin_dibutuhkan, "Tukar Paket " + nama)

                resi = "PKL-MLBB-" + str(random.randint(10000, 99999))
                now = datetime.now(WIB)
                tanggal = now.strftime('%d-%m-%Y')
                hari_map = {'Mon':'Senin','Tue':'Selasa','Wed':'Rabu','Thu':'Kamis','Fri':'Jumat','Sat':'Sabtu','Sun':'Minggu'}
                hari = hari_map.get(now.strftime('%a'), now.strftime('%a'))
                jam = now.strftime('%H:%M:%S WIB')
                ts = int(now.timestamp())

                order_line = (str(chat_id) + "|" + tanggal + "|" + hari + "|" + jam + "|" + nama + "|" +
                              str(poin_dibutuhkan) + " POIN|" + resi + "|BERHASIL|" + str(ts) +
                              "|POIN|" + str(poin_dibutuhkan) + "|0\n")
                with open(F_ORDERS, "a") as f:
                    f.write(order_line)

                try:
                    import threading as _th
                    _notif_text = (
                        "ORDER PAKAI POIN!\n\n"
                        "Chat ID: <code>" + str(chat_id) + "</code>\n"
                        "Paket: <b>" + nama + "</b>\n"
                        "Poin Terpakai: " + str(poin_dibutuhkan) + "\n"
                        "Saldo Sisa: " + str(saldo_poin - poin_dibutuhkan) + " poin\n"
                        "Resi: <code>" + resi + "</code>\n"
                        "Waktu: " + hari + ", " + tanggal + " " + jam + "\n\n"
                        "<i>Order BERHASIL otomatis. Kirim script ke user!</i>"
                    )
                    _th.Thread(
                        target=send_message_to_telegram,
                        args=(ADMIN_TELEGRAM_ID, _notif_text),
                        daemon=True
                    ).start()
                except Exception as e:
                    print(f"[API] notif admin poin error: {e}")

                return jsonify({
                    "status": "OK",
                    "message": "Order pakai poin berhasil!",
                    "resi": resi,
                    "harga_final": poin_dibutuhkan,
                    "harga_final_str": str(poin_dibutuhkan) + " Poin",
                    "paket": nama,
                    "saldo_poin_sisa": saldo_poin - poin_dibutuhkan,
                    "waktu": hari + ", " + tanggal + " " + jam,
                    "payment_method": "POIN"
                })

            harga_final = harga
            diskon_detail = []

            flashsale_diskon, _ = read_flashsale()
            if flashsale_diskon > 0:
                harga_final = int(harga_final * (100 - flashsale_diskon) / 100)
                diskon_detail.append("FlashSale -" + str(flashsale_diskon) + "%")

            tier_label, multiplier, diskon_tier = get_user_tier(chat_id)
            if diskon_tier > 0:
                harga_final = int(harga_final * (100 - diskon_tier) / 100)
                diskon_detail.append("Tier -" + str(diskon_tier) + "%")

            if get_coupon_status(chat_id) == "AVAILABLE":
                harga_final -= 10000
                diskon_detail.append("KuponNewUser -Rp10.000")

            lucky_persen = get_user_lucky_diskon_persen(chat_id)
            if lucky_persen > 0:
                harga_final = int(harga_final * (100 - lucky_persen) / 100)
                diskon_detail.append("LuckyDraw -" + str(lucky_persen) + "%")

            voucher_rupiah = get_user_voucher_rupiah(chat_id)
            if voucher_rupiah > 0:
                harga_final -= voucher_rupiah
                diskon_detail.append("Voucher -Rp" + str(voucher_rupiah))

            harga_final = max(0, harga_final)
            print("[API] Order " + str(chat_id) + " - diskon: " + (", ".join(diskon_detail) if diskon_detail else "NONE"))

            resi = "PKL-MLBB-" + str(random.randint(10000, 99999))
            now = datetime.now(WIB)
            tanggal = now.strftime('%d-%m-%Y')
            hari_map = {'Mon':'Senin','Tue':'Selasa','Wed':'Rabu','Thu':'Kamis','Fri':'Jumat','Sat':'Sabtu','Sun':'Minggu'}
            hari = hari_map.get(now.strftime('%a'), now.strftime('%a'))
            jam = now.strftime('%H:%M:%S WIB')
            ts = int(now.timestamp())

            order_line = (str(chat_id) + "|" + tanggal + "|" + hari + "|" + jam + "|" + nama + "|Rp " +
                          str(harga_final) + "|" + resi + "|PENDING|" + str(ts) + "|" +
                          payment_method + "|0|0\n")
            with open(F_ORDERS, "a") as f:
                f.write(order_line)

            if get_coupon_status(chat_id) == "AVAILABLE":
                set_coupon_status_api(chat_id, "PENDING")
                print("[API] Kupon new user " + str(chat_id) + " -> PENDING")
            if voucher_rupiah > 0:
                consume_user_voucher_api(chat_id)
                print("[API] Voucher rupiah " + str(chat_id) + " consumed")
            if lucky_persen > 0:
                consume_user_lucky_diskon_api(chat_id)
                print("[API] Lucky draw diskon " + str(chat_id) + " consumed")

            return jsonify({
                "status": "OK", "message": "Order berhasil dibuat",
                "resi": resi, "harga_final": harga_final,
                "harga_final_str": "Rp " + str(harga_final), "paket": nama,
                "voucher_diskon": voucher_rupiah,
                "waktu": hari + ", " + tanggal + " " + jam,
                "payment_method": "TRANSFER"
            })
    except Exception as e:
        print(f"[API] create_order error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@app.route('/api/upload-bukti', methods=['POST'])
def upload_bukti():
    try:
        chat_id = str(request.form.get('chat_id', '')).strip()
        resi = str(request.form.get('resi', '')).strip().upper()
        nama_user = request.form.get('nama_user', 'Pembeli APK')

        if not chat_id or not resi:
            return jsonify({"status": "ERROR", "message": "Chat ID & Resi wajib diisi"}), 400
        if 'foto' not in request.files:
            return jsonify({"status": "ERROR", "message": "File foto tidak ditemukan"}), 400

        foto = request.files['foto']
        if not foto or not foto.filename:
            return jsonify({"status": "ERROR", "message": "File kosong"}), 400

        order = get_order_by_resi(resi)
        if not order:
            return jsonify({"status": "ERROR", "message": "Resi tidak ditemukan"}), 404
        if order['status'] != 'PENDING':
            return jsonify({"status": "ERROR", "message": f"Order sudah diproses ({order['status']})"}), 400

        ensure_proofs_folder()
        ext = os.path.splitext(foto.filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            ext = '.jpg'
        safe_resi = resi.replace("/", "_").replace("\\", "_")
        filename = f"{safe_resi}_{chat_id}_{int(time.time())}{ext}"
        filepath = os.path.join(F_PROOFS, filename)
        foto.save(filepath)
        print(f"[API] 📸 Bukti saved: {filepath}")

        caption = (
            f"🚨 <b>BUKTI TRANSFER MASUK (VIA APK)!</b>\n\n"
            f"👤 User: <b>{nama_user}</b>\n"
            f"🆔 Chat ID: <code>{chat_id}</code>\n"
            f"🔑 Resi: <code>{resi}</code>\n"
            f"📦 Paket: <b>{order['paket']}</b>\n"
            f"💰 Harga: <b>{order['harga']}</b>\n"
            f"⏱️ {datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S WIB')}\n\n"
            f"👇 Cek mutasi, klik ACC atau TOLAK!"
        )
        reply_markup = {
            "inline_keyboard": [[
                {"text": "✅ ACC", "callback_data": f"acc|{chat_id}|{resi}"},
                {"text": "❌ TOLAK", "callback_data": f"tolak|{chat_id}|{resi}"}
            ]]
        }
        ok, info = send_photo_to_telegram(filepath, caption, reply_markup)
        if not ok:
            return jsonify({"status": "ERROR", "message": f"Gagal kirim ke admin: {info}"}), 500

        return jsonify({
            "status": "OK",
            "message": "Bukti berhasil dikirim! Menunggu ACC admin.",
            "resi": resi
        })
    except Exception as e:
        print(f"[API] upload_bukti error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/cek-resi', methods=['GET'])
def cek_resi():
    resi = request.args.get('resi', '').strip().upper()
    if not resi:
        return jsonify({"status": "ERROR", "message": "Resi tidak boleh kosong"}), 400
    order = get_order_by_resi(resi)
    if order:
        return jsonify({"status": "OK", "order": order})
    return jsonify({"status": "ERROR", "message": "Resi tidak ditemukan"}), 404

@app.route('/api/cek-pending', methods=['GET'])
def cek_pending():
    chat_id = request.args.get('chat_id', '').strip()
    if not chat_id:
        return jsonify({"status": "ERROR", "message": "Chat ID wajib diisi"}), 400
    pending = []
    try:
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[0] == str(chat_id) and parts[7].strip() == "PENDING":
                    pending.append({
                        'resi': parts[6], 'paket': parts[4], 'harga': parts[5],
                        'tanggal': parts[1], 'jam': parts[3]
                    })
    except FileNotFoundError:
        pass
    return jsonify({"status": "OK", "pending": pending, "count": len(pending)})

@app.route('/api/cancel-order', methods=['POST'])
def cancel_order():
    try:
        data = request.json
        chat_id = str(data.get('chat_id', '')).strip()
        resi = str(data.get('resi', '')).strip().upper()
        if not chat_id or not resi:
            return jsonify({"status": "ERROR", "message": "Chat ID & Resi wajib diisi"}), 400
        order = get_order_by_resi(resi)
        if not order:
            return jsonify({"status": "ERROR", "message": "Resi tidak ditemukan"}), 404
        if order['chat_id'] != chat_id:
            return jsonify({"status": "ERROR", "message": "Resi bukan milik Anda"}), 403
        if order['status'] != 'PENDING':
            return jsonify({"status": "ERROR", "message": f"Order sudah diproses ({order['status']})"}), 400
        rows = []
        updated = False
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[6].strip().upper() == resi:
                    parts[7] = "CANCELLED"
                    updated = True
                rows.append('|'.join(parts) + "\n")
        if updated:
            with open(F_ORDERS, "w") as f:
                f.writelines(rows)
            return jsonify({"status": "OK", "message": "Pesanan berhasil dibatalkan"})
        return jsonify({"status": "ERROR", "message": "Gagal update status"}), 500
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/cek-poin', methods=['GET'])
def cek_poin():
    chat_id = request.args.get('chat_id', '').strip()
    if not chat_id:
        return jsonify({"status": "ERROR", "message": "Chat ID tidak boleh kosong"}), 400
    points = read_points(chat_id)
    tier_label, multiplier, diskon = get_user_tier(chat_id)
    total_order = count_user_success_orders(chat_id)
    return jsonify({
        "status": "OK",
        "data": {"chat_id": chat_id, "points": points, "tier": tier_label,
                 "multiplier": multiplier, "diskon": diskon, "total_order": total_order}
    })

@app.route('/api/riwayat', methods=['GET'])
def api_riwayat():
    chat_id = request.args.get('chat_id', '').strip()
    if not chat_id:
        return jsonify({"status": "ERROR", "message": "Chat ID wajib diisi"}), 400
    orders = get_user_orders_list(chat_id, limit=15)
    return jsonify({"status": "OK", "orders": orders, "total": len(orders)})

@app.route('/api/leaderboard', methods=['GET'])
def api_leaderboard():
    lb = get_leaderboard(10)
    return jsonify({"status": "OK", "leaderboard": lb})

@app.route('/api/referral', methods=['GET'])
def api_referral():
    chat_id = request.args.get('chat_id', '').strip()
    if not chat_id:
        return jsonify({"status": "ERROR", "message": "Chat ID wajib diisi"}), 400
    total, bonus_cair = get_referral_stats(chat_id)
    bot_username = "Pakel_Mlbb_Store_bot"
    link = f"https://t.me/{bot_username}?start=ref_{chat_id}"
    return jsonify({
        "status": "OK",
        "data": {"total_ref": total, "bonus_cair": bonus_cair,
                 "link": link, "bot_username": bot_username}
    })

@app.route('/api/referral/register', methods=['POST'])
def api_referral_register():
    try:
        data = request.json
        referrer_id = str(data.get('referrer_id', '')).strip()
        referred_id = str(data.get('referred_id', '')).strip()
        if not referrer_id or not referred_id:
            return jsonify({"status": "ERROR", "message": "Data tidak lengkap"}), 400
        ok = register_referral(referrer_id, referred_id)
        if ok:
            return jsonify({"status": "OK", "message": "Referral berhasil didaftarkan"})
        else:
            return jsonify({"status": "ERROR", "message": "Referral tidak valid / sudah terdaftar"}), 400
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/lucky-draw', methods=['GET'])
def api_lucky_draw():
    chat_id = request.args.get('chat_id', '').strip()
    if not chat_id:
        return jsonify({"status": "ERROR", "message": "Chat ID wajib diisi"}), 400
    can = can_spin_now(chat_id)
    last = get_last_spin_time(chat_id)
    sisa_detik = 0
    if last > 0:
        sisa_detik = max(0, (LUCKY_DRAW_COOLDOWN_JAM * 3600) - (time.time() - last))
    return jsonify({
        "status": "OK",
        "data": {"can_spin": can, "last_spin": last, "sisa_detik": int(sisa_detik)}
    })

@app.route('/api/lucky-draw/spin', methods=['POST'])
def api_lucky_draw_spin():
    try:
        data = request.json
        chat_id = str(data.get('chat_id', '')).strip()
        if not chat_id or not chat_id.isdigit():
            return jsonify({"status": "ERROR", "message": "Chat ID tidak valid"}), 400
        if not can_spin_now(chat_id):
            return jsonify({"status": "ERROR", "message": "Kamu sudah spin hari ini!"}), 400
        hadiah = roll_lucky_draw()
        label, tipe, nilai, _ = hadiah
        save_spin(chat_id)
        result = {"status": "OK", "hadiah": label, "tipe": tipe, "nilai": nilai}
        if tipe == "poin":
            new_total = add_user_points(chat_id, nilai, "Hadiah Lucky Draw")
            result['total_poin'] = new_total
            result['message'] = f"Selamat! +{nilai} poin masuk ke saldo kamu."
        elif tipe == "diskon":
            try:
                rows = []
                if os.path.exists(F_USER_VOUCHER):
                    with open(F_USER_VOUCHER, "r") as f:
                        rows = [ln.strip() for ln in f if ln.strip()]
                rows.append(f"{chat_id}|DISKON{nilai}|{int(time.time())}")
                with open(F_USER_VOUCHER, "w") as f:
                    f.write("\n".join(rows) + "\n")
            except Exception as e:
                print(f"[API] save diskon error: {e}")
            result['message'] = f"Selamat! Diskon {nilai}% aktif otomatis di akunmu."
        else:
            result['message'] = "JACKPOT! Kamu menang Paket Semi-Safe GRATIS. Hubungi admin untuk klaim."
            try:
                send_message_to_telegram(
                    ADMIN_TELEGRAM_ID,
                    f"🎰 <b>LUCKY DRAW JACKPOT!</b>\n\n"
                    f"👤 User ID: <code>{chat_id}</code>\n"
                    f"🎁 Hadiah: {label}\n\n"
                    f"Segera hubungi user untuk klaim!"
                )
            except Exception:
                pass
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/redeem-voucher', methods=['POST'])
def redeem_voucher():
    try:
        data = request.json
        chat_id = str(data.get('chat_id', '')).strip()
        kode = data.get('kode', '').strip().upper()
        if not chat_id or not kode:
            return jsonify({"status": "ERROR", "message": "Data tidak lengkap"}), 400
        if user_has_voucher(chat_id, kode):
            return jsonify({"status": "ERROR", "message": "Kamu sudah redeem voucher ini"}), 400
        with vouchers_lock:
            vouchers = read_vouchers()
            if kode not in vouchers:
                return jsonify({"status": "ERROR", "message": "Kode voucher tidak ditemukan"}), 404
            v = vouchers[kode]
            if v['terpakai'] >= v['max']:
                return jsonify({"status": "ERROR", "message": "Kuota voucher habis"}), 400
            if v['expired'] > 0 and time.time() > v['expired']:
                return jsonify({"status": "ERROR", "message": "Voucher sudah expired"}), 400
            save_user_voucher(chat_id, kode, v['diskon'])
            v['terpakai'] += 1
            tmp = F_VOUCHERS + ".tmp"
            rows = []
            for k, vv in vouchers.items():
                rows.append(f"{k}|{vv['diskon']}|{vv['max']}|{vv['terpakai']}|{vv['expired']}")
            with open(tmp, "w") as f:
                f.write("\n".join(rows) + "\n")
            os.replace(tmp, F_VOUCHERS)
            return jsonify({"status": "OK", "message": "Voucher berhasil di-redeem",
                            "kode": kode, "diskon": v['diskon'],
                            "sisa_kuota": v['max'] - v['terpakai']})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@app.route('/api/vouchers', methods=['GET'])
def get_vouchers():
    vouchers = read_vouchers()
    now_ts = time.time()
    aktif = []
    for kode, v in vouchers.items():
        if v['terpakai'] < v['max'] and (v['expired'] == 0 or now_ts < v['expired']):
            aktif.append({"kode": kode, "diskon": v['diskon'],
                          "sisa": v['max'] - v['terpakai'], "expired": v['expired']})
    return jsonify({"status": "OK", "vouchers": aktif})

@app.route('/api/cek-user', methods=['GET'])
def cek_user():
    chat_id = request.args.get('chat_id', '').strip()
    if not chat_id or not chat_id.isdigit():
        return jsonify({"status": "ERROR", "message": "Chat ID tidak valid"}), 400
    if not TELEGRAM_TOKEN:
        return jsonify({"status": "ERROR", "message": "Token bot belum diset"}), 500
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChat"
        r = req.get(url, params={"chat_id": chat_id}, timeout=8)
        data = r.json()
        if data.get('ok'):
            chat = data.get('result', {})
            nama = ' '.join(filter(None, [chat.get('first_name'), chat.get('last_name')])) or chat.get('title') or 'User'
            return jsonify({
                "status": "OK",
                "user": {
                    "chat_id": chat_id, "nama": nama.strip(),
                    "username": chat.get('username', ''),
                    "type": chat.get('type', 'private')
                }
            })
        else:
            return jsonify({"status": "NOT_FOUND", "message": data.get('description', 'Tidak ditemukan')}), 200
    except Exception as e:
        print(f"[API] cek_user error: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/user-vouchers', methods=['GET'])
def api_user_vouchers():
    chat_id = request.args.get('chat_id', '').strip()
    if not chat_id:
        return jsonify({"status": "ERROR", "message": "Chat ID wajib diisi"}), 400
    vouchers = get_user_voucher_list(chat_id)
    total_diskon = sum(v['diskon'] for v in vouchers)
    return jsonify({
        "status": "OK", "vouchers": vouchers,
        "total_diskon": total_diskon, "count": len(vouchers)
    })









@app.route('/api/report-error', methods=['POST'])
def api_report_error():
    """Terima error report dari APK client."""
    try:
        data = request.json or {}
        err_type = str(data.get('type', 'unknown'))[:50]
        err_msg = str(data.get('message', ''))[:500]
        err_file = str(data.get('file', ''))[:200]
        err_line = str(data.get('line', ''))[:20]
        chat_id = str(data.get('chat_id', 'anon'))[:20]
        ua = str(request.headers.get('User-Agent', ''))[:200]
        now_str = datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S')
        try:
            with open(F_ERROR_LOG_API, "a") as f:
                f.write(now_str + " | " + chat_id + " | " + err_type + " | " + err_msg + " | " + err_file + ":" + err_line + " | " + ua + "\n")
        except Exception:
            pass
        return jsonify({"status": "OK"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@app.route('/api/admin/recent-errors', methods=['GET'])
def api_recent_errors():
    """Ambil error log terbaru (buat admin)."""
    try:
        limit = int(request.args.get('limit', 20))
        if limit < 1: limit = 1
        if limit > 100: limit = 100
        if not os.path.exists(F_ERROR_LOG_API):
            return jsonify({"status": "OK", "errors": [], "count": 0})
        with open(F_ERROR_LOG_API, "r") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        recent = lines[-limit:]
        return jsonify({"status": "OK", "errors": recent, "count": len(recent), "total": len(lines)})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/inbox/clear', methods=['POST'])
def api_inbox_clear():
    """Hapus inbox user tertentu."""
    try:
        data = request.json
        chat_id = str(data.get('chat_id', '')).strip()
        if not chat_id:
            return jsonify({"status": "ERROR", "message": "chat_id wajib"}), 400
        if not os.path.exists(F_INBOX):
            return jsonify({"status": "OK", "message": "Inbox kosong"})
        with open(F_INBOX, "r") as f:
            lines = [ln for ln in f if ln.strip()]
        kept = [ln for ln in lines if not ln.startswith(chat_id + "|")]
        removed = len(lines) - len(kept)
        with open(F_INBOX, "w") as f:
            f.writelines(kept)
        return jsonify({"status": "OK", "removed": removed})
    except Exception as e:
        print("[API] api_inbox_clear error: " + str(e))
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/inbox', methods=['GET'])
def api_inbox():
    """Ambil inbox user (max 50 terbaru)."""
    try:
        chat_id = request.args.get('chat_id', '').strip()
        if not chat_id:
            return jsonify({"status": "ERROR", "message": "chat_id wajib"}), 400
        limit = int(request.args.get('limit', 50))
        if limit < 1: limit = 1
        if limit > 100: limit = 100
        if not os.path.exists(F_INBOX):
            return jsonify({"status": "OK", "inbox": [], "count": 0})
        with open(F_INBOX, "r") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        result = []
        for ln in lines:
            parts = ln.split('|')
            if len(parts) < 5:
                continue
            if parts[0] != chat_id:
                continue
            try:
                ts = int(parts[4])
            except ValueError:
                ts = 0
            result.append({
                "type": parts[1],
                "title": parts[2],
                "body": parts[3],
                "timestamp": ts,
            })
        result.sort(key=lambda x: x['timestamp'], reverse=True)
        result = result[:limit]
        return jsonify({"status": "OK", "inbox": result, "count": len(result)})
    except Exception as e:
        print("[API] api_inbox error: " + str(e))
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/testimoni', methods=['GET'])
def api_testimoni():
    """Baca testimoni real dari file."""
    try:
        limit = int(request.args.get('limit', 20))
        if limit < 1: limit = 1
        if limit > 50: limit = 50
        if not os.path.exists(F_TESTIMONI):
            return jsonify({"status": "OK", "testimoni": [], "count": 0})
        with open(F_TESTIMONI, "r") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        recent = lines[-limit:]
        result = []
        for ln in reversed(recent):
            parts = ln.split('|')
            if len(parts) >= 6:
                try:
                    ts = int(parts[4])
                except ValueError:
                    ts = 0
                result.append({
                    "chat_id_masked": parts[1],
                    "paket": parts[2],
                    "harga": parts[3],
                    "timestamp": ts,
                    "metode": parts[5],
                })
        return jsonify({"status": "OK", "testimoni": result, "count": len(result)})
    except Exception as e:
        print("[API] api_testimoni error: " + str(e))
        return jsonify({"status": "ERROR", "message": str(e)}), 500

# =====================================================================================
#  ENDPOINT BARU v7 — RESTOCK LOG (buat notif restock di APK)
# =====================================================================================
@app.route('/api/restock-log', methods=['GET'])
def api_restock_log():
    """Baca restock log terbaru buat notif di APK."""
    try:
        limit = int(request.args.get('limit', 5))
        if limit < 1:
            limit = 1
        if limit > 50:
            limit = 50

        if not os.path.exists(F_RESTOCK_LOG):
            return jsonify({"status": "OK", "restock": [], "count": 0})

        with open(F_RESTOCK_LOG, "r") as f:
            lines = [ln.strip() for ln in f if ln.strip()]

        recent = lines[-limit:]
        restock = []
        # Ambil nama paket dari MASTER atau custom
        all_paket = get_all_paket_combined_api()

        for ln in reversed(recent):
            parts = ln.split('|')
            if len(parts) >= 5:
                kode = parts[1]
                nama_paket = all_paket.get(kode, {}).get('nama', kode)
                try:
                    stok_lama = int(parts[2])
                    stok_baru = int(parts[3])
                except ValueError:
                    stok_lama = 0
                    stok_baru = 0
                restock.append({
                    "timestamp": parts[0],
                    "kode": kode,
                    "nama": nama_paket,
                    "stok_lama": stok_lama,
                    "stok_baru": stok_baru,
                    "trigger": parts[4],
                })

        return jsonify({
            "status": "OK",
            "restock": restock,
            "count": len(restock),
            "total_log": len(lines)
        })
    except Exception as e:
        print(f"[API] api_restock_log error: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

# =====================================================================================
#  RUN — STANDALONE MODE
# =====================================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"[INFO] Pakel MlbbStore APK API v7 running on port {port}")
    ensure_stocks_file()
    ensure_proofs_folder()
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)