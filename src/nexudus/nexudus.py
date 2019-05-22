'''
This file is part of PROJECTNAME.

PROJECTNAME is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

PROJECTNAME is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along
with PROJECTNAME.  If not, see
<https://www.gnu.org/licenses/>.
'''

import logging
import sys
import pprint

import requests
import json
from wtforms.validators import ValidationError

from .. import config
from ..db import models

def run(initial=False, callback=None):
    '''
    Entry point for invoice processing.
    Establishes a connection to Nexudus and processes any new invoices.

    :param initial: True if this is the first run of the job upon
                    starting up the app.
    :param callback: Callback function TODO
    '''

    # Get logger and tell it we're doing something
    logger = logging.getLogger('invoicer')
    logger.debug("Running...")

    # Connect to Nexudus
    populate_member_table()

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

def nexudus_get_invoice_list():
    '''

    '''

    payload = {
        'CoworkerInvoice_Paid' : 'false',
    }

    nexudus_process_onebyone('billing/coworkerinvoices', lambda r: print(r["Coworker"]), payload)

def populate_member_table():
    '''

    '''

    def callback(rs):
        for r in rs:
            # pp = pprint.PrettyPrinter(indent=4)
            # pp.pprint(r)
            print(r["FullName"])

    payload = {

    }

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
            if u["UserId"]:
                return models.AuthUser(u["UserId"])
            else:
                print("yo!")
                sys.stdout.flush()
                return None
        except IndexError as e:
            print("uh oh!")
            sys.stdout.flush()
            return None
        except KeyError as e:
            print("no!")
            sys.stdout.flush()
            return None
    else:
        print(email)
        print(config.NEXUDUS_EMAIL)
        print(password)
        print(config.NEXUDUS_PASS)
        sys.stdout.flush()
        return None
