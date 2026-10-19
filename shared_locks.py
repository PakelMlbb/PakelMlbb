# =====================================================================================
#  SHARED LOCKS — dipakai bersama oleh bot (pakeltest.py) dan API (apk_api.py)
#
#  Kenapa file ini ada?
#  Bot dan API jalan di SATU proses (lihat main.py), tapi sebelumnya masing-masing
#  bikin Lock sendiri-sendiri (orders_lock di bot != orders_lock di API), jadi
#  keduanya TIDAK saling mengunci dan bisa saling menimpa orders.txt / points.txt.
#
#  Dengan file ini, kedua modul memakai objek lock yang sama.
#  RLock dipakai (bukan Lock) supaya fungsi yang saling memanggil dalam thread
#  yang sama tidak deadlock.
#
#  Aturan urutan lock (hindari deadlock):  orders_lock  ->  points_lock / stocks
#  Jangan pernah mengambil orders_lock saat sedang memegang points_lock.
# =====================================================================================
import threading

orders_lock = threading.RLock()
points_lock = threading.RLock()
vouchers_lock = threading.RLock()
user_voucher_lock = threading.RLock()
coupons_lock = threading.RLock()
stocks_lock = threading.RLock()
referrals_lock = threading.RLock()
users_lock = threading.RLock()
spin_lock = threading.RLock()
