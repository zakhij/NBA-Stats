#Originally done in PyCharm. This code connects to NBA stats endpoints to create a graph that displays given player's points per game (PPG) over time 
#for each season they have been in the NBA.

import pandas as pd
pd.set_option('display.max_columns', None)
import time
from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playerdashboardbyyearoveryear
from matplotlib import pyplot as plt

def careerVisualizer(playerName):
    player = players.get_players()
    PPGList = []
    SeasonList = []
    pl = [p for p in player if p['full_name'].lower() in playerName.lower()][0]
    pID = pl['id']
    playerCareerYoY = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(pID).get_data_frames()[1]
    print(playerCareerYoY.columns)
    print(playerCareerYoY.sort_values(by='GROUP_VALUE'))
    for k in playerCareerYoY['GROUP_VALUE'].sort_values():
        if k not in SeasonList:
            real = k[-2:]
            print(int(real))
            SeasonList.append(real)
            ppg = playerCareerYoY.loc[playerCareerYoY['GROUP_VALUE'] == k,'PTS']/playerCareerYoY.loc[playerCareerYoY['GROUP_VALUE'] == k,'GP']
            PPGList.append(round(ppg.values[0],1))
    plt.plot(SeasonList, PPGList, '-o')
    plt.xlabel('Seasons in NBA')
    plt.ylabel('Points per Game Scored')
    plt.show()

careerVisualizer("Stephen Curry")
