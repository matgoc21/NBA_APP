import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from sklearn.metrics import accuracy_score, mean_absolute_error

def train_team_estimators():
    df = pd.read_csv('processed_team_logs.csv')
    df.columns = df.columns.str.strip()

    df['HOME_GAME'] = df['MATCHUP'].str.contains('vs.').astype(int)


    df_home = df[df['HOME_GAME'] == 1].copy()
    df_away = df[df['HOME_GAME'] == 0].copy()

    matchups = pd.merge(
        df_home, df_away,
        on='GAME_ID',
        suffixes=('_HOME', '_AWAY')
    )
    matchups = matchups.dropna(subset=['EWMA_NET_RTG_HOME', 'EWMA_NET_RTG_AWAY'])

    #Definition of vectors x
    #Clasification (1 == home win, 0 = home lose)
    Y_clf = (matchups['PTS_HOME'] > matchups['PTS_AWAY']).astype(int)
    #Regression (Point difference from the point of view of home team)
    Y_reg = matchups['PTS_HOME'] - matchups['PTS_AWAY']
    #Features X based on the deltas
    X = pd.DataFrame()
    X['DELTA_NET_RTG'] = matchups['EWMA_NET_RTG_HOME'] - matchups['EWMA_NET_RTG_AWAY']
    X['DELTA_eFG_PCT'] = matchups['EWMA_eFG_PCT_HOME'] - matchups['EWMA_eFG_PCT_AWAY']
    X['DELTA_POSS'] = matchups['EWMA_POSS_HOME'] - matchups['EWMA_POSS_AWAY']
    X['HOME_DAYS_REST'] = matchups['DAYS_REST_HOME']
    X['AWAY_DAYS_REST'] = matchups['DAYS_REST_AWAY']

    clf_model = xgb.XGBClassifier(
        n_estimators = 100,
        learning_rate=0.05,
        max_depth=3,
        objective='binary:logistic',
        random_state=42
    )

    clf_model.fit(X, Y_clf)

    predictions_clf = clf_model.predict(X)
    acc = accuracy_score(Y_clf, predictions_clf)
    print(f"[Win Probability] Accuracy: {acc*100:.1f}%")
    joblib.dump(clf_model, 'nba_team_win_prob_model.joblib')

    #Regressor training
    reg_model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )

    reg_model.fit(X, Y_reg)

    predictions_reg = reg_model.predict(X)
    mae = mean_absolute_error(Y_reg, predictions_reg)
    print(f"[Point Differential] MAE: {mae:.1f} points")
    joblib.dump(reg_model, 'nba_team_point_diff_model.joblib')
if __name__ == "__main__":
    train_team_estimators()
