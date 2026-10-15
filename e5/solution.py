import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

START_URL = f"{BASE_URL}/v1/s1/e5/actions/start"
TURN_URL = f"{BASE_URL}/v1/s1/e5/actions/perform-turn"

headers = {
    "accept": "application/json",
    "API-KEY": API_KEY,
    "Content-Type": "application/json"
}


def parse_radar(radar_str):
    enemy = None
    hope = None
    obstacles = set()
    grid = [["." for _ in range(8)] for _ in range(8)]

    rows = radar_str.strip().split("|")
    for row_data in rows:
        if not row_data:
            continue
        for i in range(0, len(row_data), 3):
            cell = row_data[i:i+3]
            if len(cell) < 3:
                continue
            col_char = cell[0]
            val = cell[1]
            row_num = int(cell[2])

            col_idx = ord(col_char) - ord('a')
            matrix_row = 8 - row_num

            grid[matrix_row][col_idx] = val

            if val == "^":
                enemy = (col_char, row_num)
            elif val == "#":
                hope = (col_char, row_num)
            elif val == "$":
                obstacles.add((col_char, row_num))

    return enemy, hope, obstacles, grid


def print_grid(grid):
    print("\n    a b c d e f g h")
    print("   -----------------")
    for r in range(8):
        row_num = 8 - r
        row_str = " ".join(grid[r])
        print(f"{row_num} | {row_str} | {row_num}")
    print("   -----------------")
    print("    a b c d e f g h\n")


def send_turn(action, attack_pos=None):
    payload = {
        "action": action,
        "attack_position": attack_pos
    }
    try:
        res = requests.post(TURN_URL, headers=headers, json=payload, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error ejecutando turno ({action}): {e}") from None


def start_mission():
    try:
        # Se envía json={} por si el endpoint espera un body presente
        res = requests.post(START_URL, headers=headers, json={}, timeout=10)
        res.raise_for_status()
        
        # Si devuelve texto plano, tomamos el texto; si es JSON, lo parseamos
        try:
            return res.json()
        except Exception:
            return res.text
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error iniciando mision: {e}") from None


def main():
    print("[1/4] Iniciando mision...")
    start_data = start_mission()
    print("Mision iniciada con exito:", start_data)

    # --- Turno 1: Radar ---
    print("\n[Turno 1] Solicitando radar...")
    t1_res = send_turn("radar")
    t1_enemy, t1_hope, t1_obs, t1_grid = parse_radar(t1_res.get("action_result", ""))
    print(f"Estado T1 -> Enemigo: {t1_enemy} | Hope: {t1_hope}")
    print(f"Turnos restantes: {t1_res.get('turns_remaining')} | Tiempo: {t1_res.get('time_remaining')}s")
    print_grid(t1_grid)

    # --- Turno 2: Radar ---
    print("\n[Turno 2] Solicitando radar...")
    t2_res = send_turn("radar")
    t2_enemy, t2_hope, t2_obs, t2_grid = parse_radar(t2_res.get("action_result", ""))
    print(f"Estado T2 -> Enemigo: {t2_enemy} | Hope: {t2_hope}")
    print(f"Turnos restantes: {t2_res.get('turns_remaining')} | Tiempo: {t2_res.get('time_remaining')}s")
    print_grid(t2_grid)

    # Analisis T1 -> T2
    dx = ord(t2_enemy[0]) - ord(t1_enemy[0])
    dy = t2_enemy[1] - t1_enemy[1]
    print("=" * 45)
    print("ANALISIS DE MOVIMIENTO (T1 -> T2):")
    print(f"Desplazamiento X: {dx:+d} ({t1_enemy[0]} -> {t2_enemy[0]})")
    print(f"Desplazamiento Y: {dy:+d} ({t1_enemy[1]} -> {t2_enemy[1]})")
    print("=" * 45)

    # Prediccion manual del usuario para T3
    pred_t3 = input("\nIngresa tu prediccion para la posicion del enemigo en Turno 3 (ej. f6): ").strip().lower()

    # --- Turno 3: Radar ---
    print("\n[Turno 3] Solicitando radar para verificar...")
    t3_res = send_turn("radar")
    t3_enemy, t3_hope, t3_obs, t3_grid = parse_radar(t3_res.get("action_result", ""))
    actual_pos_str = f"{t3_enemy[0]}{t3_enemy[1]}"
    
    print(f"Estado Real T3 -> Enemigo: {t3_enemy} | Hope: {t3_hope}")
    print(f"Turnos restantes: {t3_res.get('turns_remaining')} | Tiempo: {t3_res.get('time_remaining')}s")
    print_grid(t3_grid)

    if pred_t3 == actual_pos_str:
        print(f"Le pegaste a la prediccion del T3 ({actual_pos_str}).")
    else:
        print(f"Ojo: predijiste {pred_t3}, pero cayo en {actual_pos_str}.")

    # --- Turno 4: Ataque definitivo ---
    print("\n" + "=" * 45)
    print("PREPARANDO DISPARO FINAL (TURNO 4)")
    print("=" * 45)
    col_shot = input("Ingresa columna de disparo (a-h): ").strip().lower()
    row_shot = int(input("Ingresa fila de disparo (1-8): ").strip())

    ataque_res = send_turn("attack", {"x": col_shot, "y": row_shot})
    print("\nResultado final del ataque:")
    print(ataque_res)


if __name__ == "__main__":
    main()