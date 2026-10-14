import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

MEASUREMENT_URL = f"{BASE_URL}/v1/s1/e1/resources/measurement"
SOLUTION_URL = f"{BASE_URL}/v1/s1/e1/solution"

headers = {
    "accept": "application/json",
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}


def get_telemetry():
    attempts = 0
    print("Buscando medición válida a través de la interferencia...")

    while True:
        attempts += 1
        try:
            res = requests.get(MEASUREMENT_URL, headers=headers, timeout=10)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Hubo un error con la conexion en get_telemetry: {e}") from None

        dist_str = data.get("distance")
        time_str = data.get("time")

        if dist_str != "failed to measure, try again" and time_str != "failed to measure, try again":
            print(f"\n[+] Telemetría capturada en intento {attempts}:")
            print(f"    Raw: {data}")
            # Parsear los valores de distancia y tiempo
            distance = float(dist_str.split()[0])
            time_val = float(time_str.split()[0])
            return distance, time_val
        # print(f"Intento {attempts} | val: {dist_str} | time: {time_str}")

        time.sleep(0.1)


def solve():
    distance, time_val = get_telemetry()

    raw_speed = distance / time_val
    print(f"Velocidad bruta: {raw_speed}")

    speed = int(round(raw_speed))
    print(f"Velocidad calculada: {speed}")

    payload = {"speed": speed}
    print(f"Enviando payload a {SOLUTION_URL}: {payload}")

    try:
        response = requests.post(SOLUTION_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Hubo un error enviando la solucion en e1: {e}") from None

    print(f"\nSTATUS {response.status_code}:")
    print(response.json() if response.headers.get("content-type") == "application/json" else response.text)


if __name__ == "__main__":
    solve()