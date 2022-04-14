#Originally written in PyCharm. Class object created to facilitate the adding and updating of NBA stats data (both from CSVs and from nba_api package endpoints)
#to the AWS RDS via mySQL connection. Currently, the only table that is stored and maintained in the database is 2021-22 season player statistics
#from the LeagueDashPlayerStats NBA API endpoint. In the future, I will likely work to incorporate other tables related to player statistics, and perhaps even
#expand to team, game, and lineup data. 

import pymysql
import sqlalchemy
import pandas as pd
from nba_api.stats import endpoints as ep


class NBAStatsToSQL:
    def __init__(self):
        self.user = "zhijaouy"
        self.pw = " " #Removed for privacy purposes
        self.host ="nbastatsaws1.cx08ymmfb8n8.us-east-1.rds.amazonaws.com" #mySQL Server Address
        self.dbSchema = "nbastats"
        self.masterTables = ["leaguedashplayerstats"] #Tables by which important identifiers such as PLAYER_ID originate from
        self.engine = sqlalchemy.create_engine(f"mysql+pymysql://"f"{self.user}:{self.pw}@{self.host}/{self.dbSchema}")

    def uploadEndpoint(self,endpoint):
        epFunction = f"ep.{endpoint.lower()}.{endpoint}().get_data_frames()[0]"
        epCall = eval(endpointFunction)
        epCall.to_sql(endpoint.lower(), self.engine, index=False)
        if endpoint.lower() not in self.masterTables:
                self.engine.execute(f'ALTER TABLE `{endpoint.lower()}` ADD PRIMARY KEY (`PLAYER_ID`);')
                self.engine.execute(f'ALTER TABLE `{endpoint.lower()}` ADD FOREIGN KEY (`PLAYER_ID`) \
                   REFERENCES leaguedashplayerstats(`PLAYER_ID`);')
                
    def updateEndpoint(self,endpoint):
            epFunction = f"ep.{endpoint.lower()}.{endpoint}().get_data_frames()[0]"
            epCall = eval(epFunction)
            self.engine.execute(f'DROP TABLE `{endpoint.lower()}`;')
            epCall.to_sql(endpoint.lower(), self.engine, index=False)
            if endpoint.lower() not in self.masterTables:
                self.engine.execute(f'ALTER TABLE `{endpoint.lower()}` ADD PRIMARY KEY (`PLAYER_ID`);')
                self.engine.execute(f'ALTER TABLE `{endpoint.lower()}` ADD FOREIGN KEY (`PLAYER_ID`) \
                   REFERENCES leaguedashplayerstats(`PLAYER_ID`);') 

    def uploadCSV(self,url):
        tableName = url.split('/')[-1][:-4]
        readingCSV = pd.read_csv(url,index_col=0)
        readingCSV.to_sql(tableName,self.engine,index=False)
        #Verify that the CSV has a PLAYER_ID column to ensure referential integrity 
        self.engine.execute(f'ALTER TABLE `{endpoint.lower()}` ADD PRIMARY KEY (`PLAYER_ID`);')
               self.engine.execute(f'ALTER TABLE `{endpoint.lower()}` ADD FOREIGN KEY (`PLAYER_ID`) \
                  REFERENCES leaguedashplayerstats(`PLAYER_ID`);') 

    def updateCSV(self,url):
        tableName = url.split('/')[-1][:-4]
        readingCSV = pd.read_csv(url, index_col=0)
        self.engine.execute(f'DROP TABLE `{tableName}`;')
        readingCSV.to_sql(tableName, self.engine, index=False)
        self.engine.execute(f'ALTER TABLE `{endpoint.lower()}` ADD PRIMARY KEY (`PLAYER_ID`);')
               self.engine.execute(f'ALTER TABLE `{endpoint.lower()}` ADD FOREIGN KEY (`PLAYER_ID`) \
                  REFERENCES leaguedashplayerstats(`PLAYER_ID`);') 

NBAStatsToSQL().updateEndpoint('LeagueDashPlayerStats')
