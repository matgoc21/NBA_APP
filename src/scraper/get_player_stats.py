import pandas as pd
from nba_api.stats.endpoints import boxscoretraditionalv2
import time
import os

INPUT_FILE = '../../data/raw/games_2023-24.csv'
OUTPUT_FILE = '../../data/raw/player_stats_2023-24.csv'

def get_game_ids(csv_path):
    df = pd.read_csv(csv_path)

    game_ids = df['GAME_ID'].astype(str).str.zfill(10).unique()
    return game_ids

def fetch_box_scores(game_ids_list):

    all_stats = []
    total = len(game_ids_list)

    print(f"Rozpoczynam pobieranie statystyk dla {total} meczów...")

    for i, game_id in enumerate(game_ids_list):
        try:
            box_score = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id = game_id)
            player_stats = box_score.player_stats.get_data_frame()
            player_stats['GAME_ID'] = game_id
            all_stats.append(player_stats)
            print(f"[{i+1}/total] Pobrano mecz o ID: {game_id}")
            time.sleep(0.6)
        except Exception as e:
            print(f"Błąd przy meczu {game_id}: {e}")
            time.sleep(1)

    if all_stats:
        return pd.concat(all_stats, ignore_index=True)
    else:
            return pd.DataFrame()

if __name__ == "__main__":
    ids = get_game_ids(INPUT_FILE)
    final_df = fetch_box_scores(ids)
    if not final_df.empty:
        final_df.to_csv(OUTPUT_FILE, index = False)
        print(f"Sukces, zapisano statystyki do {OUTPUT_FILE}")
        print(final_df.head())
    else:
        print("Błąd")