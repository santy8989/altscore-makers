import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

SWAPI_PLANETS_URL = "https://swapi.dev/api/planets/"
ORACLE_URL = f"{BASE_URL}/v1/s1/e3/resources/oracle-rolodex"
SOLUTION_URL = f"{BASE_URL}/v1/s1/e3/solution"

headers = {
    "accept": "application/json",
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}

character_cache = {}


def get_side_from_oracle(character_name):
    if character_name in character_cache:
        return character_cache[character_name]

    try:
        res = requests.get(
            ORACLE_URL,
            headers=headers,
            params={"name": character_name},
            timeout=10
        )
        res.raise_for_status()
        data = res.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error consultando el oraculo para {character_name}: {e}") from None

    encoded_notes = data.get("oracle_notes")
    if not encoded_notes:
        character_cache[character_name] = "unknown"
        return "unknown"

    try:
        decoded_text = base64.b64decode(encoded_notes).decode("utf-8").lower()
    except Exception as e:
        raise RuntimeError(f"Error decodificando Base64 de {character_name}: {e}") from None

    if "light side" in decoded_text:
        side = "light"
    elif "dark side" in decoded_text:
        side = "dark"
    else:
        side = "unknown"

    character_cache[character_name] = side
    return side


def find_balanced_planet():
    current_url = SWAPI_PLANETS_URL
    page = 1

    print("Iniciando escaneo de planetas en SWAPI...")

    while current_url:
        print(f"Consultando pagina {page} de planetas...")
        try:
            res = requests.get(current_url, timeout=10)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error con SWAPI en la pagina {page}: {e}") from None

        for planet in data.get("results", []):
            residents = planet.get("residents", [])
            if not residents:
                continue

            planet_name = planet.get("name")
            light_count = 0
            dark_count = 0
            total_residents = len(residents)

            print(f"Analizando {planet_name} ({total_residents} residentes)...")

            for resident_url in residents:
                try:
                    res_char = requests.get(resident_url, timeout=10)
                    res_char.raise_for_status()
                    char_name = res_char.json().get("name")
                except requests.exceptions.RequestException as e:
                    raise RuntimeError(f"Error obteniendo residente de {planet_name}: {e}") from None

                side = get_side_from_oracle(char_name)
                if side == "light":
                    light_count += 1
                elif side == "dark":
                    dark_count += 1

            if total_residents > 0:
                ibf = (light_count - dark_count) / total_residents
                print(f"  -> {planet_name}: Light={light_count}, Dark={dark_count}, Total={total_residents}, IBF={ibf}")

                if ibf == 0 and (light_count + dark_count) > 0:
                    print(f"\n[+] Planeta en equilibrio encontrado: {planet_name}")
                    return planet_name

        current_url = data.get("next")
        page += 1

    raise RuntimeError("Error: no se encontro ningun planeta en equilibrio")


def submit_solution(planet_name):
    payload = {"planet": planet_name}
    print(f"Enviando solucion: {payload}")

    try:
        res = requests.post(SOLUTION_URL, headers=headers, json=payload, timeout=10)
        res.raise_for_status()
        return res.json() if res.headers.get("content-type") == "application/json" else res.text
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error enviando la solucion en e3: {e}") from None


def main():
    planet = find_balanced_planet()
    resultado = submit_solution(planet)
    print(f"Respuesta del servidor: {resultado}")


if __name__ == "__main__":
    main()