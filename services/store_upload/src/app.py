import logging
import os

from random import choice, randint
from time import sleep

import redis

# ------------------------------------------------------

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_DB = int(os.environ.get('REDIS_DB', '1'))
OPT_PUBLISH = os.environ.get('OPT_PUBLISH', None)
OPT_STORES_PER_UPDATE = int(os.environ.get('OPT_STORES_PER_UPDATE', '25'))
OPT_SLEEP_SECONDS = float(os.environ.get('OPT_SLEEP_SECONDS', '1'))

logger = logging.getLogger(__name__)
logging.basicConfig(level = os.environ.get('LOGLEVEL', 'INFO'))

# ------------------------------------------------------

stores = [x for x in range(13000)]

# Remove some stores
logger.info('Removing stores from the list')
for _ in range(10):
    idx = randint(0, len(stores))
    out_of_order = stores.pop(idx)
    logger.info(f'\t{out_of_order}')

# ------------------------------------------------------
# Main

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    updates = 0
    show_update_every = OPT_STORES_PER_UPDATE * 100

    while True:
        for i in range(OPT_STORES_PER_UPDATE):
            store = choice(stores)
            logger.debug(f'Posting {store}')
            r.set(store, '<menu>')
            if OPT_PUBLISH is not None:
                r.publish('foe', store)

            updates += 1
            if (updates % show_update_every) == 0:
                logger.info(f'Sent {updates:>8,d} updates')

        sleep(OPT_SLEEP_SECONDS)


if __name__ == '__main__':
    main()
