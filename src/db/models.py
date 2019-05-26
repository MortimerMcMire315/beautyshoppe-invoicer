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

from sqlalchemy import (
        Column, DateTime, Text, Integer, ForeignKey, Boolean, BigInteger,
        DECIMAL)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Member(Base):
    """Beauty Shoppe coworker."""

    __tablename__ = 'member'
    id = Column(Integer, primary_key=True)
    nexudus_user_id = Column(BigInteger)
    fullname = Column(Text)
    email = Column(Text)
    routing_number = Column(Text)
    account_number = Column(Text)
    process_automatically = Column(Boolean)

    def __str__(self):
        return self.email


class Invoice(Base):
    """Invoice emitted from Nexudus supplemented with our own status info."""

    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True)
    nexudus_invoice_id = Column(BigInteger)
    nexudus_user_id = Column(BigInteger, ForeignKey('member.nexudus_user_id'))
    time_created = Column(DateTime)
    amount = Column(DECIMAL(precision=10, scale=2))
    processed = Column(Boolean)
    txn_id = Column(BigInteger)
    txn_status = Column(Text)

    member = relationship("Member")


class Log(Base):
    """Basic log table."""

    __tablename__ = 'log'
    id = Column(BigInteger, primary_key=True)
    log_level = Column(Text)
    log_message = Column(Text)
    time_created = Column(DateTime)


class AuthUser():
    """
    Dummy class only used for flask-login authentication.

    Will only be created upon successful authentication.
    """

    def __init__(self, nexudus_id):
        """Set the user's nexudus ID."""
        self.nexudus_id = nexudus_id

    @property
    def is_authenticated(self):
        """Required for Flask-Login. Always true."""
        return True

    @property
    def is_active(self):
        """Required for Flask-Login. Always true."""
        return True

    @property
    def is_anonymous(self):
        """Required for Flask-Login. True if authenticated."""
        if self.authenticated:
            return False
        else:
            return True

    def get_id(self):
        """Return Nexudus ID."""
        return self.nexudus_id

    def __unicode__(self):
        """Return user's email address."""
        return self.email
