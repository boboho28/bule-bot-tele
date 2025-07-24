import logging
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging untuk melihat error lebih jelas
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# =================================================================
# KONFIGURASI BOT (TOKEN ANDA DI SINI)
# =================================================================
BOT_TOKEN = "7782307572:AAGDHOqlEHgU6T56ug0S1TAFLRrHDuH7TrU"

MAP_ASET = {
    "BTCUSD": "BTC-USD", "BTC-USD": "BTC-USD",
    "XAUUSD": "GC=F", "GOLD": "GC=F", "EMAS": "GC=F",
    "US30": "^DJI", "DOWJONES": "^DJI",
    "ETHUSD": "ETH-USD",
    "EURUSD": "EURUSD=X"
}

# =================================================================
# FUNGSI-FUNGSI BOT
# =================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Halo {user.mention_html()}!\n\nKetikkan simbol aset untuk mendapatkan harga (Contoh: BTCUSD, XAUUSD, US30).",
    )

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.upper()
    logging.info(f"Menerima permintaan harga untuk: {user_input}")
    
    ticker = MAP_ASET.get(user_input)
    if not ticker:
        await update.message.reply_text(f"Maaf, simbol '{user_input}' tidak dikenali.")
        return

    await update.message.reply_text(f"Mencari harga untuk {user_input} ({ticker})...")
    
    try:
        data = yf.Ticker(ticker)
        harga_info = data.history(period='2d', interval='1h')
        
        if harga_info.empty:
            await update.message.reply_text(f"Tidak dapat mengambil data untuk {user_input}. Mungkin pasar tutup.")
            return
            
        harga_terakhir = harga_info['Close'].iloc[-1]
        waktu_terakhir = harga_info.index[-1]
        
        pesan_balasan = (
            f"Harga *{user_input}*\n\n"
            f"▪️ Harga: *${harga_terakhir:,.4f}*\n"
            f"▪️ Waktu: `{waktu_terakhir.strftime('%Y-%m-%d %H:%M:%S %Z')}`"
        )
        await update.message.reply_text(pesan_balasan, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error saat mengambil data untuk {ticker}: {e}", exc_info=True)
        await update.message.reply_text(f"Terjadi kesalahan teknis saat mengambil data.")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_price))
    
    print("Bot Pengecek Harga online sedang berjalan...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
