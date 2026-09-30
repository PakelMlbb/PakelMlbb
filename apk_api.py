# =====================================================================================
#  PAKEL MLBBSTORE — APK API SERVER
#  Jembatan antara APK & Bot Telegram
#  Deploy bareng bot Telegram di Railway
# =====================================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import time
from datetime import datetime, timezone, timedelta

# =====================================================================================
#  KONFIGURASI (SAMA DENGAN BOT TELEGRAM)
# =====================================================================================
WIB = timezone(timedelta(hours=7))
DATA_DIR = os.environ.get('DATA_DIR', '.')

F_USERS = os.path.join(DATA_DIR, "users.txt")
F_ORDERS = os.path.join(DATA_DIR, "orders.txt")
F_POINTS = os.path.join(DATA_DIR, "points.txt")
F_VOUCHERS = os.path.join(DATA_DIR, "vouchers.txt")
F_USER_VOUCHER = os.path.join(DATA_DIR, "user_voucher.txt")
F_STOCKS = os.path.join(DATA_DIR, "stocks.txt")
F_FLASHSALE = os.path.join(DATA_DIR, "flashsale.txt")
F_COUPONS = os.path.join(DATA_DIR, "coupons.txt")
F_REFERRALS = os.path.join(DATA_DIR, "referrals.txt")
F_LASTTIER = os.path.join(DATA_DIR, "last_tier.txt")

ADMIN_TELEGRAM_ID = 8772023108

# =====================================================================================
#  DATA PAKET (HARUS SAMA DENGAN BOT TELEGRAM)
# =====================================================================================
MASTER_PAKET = {
    'buy_natural': ("Natural Balance (30 Hari)", 120000, "Rp 120.000", 45, "..."),
    'buy_light': ("Light VIP + Drone (30 Hari)", 95000, "Rp 95.000", 35, "..."),
    'buy_semisafe': ("Semi-Safe 14 Hari", 75000, "Rp 75.000", 25, "..."),
    'buy_lifetimesafe': ("Lifetime Safe Permanent", 200000, "Rp 200.000", 75, "..."),
    'buy_sultan': ("Sultan One Hit 100% (30 Hari)", 150000, "Rp 150.000", 55, "..."),
    'buy_pro': ("VIP Pro One Hit 80% (30 Hari)", 100000, "Rp 100.000", 40, "..."),
    'buy_semiprivate': ("Semi-Private 14 Hari", 75000, "Rp 75.000", 25, "..."),
    'buy_permanent': ("Permanent Legend (Lifetime)", 250000, "Rp 250.000", 90, "..."),
}

# =====================================================================================
#  FLASK APP
# =====================================================================================
app = Flask(__name__)
CORS(app)  # Biar APK bisa akses

# =====================================================================================
#  HELPER FUNCTIONS (SAMA DENGAN BOT)
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
    return stocks

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

# =====================================================================================
#  API ENDPOINTS
# =====================================================================================

@app.route('/', methods=['GET'])
def home():
    """Test API jalan."""
    return jsonify({
        "status": "OK",
        "message": "Pakel MlbbStore APK API",
        "version": "1.0",
        "time": datetime.now(WIB).strftime('%d-%m-%Y %H:%M:%S WIB')
    })

@app.route('/api/paket', methods=['GET'])
def get_paket():
    """Ambil semua paket."""
    stocks = read_stocks()
    flashsale_diskon, flashsale_sisa = read_flashsale()
    
    paket_list = []
    for kode, data in MASTER_PAKET.items():
        nama, harga, harga_str, poin, deskripsi = data
        stok = stocks.get(kode, 0)
        
        # Hitung harga flash sale
        harga_final = harga
        if flashsale_diskon > 0:
            harga_final = int(harga * (100 - flashsale_diskon) / 100)
        
        paket_list.append({
            "kode": kode,
            "nama": nama,
            "harga": harga,
            "harga_str": harga_str,
            "harga_final": harga_final,
            "harga_final_str": f"Rp {harga_final:,}",
            "poin": poin,
            "stok": stok,
            "deskripsi": deskripsi,
            "flashsale": flashsale_diskon > 0,
            "flashsale_diskon": flashsale_diskon
        })
    
    return jsonify({
        "status": "OK",
        "paket": paket_list,
        "flashsale_diskon": flashsale_diskon,
        "flashsale_sisa": flashsale_sisa
    })

@app.route('/api/order', methods=['POST'])
def create_order():
    """Buat order baru dari APK."""
    try:
        data = request.json
        chat_id = data.get('chat_id')
        paket_kode = data.get('paket_kode')
        payment_method = data.get('payment_method', 'TRANSFER')
        voucher_kode = data.get('voucher_kode', '')
        username = data.get('username', '')
        nama_user = data.get('nama_user', '')
        
        if not chat_id or not paket_kode:
            return jsonify({"status": "ERROR", "message": "Data tidak lengkap"}), 400
        
        if paket_kode not in MASTER_PAKET:
            return jsonify({"status": "ERROR", "message": "Paket tidak ditemukan"}), 400
        
        nama, harga, harga_str, poin, _ = MASTER_PAKET[paket_kode]
        
        # Cek stok
        stocks = read_stocks()
        stok = stocks.get(paket_kode, 0)
        if stok <= 0:
            return jsonify({"status": "ERROR", "message": "Stok habis"}), 400
        
        # Hitung harga final
        harga_final = harga
        
        # Flash sale
        flashsale_diskon, _ = read_flashsale()
        if flashsale_diskon > 0:
            harga_final = int(harga * (100 - flashsale_diskon) / 100)
        else:
            # Diskon tier
            tier_label, multiplier, diskon_tier = get_user_tier(chat_id)
            if diskon_tier > 0:
                harga_final = int(harga * (100 - diskon_tier) / 100)
            
            # Promo member baru
            if get_coupon_status(chat_id) == "AVAILABLE":
                harga_final -= 10000
        
        # Voucher
        if voucher_kode:
            vouchers = read_vouchers()
            kode_up = voucher_kode.upper().strip()
            if kode_up in vouchers:
                v = vouchers[kode_up]
                if v['terpakai'] < v['max'] and (v['expired'] == 0 or time.time() < v['expired']):
                    harga_final -= v['diskon']
        
        harga_final = max(0, harga_final)
        
        # Generate resi
        resi = f"PKL-MLBB-{random.randint(10000, 99999)}"
        
        # Simpan order
        now = datetime.now(WIB)
        tanggal = now.strftime('%d-%m-%Y')
        hari_map = {'Mon':'Senin','Tue':'Selasa','Wed':'Rabu','Thu':'Kamis','Fri':'Jumat','Sat':'Sabtu','Sun':'Minggu'}
        hari = hari_map.get(now.strftime('%a'), now.strftime('%a'))
        jam = now.strftime('%H:%M:%S WIB')
        ts = int(now.timestamp())
        
        order_line = f"{chat_id}|{tanggal}|{hari}|{jam}|{nama}|Rp {harga_final:,}|{resi}|PENDING|{ts}|{payment_method}|0|0\n"
        with open(F_ORDERS, "a") as f:
            f.write(order_line)
        
        return jsonify({
            "status": "OK",
            "message": "Order berhasil dibuat",
            "resi": resi,
            "harga_final": harga_final,
            "harga_final_str": f"Rp {harga_final:,}",
            "paket": nama
        })
    
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/cek-resi', methods=['GET'])
def cek_resi():
    """Cek status resi."""
    resi = request.args.get('resi', '').strip().upper()
    if not resi:
        return jsonify({"status": "ERROR", "message": "Resi tidak boleh kosong"}), 400
    
    try:
        with open(F_ORDERS, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 8 and parts[6].strip().upper() == resi:
                    return jsonify({
                        "status": "OK",
                        "order": {
                            "chat_id": parts[0],
                            "tanggal": parts[1],
                            "hari": parts[2],
                            "jam": parts[3],
                            "paket": parts[4],
                            "harga": parts[5],
                            "resi": parts[6],
                            "status": parts[7],
                            "metode": parts[9] if len(parts) > 9 else "TRANSFER"
                        }
                    })
    except FileNotFoundError:
        pass
    
    return jsonify({"status": "ERROR", "message": "Resi tidak ditemukan"}), 404

@app.route('/api/cek-poin', methods=['GET'])
def cek_poin():
    """Cek poin user."""
    chat_id = request.args.get('chat_id', '').strip()
    if not chat_id:
        return jsonify({"status": "ERROR", "message": "Chat ID tidak boleh kosong"}), 400
    
    points = read_points(chat_id)
    tier_label, multiplier, diskon = get_user_tier(chat_id)
    total_order = count_user_success_orders(chat_id)
    
    return jsonify({
        "status": "OK",
        "data": {
            "chat_id": chat_id,
            "points": points,
            "tier": tier_label,
            "multiplier": multiplier,
            "diskon": diskon,
            "total_order": total_order
        }
    })

@app.route('/api/redeem-voucher', methods=['POST'])
def redeem_voucher():
    """Redeem voucher dari APK."""
    try:
        data = request.json
        chat_id = data.get('chat_id')
        kode = data.get('kode', '').strip().upper()
        
        if not chat_id or not kode:
            return jsonify({"status": "ERROR", "message": "Data tidak lengkap"}), 400
        
        # Cek duplikat
        if user_has_voucher(chat_id, kode):
            return jsonify({"status": "ERROR", "message": "Kamu sudah redeem voucher ini"}), 400
        
        vouchers = read_vouchers()
        if kode not in vouchers:
            return jsonify({"status": "ERROR", "message": "Kode voucher tidak ditemukan"}), 404
        
        v = vouchers[kode]
        if v['terpakai'] >= v['max']:
            return jsonify({"status": "ERROR", "message": "Kuota voucher habis"}), 400
        
        if v['expired'] > 0 and time.time() > v['expired']:
            return jsonify({"status": "ERROR", "message": "Voucher sudah expired"}), 400
        
        # Simpan ke user
        save_user_voucher(chat_id, kode, v['diskon'])
        
        # Increment terpakai
        v['terpakai'] += 1
        rows = []
        for k, vv in vouchers.items():
            rows.append(f"{k}|{vv['diskon']}|{vv['max']}|{vv['terpakai']}|{vv['expired']}")
        with open(F_VOUCHERS, "w") as f:
            f.write("\n".join(rows) + "\n")
        
        sisa = v['max'] - v['terpakai']
        
        return jsonify({
            "status": "OK",
            "message": "Voucher berhasil di-redeem",
            "kode": kode,
            "diskon": v['diskon'],
            "sisa_kuota": sisa
        })
    
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route('/api/vouchers', methods=['GET'])
def get_vouchers():
    """Ambil semua voucher aktif."""
    vouchers = read_vouchers()
    now_ts = time.time()
    aktif = []
    for kode, v in vouchers.items():
        if v['terpakai'] < v['max'] and (v['expired'] == 0 or now_ts < v['expired']):
            aktif.append({
                "kode": kode,
                "diskon": v['diskon'],
                "sisa": v['max'] - v['terpakai'],
                "expired": v['expired']
            })
    
    return jsonify({"status": "OK", "vouchers": aktif})

# =====================================================================================
#  RUN — STANDALONE MODE
# =====================================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[INFO] Pakel MlbbStore APK API running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)