from django.core.management.base import BaseCommand
from api.models import Team, Player
from nba_api.stats.static import teams

class Command(BaseCommand):
    help = 'Fetch NBA teams and players from the API and store them in the database'

    def handle(self, *args, **kwargs):
        nba_teams = teams.get_teams()
        for t in nba_teams:
            Team.objects.update_or_create(
                nba_id=t['id'],
                defaults={
                    'name': t['full_name'],
                    'city': t['city'],
                    'abbreviation': t['abbreviation']
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Successfully fetched and stored {len(nba_teams)}NBA teams.'))