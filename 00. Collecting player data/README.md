# 00. Collecting Battlefield 4 Player Statistics
This project's main goal is to build a rich dataset of Battlefield 4 player statistics for analysis and machine learning experiments. It uses publicly available APIs to gather data from active servers, process it, and store it in a clean, structured format. The collected data is intended for data analysis and machine learning experiments. 

## Features
* **Automated Data Scraper:** Continuously fetches data from all active Battlefield 4 servers.
* **Comprehensive Stat Collection:** Gathers a wide range of player stats, from general performance metrics like K/D to detailed stats for weapon and vehicle categories
* **Well Organized Updates:** Efficiently adds new, unique players to the dataset without creating duplicates

## Usage
The data scraper is run from the command line using `run_scraper.py`. Customize its behavior with the following arguments:
* `--o`: Path to the output CSV file. Default: `dataset.csv`
* `--d`: Delay in seconds between individual API requests. Default: `0.5`
* `--i`: Interval in seconds between full scraping cycles. Set to 0 to run only once. Default: `0`

For example, to start scraping with a 1-second delay between requests and a 10-minute interval between cycles, saving the data to `stats.csv`:
```bash
python run_scraper.py --o stats.csv --d 1 --i 600
```
The script will run continuously, logging its progress to the console. You can stop it with `Ctrl+C`

## Data Collected
The scraper gathers a wide array of statistics, which are flattened into a single row per player in the final dataset.
* **General Player Stats**: `userName`, `id`, `rank`, `scorePerMinute`, `killsPerMinute`, `killDeath`, `quits`, `accuracy`, `headshots`, `kills`, `deaths`, `wins`, `loses`,`avengerKills`, `saviorKills`, `headShots`, `heals`, `revives`, `repairs`, `resupplies`, `killAssists`, `skill`, `longestHeadShot`, `highestKillStreak`.
* **Weapon Stats**: for each weapon category (`LMGs`, `Shotguns`, `Gadgets Explosives`, `Hand Grenades`, `Carbines`, `Rocket Launchers`, `PDWs`, `DMRs`, `Handguns`, `Assault Rifles`, `Underslung Launchers`, `Sniper Rifles`, `Special`), the following stats are aggregated:
    - `kills`
    - `time` (seconds used)
    - `killsPerMinute`
    - `headShots`
    - `headShotKillRate`
* **Vehicle Stats**: For each vehicle category (`Infantry Fighting Vehicle`, `Stationary`, `Soldier Equipment`, `Air Helicopter Scout`, `Transport`, `Anti Air`, `Mobile Artillery`, `Main Battle Tanks`, `Air Helicopter Attack`, `Air`, `Air Jet Stealth`, `Air Jet Attack`, `Fast Attack Craft`), the following stats are aggregated:
    - `kills`
    - `time` (seconds used)
    - `destroyed`
    - `killsPerMinute`
