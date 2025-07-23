import requests
from flask import Flask, request, jsonify
from config import BOT_TOKEN, CHAT_ID

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    symbol = data.get("symbol")
    price = data.get("price")
    direction = data.get("direction")
    timeframe = data.get("timeframe")
    note = data.get("note")
    image = data.get("image")

    message = f'⚠️ *Trade Alert*\n\n*Symbol:* {symbol}\n*Price:* {price}\n*Direction:* {direction}\n*Timeframe:* {timeframe}\n*Note:* {note}'

    if image:
        send_image(image, message)
    else:
        send_message(message)

    return jsonify({"status": "Alert received"}), 200

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def send_image(image_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(debug=True)