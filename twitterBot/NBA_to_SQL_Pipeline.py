'''Class object created to facilitate the adding and updating of NBA stats data (both from CSVs and from nba_api package endpoints)
to the AWS RDS via mySQL connection. Currently, the only table that is stored and maintained in the database is 2021-22 season player statistics
from the LeagueDashPlayerStats NBA API endpoint. However, other tables can be incorporated, such as data tables related to player statistics, and perhaps even
expand to team, game, and lineup data. Running the file updates the LeagueDashPlayerStats table.'''

import pymysql
import sqlalchemy
from sqlalchemy.engine import Engine
import pandas as pd
from nba_api.stats import endpoints as ep
from typing import List, Dict
import configparser

class NBAStatsToSQL:
    def __init__(self, user: str, password: str, host: str, dbschema: str) -> None:
        """Initialize the NBAStatsToSQL object with database credentials and setup the engine."""
        self.user = user
        self.pw = password
        self.host = host
        self.dbSchema = dbschema
        self.masterTables = ['leaguedashplayerstats']
        self.engine = sqlalchemy.create_engine(f"mysql+pymysql://{self.user}:{self.pw}@{self.host}/{self.dbSchema}")

    def _setup_keys(self, table_name: str) -> None:
        """Sets up primary and foreign keys for the table if it's not a master table."""
        if table_name not in self.masterTables:
            self.engine.execute(f'ALTER TABLE `{table_name}` ADD PRIMARY KEY (`PLAYER_ID`);')
            self.engine.execute(f'ALTER TABLE `{table_name}` ADD FOREIGN KEY (`PLAYER_ID`) \
                                 REFERENCES leaguedashplayerstats(`PLAYER_ID`);') 

    def uploadEndpoint(self, endpoint: str) -> None:
        """Fetch data for a given NBA API endpoint and upload it to a corresponding SQL table."""
        epFunction = f"ep.{endpoint.lower()}.{endpoint}().get_data_frames()[0]"
        epCall = eval(epFunction)
        epCall.to_sql(endpoint.lower(), self.engine, index=False)
        self._setup_keys(endpoint.lower())

    def updateEndpoint(self, endpoint: str) -> None:
        """Update data in the table for a given NBA API endpoint."""
        epFunction = f"ep.{endpoint.lower()}.{endpoint}().get_data_frames()[0]"
        epCall = eval(epFunction)
        self.engine.execute(f'DROP TABLE `{endpoint.lower()}`;')
        epCall.to_sql(endpoint.lower(), self.engine, index=False)
        self._setup_keys(endpoint.lower())

    def uploadCSV(self, url: str) -> None:
        """Upload NBA stats data from a CSV file to a corresponding SQL table."""
        tableName = url.split('/')[-1][:-4].lower()
        readingCSV = pd.read_csv(url, index_col=0)
        readingCSV.to_sql(tableName, self.engine, index=False)
        self._setup_keys(tableName)

    def updateCSV(self, url: str) -> None:
        """Update data in an pre-existing SQL table from a CSV file."""
        tableName = url.split('/')[-1][:-4].lower()
        readingCSV = pd.read_csv(url, index_col=0)
        self.engine.execute(f'DROP TABLE `{tableName}`;')
        readingCSV.to_sql(tableName, self.engine, index=False)
        self._setup_keys(tableName)

def main():
    #Load configs
    config = configparser.ConfigParser()
    config.read('config.ini')

    #Login to DB, initialize instance
    user = config['Database']['USER']
    password = config['Database']['PASSWORD']
    host = config['Database']['HOST']
    db_schema = config['Database']['SCHEMA']
    db_instance = NBAStatsToSQL(user, password, host, db_schema)

    #Update endpoint
    db_instance.updateEndpoint('LeagueDashPlayerStats')

if __name__ == '__main__':
    main()

    
