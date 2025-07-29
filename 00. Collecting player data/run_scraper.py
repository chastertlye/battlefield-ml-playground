from scraper import get_all_servers, players_from_servers, update_dataset
import logging as log
import argparse
import time

log.basicConfig(level=log.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# Constants for default argument values
DEFAULT_OUTPUT_FILE = "dataset.csv"
DEFAULT_REQUEST_DELAY = 0.5  # seconds
DEFAULT_SCRAPING_INTERVAL = 10  # seconds


def main():
    parser = argparse.ArgumentParser(description="Battlefield 4 Player Stats Scraper")
    parser.add_argument(
        "--o",
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        help=f"Path to the output CSV file for player statistics. (default: {DEFAULT_OUTPUT_FILE})",
    )
    parser.add_argument(
        "--d",
        type=float,
        default=DEFAULT_REQUEST_DELAY,
        help=f"Delay in seconds between API requests to avoid rate limiting. (default: {DEFAULT_REQUEST_DELAY}s)",
    )
    parser.add_argument(
        "--i",
        type=int,
        default=DEFAULT_SCRAPING_INTERVAL,
        help=f"Interval in seconds between full scraping cycles. (default: {DEFAULT_SCRAPING_INTERVAL}s)",
    )
    args = parser.parse_args()
    while True:
        log.info("Starting Battlefield 4 player stats scraping process.")
        servers_data = get_all_servers(delay=args.d)
        if not servers_data:
            log.error("Failed to retrieve server data. Skipping this cycle.")
            time.sleep(args.i)
            continue
        player_names = players_from_servers(servers_data)
        log.info(f"Updating player stats dataset: {args.o}")
        update_dataset(args.o, player_names, delay=args.d)
        log.info(
            f"Scraping process completed. Waiting {args.i} seconds until the next cycle..."
        )
        time.sleep(args.i)


if __name__ == "__main__":
    main()