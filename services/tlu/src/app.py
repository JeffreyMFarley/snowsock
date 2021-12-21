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
# Main

def main():
    # Connect to redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    # Set up the threads
    with mp.Manager() as manager:
        stores = manager.dict()

        proc_monitor = mp.Process(target=monitor, args=(r, stores))
        proc_monitor.start()

        while True:
            heap = []
            snapshot = list(stores.items())
            for store,stamp in snapshot:
                heapq.heappush(heap, (stamp, store))
            slowest = heapq.nsmallest(10, heap)

            watch = []

            now = datetime.utcnow()
            for stamp, store in slowest:
                lu = datetime.utcfromtimestamp(stamp)
                delta = now - lu
                watch.append(f'\t{store:>6s}: {delta.total_seconds():3.2f} seconds old')

            logger.info('\n'.join(watch))
            sleep(15)

        proc_monitor.join()


if __name__ == '__main__':
    main()
