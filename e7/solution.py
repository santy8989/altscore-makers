import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
TUNNEL_URL = os.getenv("TUNNEL_URL")

SOLUTION_URL = f"{BASE_URL}/v1/s1/e7/solution"

headers = {
    "accept": "application/json",
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "base_url": TUNNEL_URL
}


def main():
    if not TUNNEL_URL:
        print("Error: TUNNEL_URL no esta definida en el archivo .env")
        return

    print("=" * 45)
    print("ENVIANDO SOLUCIÓN EPISODIO 7")
    print(f"Target: {SOLUTION_URL}")
    print(f"Payload: {payload}")
    print("=" * 45)

    confirm = input("\nConfirmar envío al robot de reparación? (s/n): ").strip().lower()
    if confirm == "s":
        res = requests.post(SOLUTION_URL, headers=headers, json=payload, timeout=20)
        print("\nStatus Code:", res.status_code)
        print("Respuesta del servidor:")
        print(res.text)


if __name__ == "__main__":
    main()