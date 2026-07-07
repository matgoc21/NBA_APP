# %%
import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql://nba_user:supertajnehaslo123@localhost:5432/nba_predictions"
engine = create_engine(DB_URL)

print("Pobieranie danych z bazy...")

games_df = pd.read_sql("SELECT * FROM raw_games", engine)
stats_df = pd.read_sql("SELECT * FROM raw_player_stats", engine)

# print(f"Pobrano {len(games_df)} wierszy o meczach.")
# print(f"Pobrano {len(stats_df)} wierszy o graczach.")


# Łączenie tabel i proste cechy
games_subset = games_df[['GAME_ID', 'TEAM_ID', 'GAME_DATE', 'MATCHUP']].copy()
merged_df = pd.merge(stats_df, games_subset, on=['GAME_ID', 'TEAM_ID'], how='left')
merged_df['HOME_GAME'] = merged_df['MATCHUP'].str.contains('vs.').astype(int)
merged_df['GAME_DATE'] = pd.to_datetime(merged_df['GAME_DATE'])
merged_df = merged_df.sort_values(by=['PLAYER_ID', 'GAME_DATE']).reset_index(drop=True)
#Zmęczenie i Forma
merged_df['DAYS_REST'] = merged_df.groupby('PLAYER_ID')['GAME_DATE'].diff().dt.days - 1
merged_df['DAYS_REST'] = merged_df['DAYS_REST'].fillna(10)

merged_df['PTS_5G_AVG'] = merged_df.groupby('PLAYER_ID')['PTS'].transform(
    lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
).round(1)
merged_df['AST_5G_AVG'] = merged_df.groupby('PLAYER_ID')['AST'].transform(
    lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
).round(1)
merged_df['REB_5G_AVG'] = merged_df.groupby('PLAYER_ID')['REB'].transform(
    lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
).round(1)
#Czyszczenie (usunięcie pustych wierszy)
print(f"\nLiczba wierszy przed czyszczeniem: {len(merged_df)}")
ml_df = merged_df.dropna(subset=['PTS', 'PTS_5G_AVG', 'AST_5G_AVG', 'REB_5G_AVG']).copy()
print(f"\nLiczba wierszy po czyszczeniu: {len(ml_df)}")
#Zapis do bazy danych
table_name = 'ml_player_features'
print(f"\nZapisywanie {len(ml_df)} wierszy do nowej tabeli '{table_name}' w PostgreSQL...")
ml_df.to_sql(table_name, engine, if_exists='replace', index=False)
print("Sukces!")