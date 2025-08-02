from scraper import get_all_servers, players_from_servers, update_dataset
import logging as log
import argparse
import time
import sys
log.basicConfig(level=log.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# Constants for default argument values
DEFAULT_OUTPUT_FILE = "dataset.csv"
DEFAULT_REQUEST_DELAY = 0.0  # seconds
DEFAULT_SCRAPING_INTERVAL = 0  # seconds


def _run_cycle(output_file, delay):
    servers_data = get_all_servers(delay=delay)
    if not servers_data:
        return False
    player_names = players_from_servers(servers_data)
    log.info(f"Updating player stats dataset: {output_file}")
    update_dataset(output_file, player_names, delay=delay)
    return True


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
        help=f"Interval in seconds between full scraping cycles. Set to 0 to run only once. (default: {DEFAULT_SCRAPING_INTERVAL}s)",
    )
    args = parser.parse_args()
    try:
        if args.i > 0:
            log.info("Starting continuous scraping mode.")
            while True:
                success = _run_cycle(args.o, args.d)
                if success:
                    log.info(
                        f"Scraping process completed. Waiting {args.i} seconds until the next cycle..."
                    )
                    time.sleep(args.i)
                else:
                    log.error("Failed to retrieve server data. Skipping this cycle.")
        else:
            log.info("Starting single-run scraping mode.")
            success = _run_cycle(args.o, args.d)
            if success:
                log.info(f"Scraping process completed. Exiting.")
            else:
                log.error("Failed to retrieve server data. Exiting.")
    except KeyboardInterrupt:
        log.info("Interrupted by user. Shutting down.")
        sys.exit(0)

if __name__ == "__main__":
    main()