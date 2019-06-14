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
from .. import config
from ..db import conn, models
from ..db.models import Invoice, Member

manually_initiated = False


def log_message(msg, level=logging.INFO):
    """
    Log something to the database and/or to the web frontend.

    :param msg: The string to log.
    :param level: debug, info, warning, error, critical
    """
    global manually_initiated


    if manually_initiated:
        ajax_logger = logging.getLogger('invoicer_ajax')
        ajax_logger.log(level, msg)


    # Always log to the DB. Strip out the visual markers first.
    strippedmessage = msg.replace('>>>', '').strip()
    db_logger = logging.getLogger('invoicer_db')
    db_logger.log(level, strippedmessage)


def run(manual=False):
    """
    Establish a connection to Nexudus and processes any new invoices.

    :param manual: True if the user initiated this run from the web
                   interface.
    """

    global manually_initiated
    manually_initiated = manual

    log_message("Running...")

    # db_logger = logging.getLogger('invoicer_db')
    # db_logger.info("Running...")

    # Connect to Nexudus
    sm = conn.get_db_sessionmaker()

    # Perform this entire process for each nexudus space that we want to
    # manage.
    for nexudus_space_id in config.NEXUDUS_SPACE_USAEPAY_MAP:
        log_message("")
        log_message("For Nexudus space " + str(nexudus_space_id) + ":")

        # TODO maybe clean up members that are no longer active first
        log_message(">>> Syncing member table...")
        nexudus.sync_member_table(sm, nexudus_space_id)

        log_message(">>> Getting unpaid invoices from Nexudus...")
        nexudus.sync_invoice_table(sm, nexudus_space_id)

        log_message(">>> Checking for new transactions to send to USAePay...")
        charge_unpaid_invoices(sm, nexudus_space_id)

        log_message(">>> Checking for settled transactions...")
        check_txn_statuses(sm, nexudus_space_id)

        log_message(">>> Submitting paid invoices to Nexudus...")
        finalize_invoices(sm)


def get_usaepay_api_creds(nexudus_space_id):
    """
    Get the API key we will be using to connect to USAePay.

    :param nexudus_space_id: ID of the Nexudus space we are currently
                             processing records for.
    :returns: (api_key, api_pin)
    """
    try:
        api_key = config.NEXUDUS_SPACE_USAEPAY_MAP[nexudus_space_id]["api_key"]
        api_pin = config.NEXUDUS_SPACE_USAEPAY_MAP[nexudus_space_id]["api_pin"]
        return (api_key, api_pin)
    except KeyError as e:
        log_message("Invalid configuration: NEXUDUS_SPACE_USAEPAY_MAP is not "
                    "set up correctly in the config file. Check the "
                    "config-example.py file for reference.",
                    logging.ERROR)
        raise


def charge_single_invoice(invoice, db_sess, nexudus_space_id):
    """

    :param invoice: models.Invoice object
    :param db_sess: SQLAlchemy database session object
    :param nexudus_space_id: ID of the Nexudus space we are currently
                             processing records for.
    """
    creds = get_usaepay_api_creds(nexudus_space_id)

    try:
        res = usaepay.create_transaction(invoice, creds)
        if res["result_code"] != usaepay.RESULT_APPROVED:
            log_transaction_exception(res["error"], 
                                      invoice.member.email)

        invoice.txn_key = res["key"]
        invoice.txn_resultcode = res["result_code"]
        invoice.txn_result = res["result"]
        db_sess.commit()

    except KeyError as e:
        log_message("Key %s not found in USAePay response!" % str(e),
                    logging.ERROR)

    except HTTPError as e:
        log_message("Charge request to USAePay failed. Message: " + str(e),
                    logging.ERROR)


def charge_unpaid_invoices(sm, nexudus_space_id):
    """
    Run unpaid invoices in our database through USAePay.

    An invoice is considered "unpaid" (aka due) if it is in our database, but
    has no txn_status. Any invoice that we've attempted to send to SQLAlchemy
    will have some txn_status.

    :param sm: SQLAlchemy sessionmaker object
    :param nexudus_space_id: ID of the Nexudus space we are currently
                             processing records for.
    """
    db_sess = sm()

    # Only try to pay invoices if the corresponding Member is set to be
    # processed automatically AND the invoice does not yet have a transaction
    # status AND the member has account/routing information.
    unsent_invoices = db_sess.query(Invoice).\
        filter(
            Invoice.nexudus_space_id == nexudus_space_id
        ).\
        filter(
            Invoice.member.has(process_automatically=True)
        ).\
        filter(
            and_(
                Invoice.member.has(Member.account_number != None),  # noqa
                Invoice.member.has(Member.account_number != ''),
                Invoice.member.has(Member.routing_number != None),
                Invoice.member.has(Member.routing_number != '')
            )
        ).\
        filter(
            or_(
                Invoice.txn_resultcode == None,
                Invoice.txn_resultcode == '',
                # We'll try invoices with declined/error results again, so the
                # manager keeps seeing an error message.
                Invoice.txn_resultcode == usaepay.RESULT_DECLINED,
                Invoice.txn_resultcode == usaepay.RESULT_ERROR
            )
        ).all()

    if len(unsent_invoices) == 0:
        log_message("    No new transactions sent.")

    for invoice in unsent_invoices:
        log_message(
            "    Processing invoice for " + str(invoice.member) +
            "... Sending new transaction to USAePay"
        )

        charge_single_invoice(invoice, db_sess, nexudus_space_id)


def check_txn_statuses(sm, nexudus_space_id):
    """
    Check if any "Approved" invoices have been submitted to the bank.

    :param sm: SQLAlchemy sessionmaker object
    :param nexudus_space_id: ID of the Nexudus space we are currently
                             processing records for.
    """

    db_sess = sm()
    approved_invoices = db_sess.query(Invoice).\
        filter(Invoice.nexudus_space_id == nexudus_space_id).\
        filter(Invoice.member.has(process_automatically=True)).\
        filter_by(txn_resultcode=usaepay.RESULT_APPROVED).\
        filter(
            or_(
                Invoice.txn_statuscode != usaepay.STATUS_SETTLED,
                Invoice.txn_statuscode == None
            )
        ).\
        all()

    if len(approved_invoices) == 0:
        log_message("    No Approved, unsettled transactions found.")

    for invoice in approved_invoices:
        mark_transaction_status(invoice, db_sess, nexudus_space_id)


def log_transaction_exception(result, email):
    """
    Mark transaction status and log the error.

    :param result: USAePay transaction result message
    :param email: User's email address
    """
    log_message("    Error processing invoice for user %s: %s"
                % (email, result),
                logging.ERROR
               )

def finalize_invoice(invoice, db_sess):
    """
    Inform Nexudus that one invoice has been paid.

    If successful, mark the invoice as finalized in our database.

    :param invoice: models.Invoice object
    :param db_sess: SQLAlchemy database session object
    """
    result, msg = nexudus.mark_invoice_paid(invoice.nexudus_invoice_id)

    if result:
        invoice.finalized = True
        db_sess.commit()
        log_message("    Successfully updated invoice %s in Nexudus."
                    % invoice.nexudus_invoice_id,
                    logging.INFO)
    else:
        log_message("    Could not mark invoice %s paid in Nexudus! Error: %s"
                    % (invoice.nexudus_invoice_id, msg),
                    logging.ERROR)


def finalize_invoices(sm):
    """
    Inform Nexudus of all settled invoices.

    :param sm: SQLAlchemy sessionmaker object
    """
    db_sess = sm()

    # Get all settled, unfinalized invoices.
    settled_unfinalized_invoices = db_sess.query(Invoice).\
        filter_by(txn_statuscode=usaepay.STATUS_SETTLED).\
        filter_by(finalized=False).\
        all()

    for invoice in settled_unfinalized_invoices:
        finalize_invoice(invoice, db_sess)


def mark_transaction_status(invoice, db_sess, nexudus_space_id):
    """

    :param invoice: models.Invoice object
    :param db_sess: SQLAlchemy database session object
    """
    usaepay_creds = get_usaepay_api_creds(nexudus_space_id)
    try:
        log_message(
            "    Checking transaction status for " +
            str(invoice.member) +
            " (Invoice ID " + str(invoice.nexudus_invoice_id) + ")"
            "..."
        )
        status_dict = usaepay.get_transaction_status(invoice.txn_key, usaepay_creds)
        invoice.txn_statuscode = status_dict["status_code"]
        invoice.txn_status = status_dict["status"]

        log_message(
            "    USAePay Transaction "
            + str(invoice.txn_key)
            + ": "
            + str(invoice.txn_status)
        )

        db_sess.commit()

    except KeyError as e:
        log_message("Key %s not found in USAePay response!" % str(e),
                    logging.ERROR)

    except HTTPError as e:
        log_message("CRITICAL: Request to USAePay failed. Message: " + str(e),
                    logging.ERROR)
