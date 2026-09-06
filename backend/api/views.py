import os
import joblib
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from nba_api.stats.endpoints import playergamelogs, teamgamelogs
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Team, Player, Game
import xgboost as xgb
# Create your views here.

#Loading fleet of models into the RAM memory
TARGETS = ['pts', 'reb', 'ast', 'stl', 'blk', 'tov', 'fg3m']
ML_MODELS = {}
TEAM_WIN_MODEL_PATH = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'nba_team_win_prob_model.joblib'))
TEAM_DIFF_MODEL_PATH = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'nba_team_point_diff.joblib'))

TEAM_WIN_MODEL = joblib.load(TEAM_WIN_MODEL_PATH) if os.path.exists(TEAM_WIN_MODEL_PATH) else None
TEAM_DIFF_MODEL = joblib.load(TEAM_DIFF_MODEL_PATH) if os.path.exists(TEAM_DIFF_MODEL_PATH) else None

for target in TARGETS:
    model_path = os.path.abspath(os.path.join(str(settings.BASE_DIR), '...', f'nba_player_{target}_model.joblib' ))
    if os.path.exist(model_path):
        ML_MODELS[target] = joblib.load(model_path)
    else:
        print(f"Warning: No model for stat: {target.upper()}")


@csrf_exempt       
def predict_score(request):
    """
    Predict player stats using a loaded fleet of XGBoost estimators.
    """

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player = get_object_or_404(Player, id=data.get('player_id'))
            game = get_object_or_404(Game, id = data.get('game_id'))

            #home_game = 1 if player.team == game.home_team else 0

            year = game.game_date.year
            season_year = year if game.game_date.month > 7 else year - 1
            season_str = f"{season_year}-{str(season_year + 1)[-2:]}"

            #date_before_game = (game.game_date - timedelta(days=1)).strftime('%m/%d/%Y')
            try:

                log = playergamelogs.PlayerGameLogs(
                    player_id_nullable=player.nba_id,
                    season_nullable=season_str,
                )
                df_player = log.get_data_frames()[0]
                team_log = teamgamelogs.TeamGameLogs(season_nullable = season_str)
                df_team = team_log.get_data_frames()[0]
            except Exception as api_err:
                print(f"NBA API ERROR: {api_err}")
                df_player = pd.DataFrame()
                df_team = pd.DataFrame()

            #in case of a debut/ first match of the season
            predictions = {target.upper(): 0.0 for target in TARGETS}
            debug_features = {'days_rest': 7, 'ewma_min': 0.0, 'ewma_usg': 0.0, 'ewma_ts': 0.0}
            
            if not df_player.empty and not df_team.empty:
                if df_player['MIN'].dtype == object:
                    df_player['MIN'] = df_player['MIN'].astype(str).split(':').apply(
                        lambda x: int(x[0]) + int(x[1])/60 if isinstance(x, list) and len(x) == 2 else 0.0
                    )
                team_cols = ['GAME_ID', 'TEAM_ID', 'FGA', 'FTA', 'TOV']
                df_team_subset = df_team[team_cols].copy()
                df_team_subset.columns = ['GAME_ID', 'TEAM_ID', 'TEAM_FGA', 'TEAM_FTA', 'TEAM_TOV']
                df_player = df_player.merge(df_team_subset, on=['GAME_ID', 'TEAM_ID'], how='left')

                df_player['GAME_DATE_OBJ'] = pd.to_datetime(df_player['GAME_DATE']).dt.date

                #filtering only matches before the date
                df_filtered = df_player[df_player['GAME_DATE_OBJ'] < game.game_date].copy()
                #Sorting asc
                df_filtered = df_filtered.sort_values(by='GAME_DATE_OBJ', ascending=True)
                if not df_filtered.empty:
                    #Calculating advanced metrics
                    df_filtered['TS_PCT'] = df_filtered['PTS'] / (2 *(df_filtered['FGA'] + 0.44 * df_filtered['FTA']))
                    df_filtered['TS_PCT'] = df_filtered['TS_PCT'].fillna(0)

                    num = (df_filtered['FGA'] + 0.44 * df_filtered['FTA'] + df_filtered['TOV']) * 48
                    den = df_filtered['MIN'] * (df_filtered['TEAM_FGA'] + 0.44 * df_filtered['TEAM_FTA'] + df_filtered['TEAM_TOV'])
                    df_filtered['USG_PCT'] = 100 * (num / den)
                    df_filtered['USG_PCT'] = df_filtered['USG_PCT'].fillna(0)

                    #autoregression
                    features_to_ewma = ['MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG3M', 'TS_PCT', 'USG_PCT']
                    for col in features_to_ewma:
                        df_filtered[f'EWMA_{col}'] = df_filtered[col].ewm(span=5, adjust=False).mean()
                    #Saving state right before the game
                    latest_state = df_filtered.iloc[-1]
                    days_rest = (game.game_date - latest_state['GAME_DATE_OBJ']).days

                    debug_features = {
                        'days_rest': int(days_rest),
                        'ewma_min': round(latest_state['EWMA_MIN'], 2),
                        'ewma_usg': round(latest_state['EWMA_USG_PCT'], 2),
                        'ewma_ts': round(latest_state['EWMA_TS'], 3)
                    }

                    #Generating prediction for every stat

                    for target in TARGETS:
                        if target in ML_MODELS:
                            ewma_target_key = f'EWMA_{target.upper()}'
                            x_input = np.array([[
                                latest_state['EWMA_MIN'],
                                latest_state['EWMA_USG_PCT'],
                                latest_state['EWMA_TS_PCT'],
                                days_rest,
                                latest_state.get(ewma_target_key, 0.0)
                            ]])
                            pred_val = ML_MODELS[target].predict(x_input)[0]
                            predictions[target.upper()] = round(float(pred_val), 1)

            return JsonResponse({
                'predicted_points': predictions.get('PTS', 0.0),
                'predictions': predictions,
                'debug_features': debug_features,
                'status': 'success'
            })
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({
                'error': str(e)}, 
                status=500)
    return JsonResponse({
        'error': 'Only POST method allowed'
    }, status = 405)

def get_teams(request):
    """
    Get list of NBA teams
    
    """
    teams_query = Team.objects.all().values('id', 'name')
    teams_list = list(teams_query)
    return JsonResponse(teams_list, safe=False)
def get_players_by_team(request, team_id):
    players = Player.objects.filter(team__id=team_id).values('id', 'full_name', 'position')
    return JsonResponse(list(players), safe=False)
def get_games(request):

    games_query = Game.objects.select_related('home_team', 'away_team').all().order_by('-game_date')

    games_list = []
    for game in games_query:
        games_list.append({
            'id': game.id,
            'nba_game_id': game.nba_game_id,
            'game_date': game.game_date.strftime('%Y-%m-%d'),
            'home_team': {
                'id': game.home_team.id,
                'name': game.home_team.name,
                'abbreviation': game.home_team.abbreviation
            },
            'away_team': {
                'id': game.away_team.id,
                'name': game.away_team.name,
                'abbreviation': game.away_team.abbreviation
            }
        })
    return JsonResponse(games_list, safe=False)
@csrf_exempt
def predict_matchup(request):
    """
    predict team win probability and point differential using hybrid models.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            game = get_object_or_404(Game, id=data.get('game_id'))

            season_year = game.game_date.year if game.game_date.month > 7 else game.game_date.year - 1
            season_str = f"{season_year}-{str(season_year + 1)[-2:]}"

            #downloading logs for entire league, for self-merge and net-rating

            team_log = teamgamelogs.TeamGameLogs(season_nullable=season_str)
            df = team_log.get_data_frames()[0]

            if df.empty:
                return JsonResponse({'error': 'No data for season'}, status=400)

            df['GAME_DATE_OBJ'] = pd.to_datetime(df['GAME_DATE']).dt.date

            opp_cols = ['GAME_ID', 'TEAM_ID', 'PTS', 'FGA', 'FTA', 'OREB', 'TOV']
            df_opp = df[opp_cols].copy()
            df_opp.columns = ['GAME_ID', 'OPP_TEAM_ID', 'OPP_PTS', 'OPP_FGA', 'OPP_FTA', 'OPP_OREB', 'OPP_TOV']

            df = df.merge(df_opp, on='GAME_ID')
            df = df[df['TEAM_ID'] != df['OPP_TEAM_ID']].copy()
            df = df.sort_values(by=['TEAM_ID', 'GAME_DATE_OBJ'])

            #Calculating advanced stats

            df['POSS'] = 0.5 * (df['FGA'] + 0.44 * df['FTA'] - df['OREB'] + df['TOV'] + 
                                df['OPP_FGA'] + 0.44 * df['OPP_FTA'] - df['OPP_OREB'] + df['OPP_TOV'])
            df['eFG_PCT'] = (df['FGM'] + 0.5 * df['FG3M']) / df['FGA']
            df['OFF_RTG'] = 100 * (df['PTS'] / df['POSS'])
            df['DEF_RTG'] = 100 * (df['OPP_PTS'] / df['POSS'])
            df['NET_RTG'] = df['OFF_RTG'] - df['DEF_RTG']

            def get_team_state(team_nba_id):
                team_df = df[(df['TEAM_ID'] == team_nba_id) & (df['GAME_DATE_OBJ'] < game.game_date)].copy()
                if team_df.empty:
                    return {'NET_RTG': 0, 'eFG_PCT': 0.5, 'POSS': 100, 'REST': 7}
                for col in ['NET_RTG', 'eFG_PCT', 'POSS']:
                    team_df[f'EWMA_{col}'] = team_df[col].ewm(span=5, adjust=False).mean()
                last_game = team_df.iloc[-1]
                rest_days = (game.game_date - last_game['GAME_DATE_OBJ']).days

                return {
                    'NET_RTG': last_game['EWMA_NET_RTG'],
                    'eFG_PCT': last_game['EWMA_eFG_PCT'],
                    'POSS': last_game['EWMA_POSS'],
                    'REST': rest_days
                }

            home_state = get_team_state(game.home_team.nba_id)
            away_state = get_team_state(game.away_team.nba_id)

            #COnstructing X feature vector

            x_input = np.array([[
                home_state['NET_RTG'] - away_state['NET_RTG'],
                home_state['eFG_PCT'] - away_state['eFG_PCT'],
                home_state['POSS'] - away_state['POSS'],
                home_state['REST'],
                away_state['REST']
            ]])

            #prediction
            win_prob = TEAM_WIN_MODEL.predict_proba(x_input)[0][1] if TEAM_WIN_MODEL else 0.5
            point_diff = TEAM_DIFF_MODEL.predict(x_input)[0] if TEAM_DIFF_MODEL else 0.0

            return JsonResponse({
                'win_probability': round(float(win_prob) * 100, 1),
                'point_differential': round(float(point_diff), 1),
                'predict_winner': game.home_team.name if win_prob >= 0.5 else game.away_team.name,
                'status': 'success'
            })
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status = 500)
    return JsonResponse({'error': 'Method not allowed'}, status = 405)