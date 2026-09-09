from django.urls import path
#from .views import PredictPlayerScoreView
from api import views

urlpatterns = [
    path('predict-score/', views.predict_score, name = 'predict-score'),
    path('teams/', views.get_teams, name='get_teams'),
    path('teams/<int:team_id>/players/', views.get_players_by_team, name='team-players'),
    path('games/', views.get_games, name='get_games'),
    path('predict-matchup/', views.predict_matchup, name='predict_matchup'),

]