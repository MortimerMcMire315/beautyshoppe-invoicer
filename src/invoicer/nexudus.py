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
import sys
import pprint

import requests
import json
from wtforms.validators import ValidationError
from sqlalchemy.orm.exc import MultipleResultsFound

from .. import config
from ..db import models, conn

def nexudus_get(url_part, payload):
    '''
    Generator which GETs Nexudus records and yields batches of records.

    :param url_part: Nexudus API URL - everything after "/api/".
    :param payload: GET variables to send along with API request
    :returns: Yields a batch of records (list of dicts).
    :raises: TODO
    '''

    url = config.NEXUDUS_API_URL + url_part
    creds = (config.NEXUDUS_EMAIL, config.NEXUDUS_PASS)
    params = payload
    has_next_page = True
    current_page = 0

    while has_next_page:
        current_page += 1
        params["page"] = current_page
        r = requests.get(url, params=params, auth=creds)

        #TODO handle request errors
        res = r.json()
        has_next_page = res["HasNextPage"]

        yield res["Records"]

def nexudus_process_onebyone(url_part, callback, payload={}):
    '''
    Make a Nexudus GET request and process each single returned record with the
    given callback function.

    :param url_part: Nexudus API URL - everything after "/api/".
    :param callback: Callback function to process each return record. Takes a
                     single argument (dict)
    :param payload: GET variables to send along with API request. Default
                    empty.
    '''
    for record_list in nexudus_get(url_part, payload):
        for record in record_list:
            callback(record)

def nexudus_process_batch(url_part, callback, payload={}):
    '''
    Make a Nexudus GET request and process the returned records in batches.
    Default batch size is 25, but can be changed with a payload variable, e.g.
    { "size" : 1000 }

    :param url_part: Nexudus API URL - everything after "/api/".
    :param callback: Callback function to process each return record. Takes a
                     single argument (dict)
    :param payload: GET variables to send along with API request. Default
                    empty.
    '''
    for record_list in nexudus_get(url_part, payload):
        callback(record_list)

def nexudus_get_first(url_part, payload={}):
    g = nexudus_get(url_part, payload)
    return next(g)[0]

def get_invoice_list():
    '''

    '''

    payload = {
        'CoworkerInvoice_Paid' : 'false',
        'CoworkerInvoice_Coworker' : 721134193,
        'CoworkerInvoice_Coworker' : 253585422
    }

    nexudus_process_onebyone('billing/coworkerinvoices', lambda r: (print(r["CoworkerId"]), print(r["BusinessId"])), payload)

def add_or_overwrite_member(record, db_sess):
    '''
    :param record: Member dict from Nexudus API call
    :param db_sess: DB Session
    :return: A merged Member to store in our database.

    Compare a Member record from the Nexudus database with any record we have
    for the same user. If a non-null field from the Nexudus database
    contradicts a field in our database, overwrite our field (favoring Nexudus
    as the primary source of user data).
    '''

    try:
        local_user = db_sess.query(models.Member).filter_by(nexudus_user_id = record["Id"]).one_or_none()
    except MultipleResultsFound as e:
        local_users = db_sess.query(models.Member).filter_by(nexudus_user_id = record["Id"]).all()
        print(record)
        for u in local_users:
            print(u.fullname)
            print(u.nexudus_user_id)
            sys.stdout.flush()
            print()
        exit(1)

    if not local_user:
        local_user = models.Member()
        db_sess.add(local_user)

    local_user.nexudus_user_id = record["Id"]
    local_user.fullname = record["FullName"]
    local_user.email = record["Email"]
    local_user.routing_number = record["BankBranch"]
    local_user.account_number = record["BankAccount"]

    nstrip = lambda s: s.strip() if s else None

    if nstrip(local_user.routing_number) and nstrip(local_user.account_number):
        local_user.process_automatically = True # TODO work this out
    else:
        local_user.process_automatically = False

    # TODO is it okay to commit every single one separately?
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(record)
    print("Committing " + local_user.email + " ...")
    db_sess.commit()

def process_invoices(callback, sm):

    spaces = config.NEXUDUS_SPACE_IDS
    if spaces:
        for space in spaces:
            payload['CoworkerInvoice_Business'] = space
            nexudus_process_onebyone('spaces/coworkers', callback, payload)
    else:
        nexudus_process_onebyone('spaces/coworkers', callback, payload)

def populate_member_table(sm):
    '''
    Fills local Member table with records from the Nexudus database.

    :param sm: Database sessionmaker
    '''

    db_sess = sm()
    def callback(records):
        for record in records:
            member = add_or_overwrite_member(record, db_sess)

    payload = {
        'Coworker_Active' : 'true'
    }

    # It is important that we only grab coworkers from the spaces we actually
    # want to manage. If we don't do this, coworkers will be pulled from all
    # spaces that this account has access to.
    spaces = config.NEXUDUS_SPACE_IDS
    if spaces:
        for space in spaces:
            payload['Coworker_InvoicingBusiness'] = space
            nexudus_process_batch('spaces/coworkers', callback, payload)
    else:
        nexudus_process_batch('spaces/coworkers', callback, payload)

def authAPIUser(email, password):
    '''
    Simple authentication - just ensure that the login user has API access.
    '''

    if email == config.NEXUDUS_EMAIL and password == config.NEXUDUS_PASS:
        payload = {
            'Coworker_Email' : email
        }

        try:
            u = nexudus_get_first('spaces/coworkers', payload)
            if u["Id"]:
                return models.AuthUser(u["Id"])
            else:
                return None
        except IndexError as e:
            return None
        except KeyError as e:
            return None
    else:
        return None
