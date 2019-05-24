import logging

from . import nexudus
from ..db import conn, models

def run(initial=False):
    '''
    Entry point for invoice processing.
    Establishes a connection to Nexudus and processes any new invoices.

    :param sm: Database sessionmaker
    :param initial: True if this is the first run of the job upon
                    starting up the app.
    '''

    # Get logger and tell it we're doing something
    logger = logging.getLogger('invoicer')
    logger.debug("Running...")

    # Connect to Nexudus
    sm = conn.get_db_sessionmaker()
    nexudus.sync_member_table(sm)
    nexudus.sync_invoice_table(sm)

def charge_payment(Invoice):
    pass
