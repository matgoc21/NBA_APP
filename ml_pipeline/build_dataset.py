import pandas as pd
import time
from nba_api.stats.endpoints import teamgamelogs, playergamelogs

SEASONS = ['2024-25', '2025-26']

def fetch_base_data():
    team_logs_list = []
    player_logs_list=[]

    for season in SEASONS:
        print(f"Pobieranie logów dla sezonu {season}")

        #Matrix for Y_reg and Y_clf (teams)
        team_log = teamgamelogs.TeamGameLogs(season_nullable=season)
        team_logs_list.append(team_log.get_data_frames)
        time.sleep(1.5) # rate-limiting prevention

        #Matrix for indivdual estimators

        player_log = playergamelogs.PlayerGameLogs(season_nullable=season)
        player_logs_list.append(player_log.get_data_frames)
        time.sleep(1.5)

    df_team = pd.concat(team_logs_list, ignore_index= True)
    df_player = pd.concat(player_logs_list, ignore_index)

    df_team.to_csv('raw_team_logs.csv', index = False)
    df_player.to_csv('raw_player_logs.csv', index = False)
    print("Finished loading matrix'es.")

    return df_team, df_player
if __name__ == "__main__":
    fetch_base_data()