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

# Documentation: https://web.archive.org/web/20190611191118/https://help.usaepay.info/developer/reference/transactioncodes/

RESULT_APPROVED = "A"
RESULT_DECLINED = "D"
RESULT_PENDING = "P"
RESULT_ERROR = "E"
RESULT_VERIFICATION = "V"
STATUS_NEW = "N"
STATUS_PENDING = "P"
STATUS_SUBMITTED = "B"
STATUS_FUNDED = "F"
STATUS_SETTLED = "S"
STATUS_ERROR = "E"
STATUS_VOIDED = "V"
STATUS_RETURNED = "R"
STATUS_TIMEDOUT = "T"
STATUS_ONHOLD_MANAGER = "M"
STATUS_ONHOLD_PROCESSOR = "H"


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


def api_request(api_url, creds, payload=None, reqtype='POST'):
    """
    Send a request to USAePay's REST API.

    Sparse documentation for the API can be found here:
        https://help.usaepay.info/developer/rest-api/
        https://help.usaepay.info/developer/rest-api/changelog/

    :param api_url: URL fragment (e.g. '/transactions')
    :param creds: Tuple of strings: (api_key, api_pin)
    :param payload: Data to send in JSON format
    :return: TODO
    """
    apikey = creds[0]
    apipin = creds[1]

    seed = ''.join(random.choices(string.ascii_letters, k=10))
    prehash = apikey + seed + apipin
    apihash = 's2/' + seed + '/' +\
        hashlib.sha256(prehash.encode('utf-8')).hexdigest()
    hashcreds = (apikey, apihash)

    # debug_api_request(seed, prehash, apihash)

    if reqtype == 'GET':
        reqfunc = requests.get
    elif reqtype == 'POST':
        reqfunc = requests.post
    else:
        raise Exception("Unsupported request type " + reqtype)

    if payload is None:
        r = reqfunc(config.USAEPAY_API_URL + api_url,
                    auth=hashcreds)
    else:
        r = reqfunc(config.USAEPAY_API_URL + api_url,
                    auth=hashcreds,
                    json=payload)
    return r


def create_transaction(invoice, creds):
    """
    Create a USAePay charge based on the given invoice.

    :param invoice: models.Invoice object
    :param creds: Tuple of strings: (api_key, api_pin)
    :return: USAePay JSON response object.
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

    r = api_request('/transactions', creds, payload=payload)
    r.raise_for_status()
    return r.json()


def get_transaction_status(txn_key, creds):
    """
    Get the status of a past transaction.

    :param txn_key: Transaction key previously stored in the Invoice table
    :param creds: Tuple of strings: (api_key, api_pin)
    :return: Python dictionary mapping of the USAePay JSON response object.
             Example response:
                {
                    "type": "transaction",
                    "key": "5nft7t7vzx1277g",
                    "refnum": "3103559243",
                    "created": "2019-05-31 07:37:28",
                    "trantype_code": "K",
                    "trantype": "Check Sale",
                    "result_code": "A",
                    "result": "Approved",
                    "authcode": "TM6568",
                    "status_code": "S",
                    "status": "Settled",
                    "check": {
                        "accountholder": "Seth Yoder",
                        "checknum": "",
                        "trackingnum": "19053159313448",
                        "effective": "2019-06-03",
                        "processed": "2019-05-31",
                        "settled": "2019-06-01",
                        "returned": None,
                        "banknote": None
                    },
                    "amount": "2.00",
                    "amount_detail": {
                        "tip": "0.00",
                        "tax": "0.00",
                        "shipping": "0.00",
                        "discount": "0.00"
                    }
                }
    """

    r = api_request('/transactions/' + txn_key, creds, reqtype='GET')
    r.raise_for_status()

    return r.json()
