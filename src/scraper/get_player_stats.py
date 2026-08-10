import pandas as pd
from nba_api.stats.endpoints import boxscoretraditionalv2
import time
import random
import os

# Konfiguracja
INPUT_FILE = '../../data/raw/games_2023-24.csv'
OUTPUT_FILE = '../../data/raw/player_stats_2023-24.csv'


def get_game_ids(csv_path):
    df = pd.read_csv(csv_path)
    return df['GAME_ID'].astype(str).str.zfill(10).unique()


def fetch_box_scores(game_ids_list):
    total_games = len(game_ids_list)

    # KROK 1: Program sprawdza utworzony plik i wpisuje ID do "szybkiej tablicy" (zbioru set)
    downloaded_ids = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            existing_df = pd.read_csv(OUTPUT_FILE)
            downloaded_ids = set(existing_df['GAME_ID'].astype(str).str.zfill(10).unique())
            print(f"Znaleziono plik! W szybkiej pamięci zapisano {len(downloaded_ids)} pobranych meczów.")
        except pd.errors.EmptyDataError:
            print("Plik istnieje, ale jest pusty.")

    # Flaga określająca, czy musimy zapisać nagłówki kolumn w pliku CSV
    # (Jeśli plik nie istnieje lub jest pusty, to musimy zapisać nagłówek)
    write_header = not os.path.exists(OUTPUT_FILE) or len(downloaded_ids) == 0

    print("Rozpoczynam weryfikację i pobieranie...")

    # KROK 2: Program zczytuje id meczu z głównej listy
    for i, game_id in enumerate(game_ids_list):

        # KROK 3 i 4: Szybko sprawdza czy id meczu znajduje się w pobranych
        if game_id in downloaded_ids:
            # Jeżeli tak, przechodzi do następnego meczu
            continue

            # KROK 5: Jeżeli nie, pobiera mecz /603/1230] Pobrano i ZAPISANO mecz ID: 0022300574
        sukces = False
        proby = 0

        while not sukces and proby < 3:
            try:
                box_score = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
                player_stats = box_score.player_stats.get_data_frame()
                player_stats['GAME_ID'] = game_id

                # NATYCHMIASTOWY ZAPIS DO PLIKU!
                # mode='a' oznacza "append" (dopisz na końcu), a nie "nadpisz"
                player_stats.to_csv(OUTPUT_FILE, mode='a', index=False, header=write_header)
                write_header = False  # Nagłówek zapisujemy tylko raz, potem dopisujemy same dane

                # Dodajemy jego id do szybkiej tablicy
                downloaded_ids.add(game_id)

                print(f"[{i + 1}/{total_games}] Pobrano i ZAPISANO mecz ID: {game_id}")
                sukces = True

                # Udajemy człowieka
                time.sleep(random.uniform(1.5, 3.5))

            except Exception as e:
                proby += 1
                czas_czekania = 5 * proby
                print(f"Błąd przy meczu {game_id} (Próba {proby}/3): {e}")
                print(f"Czekam {czas_czekania} sekund przed ponowieniem...")
                time.sleep(czas_czekania)

        if not sukces:
            print(f"UWAGA: Całkowicie pominięto mecz {game_id} ze względu na błędy serwera.")


if __name__ == "__main__":
    ids = get_game_ids(INPUT_FILE)
    fetch_box_scores(ids)
    print("Skrypt zakończył działanie!")