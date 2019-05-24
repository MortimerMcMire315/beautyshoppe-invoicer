# nexudus-usaepay-gateway
Python app to monitor Nexudus invoices and submit ACH payments to USAePay

## Objective
Automate ACH payments by connecting the Nexudus invoice system to USAePay's ACH billing system.

## Installation
1. Rename `.env_example` to `.env` and fill in the desired MySQL credentials
2. Rename `src/config-example.py` to `src/config.py` and fill in all of the required fields
3. In the root folder: `docker-compose build && docker-compose up`
4. Navigate to localhost:5000
