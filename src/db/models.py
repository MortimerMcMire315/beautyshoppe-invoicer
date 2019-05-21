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

from sqlalchemy import Column, DateTime, Text, Integer, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Member(Base):
    '''
    Beauty Shoppe coworker
    '''

    __tablename__ = 'member'
    id = Column(Integer, primary_key=True)
    nexudus_user_id = Column(BigInteger)
    firstname = Column(Text)
    lastname = Column(Text)
    email = Column(Text)
    routing_number = Column(Text)
    account_number = Column(Text)

class Invoice(Base):
    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True)
    nexudus_invoice_id = Column(BigInteger)
    nexudus_user_id = Column(BigInteger)
    time_created = Column(DateTime)
    amount = Column(Integer)
    processed = Column(Boolean)
    txn_id = Column(BigInteger)
    txn_status = Column(Text)

class Log(Base):
    __tablename__ = 'log'
    id = Column(BigInteger, primary_key=True)
    log_level = Column(Text)
    log_message = Column(Text)
    time_created = Column(DateTime)
