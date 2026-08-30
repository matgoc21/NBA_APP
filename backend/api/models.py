from django.db import models

# Create your models here.
class Team(models.Model):
    nba_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100, unique = True)
    city = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.city} {self.name} ({self.abbreviation})"
class Player(models.Model):
    nba_id = models.IntegerField(unique=True)
    full_name = models.CharField(max_length=200)
   # first_name = models.CharField(max_length = 100)
   # last_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    position =models.CharField(max_length=20, null = True, blank = True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name}"
class Game(models.Model):
    nba_game_id = models.CharField(max_length=20, unique=True)
    game_date = models.DateField()
    home_team = models.ForeignKey(Team, on_delete = models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete = models.CASCADE, related_name='away_games')

    def __str__(self):
        return f"{self.game_date}: {self.away_team.abbreviation} @ {self.home_team.abbreviation}"