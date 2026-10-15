import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
SOLUTION_URL = f"{BASE_URL}/v1/s1/e6/solution"

POKEAPI_BASE = "https://pokeapi.co/api/v2"

# Los 18 tipos requeridos en orden alfabético
TARGET_TYPES = [
    "bug", "dark", "dragon", "electric", "fairy", "fighting",
    "fire", "flying", "ghost", "grass", "ground", "ice",
    "normal", "poison", "psychic", "rock", "steel", "water"
]

headers = {
    "accept": "application/json",
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}


def fetch_pokemon_height(url, session):
    try:
        res = session.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()
        return data.get("height", 0)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return 0


def get_type_averages():
    session = requests.Session()

    # 1. Obtener la lista de URLs de Pokémon para cada uno de los 18 tipos
    print("[1/3] Descargando listas de Pokémon por cada tipo...")
    type_pokemon_urls = {}
    all_urls = set()

    for p_type in TARGET_TYPES:
        res = session.get(f"{POKEAPI_BASE}/type/{p_type}", timeout=15)
        res.raise_for_status()
        data = res.json()

        urls = [p["pokemon"]["url"] for p in data["pokemon"]]
        type_pokemon_urls[p_type] = urls
        all_urls.update(urls)
        print(f"  - Tipo {p_type:8s}: {len(urls)} Pokémon")

    # 2. Descargar alturas de Pokémon únicos en paralelo
    print(f"\n[2/3] Descargando alturas de {len(all_urls)} Pokémon únicos...")
    heights_cache = {}

    with ThreadPoolExecutor(max_workers=25) as executor:
        future_to_url = {
            executor.submit(fetch_pokemon_height, url, session): url
            for url in all_urls
        }
        completed = 0
        total = len(all_urls)

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            heights_cache[url] = future.result()
            completed += 1
            if completed % 150 == 0 or completed == total:
                print(f"  Progreso: {completed}/{total} descargados...")

    # 3. Calcular el promedio de altura por tipo con 3 decimales
    print("\n[3/3] Calculando promedios por tipo...")
    heights_result = {}

    for p_type in TARGET_TYPES:
        urls = type_pokemon_urls[p_type]
        if not urls:
            heights_result[p_type] = 0.0
            continue

        heights = []
        for u in urls:
            if u in heights_cache:
                heights.append(heights_cache[u])
                
        avg_height = sum(heights) / len(heights)
        heights_result[p_type] = round(avg_height, 3)
        print(f"  {p_type:10s} -> {heights_result[p_type]:.3f} (en {len(heights)} registros)")

    return heights_result


def main():
    heights_data = get_type_averages()

    payload = {
        "heights": heights_data
    }

    print("\n" + "=" * 50)
    print("PAYLOAD LISTO PARA ENVIAR:")
    print(payload)
    print("=" * 50)

    confirm = input("\n¿Enviar solucion al servidor? (s/n): ").strip().lower()
    if confirm == "s":
        res = requests.post(SOLUTION_URL, headers=headers, json=payload, timeout=15)
        print("\nStatus Code:", res.status_code)
        print("Respuesta del servidor:")
        print(res.text)


if __name__ == "__main__":
    main()