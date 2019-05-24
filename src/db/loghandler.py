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

import time
import logging
import datetime

from sqlalchemy.exc import SQLAlchemyError

from . import models


class SQLALogHandler(logging.Handler):
    """A log handler that will log directly to our database."""

    def __init__(self, db_session):
        """
        Initialize.

        :param db_session: Live SQLA database session.
        """
        logging.Handler.__init__(self)
        self.db_session = db_session

    def emit(self, record):
        """Write a log directly to our database."""
        # Set current time
        t = int(time.time())
        logrow = models.Log(log_level=record.levelname,
                            log_message=record.msg,
                            time_created=datetime.datetime.now())

        try:
            self.db_session.add(logrow)
            self.db_session.commit()
        except SQLAlchemyError as e:
            print("Fatal error: Could not log to database:")
            print(e)
