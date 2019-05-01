from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .. import config
from .models import Base

def get_db_sessionmaker():
    connection_string = '{DB_TYPE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'.format(
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
