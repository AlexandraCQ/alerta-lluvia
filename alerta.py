import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": texto
    })

if __name__ == "__main__":
    ahora = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    enviar_mensaje(f"✅ Sistema activo correctamente\nHora: {ahora}")
