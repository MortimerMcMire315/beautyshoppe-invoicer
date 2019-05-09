from sqlalchemy import Column, DateTime, Text, Integer, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

'''
Beauty Shoppe member
'''
class Member(Base):
    __tablename__ = 'member'
    id = Column(Integer, primary_key=True)
    nexudus_id = Column(Integer)
    firstname = Column(Text)
    lastname = Column(Text)
    email = Column(Text)
    routing_number = Column(Text)
    account_number = Column(Text)

class Invoice(Base):
    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True)
    nexudus_id = Column(Integer)
    timecreated = Column(Integer)
    amount = Column(Integer)
    processed = Column(Boolean)
    txn_id = Column(BigInteger)
    txn_status = Column(Text)

class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    log_level = Column(Text)
    log_message = Column(Text)
    invoice_id = Column(Integer, ForeignKey("invoice.id"))
    invoice = relationship("Invoice")
