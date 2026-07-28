from django.urls import path
from .views import PredictPlayerScoreView

urlpatterns = [
    path('predict/', PredictPlayerScoreView.as_view(), name = 'predict_score'),
]