import time
from django.core.management.base import BaseCommand
from api.models import Player, Team
from nba_api.stats.endpoints import commonteamroster

class Command(BaseCommand):
    help = 'Fetch rosters for nba teams from nba API'

    def handle(self, *args, **kwargs):
        teams = Team.objects.all()
        for team in teams:
            self.stdout.write(f'Fetching roster for team: {team.name}')
            roster = commonteamroster.CommonTeamRoster(team_id = team.nba_id)
            df_roster = roster.get_data_frames()[0]
            for _, row in df_roster.iterrows():
                Player.objects.update_or_create(
                    nba_id=row['PLAYER_ID'],
                    defaults={
                        'full_name': row['PLAYER'],
                        'team': team,
                        'position': row['POSITION'],
                        'is_active': True
                    }
                )
            time.sleep(0.6)  # Sleep to avoid hitting the API rate limit
        self.stdout.write(self.style.SUCCESS('Successfully fetched and stored rosters for all NBA teams.'))    