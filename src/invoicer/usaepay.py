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

import sys
import hashlib
import random
import string
import logging

import requests

from .. import config

APPROVED = "A"

def debug_api_request(seed, prehash, apihash):
    """
    Print info about a USAePay API request.

    :param seed: Random seed
    :param prehash: USAePay prehash value
    :param apihash: USAePay hash value
    """
    print("Prehash: " + prehash)
    print("Seed: " + seed)
    print(
        "Hashed prehash: " +
        hashlib.sha256(prehash.encode('utf-8')).hexdigest()
    )
    print("API hash: " + apihash)

    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    sys.stdout.flush()


def api_request(api_url, payload=None, reqtype='POST'):
    """
    Send a request to USAePay's REST API.

    Sparse documentation for the API can be found here:
        https://help.usaepay.info/developer/rest-api/
        https://help.usaepay.info/developer/rest-api/changelog/

    :param api_url: URL fragment (e.g. '/transactions')
    :param payload: Data to send in JSON format
    :return: TODO
    """
    seed = ''.join(random.choices(string.ascii_letters, k=10))

    prehash = config.USAEPAY_API_KEY + seed + config.USAEPAY_API_PIN
    apihash = 's2/' + seed + '/' +\
        hashlib.sha256(prehash.encode('utf-8')).hexdigest()
    creds = (config.USAEPAY_API_KEY, apihash)

    # debug_api_request(seed, prehash, apihash)

    if reqtype == 'GET':
        reqfunc = requests.get
    elif reqtype == 'POST':
        reqfunc = requests.post
    else:
        raise Exception("Unsupported request type " + reqtype)

    if payload is None:
        r = reqfunc(config.USAEPAY_API_URL + api_url,
                          auth=creds)
    else:
        r = reqfunc(config.USAEPAY_API_URL + api_url,
                       auth=creds,
                       json=payload)
    return r


def create_transaction(invoice):
    """
    Create a USAePay charge based on the given invoice.

    :param invoice: models.Invoice object
    :return: TODO
    """
    payload = {
        'command': 'check:sale',
        'amount': str(invoice.amount),
        'check': {
            'accountholder': invoice.member.billing_name,
            'account': invoice.member.account_number,
            'routing': invoice.member.routing_number,
        },
    }

    r = api_request('/transactions', payload=payload)
    r.raise_for_status()
    return r.json()


def get_transaction_status(txn_key):
    """

    """

    r = api_request('/transactions/' + txn_key, reqtype='GET')
    r.raise_for_status()

    return r.json()
