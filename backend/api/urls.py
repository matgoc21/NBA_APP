from django.urls import path
from .views import PredictPlayerScoreView
from api import views

urlpatterns = [
    path('predict/', PredictPlayerScoreView.as_view(), name = 'predict'),
    path('teams/', views.get_teams, name='get_teams'),
    path('teams/<int:team_id>/players/', views.get_players_by_team, name='team-players'),

]