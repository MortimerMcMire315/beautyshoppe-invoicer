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

import os
import sys
import hashlib
import base64
import random
import string

import requests

from .. import config

def create_charge(invoice):
    """
    Create a USAePay charge based on the given invoice

    :param invoice: models.Invoice object
    """
    # Documentation: https://help.usaepay.info/developer/rest-api/
    seed = ''.join(random.choices(string.ascii_letters, k=10))

    prehash = config.USAEPAY_API_KEY + seed + config.USAEPAY_API_PIN
    print("Prehash: " + prehash)
    print("Seed: " + seed)
    print("Hashed prehash: " + hashlib.sha256(prehash.encode('utf-8')).hexdigest())
    apihash = 's2/' + seed + '/' + hashlib.sha256(prehash.encode('utf-8')).hexdigest()
    print("API hash: " + apihash)
    creds = (config.USAEPAY_API_KEY, apihash)

    payload = {
        'command': 'check:sale',
        'routing': '123456789',
        'account': '129837102971203987',
        'amount': '1.00',
    }

    r = requests.get(config.USAEPAY_API_URL, auth=creds, params=payload)

    print(r.status_code)
    print(r.text)
    sys.stdout.flush()
