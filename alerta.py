import csv
import os
from datetime import datetime, timedelta
import requests

# ================= ZONA HORARIA =================
TZ_OFFSET = -5  # Perú UTC-5
# ===============================================

# ================= TELEGRAM =====================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# ===============================================

CSV_FILE = "lluvia_200333.csv"
ESTADO_FILE = "estado_alerta.txt"

# ================ UMBRALES ======================
UMBRAL_INICIO = 2.0
UMBRAL_AMARILLO = 3.0
UMBRAL_NARANJA = 5.0
UMBRAL_ROJA = 7.0
# ===============================================

NOMBRE_ESTACION = "ESTACIÓN ANTENA"


def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": texto})


def obtener_acumulado_60min():
    if not os.path.exists(CSV_FILE):
        return 0.0

    ahora = datetime.utcnow() + timedelta(hours=TZ_OFFSET)
    hace_60 = ahora - timedelta(minutes=60)
    total = 0.0

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = datetime.strptime(row["fecha_hora"], "%Y-%m-%d %H:%M")
            if t >= hace_60:
                total += float(row["lluvia_mm_5min"])

    return round(total, 2)


def obtener_intensidad_actual():
    if not os.path.exists(CSV_FILE):
        return 0.0

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return 0.0

    return round(float(rows[-1]["lluvia_mm_5min"]), 2)


def determinar_nivel(mm):
    if mm >= UMBRAL_ROJA:
        return "ROJA"
    elif mm >= UMBRAL_NARANJA:
        return "NARANJA"
    elif mm >= UMBRAL_AMARILLO:
        return "AMARILLO"
    elif mm >= UMBRAL_INICIO:
        return "LLUVIA"
    else:
        return "NINGUNO"


def leer_estado():
    if os.path.exists(ESTADO_FILE):
        with open(ESTADO_FILE) as f:
            return f.read().strip()
    return "NINGUNO"


def guardar_estado(n):
    with open(ESTADO_FILE, "w") as f:
        f.write(n)


def main():
    acumulado = obtener_acumulado_60min()
    intensidad = obtener_intensidad_actual()
    nivel_actual = determinar_nivel(acumulado)
    nivel_anterior = leer_estado()

    hora = (datetime.utcnow() + timedelta(hours=TZ_OFFSET)).strftime("%H:%M")

    if nivel_actual == nivel_anterior:
        return

    # 🟦 FIN DE ALERTA
    if nivel_actual == "NINGUNO" and nivel_anterior != "NINGUNO":
        mensaje = (
            f"🟦 FIN DE ALERTA\n"
            f"{NOMBRE_ESTACION}\n"
            f"Acumulado 1h: {acumulado} mm\n"
            f"Intensidad actual: {intensidad} mm/5min\n"
            f"Hora: {hora}"
        )
        enviar_mensaje(mensaje)
        guardar_estado(nivel_actual)
        return

    # 🔔 CAMBIO DE NIVEL
    iconos = {
        "LLUVIA": "🌧️",
        "AMARILLO": "🟡",
        "NARANJA": "🟠",
        "ROJA": "🔴",
    }

    mensaje = (
        f"{iconos[nivel_actual]} ALERTA {nivel_actual}\n"
        f"{NOMBRE_ESTACION}\n"
        f"Acumulado 1h: {acumulado} mm\n"
        f"Intensidad actual: {intensidad} mm/5min\n"
        f"Hora: {hora}"
    )

    enviar_mensaje(mensaje)
    guardar_estado(nivel_actual)


if __name__ == "__main__":
    main()

