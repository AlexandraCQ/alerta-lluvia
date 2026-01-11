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
            rainfall_day_mm = sensor["data"][0]["rainfall_day_mm"]
            break

    if rainfall_day_mm is None:
        raise RuntimeError("No se encontró rainfall_day_mm")

    # 2️⃣ Leer acumulado anterior
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            prev = float(f.read().strip())
    else:
        prev = rainfall_day_mm

    lluvia_5min = max(0.0, rainfall_day_mm - prev)

    # 3️⃣ Guardar nuevo acumulado
    with open(STATE_FILE, "w") as f:
        f.write(str(rainfall_day_mm))

    # 4️⃣ Hora Perú
    now = (datetime.utcnow() + timedelta(hours=TZ_OFFSET)).strftime("%Y-%m-%d %H:%M")

    # 5️⃣ Crear CSV si no existe
    existe = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["fecha_hora", "station_id", "lluvia_mm_5min"])
        writer.writerow([now, STATION_ID, f"{lluvia_5min:.2f}"])


if __name__ == "__main__":
    main()
