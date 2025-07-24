import yfinance as yf
import pandas as pd
import requests
import time

# =================================================================
# KONFIGURASI BOT ANALIS (UBAH BAGIAN INI)
# =================================================================
WEBHOOK_URL = "https://bule-bot-tele.onrender.com/webhook" # <<< PASTIKAN INI URL ANDA
TICKERS = {"US30": "^DJI", "XAUUSD": "GC=F", "BTCUSD": "BTC-USD"}
TIMEFRAME = "15M"
SMA_TREN = 200
PERIODE_SWING = 50
INTERVAL_CEK = 3600

# =================================================================
# KODE UTAMA BOT ANALIS (TIDAK PERLU DIUBAH)
# =================================================================
print("=============================================")
print(" Bot Analis Cerdas v2.2 (Perbaikan Stabilitas)")
print(f" Aset: {', '.join(TICKERS.keys())} | Timeframe: {TIMEFRAME}")
print(f" Strategi: Tren (SMA {SMA_TREN}) + Breakout Swing (Periode {PERIODE_SWING})")
print("=============================================")

status_sinyal = {ticker: None for ticker in TICKERS.keys()}

def cek_sinyal(nama_aset, ticker_simbol):
    global status_sinyal
    
    try:
        print(f"\n[{time.strftime('%H:%M:%S')}] Menganalisa {nama_aset} ({ticker_simbol})...")
        data = yf.download(tickers=ticker_simbol, period="30d", interval=TIMEFRAME, auto_adjust=True, progress=False)
        
        if data.empty or len(data) < PERIODE_SWING:
            print(f" -> Data untuk {nama_aset} tidak cukup atau kosong. Dilewati.")
            return

        # ================== PERBAIKAN TOTAL DIMULAI DI SINI ==================
        
        # 1. Hitung SMA pada data mentah
        data['SMA_TREN'] = data['Close'].rolling(window=SMA_TREN).mean()
        
        # 2. Hapus baris NaN HANYA setelah SMA dihitung
        data.dropna(subset=['SMA_TREN'], inplace=True)
        if data.empty:
            print(f" -> Data tidak cukup setelah menghitung SMA Tren.")
            return

        # 3. Ambil data terakhir untuk dianalisa
        baris_terakhir = data.iloc[-1]
        
        # 4. Cari swing high/low dari data SEBELUM baris terakhir
        data_sebelumnya = data.iloc[:-1] # Semua data KECUALI baris terakhir
        periode_data_swing = data_sebelumnya.tail(PERIODE_SWING) # Ambil 50 bar terakhir dari data sebelumnya
        
        swing_high_level = periode_data_swing['High'].max()
        swing_low_level = periode_data_swing['Low'].min()

        # ================== PERBAIKAN TOTAL SELESAI DI SINI ==================
        
        tren = "Uptrend" if baris_terakhir['Close'] > baris_terakhir['SMA_TREN'] else "Downtrend"
        print(f" -> Tren terdeteksi: {tren}")
        print(f" -> Harga: {baris_terakhir['Close']:.2f} | Swing High: {swing_high_level:.2f} | Swing Low: {swing_low_level:.2f}")

        sinyal_sekarang = None
        catatan_sinyal = ""

        if tren == "Uptrend" and baris_terakhir['Close'] > swing_high_level:
            sinyal_sekarang = "Bullish Breakout"
            catatan_sinyal = f"Harga menembus Swing High ({swing_high_level:,.2f}) searah Uptrend."
            print(f" 🔥 SINYAL TERDETEKSI: {sinyal_sekarang} untuk {nama_aset}!")

        elif tren == "Downtrend" and baris_terakhir['Close'] < swing_low_level:
            sinyal_sekarang = "Bearish Breakout"
            catatan_sinyal = f"Harga menembus Swing Low ({swing_low_level:,.2f}) searah Downtrend."
            print(f" 📉 SINYAL TERDETEKSI: {sinyal_sekarang} untuk {nama_aset}!")
        else:
            print(" -> Tidak ada sinyal breakout baru yang valid.")

        if sinyal_sekarang and sinyal_sekarang != status_sinyal[nama_aset]:
            payload = {"symbol": nama_aset, "price": f"{baris_terakhir['Close']:,.4f}", "direction": sinyal_sekarang, "timeframe": TIMEFRAME, "note": catatan_sinyal}
            print(f" -> Mengirim notifikasi ke Telegram...")
            try:
                requests.post(WEBHOOK_URL, json=payload, timeout=10)
                print(" -> Notifikasi berhasil dikirim!")
                status_sinyal[nama_aset] = sinyal_sekarang
            except Exception as e:
                print(f" -> GAGAL mengirim notifikasi: {e}")
        
    except Exception as e:
        print(f" -> Terjadi kesalahan fatal pada analisa {nama_aset}: {e}")

if __name__ == "__main__":
    while True:
        for nama_aset, ticker_simbol in TICKERS.items():
            cek_sinyal(nama_aset, ticker_simbol)
            time.sleep(5) 
        print(f"\nSemua aset telah diperiksa. Menunggu {INTERVAL_CEK / 60:.0f} menit sebelum siklus berikutnya...")
        time.sleep(INTERVAL_CEK)
