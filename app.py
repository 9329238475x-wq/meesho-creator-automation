from __future__ import annotations

import argparse
from database.db import init_db
from scheduler import run_daily_job, start_scheduler


def main() -> None:
    parser = argparse.ArgumentParser(description="Meesho Creator Automation")
    parser.add_argument("--run-once", action="store_true", help="Run the pipeline once immediately")
    args = parser.parse_args()

    init_db()
    if args.run_once:
        run_daily_job()
    else:
        start_scheduler()


if __name__ == "__main__":
    main()
