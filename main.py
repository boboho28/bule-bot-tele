import os
import requests
from flask import Flask, request, jsonify

# =================================================================
# SETUP APLIKASI FLASK
# =================================================================
app = Flask(__name__)

# =================================================================
# AMBIL DATA RAHASIA DARI RENDER (ENVIRONMENT VARIABLES)
# Ini adalah cara yang aman. Nilai token dan ID tidak ada di dalam kode.
# =================================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# =================================================================
# FUNGSI UNTUK MENGIRIM PESAN KE TELEGRAM
# =================================================================
def send_telegram_alert(message_text, image_url=None):
    """Mengirim pesan teks, dan gambar jika ada, ke Telegram."""
    
    # Kirim pesan teks terlebih dahulu
    text_payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=text_payload)
    
    # Jika ada URL gambar, kirim foto secara terpisah
    if image_url:
        image_payload = {
            "chat_id": CHAT_ID,
            "photo": image_url
        }
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", json=image_payload)

# =================================================================
# ENDPOINT /WEBHOOK (TEMPAT MENERIMA SINYAL)
# =================================================================
@app.route("/webhook", methods=["POST"])
def webhook_receiver():
    # Pertama, periksa apakah BOT_TOKEN dan CHAT_ID berhasil dimuat dari Render.
    # Jika tidak, ini akan menjadi pesan error pertama yang Anda lihat.
    if not BOT_TOKEN or not CHAT_ID:
        error_message = "Kesalahan Server: Pastikan BOT_TOKEN dan CHAT_ID sudah diatur dengan benar di Environment Variables Render."
        print(error_message) # Untuk log di Render
        return jsonify({"status": "error", "message": error_message}), 500

    try:
        # Ambil data JSON yang dikirim oleh Postman/TradingView
        data = request.get_json()
        print(f"Data diterima: {data}") # Untuk debugging di log Render

        # Ekstrak setiap bagian data dengan aman
        symbol = data.get("symbol", "Tidak ada simbol")
        price = data.get("price", "N/A")
        direction = data.get("direction", "N/A")
        timeframe = data.get("timeframe", "N/A")
        note = data.get("note", "-")
        image = data.get("image", None) # Default ke None jika tidak ada gambar

        # Buat pesan yang akan dikirim
        formatted_message = (
            f"🔔 *Sinyal Baru!*\n\n"
            f"▪️ *Simbol:* `{symbol}`\n"
            f"▪️ *Harga:* `{price}`\n"
            f"▪️ *Arah:* {direction}\n"
            f"▪️ *Timeframe:* {timeframe}\n"
            f"▪️ *Catatan:* {note}"
        )

        # Kirim notifikasi menggunakan fungsi yang sudah kita buat
        send_telegram_alert(formatted_message, image)

        # Beri respons sukses ke pengirim sinyal
        return jsonify({"status": "ok", "message": "Sinyal berhasil diterima dan dikirim ke Telegram."}), 200

    except Exception as e:
        # Jika terjadi error lain saat memproses data
        error_message = f"Terjadi kesalahan saat memproses permintaan: {str(e)}"
        print(error_message) # Untuk log di Render
        return jsonify({"status": "error", "message": error_message}), 500

# =================================================================
# ENDPOINT / (UNTUK MEMERIKSA APAKAH BOT HIDUP)
# =================================================================
@app.route("/")
def index():
    """Halaman dasar untuk menunjukkan bahwa layanan aktif."""
    return "<h1>Bot Telegram Aktif!</h1><p>Gunakan endpoint <code>/webhook</code> dengan metode POST untuk mengirim sinyal.</p>", 200

# =================================================================
# JALANKAN SERVER (Render akan menggunakan ini)
# =================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
