import requests
import logging as log
import time
import pandas as pd
import os
from Сonfiguration import (
    PLAYER_BASE_STATS,
    WEAPON_TYPES,
    VEHICLE_TYPES,
    VEHICLE_MAP,
    BFLIST_BASE,
    GAMETOOLS_BASE
)

log.basicConfig(level=log.INFO, format="%(levelname)s [%(asctime)s]: %(message)s")


def get_livestats():
    """Fetches live statistics about the number of active servers and players currently online"""

    try:
        response = requests.get(BFLIST_BASE + "livestats").json()
        log.info(
            f'Succesfully fetched livestats: {response["servers"]} servers and {response["players"]} players active'
        )
        return response["servers"], response["players"]
    except Exception as e:
        log.error(f"Error occured while fetching livestats: {e}")
        return None, None


def get_all_servers(delay: float = 0.5):
    """Retrieves data for all currently active Battlefield 4 servers"""
    
    total_servers, _ = get_livestats()
    data = {"servers": []}
    hasMore = True
    cursor = None
    after = None
    currently_fetched = 0
    try:
        while hasMore:
            payload = {}

            if cursor and after:
                payload = {"cursor": cursor, "after": after}
            response = requests.get(BFLIST_BASE + "servers", params=payload).json()
            currently_fetched += len(response["servers"])

            cursor = response["cursor"]
            hasMore = response["hasMore"]
            last_ip, last_port = (
                response["servers"][-1]["ip"],
                response["servers"][-1]["port"],
            )
            after = f"{last_ip}:{last_port}"

            log.info(f"Succesfully fetched {currently_fetched}/{total_servers} servers")
            
            # Remove servers with no players
            for server in response["servers"]:
                if len(server["players"]) == 0:
                    response["servers"].remove(server)
            data["servers"].extend(response["servers"])

            time.sleep(delay)

        return data
    except Exception as e:
        log.error(f"Error occured while fetching servers: {e}")
        return None


def players_from_servers(data: map):
    """Extracts unique player names from a list of servers"""
    
    players = []
    try:
        for server in data["servers"]:
            for player in server["players"]:
                name = player["name"]
                players.append(name)
        return list(set(players))  # Return only unique names
    except Exception as e:
        log.error(f"Error occured while proceeding players: {e}")
        return None


def get_player_stats(name: str):
    """Retrieves detailed stats for a given player by name"""
    try:
        response = requests.get(
            GAMETOOLS_BASE + "all", params={"name": name, "format_values": False}
        ).json()
        
        # Extract base player stats
        player_stats = {k: response[k] for k in PLAYER_BASE_STATS}
        weapon_stats = {
            k: {"kills": 0, "time": 0.0, "headShots": 0} for k in WEAPON_TYPES
        }

        # Aggregate weapon stats
        for w in response["weapons"]:
            type = w["type"]
            weapon_stats[type]["kills"] += w["kills"]
            weapon_stats[type]["time"] += (
                round(w["kills"] / w["killsPerMinute"] * 60)
                if w["killsPerMinute"] != 0
                else 0
            )
            weapon_stats[type]["headShots"] += round(
                (w["headshots"] / 100) * w["kills"]
            )

        # Calculate weapon metrics
        for type in weapon_stats:
            w = weapon_stats[type]
            killsPerMinute = round(w["kills"] / w["time"], 2) if w["time"] != 0 else 0
            headShotKillRate = (
                round(w["headShots"] / w["kills"], 2) if w["kills"] != 0 else 0
            )
            weapon_stats[type].update(
                {"killsPerMinute": killsPerMinute, "headShotKillRate": headShotKillRate}
            )

        # Flatten weapon stats into single-level dict
        weapons_flat = {
            f"{type_key} {k}": v
            for type_key, type_dict in weapon_stats.items()
            for k, v in type_dict.items()
        }
        
        player_stats.update(weapons_flat)

        # Aggregate vehicle stats
        vehicle_stats = {
            k: {"kills": 0, "time": 0, "destroyed": 0} for k in VEHICLE_TYPES
        }

        for v in response["vehicles"]:
            type = v["type"]
            if type in VEHICLE_MAP:
                type = VEHICLE_MAP[type]
            vehicle_stats[type]["kills"] += v["kills"]
            vehicle_stats[type]["destroyed"] += v["destroyed"]
            vehicle_stats[type]["time"] += v["timeIn"]

        # Calculate vehicle metrics
        for type in vehicle_stats:
            v = vehicle_stats[type]
            killsPerMinute = (
                round(v["kills"] / v["time"] * 60, 2) if v["time"] != 0 else 0
            )
            vehicle_stats[type].update({"killsPerMinute": killsPerMinute})
            
        # Flatten vehicle stats into single-level dict
        vehicles_flat = {
            f"{type_key} {k}": v
            for type_key, type_dict in vehicle_stats.items()
            for k, v in type_dict.items()
        }
        
        player_stats.update(vehicles_flat)
        return player_stats

    except Exception as e:
        log.error(f"Error occured while fetching {name}'s stats: {e}")


def update_dataset(dataset_title: str, names: list):
    """Updates a CSV dataset with new player stats. Avoids duplicates based on username or player ID."""
    exists = os.path.isfile(dataset_title)
    if exists:
        stats_df = pd.read_csv(dataset_title)

    names = list(set(names))
    new_names = []
    for name in names:
        if exists:
            if name in stats_df["userName"].values:
                continue
            stats = get_player_stats(name)
            if stats["id"] in stats_df["id"].values:
                continue
        else:
            stats = get_player_stats(name)
        new_names.append(stats)
    if new_names:
        new_names_df = pd.DataFrame(new_names)
        new_names_df.to_csv(dataset_title, mode="a", index=False, header=not exists)
