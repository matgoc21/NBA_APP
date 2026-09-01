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
from nba_api.stats.endpoints import playergamelogs
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Team, Player, Game
# Create your views here.

#LOADING THE MODEL ONCE
MODEL_PATH= os.path.abspath(os.path.join(str(settings.BASE_DIR), '..', 'models', 'nba_scoringmodel.joblib'))
MODEL = joblib.load(MODEL_PATH)
@csrf_exempt       
def predict_score(request):
    """
    Predict player score using a loded model.
    """

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player = get_object_or_404(Player, id=data.get('player_id'))
            game = get_object_or_404(Game, id = data.get('game_id'))

            home_game = 1 if player.team == game.home_team else 0

            year = game.game_date.year
            season_year = year if game.game_date.month > 7 else year - 1
            season_str = f"{season_year}-{str(season_year + 1)[-2:]}"

            date_before_game = (game.game_date - timedelta(days=1)).strftime('%m/%d/%Y')
            try:

                log = playergamelogs.PlayerGameLogs(
                    player_id_nullable=player.nba_id,
                    season_nullable=season_str,
                )
                df = log.get_data_frames()[0]
            except Exception as api_err:
                print(f"Ostrzeżenie: Błąd API NBA: {api_err}")
                df = pd.DataFrame()

            if not df.empty:

                df['GAME_DATE_OBJ'] = pd.to_datetime(df['GAME_DATE']).dt.date

                df_filtered = df[df['GAME_DATE_OBJ'] < game.game_date]

                df_filtered = df_filtered.sort_values(by='GAME_DATE_OBJ', ascending = False)

                if not df_filtered.empty:
                    pts_5g_avg = float(df_filtered.head(5)['PTS'].mean())
                    last_game_date = df_filtered.iloc[0]['GAME_DATE_OBJ']
                    days_rest = (game.game_date - last_game_date).days
                else:
                    #If first game of the season or a debut
                    pts_5g_avg = 0.0
                    days_rest = 7
            else:
                #If first game of the season or a debut
                pts_5g_avg = 0.0
                days_rest = 7
            features = np.array([[pts_5g_avg, days_rest, home_game]])

            prediction = MODEL.predict(features)[0]

            return JsonResponse({
                'predicted_points': round(prediction, 1),
                'debug_features': {
                    'pts_5g_avg' : round(pts_5g_avg, 1),
                    'days_rest': days_rest,
                    'home_game': home_game
                },
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