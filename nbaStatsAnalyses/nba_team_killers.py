"""
This code connects to NBA stats endpoints to determine which players "kill" certain teams, 
which means that they perform especially well against them over their career. Points scored 
is used as the primary metric. For example, if Player A has a career PPG value of 12, but has 
averaged 20 against the Lakers, that player is considered a Lakers Killer. 
"""

import pandas as pd
pd.set_option('display.max_columns', None)
import time
from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playerdashboardbyyearoveryear
from typing import Dict


def get_player_info():
    """From NBA Stats API, players.get_players() returns a list of dict's, with each dict 
    corresponding to a player. To make subsequent lookups easier, we return a dict where the
    key is the player's full name, and the value is the dict full of player info.
    """
    player = players.get_players()
    player_dict = {p['full_name'].lower(): p for p in player}
    return player_dict

def get_team_info():
    """From NBA Stats API, team.get_teams() returns a list of dict's, with each dict 
    corresponding to a team. To make subsequent lookups easier, we return a dict where the
    key is the team's name, and the value is the dict full of team info.
    """
    team = teams.get_teams()
    team_dict = {t['full_name'].lower(): t for t in team}
    return team_dict

def get_career_stats_against_team(player_id:int, team_id:int) -> Dict[str, float]:
    """Given the player and team, digs through the player's career PPG overall and specifically 
    against that team, returning a dict that contains both PPG values"""
    player_career_YoY = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id).get_data_frames()[1]
    player_opp_YoY = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id, opponent_team_id=team_id).get_data_frames()[1]
    
    player_stats = {}
    player_stats['overall_ppg'] = round(player_career_YoY['PTS'].sum()/player_career_YoY['GP'].sum(),1)
    player_stats['ppg_against_team'] = round(player_opp_YoY['PTS'].sum()/player_opp_YoY['GP'].sum(),1)
    player_stats['gp_against_team'] =  player_opp_YoY['GP'].sum()

    return player_stats

def check_if_killer(player_stats:Dict, game_threshold:int = 5, better_threshold:int = 1.25) -> bool:
    """Checks if a player is a killer, based on a game and performance increase threshold"""
    if player_stats['ppg_against_team'] >= player_stats['overall_ppg'] * better_threshold\
    and player_stats['gp_against_team'] >= game_threshold:
        return True
    else:
        return False

def express_stats(player_name:str, team_name:str, player_stats:Dict) -> None:
    """Prints out the stored stats of the player performance"""
    print(f"{player_name} has averaged {player_stats['overall_ppg']} points for his career, and against\
    the {team_name}, he has averaged {player_stats['ppg_against_team']} points in {player_stats['gp_against_team']} games.")


def main():
    player_name = input("Enter player name: ")
    team_name = input("Enter team name: ")

    player_info = get_player_info()
    player_id = player_info.get(player_name.lower())['id']
    team_info = get_team_info()
    team_id = team_info.get(team_name.lower())['id']

    stats = get_career_stats_against_team(player_id, team_id)
    express_stats(player_name, team_name, stats)
    if check_if_killer(stats):
        print(f"He's a certified {team_name} killer!")


main()