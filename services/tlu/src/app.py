import heapq
import logging
import multiprocessing as mp
import os

from datetime import datetime, timedelta
from time import sleep

import redis

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_DB = int(os.environ.get('REDIS_DB', '1'))
OPT_MISSING_THRESHOLD = int(os.environ.get('OPT_MISSING_THRESHOLD', '120'))

logger = logging.getLogger(__name__)
logging.basicConfig(level = os.environ.get('LOGLEVEL', 'INFO'))

# ------------------------------------------------------

def parse_command(s):
    return s.split()


# ------------------------------------------------------
# Listen thread

def monitor(redis_conn, stores):
    with redis_conn.monitor() as m:
        for command in m.listen():
            logger.debug(f'{command}')
            parts = parse_command(command['command'])
            if parts[0] == 'SET':
                logger.debug(f'Updating store {parts[1]}')
                stores[parts[1]] = command['time']


# ------------------------------------------------------
# Maintain missing thread

def run_check(stores, missing):
    while True:
        sleep(OPT_MISSING_THRESHOLD >> 2)

        now = datetime.utcnow()

        # Build a priority heap of the stores
        heap = []
        snapshot = list(stores.items())
        for store,stamp in snapshot:
            heapq.heappush(heap, (stamp, store))
            if store in missing:
                if missing[store] < stamp:
                    logger.info(f'Store {store} updated. Removing from missing')
                    del missing[store]

        # Get the ten least updated
        slowest = heapq.nsmallest(100, heap)

        # Check if they are past the threshhold
        for stamp, store in slowest:
            lu = datetime.utcfromtimestamp(stamp)
            delta = now - lu
            if delta.total_seconds() >= OPT_MISSING_THRESHOLD:
                missing[store] = stamp

# ------------------------------------------------------
# Main

def main():
    # Connect to redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    # Set up the threads
    with mp.Manager() as manager:
        stores = manager.dict()
        for i in range(13000):
            stores[str(i)] = datetime.utcnow().timestamp()

        proc_monitor = mp.Process(target=monitor, args=(r, stores))
        proc_monitor.start()

        missing = manager.dict()
        
        proc_missing = mp.Process(target=run_check, args=(stores, missing))
        proc_missing.start()

        while True:
            sleep(60)

            # Warn about missing stores
            if len(missing):
                now = datetime.utcnow()

                for store, stamp in missing.copy().items():
                    lu = datetime.utcfromtimestamp(stamp)
                    delta = now - lu
                    secs = delta.total_seconds()
                    logger.warning(f'Store {store} has not responded in {secs:3.1f} seconds')

        proc_monitor.join()
        proc_missing.join()


if __name__ == '__main__':
    main()
