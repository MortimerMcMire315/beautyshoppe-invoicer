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

import flask
from sqlalchemy import or_

from . import nexudus
from . import usaepay
from ..db import conn, models
from ..db.models import Invoice, Member


def run():
    """
    Establish a connection to Nexudus and processes any new invoices.
    """
    # Get logger and tell it we're doing something
    ajax_logger = logging.getLogger('invoicer_ajax')
    ajax_logger.info("Running...")

    # db_logger = logging.getLogger('invoicer_db')
    # db_logger.info("Running...")

    # Connect to Nexudus
    sm = conn.get_db_sessionmaker()

    # TODO clean up members that are no longer active first
    # ajax_logger.info(">>> Syncing member table...")
    # nexudus.sync_member_table(sm)

    # TODO clean up invoices that have been paid first
    ajax_logger.info(">>> Getting unpaid invoices from Nexudus...")
    nexudus.sync_invoice_table(sm)
    charge_unpaid_invoices(sm)

    # TODO check approved, pending invoices for acceptance
    check_invoice_approvals(sm)


def charge_unpaid_invoices(sm):
    """
    Run unpaid invoices in our database through USAePay.

    An invoice is considered "unpaid" (aka due) if it is in our database, but
    has no txn_status. Any invoice that we've attempted to send to SQLAlchemy
    will have some txn_status.

    :param sm: SQLAlchemy sessionmaker object
    """
    db_sess = sm()
    logger = logging.getLogger('invoicer_ajax')

    # Only try to pay invoices if the corresponding Member is set to be
    # processed automatically AND the invoice does not yet have a transaction
    # status.
    unsent_invoices = db_sess.query(Invoice).\
        filter(
            Invoice.member.has(process_automatically=True)
        ).\
        filter(
            or_(
                Invoice.txn_resultcode == None,
                Invoice.txn_resultcode == ''
            )
        ).all()

    logger.info(">>> Checking for new transactions to send to USAePay...")

    if len(unsent_invoices) == 0:
        logger.info("    No new transactions sent.")

    for invoice in unsent_invoices:
        logger.info(
            "    Processing invoice for " + str(invoice.member) +
            "... Sending new transaction to USAePay"
        )

        res = usaepay.create_transaction(invoice)

        if res["result_code"] != usaepay.APPROVED:
            log_transaction_exception(res["result_code"], res["error"])
        else:
            print(res)
            mark_transaction_status(invoice, res, db_sess)


def check_invoice_approvals(sm):
    """
    Check if any "Approved" invoices have been submitted to the bank.

    :param sm: SQLAlchemy sessionmaker object
    """

    db_sess = sm()
    logger = logging.getLogger('invoicer_ajax')


    approved_invoices = db_sess.query(Invoice).\
        filter(Invoice.member.has(process_automatically=True)).\
        filter_by(txn_resultcode='A').all()

    if len(approved_invoices) != 0:
        logger.info(">>> Checking for settled transactions...")

    for invoice in approved_invoices:
        logger.info(
            "    Checking transaction status for " +
            str(invoice.member) +
            " (Invoice ID " + str(invoice.nexudus_invoice_id) + ")"
            "..."
        )
        logger.info(
            "    USAePay Transaction "
            + str(invoice.txn_key)
            + " pending."
        )

def log_transaction_exception(result_code, result):
    """
    Mark transaction status and log the error.
    """
    print(result)


def mark_transaction_status(invoice, res, db_sess):
    """

    :param invoice: models.Invoice object
    :param res: JSON response from usaepay.create_transaction call
    :param sm: SQLAlchemy sessionmaker object
    """

    invoice.txn_key = res["key"]
    invoice.txn_resultcode = usaepay.APPROVED
    status_dict = usaepay.get_transaction_status(invoice.txn_key)
    invoice.txn_statuscode = status_dict["status_code"]
    invoice.txn_status = status_dict["status"]

    db_sess.commit()
