from sqlalchemy import Column, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from .. import config

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

def get_db_sessionmaker():
    from sqlalchemy import create_engine
    connection_string = '{DB_TYPE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'.format(
        DB_TYPE=config.DB_TYPE,
        DB_USER=config.DB_USER,
        DB_PASS=config.DB_PASS,
        DB_HOST=config.DB_HOST,
        DB_PORT=config.DB_PORT,
        DB_NAME=config.DB_NAME
    )
    engine = create_engine(connection_string)

    from sqlalchemy.orm import sessionmaker
    sessionmaker = sessionmaker()
    sessionmaker.configure(bind=engine)
    Base.metadata.create_all(engine)
    return sessionmaker
