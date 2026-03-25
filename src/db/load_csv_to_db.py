import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql://nba_user:supertajnehaslo123@localhost:5432/nba_predictions"
FILES_TO_LOAD = {
    'raw_games': '../../data/raw/games_2023-24.csv',
    'raw_player_stats': '../../data/raw/player_stats_2023-24.csv'
}

def load_data():
    print("Łączenie z bazą danych")
    engine = create_engine(DB_URL)
    for table_name, file_path in FILES_TO_LOAD.items():
        print(f"Wczytywanie pliku {file_path}...")
        try:
            df = pd.read_csv(file_path)

            print(f"Wysyłanie {len(df)} wierszy do tabel {table_name}...\n")
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Tabela '{table_name} gotowa. \n")

        except FileNotFoundError:
            print(f"BŁAD: Nie znaleziono pliku {file_path}\n")
        except Exception as e:
            print(f"Wystąpił błąd: {e}\n")
if __name__ == "__main__":
    load_data()