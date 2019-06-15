# beautyshoppe-invoicer
Python app to monitor raised Nexudus invoices and automatically charge them using USAePay ACH withdrawal.

## Installation
1. Rename (or copy) `.env_example` to `.env` and fill in the desired MySQL credentials
2. Rename (or copy) `src/config-example.py` to `src/config.py` and fill in all of the required fields. Detailed documentation can be found in the example file. Note that any changes to the `src/config.py` file require an app restart.
3. In the root folder: `docker-compose build && docker-compose up`
4. Navigate to localhost:5000 or wherever you have chosen to host the web app. Port numbers can be changed in `docker-compose.yml`.

## Usage
Upon startup, the app will spawn automatic jobs in the background to start processing invoices. By default, the invoice processing job runs every 1000 seconds. This is arbitrary and can be changed with the `SECONDS_BETWEEN_JOBS` constant in `src/config.py`. By default, the job will not run as soon as the app starts; it will wait for the entire interval and *then* run for the first time.

Once you navigate to the app main page, log in with the manager account. This must match the `NEXUDUS_EMAIL` and `NEXUDUS_PASS` credentials in `src/config.py`.

Then, click the "Process Invoices" button to sync the member and invoice tables. This may take a while; the speed is highly dependent on the number of Nexudus users managed by this account. For each space defined in `NEXUDUS_SPACE_USAEPAY_MAP` (in the config file), the invoice processing system will proceed through 5 steps:

#### Sync member table
Queries Nexudus for this space's members, and loads them into the local Member table. Each member has a "Process Automatically" flag, which controls whether this system will pay attention to their unpaid invoices. By default, this is set to False for all newly-loaded members. If the `PROCESS_AUTOMATICALLY` constant is set to `True` in the configuration file, each member's "Process Automatically" flag will be set to True **if** there is ACH data in their Routing Number and Account Number fields in their Nexudus member profile. 

To modify a member's Process Automatically field:
* Navigate to the Member page
* Click the pencil icon next to a member row (You can filter the table using the "Add filter" button)
* Click the big checkbox to the right of "Process Automatically" on the edit page.

#### Sync invoice table
Queries Nexudus for this space's unpaid invoices, and loads them into the local Invoice table **if** the corresponding member has Process Automatically set to True.

#### Charge unpaid invoices
For each of this space's invoices in the Invoice table, generates a USAePay charge if the corresponding user:
* has Process Automatically set to True
* has data in their Routing Number field in Nexudus
* has data in their Account Number field in Nexudus

The USAePay charge attempt will return a Result, which is stored in the local Invoice table. Result codes can be found [here](https://help.usaepay.info/developer/reference/transactioncodes/), but the full result string is also stored in the Invoice table for easy reference.

#### Check for settled transactions
After USAePay approves a charge, it takes up to a full business day to settle the transaction. So, for each "Approved" invoice, the system checks if the corresponding USAePay transaction has been settled, and marks the status in the Invoice table. Status codes can also be found on the [same USAePay reference page.](https://help.usaepay.info/developer/reference/transactioncodes/)

#### Inform Nexudus of settled transactions
For each of this space's "Settled" invoices, generates a ledger charge in Nexudus to mark the invoice as Paid. If this process is sucessful, we mark the Invoice as "Finalized" in our local table.

## Reports and information gathering
By default, the system's logger is set to `INFO` level, meaning that any messages that have an `INFO` or worse severity level will be retained in the database. This behavior can be changed in `src/config.py` using the `LOGLEVEL` constant.

To generate a CSV report, navigate to the Reports page and choose two dates, then click "Submit". A CSV download will then be sent, containing every log item generated between those two dates.

Alternatively, you can view logs by navigating to the Log page and filtering as-needed. It may be useful to click "Add filter", filter by log level, and find logs at WARNING, ERROR, or CRITICAL levels.
