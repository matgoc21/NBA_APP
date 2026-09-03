import pandas as pd
def engineer_features():
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

    if __name__ == "__main__":
        engineer_features()