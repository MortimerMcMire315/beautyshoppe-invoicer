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
from requests.exceptions import HTTPError
from sqlalchemy import or_, and_

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
    check_txn_statuses(sm)
    finalize_invoices(sm)

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
    # status AND the member has account/routing information.
    unsent_invoices = db_sess.query(Invoice).\
        filter(
            Invoice.member.has(process_automatically=True)
        ).\
        filter(
            and_(
                Invoice.member.has(Member.account_number != None),
                Invoice.member.has(Member.account_number != ''),
                Invoice.member.has(Member.routing_number != None),
                Invoice.member.has(Member.routing_number != '')
            )
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

        charge_single_invoice(invoice, db_sess)


def check_txn_statuses(sm):
    """
    Check if any "Approved" invoices have been submitted to the bank.

    :param sm: SQLAlchemy sessionmaker object
    """

    db_sess = sm()
    logger = logging.getLogger('invoicer_ajax')

    approved_invoices = db_sess.query(Invoice).\
        filter(Invoice.member.has(process_automatically=True)).\
        filter_by(txn_resultcode=usaepay.RESULT_APPROVED).\
        filter(Invoice.txn_statuscode != usaepay.STATUS_SETTLED).\
        all()

    logger.info(">>> Checking for settled transactions...")

    for invoice in approved_invoices:
        mark_transaction_status(invoice, db_sess)


def log_transaction_exception(result_code, result):
    """
    Mark transaction status and log the error.
    TODO
    """
    print(result)


def charge_single_invoice(invoice, db_sess):
    """

    :param invoice: models.Invoice object
    :param db_sess: SQLAlchemy database session object
    """
    res = usaepay.create_transaction(invoice)
    logger = logging.getLogger('invoicer_ajax')

    try:
        if res["result_code"] != usaepay.APPROVED:
            log_transaction_exception(res["result_code"], res["error"])

        invoice.txn_key = res["key"]
        invoice.txn_resultcode = usaepay.APPROVED
        invoice.txn_result = "Approved"

    except KeyError as e:
        logger.error("Key %s not found in USAePay response!" % str(e))

    except HTTPError as e:
        logger.error("CRITICAL: Request to USAePay failed. Message: " + str(e))


def finalize_invoice(invoice, db_sess):
    """
    Inform Nexudus that one invoice has been paid.

    If successful, mark the invoice as finalized in our database.

    :param invoice: models.Invoice object
    :param db_sess: SQLAlchemy database session object
    """
    logger = logging.getLogger('invoicer_ajax')
    result, msg = nexudus.mark_invoice_paid(invoice.nexudus_invoice_id)

    if result:
        invoice.finalized = True
        db_sess.commit()
        logger.error("    Successfully updated invoice %s in Nexudus." %
                     invoice.nexudus_invoice_id)
    else:
        logger.error("    Could not mark invoice %s paid in Nexudus! Error: %s" %
                     (invoice.nexudus_invoice_id, msg))


def finalize_invoices(sm):
    """
    Inform Nexudus of all settled invoices.

    :param sm: SQLAlchemy sessionmaker object
    """
    logger = logging.getLogger('invoicer_ajax')
    logger.info(">>> Submitting paid invoices to USAePay...")

    db_sess = sm()

    # Get all settled, unfinalized invoices.
    settled_unfinalized_invoices = db_sess.query(Invoice).\
        filter_by(txn_statuscode=usaepay.STATUS_SETTLED).\
        filter_by(finalized=False).\
        all()

    for invoice in settled_unfinalized_invoices:
        finalize_invoice(invoice, db_sess)


def mark_transaction_status(invoice, db_sess):
    """

    :param invoice: models.Invoice object
    :param db_sess: SQLAlchemy database session object
    """
    logger = logging.getLogger('invoicer_ajax')
    try:
        # TODO run USAePay check
        logger.info(
            "    Checking transaction status for " +
            str(invoice.member) +
            " (Invoice ID " + str(invoice.nexudus_invoice_id) + ")"
            "..."
        )
        status_dict = usaepay.get_transaction_status(invoice.txn_key)
        invoice.txn_statuscode = status_dict["status_code"]
        invoice.txn_status = status_dict["status"]

        logger.info(
            "    USAePay Transaction "
            + str(invoice.txn_key)
            + ": "
            + str(invoice.txn_status)
        )

        db_sess.commit()

    except KeyError as e:
        logger.error("Key %s not found in USAePay response!" % str(e))

    except HTTPError as e:
        logger.error("CRITICAL: Request to USAePay failed. Message: " + str(e))
