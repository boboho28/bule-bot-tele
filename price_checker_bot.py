import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =================================================================
# KONFIGURASI (UBAH BAGIAN INI)
# =================================================================

# Masukkan TOKEN BOT Anda di sini. Ini adalah bot yang sama dengan yang di Render.
BOT_TOKEN = "7782307572:AAGDHOqlEHgU6T56ug0S1TAFLRrHDuH7TrU" # <<< GANTI DENGAN TOKEN ANDA

# Pemetaan dari input pengguna ke ticker Yahoo Finance
MAP_ASET = {
    "BTCUSD": "BTC-USD",
    "BTC-USD": "BTC-USD",
    "XAUUSD": "GC=F",
    "GOLD": "GC=F",
    "EMAS": "GC=F",
    "US30": "^DJI",
    "DOWJONES": "^DJI",
    "ETHUSD": "ETH-USD",
    "EURUSD": "EURUSD=X"
}

# =================================================================
# KODE BOT INTERAKTIF (TIDAK PERLU DIUBAH)
# =================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mengirim pesan ketika perintah /start diketik."""
    user = update.effective_user
    await update.message.reply_html(
        f"Halo {user.mention_html()}!\n\nKetikkan simbol aset untuk mendapatkan harga live (Contoh: BTCUSD, XAUUSD, US30).",
    )

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Merespons pesan teks dari pengguna dan mengirimkan harga."""
    user_input = update.message.text.upper()
    
    # Cari ticker yang sesuai dari map
    ticker = MAP_ASET.get(user_input)
    
    if not ticker:
        await update.message.reply_text(f"Maaf, saya tidak mengenali aset '{user_input}'. Coba: BTCUSD, XAUUSD, US30.")
        return

    await update.message.reply_text(f"Mencari harga terbaru untuk {user_input} ({ticker})...")
    
    try:
        # Unduh data harga terakhir dari yfinance
        data = yf.Ticker(ticker)
        harga_info = data.history(period='1d', interval='1m')
        
        if harga_info.empty:
            await update.message.reply_text(f"Tidak dapat mengambil data harga untuk {user_input}.")
            return
            
        harga_terakhir = harga_info['Close'].iloc[-1]
        
        # Format pesan balasan
        pesan_balasan = (
            f"Harga Terbaru **{user_input}**\n\n"
            f"**Harga:** `${harga_terakhir:,.4f}`\n"
            f"Waktu: `{harga_info.index[-1].strftime('%Y-%m-%d %H:%M:%S %Z')}`"
        )
        
        await update.message.reply_text(pesan_balasan, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"Terjadi kesalahan saat mengambil data: {e}")

def main() -> None:
    """Jalankan bot."""
    # Buat aplikasi dan teruskan token bot Anda.
    application = Application.builder().token(BOT_TOKEN).build()

    # Daftarkan handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_price))

    print("Bot Pengecek Harga sedang berjalan...")
    # Jalankan bot sampai pengguna menekan Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
