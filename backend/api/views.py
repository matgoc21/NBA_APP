import os
import joblib
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

MODEL_PATH = os.path.join(settings.BASE_DIR, '../models/nba_scoring_model.joblib')
try:
    ml_model = joblib.load(MODEL_PATH)
    print("Model loaded")
except FileNotFoundError:
    ml_model = None
    print("Model NOT loaded")
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
