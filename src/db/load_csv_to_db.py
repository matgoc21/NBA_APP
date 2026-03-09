import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql://nba_user:supertajnehaslo123@localhost:5432/nba_predictions"
CSV_FILE_PATH = '../../data/raw/player_stats_2023-24.csv'

def load_data():
    print("Łączenie z bazą danych")
    engine = create_engine(DB_URL)
    print ("Wczytywanie pliku CSV do Pandas...")
    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {CSV_FILE_PATH}")
        return

    table_name = 'raw_player_stats'

    print(f"Wysyłanie {len(df)} wierszy do tabeli '{table_name}'...")

    df.to_sql(table_name, engine, if_exists='replace', index=False)

    print("Sukces")

if __name__ == "__main__":
    load_data()