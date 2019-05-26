"""
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
"""

import logging
import sys

from . import nexudus
from . import usaepay
from ..db import conn, models
from ..db.models import Invoice, Member


def run(initial=False):
    """
    Establish a connection to Nexudus and processes any new invoices.

    :param initial: True if this is the first run of the job upon
                    starting up the app.
    """
    # Get logger and tell it we're doing something
    logger = logging.getLogger('invoicer')
    logger.debug("Running...")

    # Connect to Nexudus
    sm = conn.get_db_sessionmaker()

    # TODO clean up members that are no longer active first
    # nexudus.sync_member_table(sm)

    # # TODO clean up invoices that have been paid first
    # nexudus.sync_invoice_table(sm)
    charge_unpaid_invoices(sm)


def charge_unpaid_invoices(sm):
    """
    Run the invoices in our database through USAePay.

    :param sm: SQLAlchemy sessionmaker obj
    """
    db_sess = sm()

    unpaid_invoices = db_sess.query(Invoice).\
        filter(Invoice.member.has(process_automatically=True)).all()

    for invoice in unpaid_invoices:
        print(invoice.member.fullname)
        sys.stdout.flush()
        usaepay.create_charge(invoice)
