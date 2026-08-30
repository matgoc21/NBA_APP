import datetime
from django.core.management.base import BaseCommand
from api.models import Game, Team
from nba_api.stats.endpoints import scoreboardv2

class Command(BaseCommand):
    help = 'Fetches matches from given day (default today) and saves them in database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Optional date in YYYY-MM-DD format'
        )
    def handle(self, *args, **kwargs):
        target_date_str = kwargs.get('date')
        if target_date_str:
            target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d').date()
        else:
            target_date = datetime.date.today()

        self.stdout.write(f"Fetching matches for date: {target_date}")

        try:
            board = scoreboardv2.ScoreboardV2(game_date=target_date.strftime('%Y-%m-%d'))
            df = board.game_header.get_data_frame()
            if df.empty:
                self.stdout.write(self.style.WARNING(f"No matches found for date: {target_date}"))
                return
            games_created = 0
            for index, row in df.iterrows():
                home_team_id = row['HOME_TEAM_ID']
                away_team_id = row['VISITOR_TEAM_ID']

                try:
                    home_team = Team.objects.get(nba_id=home_team_id)
                    away_team = Team.objects.get(nba_id=away_team_id)

                    Game.objects.update_or_create(
                        nba_game_id=row['GAME_ID'],
                        defaults={
                            'game_date': target_date,
                            'home_team': home_team,
                            'away_team': away_team
                        }
                    )
                    games_created += 1
                except Team.DoesNotExist as e:
                    self.stdout.write(self.style.ERROR(f"Team not found in database: {e}, match skipped."))

            self.stdout.write(self.style.SUCCESS(f'Successfully fetched and stored {games_created} matches for date: {target_date}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching matches: {e}"))  