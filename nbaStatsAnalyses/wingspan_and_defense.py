#Originally coded in PyCharm. This code seeks to find a relationship between wingspan (specifically wingspan-to-height ratio) and defensive impact of NBA players.
#To quantify defensive impact, PCT_PLUSMINUS, which gives the difference between a player's defensive FG% and the expected defensive FG% on the shots contested,
#was primarily used and charted. The wingspan data was sourced from https://craftednba.com/player-traits/length, while the defensive stats were obtained by
#connecting to NBA API endpoints. Correlations between wingspan ratio and deflections/min & contests/min were also looked at, although I could not find a 
#strong correlation for any defensive metric with wingspan.

import pandas as pd
pd.set_option('display.max_columns', None)
import numpy as np
from nba_api.stats import endpoints as ep
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt

playerDF = ep.leaguedashplayerbiostats.LeagueDashPlayerBioStats().get_data_frames()[0]
wingspanInfo = pd.read_csv('wingspan.csv')[['Wingspan', 'PlayerID']]
wingspanInfo = wingspanInfo.rename(columns={'Wingspan':'WINGSPAN_INCHES'})
dFGInfo = ep.leaguedashptdefend.LeagueDashPtDefend().get_data_frames()[0][['CLOSE_DEF_PERSON_ID', 'D_FGA', 'D_FG_PCT', 'PCT_PLUSMINUS']]
hustleInfo = ep.leaguehustlestatsplayer.LeagueHustleStatsPlayer().get_data_frames()[0].drop \
    (columns=['PLAYER_NAME','TEAM_ID','TEAM_ABBREVIATION','AGE','G'])

playerDF = playerDF.merge(wingspanInfo,'left',left_on='PLAYER_ID',right_on='PlayerID')
playerDF = playerDF.merge(dFGInfo,'left',left_on='PLAYER_ID',right_on='CLOSE_DEF_PERSON_ID')
playerDF = playerDF.merge(hustleInfo,'left',left_on='PLAYER_ID',right_on='PLAYER_ID')
playerDF.drop(columns=['PlayerID','CLOSE_DEF_PERSON_ID'],inplace=True)

playerDF['WINGSPAN_HEIGHT_RATIO'] = round(playerDF['WINGSPAN_INCHES']/playerDF['PLAYER_HEIGHT_INCHES'],3)
playerDF['DEFLECTIONS_PER_MIN'] = playerDF['DEFLECTIONS']/playerDF['MIN']
playerDF['CONTESTED_SHOTS_PER_MIN'] = playerDF['CONTESTED_SHOTS']/playerDF['GP']


minFilter = playerDF['MIN'] > 500
nanFilter = pd.notna(playerDF['WINGSPAN_INCHES'])




linreg = LinearRegression()

x = np.array(playerDF.loc[minFilter & nanFilter,:]['WINGSPAN_HEIGHT_RATIO']).reshape(-1,1)
y = playerDF.loc[minFilter & nanFilter,:]['PCT_PLUSMINUS']
linreg.fit(x,y)
y_pred = linreg.predict(x)
print(linreg.coef_)
print(linreg.intercept_)

plt.plot(x, y_pred)
#plt.plot(playerDF.loc[minFilter,:]['WINGSPAN_HEIGHT_RATIO'].values,playerDF.loc[minFilter,:]['DEFLECTIONS_PER_MIN'].values,'o')
plt.plot(playerDF.loc[minFilter & nanFilter,:]['WINGSPAN_HEIGHT_RATIO'].values,playerDF.loc[minFilter & nanFilter,:]['PCT_PLUSMINUS'].values,'o')
plt.show()

corr = playerDF.loc[minFilter & nanFilter,:][['WINGSPAN_HEIGHT_RATIO','DEFLECTIONS_PER_MIN','PCT_PLUSMINUS', 'CONTESTED_SHOTS_PER_MIN']].corr()
print(corr)
