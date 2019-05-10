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

from ..db import conn, models
from .. import config

import traceback
import sys

# TODO this may be unnecessary eventually
global_app = None

# TODO move elsewhere
def invoice_transfer(initial=False):
    global global_app
    global_app.logger.info("yo!")

class Config(object):
    JOBS = [
            {
                'id': 'invoice_transfer',
                'func': invoice_transfer,
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

    admin = Admin(app, url='/', name='Beauty Shoppe ACH Administration', template_mode='bootstrap3')
    admin.add_view(ModelView(models.Member, db_session))
    admin.add_view(ModelView(models.Invoice, db_session))
    admin.add_view(ModelView(models.Log, db_session))

def error_handler_setup(app):
    @app.errorhandler(500)
    def serverError(error):
        print("500 error:")
        print(traceback.format_exc())

def scheduler_setup(app):
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

def init():
    global global_app

    # Set log level
    logging.basicConfig(level=logging.DEBUG)

    # Set up Flask app
    app = Flask(__name__)
    global_app = app
    app.config.from_object(Config())
    app.secret_key=config.FLASK_SECRET

    admin_setup(app)
    error_handler_setup(app)
    scheduler_setup(app)

    app.logger.info("Running initial invoice transfer...")
    invoice_transfer(True)

    app.run(host='0.0.0.0')
