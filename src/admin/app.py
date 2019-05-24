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

from flask import Flask, render_template

from flask_apscheduler import APScheduler
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import flask_login as login

from ..invoicer import invoicer
from ..db import conn, models, loghandler
from .. import config
from . import auth

import traceback
import sys
import logging

class Config(object):
    JOBS = [
            {
                'id': 'invoice_transfer',
                'func': invoicer.run,
                'trigger': 'interval',
                'seconds': 1000,
                'max_instances': 1,
                'coalesce': True
            }
    ]
    SCHEDULER_API_ENABLED = True
    FLASK_ADMIN_SWATCH = 'cerulean'
    ENV = 'development'
    PROPAGATE_EXCEPTIONS = True

def admin_setup(app):
    '''

    '''

    # Get database sessionmaker and get a session.
    sm = conn.get_db_sessionmaker()
    db_session = sm()

    # We use this class for model views to ensure that a user must be
    # authenticated to view them.
    class AuthModelView(ModelView):
        def is_accessible(self):
            return login.current_user.is_authenticated

    class MemberAdminView(AuthModelView):
        column_filters = ('nexudus_user_id', 'fullname', 'email')

    auth.init_login(db_session, app)

    # Set up admin front page
    @app.route('/')
    def index():
        return render_template('index.html')

    admin = Admin(app, name='Beauty Shoppe ACH Administration',
                  base_template='my_master.html',
                  index_view=auth.MyAdminIndexView(),
                  template_mode='bootstrap3' )
    admin.add_view(MemberAdminView(models.Member, db_session))
    admin.add_view(AuthModelView(models.Invoice, db_session))
    admin.add_view(AuthModelView(models.Log, db_session))
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
    logging.basicConfig(level=logging.DEBUG)
    invoice_logger = logging.getLogger('invoicer')
    # Add custom log handler to log directly to DB
    invoice_logger.addHandler(loghandler.SQLALogHandler(db_session))
    return invoice_logger

def init():
    # Set up Flask app
    app = Flask(__name__)
    db_session = admin_setup(app)

    # Give the app a configuration
    app.config.from_object(Config())

    # FLASK_SECRET comes from config.py
    app.secret_key=config.FLASK_SECRET

    # Set up logging - get database session and pass it into the log setup so
    # that logs can go directly to DB
    invoice_logger = log_setup(app, db_session)

    # Add error page configurations
    error_page_setup(app)

    invoicer.run(True)
    # Start APScheduler jobs
    scheduler = scheduler_setup(app)

    app.run(host='0.0.0.0')
