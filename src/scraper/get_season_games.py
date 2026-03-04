import pandas as pd
from nba_api.stats.endpoints import leaguegamelog
import os
import time

SEASON = '2023-24'
OUTPUT_DIR = '../../data/raw'
OUTPUT_FILE = f'games_{SEASON}.csv'

def fetch_season_games(season_str):
    print(f"Pobieranie listy meczów dla szeonu {season_str}...")

    game_log = leaguegamelog.LeagueGameLog(
        season = season_str,
        season_type_all_star='Regular Season'
    )

    games_df = game_log.get_data_frames()[0]

    return games_df

if __name__ == '__main__':
    df = fetch_season_games(SEASON)

    print(f"Pobrano {len(df)} meczów.")
    print(df[['GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL']].head())

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    full_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(full_path, index=False)
    print(f"Dane zapisane w : {full_path}")
