#Originally done in Pycharm. This code connects to NBA stats endpoints to determine which players "kill" certain teams, which means that they perform especially
#well against a given team over their career. Points scored was used as the primary metric. For example, if Player A has a career PPG value of 12, but has 
#played against the Los Angeles Lakers 8 times in his career and averaged 20, that player is considered a Lakers Killer. 

import pandas as pd
pd.set_option('display.max_columns', None)
import time
from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playerdashboardbyyearoveryear


def Killer(playerName, teamName):
    player = players.get_players()
    team = teams.get_teams()
    pl = [p for p in player if p['full_name'].lower() in playerName.lower()][0]
    pName = pl['full_name']
    pID = pl['id']

    tm = [t for t in team if t['full_name'].lower() in teamName.lower()][0]
    tName = tm['full_name']
    tID = tm['id']

    playerCareerYoY = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(pID).get_data_frames()[1]
    playerOppYoY = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(pID, opponent_team_id=tID).get_data_frames()[1]
    gameThreshold = playerOppYoY['GP'].sum() >= 5
    if gameThreshold:
        careerPPG = playerCareerYoY['PTS'].sum()/playerCareerYoY['GP'].sum()
        oppPPG = playerOppYoY['PTS'].sum()/playerOppYoY['GP'].sum()
        ppgThreshold = careerPPG * 1.25 < oppPPG and oppPPG >= 5
        #careerPPM = playerCareerYoY['PTS'].sum()/playerOppYoY['']
        print(f"{pName} averages {round(careerPPG,1)} points for his career, but against"
              f" the {tName}, he has averaged {round(oppPPG,1)} PTS.")
        if ppgThreshold:
            print("He's a killer!")
    else:
        print('Not enough games played against that team, sorry!')

def teamKillers(teamName):
    player = players.get_players()
    team = teams.get_teams()
    pl = [p for p in player if p['is_active']]
    tm = [t for t in team if t['full_name'].lower() in teamName.lower()][0]
    tID = tm['id']
    killerList = []
    for p in pl:
        playerCareerYoY = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(p['id']).get_data_frames()[1]
        playerOppYoY = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(p['id'], opponent_team_id=tID).get_data_frames()[1]
        gameThreshold = playerOppYoY['GP'].sum() >=5
        if gameThreshold:
            careerPPG = playerCareerYoY['PTS'].sum()/playerCareerYoY['GP'].sum()
            oppPPG = playerOppYoY['PTS'].sum()/playerOppYoY['GP'].sum()
            ppgThreshold = careerPPG * 1.25 < oppPPG and oppPPG >= 5
            if ppgThreshold:
                killerList.append(p['full_name'])
            time.sleep(1.5)
    return killerList

Killer('Klay Thompson', 'Sacramento Kings')

print(teamKillers('Sacramento Kings'))
