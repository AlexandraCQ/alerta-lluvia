import requests
import csv
import os
from datetime import datetime

# ================= CONFIGURACIÓN =================
API_KEY = os.getenv("WEATHERLINK_API_KEY")
API_SECRET = os.getenv("WEATHERLINK_API_SECRET")
STATION_ID = 200333

BASE_DIR = "."
CSV_FILE = os.path.join(BASE_DIR, "lluvia_200333.csv")
TMP_FILE = os.path.join(BASE_DIR, "lluvia_200333.tmp")
STATE_FILE = os.path.join(BASE_DIR, "ultimo_acumulado.txt")

URL = f"https://api.weatherlink.com/v2/current/{STATION_ID}?api-key={API_KEY}"
HEADERS = {"X-Api-Secret": API_SECRET}
# =================================================


def main():
    # --- pedir datos ---
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    # --- extraer lluvia diaria ---
    rainfall_day_mm = None
    for sensor in data.get("sensors", []):
        if sensor.get("sensor_type") == 50:
            rainfall_day_mm = sensor["data"][0]["rainfall_day_mm"]
            break

    if rainfall_day_mm is None:
        raise RuntimeError("No se encontró rainfall_day_mm")

    # --- leer estado anterior ---
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            prev = float(f.read().strip())
    else:
        prev = rainfall_day_mm

    lluvia_5min = max(0.0, rainfall_day_mm - prev)

    # --- guardar nuevo estado ---
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(str(rainfall_day_mm))

    # --- leer CSV existente ---
    rows = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))

    if not rows:
        rows.append(["fecha_hora", "station_id", "lluvia_mm_5min"])

    # --- agregar nueva fila ---
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    rows.append([now, STATION_ID, f"{lluvia_5min:.2f}"])

    # --- escribir archivo temporal ---
    with open(TMP_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # --- reemplazo ---
    os.replace(TMP_FILE, CSV_FILE)


if __name__ == "__main__":
    main()
