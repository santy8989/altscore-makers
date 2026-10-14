import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

STARS_URL = f"{BASE_URL}/v1/s1/e2/resources/stars"
SOLUTION_URL = f"{BASE_URL}/v1/s1/e2/solution"

headers = {
    "accept": "application/json",
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}


def solve_standard():
    """
    Cálculo directo: descarga todas las páginas de la API recopilando la totalidad
    de estrellas y calcula el promedio sumando cada valor individualmente.
    """
    t0 = time.perf_counter()
    stars = []
    page = 1
    total_count = None

    while True:
        try:
            res = requests.get(
                STARS_URL,
                headers=headers,
                params={"page": page, "sort-by": "resonance", "sort-direction": "asc"},
                timeout=10
            )
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Hubo un dramon con la conexion en solve_standard: {e}") from None

        if total_count is None and "x-total-count" in res.headers:
            total_count = int(res.headers["x-total-count"])

        data = res.json()
        if not data:
            break

        stars.extend(data)

        if total_count and len(stars) >= total_count:
            break
        page += 1

    if not stars:
        raise RuntimeError("Hubo un error: no se recibieron estrellas en solve_standard")

    elapsed = time.perf_counter() - t0
    resonances = [s["resonance"] for s in stars]
    average = sum(resonances) / len(resonances)

    return average, len(resonances), elapsed, page


def solve_gauss():
    """
    La media aritmética de una progresión aritmética: aprovecha la simetría de la
    serie consultando únicamente los extremos para obtener (a_1 + a_n) / 2.
    """
    t0 = time.perf_counter()

    try:
        res_first = requests.get(
            STARS_URL,
            headers=headers,
            params={"page": 1, "sort-by": "resonance", "sort-direction": "asc"},
            timeout=10
        )
        res_first.raise_for_status()
        first_data = res_first.json()

        if not first_data:
            raise RuntimeError("Hubo un error: la primera pagina vino vacia")

        total_count = int(res_first.headers.get("x-total-count", len(first_data)))
        page_size = len(first_data)
        min_star = first_data[0]["resonance"]

        last_page = (total_count + page_size - 1) // page_size

        res_last = requests.get(
            STARS_URL,
            headers=headers,
            params={"page": last_page, "sort-by": "resonance", "sort-direction": "asc"},
            timeout=10
        )
        res_last.raise_for_status()
        last_data = res_last.json()

        if not last_data:
            raise RuntimeError("Hubo un error: la ultima pagina vino vacia")

        max_star = last_data[-1]["resonance"]
        average = (min_star + max_star) / 2
        elapsed = time.perf_counter() - t0

        return average, min_star, max_star, total_count, elapsed

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Hubo un error con la conexion en solve_gauss: {e}") from None

def submit_solution(average_val):
    payload = {"average_resonance": int(round(average_val))}
    try:
        res = requests.post(SOLUTION_URL, headers=headers, json=payload, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Hubo un error enviando la solucion: {e}") from None


def main():
    print("MÉTODO ESTÁNDAR: PROMEDIO DIRECTO & PAGINACIÓN COMPLETA")
    avg_standard, total_stars, time_standard, pages_standard = solve_standard()
    print(f"Metodo estandar: {avg_standard} ({total_stars} estrellas en {pages_standard} llamadas, {time_standard:.2f}s)")

    print("MÉTODO GAUSS: PROMEDIO CON SIMETRÍA")
    avg_gauss, min_star, max_star, total_header, time_gauss = solve_gauss()
    print(f"Metodo Gauss: {avg_gauss} (min {min_star}, max {max_star}, 2 llamadas, {time_gauss:.2f}s)")

    if avg_standard == avg_gauss:
        time_saved = time_standard - time_gauss
        percent_saved = (time_saved / time_standard) * 100 if time_standard > 0 else 0
        print(f"Resultados identicos. Sin gaps. Gauss ahorro {time_saved:.2f}s ({percent_saved:.1f}% mas rapido)")
        final_answer = avg_gauss
    else:
        print(f"Discrepancia detectada por gaps. Valor real: {avg_standard}")
        final_answer = avg_standard

    if final_answer is None or final_answer <= 0:
        raise RuntimeError("Hubo un error: el valor a enviar no es valido, se cancela el envio")

    print(f"Valor a enviar (previo conversion a int): {final_answer}")
    resultado_envio = submit_solution(final_answer)
    print(f"Respuesta del servidor: {resultado_envio}")


if __name__ == "__main__":
    main()