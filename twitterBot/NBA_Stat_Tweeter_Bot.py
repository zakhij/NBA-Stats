#Originally written in PyCharm. Accesses player stats data stored in AWS RDS via mySQL connection (see NBA_to_SQL_Pipeline.py). Then scans Twitter mention tweets for names of current NBA players, replying to those tweets with the respective values for the number of minutes played this season for the players that were identified. 
#This code has been uploaded on a crontab on an AWS EC2 instance, being executed every 10 minutes. 

#In the future, as I'm able to grow what types of statistics are stored in the database, I may increase the scope of what type of information the reply tweet contains.

import sqlalchemy
import pandas as pd
import tweepy
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog

user = "zhijaouy"
pw = "" #Removed for privacy purposes
host = "nbastatsaws1.cx08ymmfb8n8.us-east-1.rds.amazonaws.com"
dbschema = "nbastats"
engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{pw}@{host}/{dbschema}")
playerstatsDF = pd.read_sql("select * from leaguedashplayerstats", engine) #Extracting player stats data from SQL server

apiKey = '' #Removed for privacy purposes
apiSecret = '' #Removed for privacy purposes
accessToken = '' #Removed for privacy purposes
accessSecret = '' #Removed for privacy purposes

oauth = tweepy.OAuthHandler(apiKey, apiSecret)
oauth.set_access_token(accessToken,accessSecret)
print('Auth Success')

api = tweepy.API(oauth)
playerDB = players.get_players()

previousTweets = [mytweet.in_reply_to_status_id for mytweet in api.user_timeline(count=50)]
for tweet in api.mentions_timeline():
    if tweet.id not in previousTweets:
        for pl in playerDB:
            if pl['full_name'].lower() in tweet.text.lower():
                name = pl['full_name']
                print(f"Identified {name}")
                nameMin = playerstatsDF.loc[playerstatsDF['PLAYER_NAME'] == name,
                                            'MIN'].values[0].round(1) 
                nameMinRank = playerstatsDF.loc[playerstatsDF['PLAYER_NAME'] == name, 'MIN_RANK'].values[0]
                try:
                    api.update_status(f"{name} played {nameMin} total minutes this season, "
                                      f"which is rank {nameMinRank} out of all players this season!",
                                  in_reply_to_status_id=tweet.id,auto_populate_reply_metadata=True)
                    print(f"Successfully tweeted for {name}")
                except Exception as e:
                    print(e)
