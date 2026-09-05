import pandas as pd
import xgboost as xgb
import joblib
from sklearn.metrics import mean_absolute_error

def train_player_estimators():
    df = pd.read_csv('processed_players_log.csv')

    targets = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG3M']
    base_features = ['EWMA_MIN', 'EWMA_USG_PCT', 'EWMA_TS_PCT', 'DAYS_REST']

    for target in targets:
        #dynammic declaration of main autoregression feature for given target
        target_ewma = f'EWMA_{target}'
        current_features= base_features + [target_ewma]

        #Only rows with all needed data
        df_clean = df.dropna(subset=current_features + [target])
        X = df_clean[current_features]
        Y = df_clean[target]

        model = xgb.XGBRegressor(
            n_estimators=150,
            learning_rate=0.05,
            max_dept=4,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        model.fit(X,Y)
        predictions = model.predict(X)
        mae = mean_absolute_error(Y, predictions)

        filename=f'nba_player_{target.lower()}_model.joblib'
        joblib.dump(model, filename)

        print(f"[{target}] MAE: {mae:.2f} | Saved: {filename}")

if __name__ == "__main__":
    train_player_estimators() 