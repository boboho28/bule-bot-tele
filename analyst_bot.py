import yfinance as yf
import pandas as pd
import requests
import time

# =================================================================
# KONFIGURASI BOT ANALIS (UBAH BAGIAN INI)
# =================================================================

# 1. Masukkan URL Webhook LENGKAP dari bot "kurir" Anda di Render
WEBHOOK_URL = "https://bule-bot-tele.onrender.com/webhook" # <<< GANTI DENGAN URL ANDA

# 2. Pilih aset dan timeframe dari Yahoo Finance
#    Contoh: "BTC-USD", "ETH-USD", "GC=F" (Emas), "EURUSD=X" (Forex)
TICKER = "BTC-USD"
TIMEFRAME = "15m" # Timeframe: 1m, 5m, 15m, 1h, 1d

# 3. Pengaturan Strategi Simple Moving Average (SMA) Crossover
SMA_PENDEK = 10
SMA_PANJANG = 30

# =================================================================
# KODE UTAMA BOT ANALIS (TIDAK PERLU DIUBAH)
# =================================================================

print("=============================================")
print(f"Bot Analis Dimulai.")
print(f"Aset: {TICKER} | Timeframe: {TIMEFRAME}")
print(f"Strategi: SMA {SMA_PENDEK} vs SMA {SMA_PANJANG}")
print(f"Target Webhook: {WEBHOOK_URL}")
print("=============================================")

# Variabel untuk menyimpan sinyal terakhir agar tidak mengirim pesan berulang-ulang
sinyal_terakhir = None

def cek_sinyal():
    global sinyal_terakhir
    
    try:
        # 1. Unduh data harga terbaru
        print(f"\n[{time.strftime('%H:%M:%S')}] Mengunduh data harga untuk {TICKER}...")
        data = yf.download(tickers=TICKER, period="7d", interval=TIMEFRAME)
        
        if data.empty:
            print("Gagal mengunduh data atau data kosong. Mencoba lagi nanti.")
            return

        # 2. Hitung Indikator SMA
        data[f'SMA_{SMA_PENDEK}'] = data['Close'].rolling(window=SMA_PENDEK).mean()
        data[f'SMA_{SMA_PANJANG}'] = data['Close'].rolling(window=SMA_PANJANG).mean()

        # Ambil dua baris data terakhir untuk deteksi persilangan
        baris_terakhir = data.iloc[-1]
        baris_sebelumnya = data.iloc[-2]

        sinyal_sekarang = None

        # 3. Logika deteksi sinyal crossover
        # Crossover Bullish: SMA pendek memotong ke ATAS SMA panjang
        if baris_sebelumnya[f'SMA_{SMA_PENDEK}'] < baris_sebelumnya[f'SMA_{SMA_PANJANG}'] and baris_terakhir[f'SMA_{SMA_PENDEK}'] > baris_terakhir[f'SMA_{SMA_PANJANG}']:
            sinyal_sekarang = "Bullish"
            print(f"🔥 SINYAL TERDETEKSI: {sinyal_sekarang} 🔥")
        
        # Crossover Bearish: SMA pendek memotong ke BAWAH SMA panjang
        elif baris_sebelumnya[f'SMA_{SMA_PENDEK}'] > baris_sebelumnya[f'SMA_{SMA_PANJANG}'] and baris_terakhir[f'SMA_{SMA_PENDEK}'] < baris_terakhir[f'SMA_{SMA_PANJANG}']:
            sinyal_sekarang = "Bearish"
            print(f"📉 SINYAL TERDETEKSI: {sinyal_sekarang} 📉")
        else:
            print("Tidak ada sinyal persilangan baru.")

        # 4. Kirim notifikasi jika ada sinyal BARU
        if sinyal_sekarang and sinyal_sekarang != sinyal_terakhir:
            harga_terakhir = baris_terakhir['Close']
            
            # Siapkan "paket" data JSON untuk dikirim ke bot kurir
            payload = {
                "symbol": TICKER,
                "price": f"{harga_terakhir:,.2f}",
                "direction": sinyal_sekarang,
                "timeframe": TIMEFRAME,
                "note": f"Sinyal Otomatis: Terjadi persilangan SMA {SMA_PENDEK} / {SMA_PANJANG}."
                # "image": "URL_GAMBAR_CHART_JIKA_ADA" # Bisa ditambahkan jika punya layanan charting
            }
            
            print(f"Mengirim notifikasi ke Telegram via webhook...")
            try:
                requests.post(WEBHOOK_URL, json=payload, timeout=10)
                print("Notifikasi berhasil dikirim!")
                sinyal_terakhir = sinyal_sekarang # Simpan sinyal ini agar tidak dikirim lagi
            except Exception as e:
                print(f"GAGAL mengirim notifikasi: {e}")
        
    except Exception as e:
        print(f"Terjadi kesalahan pada fungsi cek_sinyal: {e}")


# Loop utama yang akan berjalan selamanya
if __name__ == "__main__":
    while True:
        cek_sinyal()
        # Tunggu selama 15 menit (900 detik) sebelum memeriksa lagi
        print(f"Menunggu 15 menit sebelum pengecekan berikutnya...")
        time.sleep(900)
