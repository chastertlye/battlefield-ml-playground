import requests
import logging as log
import time
import pandas as pd
import os
from Configuration import (
    PLAYER_BASE_STATS,
    WEAPON_TYPES,
    VEHICLE_TYPES,
    VEHICLE_MAP,
    BFLIST_BASE,
    GAMETOOLS_BASE,
)

log.basicConfig(level=log.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")


def get_livestats():
    """Fetches live statistics about the number of active servers and players currently online"""

    try:
        response = requests.get(BFLIST_BASE + "livestats").json()
        log.info(
            f'Succesfully fetched livestats: {response["servers"]} servers and {response["players"]} players active'
        )
        return response["servers"], response["players"]
    except Exception as e:
        log.error(f"Error fetching livestats", exc_info=True)
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
            active_servers = [s for s in response["servers"] if len(s["players"]) > 0]
            data["servers"].extend(active_servers)

            time.sleep(delay)

        return data
    except Exception as e:
        log.error(f"Error fetching servers", exc_info=True)
        return None


def players_from_servers(data: dict):
    """Extracts unique player names from a list of servers"""

    players = []
    try:
        for server in data["servers"]:
            for player in server["players"]:
                name = player["name"]
                players.append(name)
        return list(set(players))  # Return only unique names
    except Exception as e:
        log.error(f"Error proceeding players", exc_info=True)
        return None


def flatten_map(d, sep=" "):
    """Flatten double-level dict into single-level dict"""
    
    d_flat = {
        f"{type_key}{sep}{k}": v
        for type_key, type_dict in d.items()
        for k, v in type_dict.items()
    }
    return d_flat


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
                w["kills"] / w["killsPerMinute"] * 60
                if w["killsPerMinute"] != 0
                else 0
            )
            weapon_stats[type]["headShots"] += round(
                (w["headshots"] / 100) * w["kills"]
            )

        # Calculate weapon metrics
        for weapon_type in weapon_stats:
            w = weapon_stats[weapon_type]
            killsPerMinute = round(w["kills"] / w["time"], 2) if w["time"] != 0 else 0
            headShotKillRate = (
                round(w["headShots"] / w["kills"], 2) if w["kills"] != 0 else 0
            )
            weapon_stats[type].update(
                {"killsPerMinute": killsPerMinute, "headShotKillRate": headShotKillRate, "time": round(w["time"])}
            )
        weapons_flat = flatten_map(weapon_stats)
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
        for vehicle_type in vehicle_stats:
            v = vehicle_stats[type]
            killsPerMinute = (
                round(v["kills"] / v["time"] * 60, 2) if v["time"] != 0 else 0
            )
            vehicle_stats[vehicle_type].update({"killsPerMinute": killsPerMinute})
        vehicles_flat = flatten_map(vehicle_stats)
        player_stats.update(vehicles_flat)
        log.info(f"Successfully fetched {name}'s stats")
        return player_stats

    except Exception as e:
        log.error(f"Error fetching {name}'s stats", exc_info=True)


def update_dataset(dataset_title: str, names: list, delay : float = 0.5):
    """Updates a CSV dataset with new player stats."""
    
    exists = os.path.isfile(dataset_title)
    if exists:
        stats_df = pd.read_csv(dataset_title)
        existing_names = set(stats_df["userName"].values)
        existing_ids = set(stats_df["id"].values)

    names = list(set(names))
    new_names = []
    for name in names:
        if exists:
            if name in existing_names:
                continue
            stats = get_player_stats(name)
            if stats and stats["id"] in existing_ids:
                continue
        else:
            stats = get_player_stats(name)
        if stats:
            new_names.append(stats)
        time.sleep(delay)
            
    if new_names:
        new_names_df = pd.DataFrame(new_names)
        new_names_df.to_csv(dataset_title, mode="a", index=False, header=not exists)
        log.info(f"Added new {len(new_names)} players to dataset")
    else:
        log.warning(f"No players were added to dataset")