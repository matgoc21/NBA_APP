import pandas as pd
def engineer_team_features():
    print("Loading raw team data...")
    #Reading earlier saved raw_data
    df_team = pd.read_csv('raw_team_logs.csv')
    #Conversion
    df_team['GAME_DATE'] = pd.to_datetime(df_team['GAME_DATE'])
    #SELF-MERGE, pulling opponent stats into the same row
    opp_cols = ['GAME_ID', 'TEAM_ID', 'PTS', 'FGA', 'FTA', 'OREB', 'TOV']
    df_opp = df_team[opp_cols].copy()
    df_opp.columns = ['GAME_ID', 'OPP_TEAM_ID', 'OPP_PTS', 'OPP_FGA', 'OPP_FTA', 'OPP_OREB', 'OPP_TOV']

    #Join by GAME_ID 
    df_team = df_team.merge(df_opp, on='GAME_ID')
    df_team = df_team[df_team['TEAM_ID'] != df_team['OPP_TEAM_ID']].copy()

    # Sorting

    df_team = df_team.sort_values(by=['TEAM_ID', 'GAME_DATE'])

    # Basic calculation of possesions

    df_team['POSS'] = 0.5 * (
        df_team['FGA'] + 0.44 * df_team['FTA'] - df_team['OREB'] + df_team['TOV'] + 
        df_team['OPP_FGA'] + 0.44 * df_team['OPP_FTA'] - df_team['OPP_OREB'] + df_team['OPP_TOV']
    )

    #Advanced metrics for currant match
    # eFG% premiuje rzuty za 3 punkty

    df_team['eFG_PCT'] = (df_team['FGM'] + 0.5 * df_team['FG3M']) / df_team['FGA']
    df_team['OFF_RTG'] = 100 * (df_team['PTS'] / df_team['POSS'])
    df_team['DEF_RTG'] = 100 * (df_team['OPP_PTS'] / df_team['POSS'])
    df_team['NET_RTG'] = df_team['OFF_RTG'] - df_team['DEF_RTG']

    # Autoregression

    features_to_ewma =['PTS', 'eFG_PCT', 'NET_RTG', 'POSS']

    for col in features_to_ewma:
        df_team[f'EWMA_{col}'] = (
            df_team.groupby('TEAM_ID')[col].transform(lambda x: x.shift(1).ewm(span=5, adjust=False).mean())
        )

    df_team['DAYS_REST'] = df_team.groupby("TEAM_ID")['GAME_DATE'].diff().dt.days.fillna(7.0)
    #dropping unneded columns
    columns_to_drop = ['OPP_TEAM_ID', 'OPP_PTS', 'OPP_FGA', 'OPP_FTA', 'OPP_OREB', 'OPP_TOV']
    df_team = df_team.drop(columns=columns_to_drop)
    output_file = 'processed_team_logs.csv'
    df_team.to_csv(output_file, index=False)
    print(f"finished. File {output_file} ")
def engineer_player_features():

    print("Loading raw player data...")

    df_player = pd.read_csv('raw_player_logs.csv')
    df_team = pd.read_csv('raw_team_logs.csv')

    df_player['GAME_DATE'] = pd.to_datetime(df_player['GAME_DATE'])

    #Standarization of minutes
    if df_player['MIN'].dtype == object:
        df_player['MIN'] = df_player['MIN'].astype(str).str.split(':').apply(
            lambda x: int(x[0]) + int(x[1])/60 if isinstance(x, list) and len(x) == 2 else 0.0
        )

    #Relational join with team logs (for USG%)
    team_cols = ['GAME_ID', 'TEAM_ID', 'FGA', 'FTA', 'TOV']
    df_team_subset = df_team[team_cols].copy()
    df_team_subset.columns = ['GAME_ID', 'TEAM_ID', 'TEAM_FGA', 'TEAM_FTA', 'TEAM_TOV']

    df_player = df_player.merge(df_team_subset, on=['GAME_ID', 'TEAM_ID'], how='left')

    df_player = df_player.sort_values(by=['PLAYER_ID', 'GAME_DATE'])

    #TSP

    df_player['TS_PCT'] = df_player['PTS'] / (2* (df_player['FGA'] + 0.44 * df_player['FTA']))
    df_player['TS_PCT'] = df_player['TS_PCT'].fillna(0)

    #Usage Rate (USG%)
    # the 48 variable is a standard game time
    
    numerator = (df_player['FGA'] + 0.44 * df_player['FTA'] + df_player['TOV']) * 48
    denominator = df_player['MIN'] * (df_player['TEAM_FGA'] + 0.44 * df_player['TEAM_FTA'] + df_player['TEAM_TOV'])
    df_player['USG_PCT'] = 100 * (numerator/denominator)
    df_player['USG_PCT'] = df_player['USG_PCT'].fillna(0)
    #Autoregression (EWMA)

    features_to_ewma = ['MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG3M', 'TS_PCT', 'USG_PCT']

    for col in features_to_ewma:
        df_player[f"EWMA_{col}"] = (
            df_player.groupby('PLAYER_ID')[col].transform(lambda x: x.shift(1).ewm(span=5, adjust=False).mean())
        )

    #Asymetry of rest

    df_player['DAYS_REST'] = df_player.groupby('PLAYER_ID')['GAME_DATE'].diff().dt.days.fillna(7.0)

    #CLeaning and save

    df_player = df_player.drop(columns= ['TEAM_FGA', 'TEAM_FTA', 'TEAM_TOV'])
    output_file = "processed_players_log.csv"
    df_player.to_csv(output_file, index = False)
    print(f"Finsihed. Saved in a file: {output_file}")

if __name__ == "__main__":
    #engineer_team_features()
    engineer_player_features()