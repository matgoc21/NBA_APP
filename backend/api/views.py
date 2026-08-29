import os
import joblib
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Team, Player
# Create your views here.

# MODEL_PATH = os.path.join(settings.BASE_DIR, '../models/nba_scoring_model.joblib')
# try:
#     ml_model = joblib.load(MODEL_PATH)
#     print("Model loaded")
# except FileNotFoundError:
#     ml_model = None
#     print("Model NOT loaded")
BASE_DIR_STR = str(settings.BASE_DIR)
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR_STR, '..', 'models', 'nba_scoringmodel.joblib'))
print(f"Ladowanie modelu: {MODEL_PATH} \n")
try:
    ml_model = joblib.load(MODEL_PATH)
    print("--- DEBUG: Z sukcesem załadowano model Machine Learning! ---")
except Exception as e:
    ml_model = None
    print(f"--- DEBUG: BŁĄD ŁADOWANIA MODELU: {e} ---")
class PredictPlayerScoreView(APIView):
    def post(self,request):
        """
        Predict player score
        :param request:
        :return:
        """
        if ml_model is None:
            return Response(
                {"error": "Model AI not loaded"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            data = request.data
            pts_5g_avg = float(data.get('PTS_5G_AVG', 0))
            days_rest = float(data.get('DAYS_REST', 0))
            home_game = int(data.get('HOME_GAME', 0))
            input_df = pd.DataFrame([{
                'PTS_5G_AVG': pts_5g_avg,
                'DAYS_REST': days_rest,
                'HOME_GAME': home_game
            }])
            prediction = ml_model.predict(input_df)
            predicted_score = round(prediction[0], 1)
            return Response({
                "predicted_pts": predicted_score,
                "input_data": {
                    "PTS_5G_AVG": pts_5g_avg,
                    "DAYS_REST": days_rest,
                    "HOME_GAME": home_game
                }
            }, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Błąd przetwarzania: {str(e)}"},
                            status = status.HTTP_400_BAD_REQUEST)
        
def get_teams(request):
    """
    Get list of NBA teams
    
    """
    teams_query = Team.objects.all().values('id', 'name')
    teams_list = list(teams_query)
    return JsonResponse(teams_list, safe=False)