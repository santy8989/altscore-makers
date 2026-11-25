import os
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
DOOR_URL = f"{BASE_URL}/v1/s1/e8/actions/door"

headers = {
    "accept": "application/json",
    "API-KEY": API_KEY,
    "Content-Type": "application/json",
}

def sync_server_time():
    res = requests.get(f"{BASE_URL}/docs", timeout=5)
    server_date_str = res.headers.get("date")
    print(f"Header Date del servidor: {server_date_str}")

def probe_window():
    print("Iniciando sondeo hacia /v1/s1/e8/actions/door...")
    print("Esperando la transición al minuto nuevo (segundos 59 -> 00 -> 01 -> 02)...")
    
    while True:
        sec = datetime.utcnow().second
        if sec == 58:
            break
        print(f"Segundo UTC local: {sec:02d} / esperando al 58...", end="\r")
        time.sleep(0.2)

    print("\n--- ¡ENTRANDO EN ZONA DE DISPARO (59s a 02s)! ---")
    
    # Probamos durante 4 segundos disparando requests rápidos
    # Variando la palabra mágica "Revelio"
    start_time = time.time()
    while time.time() - start_time < 5:
        # 1. Post con json spell Revelio
        try:
            r1 = requests.post(DOOR_URL, headers=headers, json={"spell": "Revelio"}, timeout=2)
            print(f"[JSON] Status {r1.status_code} | Body: {r1.text}")
            if "Siempre es bueno un atajo" not in r1.text:
                print(f"--> ¡PISTA ENCONTRADA! {r1.status_code} | {r1.headers} | {r1.text}")
                return
        except Exception:
            pass

        # 2. Post con query param spell=Revelio
        try:
            r2 = requests.post(f"{DOOR_URL}?spell=Revelio", headers=headers, timeout=2)
            print(f"[QUERY] Status {r2.status_code} | Body: {r2.text}")
            if "Siempre es bueno un atajo" not in r2.text:
                print(f"--> ¡PISTA ENCONTRADA! {r2.status_code} | {r2.headers} | {r2.text}")
                return
        except Exception:
            pass

        time.sleep(0.15)

if __name__ == "__main__":
    sync_server_time()
    probe_window()