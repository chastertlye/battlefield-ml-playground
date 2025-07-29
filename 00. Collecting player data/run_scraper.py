from scraper import get_all_servers, players_from_servers, update_dataset
import logging as log
import argparse
import time
log.basicConfig(level=log.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Battlefield 4 Player Stats Scraper")
    parser.add_argument(
        "--o", 
        type=str, 
        default="dataset.csv", 
        help="Path to the output CSV file for player statistics."
    )
    parser.add_argument(
        "--d", 
        type=float, 
        default=0.5, 
        help="Delay in seconds between API requests to avoid rate limiting."
    )
    parser.add_argument(
        "--i",
        type=int,
        default=10, 
        help="Interval in seconds between full scraping cycles."
    )
    args = parser.parse_args()

    while True:
        log.info("Starting Battlefield 4 player stats scraping process.")

        # Step 1: Get all active servers
        servers_data = get_all_servers(delay=args.d)
        if not servers_data:
            log.error("Failed to retrieve server data. Skipping this cycle.")
            time.sleep(args.i) 
            continue
        player_names = players_from_servers(servers_data)
        if not player_names:
            log.warning("No players found on active servers. Skipping this cycle.")
            time.sleep(args.i)
            continue
        log.info(f"Found {len(player_names)} unique players currently online.")

        log.info(f"Updating player stats dataset: {args.o}")
        update_dataset(args.o, player_names, delay=args.d)

        log.info(f"Scraping process completed. Waiting {args.i} seconds for next cycle...")
        time.sleep(args.i) # Wait for the specified interval

if __name__ == "__main__":
    main()