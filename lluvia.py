import requests
import csv
import os
from datetime import datetime, timedelta

# ================= ZONA HORARIA =================
TZ_OFFSET = -5  # Perú UTC-5
# ===============================================

# ================= WEATHERLINK ==================
API_KEY = os.getenv("WEATHERLINK_API_KEY")
API_SECRET = os.getenv("WEATHERLINK_API_SECRET")
STATION_ID = 200333

URL = f"https://api.weatherlink.com/v2/current/{STATION_ID}?api-key={API_KEY}"
HEADERS = {"X-Api-Secret": API_SECRET}
# ===============================================

CSV_FILE = "lluvia_200333.csv"
STATE_FILE = "ultimo_acumulado.txt"


def main():
    # 1️⃣ Obtener datos de WeatherLink
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    rainfall_day_mm = None

    for sensor in data.get("sensors", []):
        if sensor.get("sensor_type") == 50:
            rainfall_day_mm = sensor["data"][0].get("rainfall_day_mm")
            break

    if rainfall_day_mm is None:
        raise RuntimeError("No se encontró rainfall_day_mm")

    # 2️⃣ Leer acumulado anterior (persistente)
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            prev = float(f.read().strip())
    else:
        prev = rainfall_day_mm  # primera ejecución

    # 3️⃣ Calcular lluvia últimos 5 minutos
    lluvia_5min = max(0.0, round(rainfall_day_mm - prev, 3))

    # 4️⃣ Guardar acumulado actual para próxima ejecución
    with open(STATE_FILE, "w") as f:
        f.write(str(rainfall_day_mm))

    # 5️⃣ Hora Perú
    now = (datetime.utcnow() + timedelta(hours=TZ_OFFSET)).strftime("%Y-%m-%d %H:%M")

    # 6️⃣ Guardar CSV
    existe = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["fecha_hora", "station_id", "lluvia_mm_5min"])
        writer.writerow([now, STATION_ID, lluvia_5min])


if __name__ == "__main__":
    main()

