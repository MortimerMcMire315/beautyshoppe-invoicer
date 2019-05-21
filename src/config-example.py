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

'''
Rename this file to config.py and fill in each field.
'''

DB_TYPE = "mysql"
DB_HOST = "example.db"
DB_PORT = 3306
DB_USER = "user"
DB_PASS = "pass"
DB_NAME = "db"

NEXUDUS_EMAIL = "email@example.com"
NEXUDUS_PASS = "password"

#Don't change unless Nexudus actually changes the API URL, which they shouldn't.
NEXUDUS_API_URL = "https://spaces.nexudus.com/api/"

# List of spaces to manage. By default, when we access the Nexudus API, we get
# data from all spaces managed by the API account. Use this list to restrict to
# certain spaces. TODO explain how to find this ID
NEXUDUS_SPACE_IDS = ["12345678","12345678", "12345678"]

#Bytestring - Generate using urandom or similar
FLASK_SECRET = b'\x00\x00\x00'
