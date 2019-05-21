import logging
import sys

import requests
import json

from .. import config

def run(initial=False, callback=None):
    """
    Entry point for invoice processing.
    Establishes a connection to Nexudus and processes any new invoices.

    :param initial: Set to True if this is the first run of the job upon
                    starting up the app.
    :param callback: Callback function TODO
    """

    # Get logger and tell it we're doing something
    logger = logging.getLogger('invoicer')
    logger.debug("Running...")

    # Connect to Nexudus
    nexudus_get_invoice_list()

def nexudus_get_invoice_list():
    url = 'https://spaces.nexudus.com/api/billing/coworkerinvoices?CoworkerInvoice_Paid=false'
    creds = (config.NEXUDUS_EMAIL, config.NEXUDUS_PASS)

    r = requests.get(url, auth=creds)

    print(r.json())
