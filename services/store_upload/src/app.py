import logging
import os

from random import choice
from time import sleep

import redis

# ------------------------------------------------------

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_DB = int(os.environ.get('REDIS_DB', '1'))

logger = logging.getLogger(__name__)
logging.basicConfig(level = os.environ.get('LOGLEVEL', 'INFO'))

# ------------------------------------------------------

stores = [x for x in range(13000)]

# ------------------------------------------------------
# Main

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    while True:
        logger.info('Sending updates')
        for i in range(300):
            store = choice(stores)
            logger.debug(f'Posting {store}')
            r.set(store, '<menu>')
            r.publish('foe', store)

        sleep(1)


if __name__ == '__main__':
    main()
