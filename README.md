# NBA-Stats 🏀

A collection of Python scripts that utilize [nba_stats](https://github.com/swar/nba_api), a package of APIs that connect to various endpoints on [NBA.com](https://www.nba.com/stats) and provide statistics and data on NBA players and teams. As an avid NBA fan, this project was a fun way to find interesting basketball insights and refine my Python skills.

## 📁 Folders & Files

### 1. `itp487`
- 📜 `nba_stats_adam.py`: Collaboration effort with USC's ITP487. Uses a class-outlined design framework to explore the relationship between player salary and impact in the 2021-2022 NBA season (through building linear regression models) and to see which player was the most cost-efficient for the season. Player salary data was retrieved from [HoopsHype.com](https://hoopshype.com/salaries/players/). 3 different values were used to quantify player impact for the season: total points scored, [RAPTOR](https://projects.fivethirtyeight.com/nba-player-ratings/) (538's now-defunct all-in-one advanced metric), and [LEBRON](https://www.bball-index.com/lebron-database/) (Basketball Index's all-in-one advanced metric). 

### 2. `nbaStatsAnalyses`
- 📜 `nba_career_ppg_visualizer.py`: Visualizes a given player's points-per-game averages across the seasons in his NBA career. 
- 📜 `nba_team_killers.py`: Analyzes whether a given player "kills" a given team, which means that the player scores highly against the team compared to his career average. For example, if Player A has a career PPG of 12, but has averaged 20 against the Lakers in his career, that player is considered a Lakers Killer. 
- 📜 `wingspan_and_defense.py`: Investigates the relationship between a player's wingspan (more specifically, wingspan-to-height ratio) and their defensive capabilities. 3 different stats are used to quantify defensive impact: deflections per minute, contests per minute, and defensive FG +/- (the difference 
between a player's defensive FG% and the expected defensive FG% on the shots contested). The script as
currently written uses DEFLECTIONS_PER_MIN. The wingspan data was sourced from [Crafted NBA](https://craftednba.com/player-traits/length), while the defensive stats were obtained by connecting to NBA API endpoints. Only weakly positive correlations were found between wingspan-to-height ratio and these defensive impact statistics.

### 3. `twitterBot`
- 📜 `NBA_Stat_Tweeter_Bot.py`: A now-defunct NBA stats Twitter-bot. This script accessed player stats data stored in an AWS RDS server via mySQL connection (see NBA_to_SQL_Pipeline.py), then scanned Twitter mention tweets for names of current NBA players, replying to those tweets with the respective values for the number of minutes played this season for the players that were identified. The code was uploaded on a crontab on an AWS EC2 instance, being executed every 10 min. For additional context, I was being blocked from accessing the API for live NBA statistics (e.g., points scored, minuted played) using a cloud-based remote EC2 instance. As such, the RDS database was used as a proxy for storing NBA statistical data. Not ideal, but this workaround was necessary to get the Twitter bot to run on a remote server.
- 📜 `NBA_to_SQL_Pipeline.py`: Creates class to facilitate the adding and updating of NBA stats data (both from CSVs and from nba_api package endpoints) to the AWS RDS via mySQL connection. Currently, the only table that is stored and maintained in the database is 2021-22 season player statistics from the LeagueDashPlayerStats NBA API endpoint. However, other tables can be incorporated, such as data tables related to player statistics, and perhaps even expand to team, game, and lineup data. Running the file updates the LeagueDashPlayerStats table.
