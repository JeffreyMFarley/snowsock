import logging
import os

from random import choice
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

# ------------------------------------------------------
# Main

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    while True:
        logger.debug('Sending updates')
        for i in range(OPT_STORES_PER_UPDATE):
            store = choice(stores)
            logger.debug(f'Posting {store}')
            r.set(store, '<menu>')
            if OPT_PUBLISH is not None:
                r.publish('foe', store)

        sleep(OPT_SLEEP_SECONDS)


if __name__ == '__main__':
    main()
