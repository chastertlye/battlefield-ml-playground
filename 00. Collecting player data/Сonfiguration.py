# Base URLs for the APIs used
BFLIST_BASE = "https://api.bflist.io/v2/bf4/"
GAMETOOLS_BASE = "https://api.gametools.network/bf4/"

# List of base player stats we want to extract
PLAYER_BASE_STATS = [
    "userName",
    "id",
    "rank",
    "scorePerMinute",
    "killsPerMinute",
    "killDeath",
    "quits",
    "accuracy",
    "headshots",
    "kills",
    "deaths",
    "wins",
    "loses",
    "avengerKills",
    "saviorKills",
    "headShots",
    "heals",
    "revives",
    "repairs",
    "resupplies",
    "killAssists",
    "skill",
    "longestHeadShot",
    "highestKillStreak",
]

# Weapon categories in Battlefield 4
WEAPON_TYPES = [
    "LMGs",
    "Shotguns",
    "Gadgets Explosives",
    "Hand Grenades",
    "Carbines",
    "Rocket Launchers",
    "PDWs",
    "DMRs",
    "Handguns",
    "Assault Rifles",
    "Underslung Launchers",
    "Sniper Rifles",
    "Special",
]

# Vehicle categories in Battlefield 4
VEHICLE_TYPES = [
    "Infantry Fighting Vehicle",
    "Stationary",
    "Soldier Equipment",
    "Air Helicopter Scout",
    "Transport",
    "Anti Air",
    "Mobile Artillery",
    "Main Battle Tanks",
    "Air Helicopter Attack",
    "Air",
    "Air Jet Stealth",
    "Air Jet Attack",
    "Fast Attack Craft",
]

# Some of vehicle types returned by API are really messy, so we need to fix them
VEHICLE_MAP = {
    "IFV LAV-25": "Infantry Fighting Vehicle",
    "Stationary ": "Stationary",
    "Soldier Equiment": "Soldier Equipment",
    "Air Helicopter Scout AH6": "Air Helicopter Scout",
    "Transport KA-60": "Transport",
    "AA 9K22 Tunguska": "Anti Air",
    "Air Helicopter Scout z11": "Air Helicopter Scout",
    "Jeep SPM3": "Transport",
    "Transport UH-1Y Venom": "Transport",
    "HIMARS": "Mobile Artillery",
    "Boat": "Transport",
    "AA LAV-AD": "Anti Air",
    "MBT T90": "Main Battle Tanks",
    "MBT M1 Abrams": "Main Battle Tanks",
    "Stationary AA": "Anti Air",
    "IFV BTR 90": "Infantry Fighting Vehicle",
} 