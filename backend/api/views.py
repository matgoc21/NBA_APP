import os
import joblib
import json
import numpy as np
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Team, Player, Game
# Create your views here.

# MODEL_PATH = os.path.join(settings.BASE_DIR, '../models/nba_scoring_model.joblib')
# try:
#     ml_model = joblib.load(MODEL_PATH)
#     print("Model loaded")
# except FileNotFoundError:
#     ml_model = None
#     print("Model NOT loaded")


# BASE_DIR_STR = str(settings.BASE_DIR)
# MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR_STR, '..', 'models', 'nba_scoringmodel.joblib'))
# print(f"Ladowanie modelu: {MODEL_PATH} \n")
# try:
#     ml_model = joblib.load(MODEL_PATH)
#     print("--- DEBUG: Z sukcesem załadowano model Machine Learning! ---")
# except Exception as e:
#     ml_model = None
#     print(f"--- DEBUG: BŁĄD ŁADOWANIA MODELU: {e} ---")
# class PredictPlayerScoreView(APIView):
#     def post(self,request):
#         """
#         Predict player score
#         :param request:
#         :return:
#         """
#         if ml_model is None:
#             return Response(
#                 {"error": "Model AI not loaded"},
#                 status=status.HTTP_503_SERVICE_UNAVAILABLE
#             )

#         try:
#             data = request.data
#             pts_5g_avg = float(data.get('PTS_5G_AVG', 0))
#             days_rest = float(data.get('DAYS_REST', 0))
#             home_game = int(data.get('HOME_GAME', 0))
#             input_df = pd.DataFrame([{
#                 'PTS_5G_AVG': pts_5g_avg,
#                 'DAYS_REST': days_rest,
#                 'HOME_GAME': home_game
#             }])
#             prediction = ml_model.predict(input_df)
#             predicted_score = round(prediction[0], 1)
#             return Response({
#                 "predicted_pts": predicted_score,
#                 "input_data": {
#                     "PTS_5G_AVG": pts_5g_avg,
#                     "DAYS_REST": days_rest,
#                     "HOME_GAME": home_game
#                 }
#             }, status = status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": f"Błąd przetwarzania: {str(e)}"},
#                             status = status.HTTP_400_BAD_REQUEST)
@csrf_exempt       
def predict_score(request):
    """
    Predict player score using a loded model.
    """

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_id = data.get('player_id')
            game_id = data.get('game_id')

            #Mock data, to be replaced with nba_api fetch

            pts_5g_avg = 22.5
            days_rest = 2
            home_game = 1

            #Loading the model

            model_path = os.path.abspath(os.path.join(str(settings.BASE_DIR), '..', 'models', 'nba_scoringmodel.joblib'))
            model = joblib.load(model_path)

            #Setting an array in exatly the way model expects it

            features = np.array([[pts_5g_avg, days_rest, home_game]])
            #Prediction
            prediction = model.predict(features)[0]

            return JsonResponse({
                'predicted_points': round(prediction, 1),
                'status': 'success'
            })
        except Exception as e:
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