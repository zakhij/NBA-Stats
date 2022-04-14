# importing modules and packages 

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

!pip install nba_api
from nba_api.stats.endpoints import leaguedashplayerstats

!pip install pandas_bokeh
import pandas_bokeh
pandas_bokeh.output_notebook()

# pandas options
pd.set_option('display.max_rows', 100)
pd.set_option('plotting.backend', 'pandas_bokeh')
pandas_bokeh.output_notebook()

# Accessing 2021-22 season player stats dataframe through NBA Stats API live endpoint
# NOTE: If there is timeout error in accessing endpoint, factory reset the runtime and try again.

#playerStatsDF = leaguedashplayerstats.LeagueDashPlayerStats().get_data_frames()[0]
#layerStatsDF.to_csv('playerStatsDF')

!wget -nc "https://github.com/zhij713/NBA-Stats-ADAM/raw/main/playerStatsDF.csv"
#Turn this into CSV, place into Github

# loading salary and advanced player impact data from designated GitHub repository

!wget -nc "https://raw.githubusercontent.com/zhij713/NBA-Stats-ADAM/main/itp487/LEBRON.csv"
!wget -nc "https://raw.githubusercontent.com/zhij713/NBA-Stats-ADAM/main/itp487/latest_RAPTOR_by_player.csv"
!wget -nc "https://raw.githubusercontent.com/zhij713/NBA-Stats-ADAM/main/itp487/salaryCleaned.csv"

playerStatsDF = pd.read_csv("playerStatsDF.csv")
LEBRONCSV = pd.read_csv("LEBRON.csv") # Raw LEBRON data, web-scraped from bball-index website using Excel's Power Query

RAPTORCSV = pd.read_csv("latest_RAPTOR_by_player.csv") # Raw RAPTOR data, downloaded from 538's website

salary = pd.read_csv("salaryCleaned.csv") # Raw salary data, web-scraped from HoopsHype website using Power Query. There were some discrepancies 
                                          # in how player names were listed compared to the official NBA Stats website, so I manually cleaned the data  
                                          # and added Player ID (as defined by NBA Stats) as a new column to facilitate data integration

# structure and shape 

print(playerStatsDF.columns)
print(salary.columns)
print(LEBRONCSV.columns)
print(RAPTORCSV.columns)

print(playerStatsDF.shape)

# basic distributon and visualization

print(playerStatsDF[['PLAYER_NAME','MIN']])

#plt.hist(playerStatsDF['PTS'])

playerStatsDF.sort_values(by='PTS',ascending=False).plot_bokeh(kind='bar',
                        x='PLAYER_NAME', y='PTS', xlabel = 'Players',
                        ylabel='Points Scored')

# NAs / NULL 

salary.dropna(how='any',inplace=True)


# Duplicate entries 

salary.drop_duplicates(subset=['PLAYER_ID'])


# Filter Columns 

salary = salary.iloc[:,:3]
playerStatsDF = playerStatsDF[['PLAYER_ID','PLAYER_NAME','TEAM_ABBREVIATION','AGE','GP','MIN','PTS']]
LEBRONCSV = LEBRONCSV[['PLAYER','LEBRON']]
RAPTORCSV['RAPTOR'] = RAPTORCSV['raptor_total']
RAPTORCSV = RAPTORCSV[['player_name','RAPTOR']]

# Integrate Data

playerStatsDF2 = pd.merge(playerStatsDF,salary,how='left',left_on='PLAYER_ID',right_on='PLAYER_ID')
playerStatsDF2 = playerStatsDF2.merge(LEBRONCSV,how='left',left_on='PLAYER_NAME',right_on='PLAYER')
playerStatsDF2 = playerStatsDF2.merge(RAPTORCSV,how='left',left_on='PLAYER_NAME',right_on='player_name')
playerStatsDF2.drop(columns=['Player','PLAYER_ID','PLAYER','player_name'],inplace=True)

print(playerStatsDF2.head(5))


# Correlations

minCutoff = 500 
playerStatsQualified = playerStatsDF2[playerStatsDF2['MIN'] >= minCutoff] #Setting and implementing a minutes played qualifier

corrMatrix = playerStatsQualified.corr()
print(corrMatrix)

# Linear Regression: Player impact metric and player salary

from sklearn.linear_model import LinearRegression

X1 = np.array(playerStatsQualified['PTS']).reshape(-1,1)
X2 = np.array(playerStatsQualified['RAPTOR']).reshape(-1,1)
X3 = np.array(playerStatsQualified['LEBRON']).reshape(-1,1)
X4 = np.array(playerStatsQualified[['PTS','RAPTOR','LEBRON']]).reshape(-1,3)

y = np.array(playerStatsQualified['2021/22']).reshape(-1,1)


model_lin1 = LinearRegression().fit(X1,y) # Modeling points scored vs. salary
model_lin2 = LinearRegression().fit(X2,y) # Modeling RAPTOR metric vs. salary
model_lin3 = LinearRegression().fit(X3,y) # Modeling LEBRON metric vs. salary
model_lin4 = LinearRegression().fit(X4,y) # Modeling all 3 metrics vs. salary

# X = 2D array with non-predictor variables
# y = 2D array with predictor variable 

# Linear Regression (testing)

print(f"Model 1 R^2: {model_lin1.score(X1,y)}")
print(f"Model 2 R^2: {model_lin2.score(X2,y)}")
print(f"Model 3 R^2: {model_lin3.score(X3,y)}")
print(f"Model 4 R^2: {model_lin4.score(X4,y)}")

# Based on the poor R^2 scores of our models, thee does not appear to be a strong correlation 
# between our player impact metrics and salary. 

# Creating prediction variables for each model to facilitate visualization
y_pred1 = model_lin1.predict(X1)
y_pred2 = model_lin2.predict(X2)
y_pred3 = model_lin3.predict(X3)
y_pred4 = model_lin4.predict(X4)

# Visualizations 

fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(25,5))

fig.suptitle('Linear Regression Lines, Player Impact vs. Player Salary')

ax1 = plt.subplot(1,3,1)
ax1. plot(X1, y, 'o')
ax1.plot(X1, y_pred1)
ax1.set_xlabel('Points Scored')
ax1.set_ylabel('Salary (in $10 Million)')

ax2 = plt.subplot(1,3,2)
ax2. plot(X2, y, 'o')
ax2.plot(X2, y_pred2)
ax2.set_xlabel('RAPTOR Score')


ax3 = plt.subplot(1,3,3)
ax3. plot(X3, y, 'o')
ax3.plot(X3, y_pred3)
ax3.set_xlabel('LEBRON Score')

plt.show()


# Listing most cost-efficient players based on our three metrics.  

playerStatsQualified['PTS/$MIL'] = 100000 * playerStatsQualified['PTS'] / playerStatsQualified['2021/22']
playerStatsQualified['RAPTOR/$MIL'] = 100000 * playerStatsQualified['RAPTOR'] / playerStatsQualified['2021/22']
playerStatsQualified['LEBRON/$MIL'] = 100000 * playerStatsQualified['LEBRON'] / playerStatsQualified['2021/22']

print(playerStatsQualified[['PLAYER_NAME','TEAM_ABBREVIATION','PTS','2021/22','PTS/$MIL']]\
      .sort_values(by='PTS/$MIL',ascending=False).head(10))
print('\n')

print(playerStatsQualified[['PLAYER_NAME','TEAM_ABBREVIATION','RAPTOR','2021/22','RAPTOR/$MIL']]\
      .sort_values(by='RAPTOR/$MIL',ascending=False).head(10))
print('\n')

print(playerStatsQualified[['PLAYER_NAME','TEAM_ABBREVIATION','LEBRON','2021/22','LEBRON/$MIL']]\
      .sort_values(by='LEBRON/$MIL',ascending=False).head(10))

playerStatsQualified[['PLAYER_NAME','TEAM_ABBREVIATION','PTS','2021/22','PTS/$MIL']]\
      .sort_values(by='PTS/$MIL',ascending=False).plot_bokeh\
      (kind='bar',x='PLAYER_NAME',y=['PTS/$MIL'])

