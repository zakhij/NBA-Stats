'''This code seeks to find a relationship between wingspan (specifically wingspan-to-height ratio) 
and defensive impact of NBA players. To quantify defensive impact, a few stats are available. I focus
on 3: Deflections per minute, Contests per minute, and Defensive FG +/-, which gives the difference 
between a player's defensive FG% and the expected defensive FG% on the shots contested. The script as
described below uses DEFLECTIONS_PER_MIN, but this could easily be swapped out for the other stats.
The wingspan data was sourced from https://craftednba.com/player-traits/length, while the defensive stats 
were obtained by connecting to NBA API endpoints. I ended up looking at correlations between wingspan ratio 
and all three of the defensive metrics, but only found weakly positive correlations.'''

import pandas as pd
pd.set_option('display.max_columns', None)
import numpy as np
from nba_api.stats import endpoints as ep
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt


def get_wingspan_data() -> pd.DataFrame:
    "Reads Wingspan CSV file and converts to dataframe"
    wingspan = pd.read_csv('wingspan.csv')[['Wingspan', 'PlayerID']]
    wingspan = wingspan.rename(columns={'Wingspan':'WINGSPAN_INCHES'})
    return wingspan

def get_player_game_stats() -> (pd.DataFrame, pd.DataFrame):
    "Hits NBA Stats endpoint to get defense/hustle game stats for players"
    defense = ep.leaguedashptdefend.LeagueDashPtDefend().get_data_frames()[0]\
        [['CLOSE_DEF_PERSON_ID', 'D_FGA', 'D_FG_PCT', 'PCT_PLUSMINUS']]
    hustle = ep.leaguehustlestatsplayer.LeagueHustleStatsPlayer().get_data_frames()[0].drop \
        (columns=['PLAYER_NAME','TEAM_ID','TEAM_ABBREVIATION','AGE','G'])
    return defense, hustle

def merge_data(player_bio: pd.DataFrame, wingspan: pd.DataFrame, defense: pd.DataFrame, hustle: pd.DataFrame) -> pd.DataFrame:
    """Merge player bio stats data with wingspan, defensive, and hustle information."""
    player_bio = player_bio.merge(wingspan,'left',left_on='PLAYER_ID',right_on='PlayerID')
    player_bio = player_bio.merge(defense,'left',left_on='PLAYER_ID',right_on='CLOSE_DEF_PERSON_ID')
    player_bio = player_bio.merge(hustle,'left',left_on='PLAYER_ID',right_on='PLAYER_ID')
    player_bio.drop(columns=['PlayerID','CLOSE_DEF_PERSON_ID'], inplace=True)
    return player_bio


def create_new_stats(player_data: pd.DataFrame) -> pd.DataFrame:
    "Adding new player bio/game statistics to perform analysis on."
    player_data['WINGSPAN_HEIGHT_RATIO'] = round(player_data['WINGSPAN_INCHES']/player_data['PLAYER_HEIGHT_INCHES'],3)
    player_data['DEFLECTIONS_PER_MIN'] = player_data['DEFLECTIONS']/player_data['MIN']
    player_data['CONTESTED_SHOTS_PER_MIN'] = player_data['CONTESTED_SHOTS']/player_data['MIN']

class LinRegModel:
    def __init__(self, data: pd.DataFrame, x_col: str, y_col: str):
        self.data = data
        self.x_col = x_col
        self.y_col = y_col
        self.min_minutes = 500
        self.model = LinearRegression()
        self.fit_model()
        
    def fit_model(self):
        """Fits the linear regression model so we have a new y_predict column."""
        x_filtered = self.filter_data_for_regression()
        y_filtered = self.data.loc[x_filtered.index, self.y_col]
        self.y_filtered = np.array(y_filtered)
        self.x_filtered = np.array(x_filtered).reshape(-1, 1)
        self.model.fit(self.x_filtered, self.y_filtered)
        self.y_pred = self.model.predict(self.x_filtered)

    def filter_data_for_regression(self) -> pd.DataFrame:
        """Filter the data based on a minimum amount of minutes played and non-null values for the independent variable."""
        minFilter = self.data['MIN'] >= self.min_minutes
        nanFilter = pd.notna(self.data[self.x_col])
        return self.data[minFilter & nanFilter][self.x_col]
        
    def plot_regression_results(self):
        """Plot the observed data points and the regression line."""
        plt.plot(self.x_filtered, self.y_pred, color='blue', linewidth=2)
        plt.scatter(self.x_filtered, self.y_filtered, color='red', marker='o')
        plt.xlabel(self.x_col)
        plt.ylabel(self.y_col)
        plt.show()
        
    def display_correlation_matrix(self):
        """Compute and display the correlation matrix for the independent and dependent variable."""
        corr = self.data[[self.x_col, self.y_col]].corr()
        print(corr)
    


def main():
    #Get data from NBA Stats and local wingspan data csv
    player_bio_stats = ep.leaguedashplayerbiostats.LeagueDashPlayerBioStats().get_data_frames()[0]
    wingspan_data = get_wingspan_data()
    defense_data, hustle_data = get_player_game_stats()

    #Merge data together and create new stats from them
    total_player_data = merge_data(player_bio_stats, wingspan_data, defense_data, hustle_data)
    total_player_data = create_new_stats(total_player_data)

    #Defining our independent and dependent variables that we want to build the LinReg model on
    x_column = "WINGSPAN_HEIGHT_RATIO"
    y_column = "DEFLECTIONS_PER_MIN"

    #Building model, plotting results
    lin_reg_model = LinRegModel(total_player_data, x_column, y_column)
    lin_reg_model.plot_regression_results()
    lin_reg_model.display_correlation_matrix()


if __name__ == '__main__':
    main()