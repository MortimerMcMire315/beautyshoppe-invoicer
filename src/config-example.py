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

"""
Rename this file to config.py and fill in each field.
"""

import logging

# Credentials to our local database.
DB_TYPE = "mysql"
DB_HOST = "example.db"
DB_PORT = 3306
DB_USER = "user"
DB_PASS = "pass"
DB_NAME = "db"

# Credentials to a Nexudus account that has API access for all of the spaces
# listed in NEXUDUS_SPACE_USAEPAY_MAP.
NEXUDUS_EMAIL = "email@example.com"
NEXUDUS_PASS = "password"

# Don't change unless Nexudus actually changes the API URL, which they
# shouldn't.
NEXUDUS_API_URL = "https://spaces.nexudus.com/api/"

# Map of spaces to manage and corresponding USAePay API keys. By default, when
# we access the Nexudus API, we get data from all spaces managed by the API
# account. Use this list to restrict to certain spaces.
#
# To find your space ID, log into spaces.nexudus.com, manage a space, and check
# the page source (CTRL-U in Chrome). then CTRL-F for "businessId".  The ID
# listed in the javascript is the ID for the space that you're currently
# managing.

NEXUDUS_SPACE_USAEPAY_MAP = {
    "12345678": {
        "api_key": "_asdfghjklasdfghjklasdfghjklasdf",
        "api_pin": "123456"
    },
    "91872033": {
        "api_key": "_examplekey",
        "api_pin": "123456"
    }
}

USAEPAY_API_URL = "https://sandbox.usaepay.com/api/v2"

# By default, should members with existing ACH info in Nexudus have their
# invoices automatically processed?
PROCESS_AUTOMATICALLY = False

# Bytestring - Generate using urandom or similar. Should be 10-20 characters
# example to generate: python -c 'import os;a=os.urandom(20);print(a)'
FLASK_SECRET = b'\x00\x00\x00'

# DEBUG, INFO, WARNING, ERROR, or CRITICAL
LOGLEVEL = logging.DEBUG
