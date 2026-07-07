import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# 1. Pobranie danych z bazy
DB_URL = "postgresql://nba_user:supertajnehaslo123@localhost:5432/nba_predictions"
engine = create_engine(DB_URL)

print("Pobieram gotowe cechy z bazy...")
df = pd.read_sql("SELECT * FROM ml_player_features", engine)

#2.definicujemy x (cechy/features) oraz y (cel/target)
# na razie przewidujemy punkty
features = ['PTS_5G_AVG', 'DAYS_REST', 'HOME_GAME']
target = 'PTS'

x = df[features]
y = df[target]

#3 podział na zbiór treningowy (80%) i (20%)
#random_state = 42 gwarantuje, że za każdym razem podzieli dane tak samo

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

print(f"Model będzie uczył się na {len(X_train)} meczach.")
print(f"Model będzie egzaminowany na {len(X_test)} meczach.")

#4. trenowanie modelu (las losowy)

print("\nTrenowanie modelu...")
#tworzymy 100 drzew decyzyjnych
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

#5 egzamin (testowanie modelu)

print("\nOcenianie modelu na zbiorze testowym...")

predictions = model.predict(X_test)

#obliczamy mean absolute error (średni błąd bezwzględny, mówi nam to średnio o ile punktów model
#pomylił się w swoich przewidywaniach
mae = mean_absolute_error(y_test, predictions)

print(f"\n---WYNIKI TESTU---")
print(f"Średni błąd modelu (MAE): {mae:.2f} punktu.")