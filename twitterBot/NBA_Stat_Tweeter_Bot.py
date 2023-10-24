'''
This file accesses player stats data stored in an AWS RDS server via mySQL 
connection (see NBA_to_SQL_Pipeline.py), then scans Twitter mention tweets for 
names of current NBA players, replying to those tweets with the respective values 
for the number of minutes played this season for the players that were identified. 
The code was uploaded on a crontab on an AWS EC2 instance, being executed every 10 min.
For additional context, I was being blocked from accessing the API for live NBA statistics 
(e.g., points scored, minuted played) using a cloud-based remote EC2 instance. As such, the
RDS database is used as a proxy for storing NBA statistical data. It's not ideal, but
this workaround was necessary to get the Twitter bot to function on a remote server.
'''

import pandas as pd
import tweepy
from nba_api.stats.static import players
from typing import List, Dict
import configparser
import logging
from NBA_to_SQL_Pipeline import NBAStatsToSQL

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def authenticate_twitter(apiKey: str, apiSecret: str, accessToken: str, accessSecret: str) -> tweepy.API:
    """Authenticate with the Twitter API and return the API instance."""
    try:
        oauth = tweepy.OAuthHandler(apiKey, apiSecret)
        oauth.set_access_token(accessToken, accessSecret)
        return tweepy.API(oauth)
    except Exception as e:
        logging.error(f"Twitter auth failure: {e}")
        return None  

def fetch_previous_tweet_replies(api: tweepy.API, count: int = 100) -> List[int]:
    """Get the list of tweets that the bot has previously replied to."""
    return [mytweet.in_reply_to_status_id for mytweet in api.user_timeline(count=count)]

def find_players_in_tweet(tweet_text: str, playerDB: List[Dict[str, str]]) -> List[str]:
    """Identify and return the NBA player's name mentioned in the tweet."""
    found_names = []
    for player in playerDB:
        if player['full_name'].lower() in tweet_text.lower():
            found_names.append(player['full_name'])
    return found_names

def fetch_player_stats(player_name: str, statsDF: pd.DataFrame) -> (float, int):
    """Fetch and return the minutes played and minutes rank of the player."""
    minutes = statsDF.loc[statsDF['PLAYER_NAME'] == player_name, 'MIN'].values[0].round(1) 
    rank = statsDF.loc[statsDF['PLAYER_NAME'] == player_name, 'MIN_RANK'].values[0]
    return minutes, rank

def reply_with_stats(api: tweepy.API, tweet_id: int, player_name: str, minutes: float, rank: int):
    """Reply to the tweet with the player's minutes statistics."""
    try:
        api.update_status(f"{player_name} played {minutes} total minutes this season, "
                          f"which is rank {rank} out of all players this season!",
                          in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
    except Exception as e:
        logging.error(f"Failed to tweet for {player_name}: {e}")


def main():
    #Load configs
    config = configparser.ConfigParser()
    config.read('config.ini')

    #Twitter API Authentication Setup
    api_key = config['Twitter']['API_KEY']
    api_secret = config['Twitter']['API_SECRET']
    access_token = config['Twitter']['ACCESS_TOKEN']
    access_secret = config['Twitter']['ACCESS_SECRET']
    twitter_api = authenticate_twitter(api_key,api_secret,access_token,access_secret)

    #Creating MySQL DB connection engine
    user = config['Database']['USER']
    password = config['Database']['PASSWORD']
    host = config['Database']['HOST']
    db_schema = config['Database']['SCHEMA']
    nba_stats_instance = NBAStatsToSQL(user, password, host, db_schema)
    engine = nba_stats_instance.engine

    #Define structures for NBA player data
    playerDB: List[Dict[str, str]] = players.get_players() #List of registered NBA players 
    playerstatsDF: pd.DataFrame = pd.read_sql("select * from leaguedashplayerstats", engine) #Live stats of NBA players

    already_replied = fetch_previous_tweet_replies(twitter_api)

    #Going through tweets that mention the bot, replying when appropriate
    for tweet in twitter_api.mentions_timeline():
        if tweet.id in already_replied: #Avoid responding to tweets we've already replied to
            continue
        else:
            found_player_names = find_players_in_tweet(tweet.text, playerDB)
            for player in found_player_names:
                mins_played, min_rank = fetch_player_stats(player, playerstatsDF)
                reply_with_stats(twitter_api, tweet.id, player, mins_played, min_rank)











if __name__ == '__main__':
    main()