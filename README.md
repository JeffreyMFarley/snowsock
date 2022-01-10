# Snowsock

Simulate watching a Redis cluster for stores not updating

## Prerequisites

1. Docker
2. New Relic License Key

## Installation

1. `git clone https://github.com/JeffreyMFarley/snowsock.git`
2. `cd snowsock/services`
3. `cp .env_example .env`
4. Use your favorite code editor to update `.env` with your New Relic license key

## Running

1. `cd snowsock/services`
3. `docker compose up`
    1. The three services will run
    1. `^C` to exit
4. `docker compose down`
