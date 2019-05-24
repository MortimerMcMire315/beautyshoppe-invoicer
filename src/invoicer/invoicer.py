'''
This file is part of nexudus-usaepay-gateway.

nexudus-usaepay-gateway is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

nexudus-usaepay-gateway is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along
with nexudus-usaepay-gateway.  If not, see
<https://www.gnu.org/licenses/>.
'''

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
