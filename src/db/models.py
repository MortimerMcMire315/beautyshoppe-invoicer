from sqlalchemy import Column, DateTime, Text, Integer, ForeignKey
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
