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

import datetime
import csv
import tempfile

import flask

from ..db import conn
from ..db.models import Log

def to_datetime(datestr):
    date = datestr.replace(' 0',' ')
    t = datetime.datetime.strptime(date, "%m/%d/%Y %I:%M %p")
    return t


def generate_csv(from_date, to_date):
    sm = conn.get_db_sessionmaker()
    db_sess = sm()

    loglines = db_sess.query(Log).\
        filter(Log.time_created > to_datetime(from_date)).\
        filter(Log.time_created < to_datetime(to_date)).\
        order_by(Log.time_created.asc()).\
        all()

    csvfile = tempfile.NamedTemporaryFile('w', newline='')
    writer = csv.writer(csvfile)

    print("yo!")
    print(loglines)

    writer.writerow(['Timestamp','Level', 'Message'])
    for l in loglines:
        writer.writerow([str(l.time_created), l.log_level, l.log_message])

    csvfile.flush()

    return csvfile
