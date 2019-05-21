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

from flask import Flask
import logging

from flask_apscheduler import APScheduler
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from ..app import invoice_processor
from ..db import conn, models, loghandler
from .. import config

import traceback
import sys

# TODO this may be unnecessary eventually
global_app = None

class Config(object):
    JOBS = [
            {
                'id': 'invoice_transfer',
                'func': invoice_processor.run,
                'args': (),
                'trigger': 'interval',
                'seconds': 10
            }
    ]
    SCHEDULER_API_ENABLED = True
    FLASK_ADMIN_SWATCH = 'cerulean'
    ENV = 'development'
    PROPAGATE_EXCEPTIONS = True

def admin_setup(app):
    db_sessionmaker = conn.get_db_sessionmaker()
    db_session = db_sessionmaker()

    class MemberAdminView(ModelView):
        column_filters = ('nexudus_id', 'firstname', 'lastname', 'email')

    admin = Admin(app, url='/', name='Beauty Shoppe ACH Administration', template_mode='bootstrap3')
    admin.add_view(MemberAdminView(models.Member, db_session))
    admin.add_view(ModelView(models.Invoice, db_session))
    admin.add_view(ModelView(models.Log, db_session))
    return db_session

def error_page_setup(app):
    @app.errorhandler(500)
    def serverError(error):
        print("500 error:")
        print(traceback.format_exc())

def scheduler_setup(app):
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    return scheduler

def log_setup(app, db_session):
    # Set log level
    logging.basicConfig(level=logging.INFO)
    invoice_logger = logging.getLogger('invoicer')
    # Add custom log handler to log directly to DB
    invoice_logger.addHandler(loghandler.SQLALogHandler(db_session))
    return invoice_logger

def init():
    # Set up Flask app
    app = Flask(__name__)

    # Give the app a configuration
    app.config.from_object(Config())

    # FLASK_SECRET comes from config.py
    app.secret_key=config.FLASK_SECRET

    # Set up logging - get database session and pass it into the log setup so
    # that logs can go directly to DB
    db_session = admin_setup(app)
    invoice_logger = log_setup(app, db_session)

    # Add error page configurations
    error_page_setup(app)

    # Set up APScheduler
    scheduler = scheduler_setup(app)

    # Run initial invoice transfer
    invoice_logger.info("Running initial invoice transfer...")
    invoice_processor.run(True)

    app.run(host='0.0.0.0')
