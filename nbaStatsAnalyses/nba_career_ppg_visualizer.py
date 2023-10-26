"""This code connects to NBA stats endpoints to create a graph that displays the 
given player's points per game (PPG) over time for each season they have been in the NBA."""

import pandas as pd
pd.set_option('display.max_columns', None)
from nba_api.stats.static import players
from nba_api.stats.endpoints import playerdashboardbyyearoveryear
from matplotlib import pyplot as plt
from typing import Dict, List


def get_player_info() -> Dict:
    """From NBA Stats API, players.get_players() returns a list of dict's, with each dict 
    corresponding to a player. To make subsequent lookups easier, we return a dict where the
    key is the player's full name, and the value is the dict full of player info.
    """
    player = players.get_players()
    player_dict = {p['full_name'].lower(): p for p in player}
    return player_dict

def get_ppg_seasons(player_id: int) -> (List, List):
    """Given the player ID, returns a list of two lists: His seasons played, and his PPG 
    for the season with the corresponding index"""
    season_list, ppg_list = [], []
    player_career_YoY = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id).get_data_frames()[1]
    for index, season in player_career_YoY.sort_values(by='GROUP_VALUE').iterrows():
        if season['GROUP_VALUE'] in season_list: #In case the player got traded mid-season
            continue
        else:
            season_list.append(season['GROUP_VALUE'])
            ppg = season['PTS'] / season['GP']
            ppg_list.append(round(ppg,1))
    season_list = list(map(abbreviate_season,season_list))
    return season_list, ppg_list

def abbreviate_season(season) -> str:
    "Abbreviates the season label. E.g. 2022-2023 becomes '23. "
    return "'"+season[-2:]

def plot_ppg_seasons(season_list: List, ppg_list:List) -> None:
    "Plots PPG across the player's seasons"
    plt.plot(season_list, ppg_list, '-o')
    for i, j in zip(season_list, ppg_list):
        plt.text(i, j+0.3, str(j)) 
    plt.xlabel('NBA Season')
    plt.ylabel('Points per Game Scored')
    plt.show()

def visualize_career_ppg(player_name: str) -> None:
    "Gets career stats of the player from NBA Stats and plots their PPG seasons over the years"
    player_info = get_player_info()
    player_id = player_info.get(player_name.lower())['id']
    seasons, ppgs = get_ppg_seasons(player_id)
    plot_ppg_seasons(seasons, ppgs)

def main():
    visualize_career_ppg("Stephen Curry")
    

main()