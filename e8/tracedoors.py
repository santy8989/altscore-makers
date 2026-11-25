import base64
import os
import time
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
DOOR_URL = f"{BASE_URL}/v1/s1/e8/actions/door"


def decode_cookie(val: str) -> str:
    cleaned = val.strip('"').strip("'")
    try:
        decoded_bytes = base64.b64decode(cleaned)
        return decoded_bytes.decode("utf-8")
    except Exception:
        return cleaned


def collect_hidden_message():
    session = requests.Session()
    session.headers.update({
        "accept": "application/json",
        "API-KEY": API_KEY,
        "Content-Type": "application/json",
    })

    print("Esperando al inicio de minuto (segundo 00) para entrar por la primera puerta...")
    while True:
        sec = datetime.now(timezone.utc).second
        if sec == 59:
            while datetime.now(timezone.utc).second == 59:
                time.sleep(0.01)
            break
        print(
            f"Segundo UTC actual: {sec:02d} | esperando a :59...",
            end="\r",
        )
        time.sleep(0.2)

    print("\n--- ¡ARRANCANDO RECORRIDO DE PUERTAS! ---")

    words = []
    step = 0
    max_steps = 60

    while step < max_steps:
        step += 1
        now = datetime.now(timezone.utc)

        try:
            res = session.post(DOOR_URL, json={}, timeout=4)
        except Exception as e:
            print(f"[{step}] Error de conexion: {e}")
            time.sleep(1.0)
            continue

        raw_cookie = session.cookies.get("gryffindor")
        body_text = res.text

        if res.status_code == 200 and raw_cookie:
            word = decode_cookie(raw_cookie)
            words.append(word)
            print(f"[{now.second:02d}s | Puerta #{step}] Palabra: {word}")

            # Si el body cambia indicando el fin del camino
            if (
                "aún tienes un camino" not in body_text
                and "Bienvenido" not in body_text
            ):
                print(f"\n--> Mensaje especial de cierre en el body: {body_text}")
                break
        else:
            print(f"[{step}] Status: {res.status_code} | Body: {body_text}")
            break

        time.sleep(0.8)

    hidden_message = " ".join(words)
    print("\n" + "=" * 60)
    print("MENSAJE OCULTO COMPLETO:")
    print(hidden_message)
    print("=" * 60)
    return hidden_message


if __name__ == "__main__":
    collect_hidden_message()