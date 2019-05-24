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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .. import config
from .models import Base


def get_db_sessionmaker():
    conn_string_template = (
        '{DB_TYPE}'
        '://{DB_USER}'
        ':{DB_PASS}'
        '@{DB_HOST}'
        ':{DB_PORT}'
        '/{DB_NAME}'
    )

    connection_string = conn_string_template.format(
        DB_TYPE=config.DB_TYPE,
        DB_USER=config.DB_USER,
        DB_PASS=config.DB_PASS,
        DB_HOST=config.DB_HOST,
        DB_PORT=config.DB_PORT,
        DB_NAME=config.DB_NAME
    )
    engine = create_engine(connection_string)

    sm = sessionmaker()
    sm.configure(bind=engine)
    Base.metadata.create_all(engine)
    return sm
