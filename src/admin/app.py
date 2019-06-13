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

import flask
from flask import Flask, render_template, redirect, request

from flask_bootstrap import Bootstrap
from flask_apscheduler import APScheduler
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import flask_login as login

from ..invoicer import invoicer
from ..db import conn, models, loghandler
from .. import config
from . import auth
from . import gencsv

import traceback
import sys
import os
import logging


class Config(object):
    """Flask config object."""

    # These jobs get run by flask-apscheduler.
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
    """Initialize admin interface."""
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

    admin = Admin(app,
                  name='Beauty Shoppe ACH Administration',
                  base_template='my_master.html',
                  index_view=auth.MyAdminIndexView(),
                  template_mode='bootstrap3')
    admin.add_view(MemberAdminView(models.Member, db_session))
    admin.add_view(AuthModelView(models.Invoice, db_session))
    admin.add_view(AuthModelView(models.Log, db_session))
    admin.add_view(auth.ReportsView(name='Reports', endpoint='reports', url='/report'))
    return db_session


def app_setup(app, db_session):
    """Define pages for the Flask app."""
    @app.errorhandler(500)
    def serverError(error):
        print("500 error:")
        print(traceback.format_exc())

    @app.route('/process-invoices/')
    def process_invoices():
        invoicer.run(True)
        return flask.Response(flask.g.get('logqueue', ''), mimetype='text/plain')

    @app.route('/generate-report/', methods=['POST'])
    def generate_report():
        if request.method == 'POST':
            csvfile = gencsv.generate_csv(request.form["from_date"], 
                                          request.form["to_date"])
            return flask.send_file(csvfile.name, as_attachment=True, mimetype='text/csv', attachment_filename='report.csv')

        @app.after_request
        def cleanup(response):
            os.close(csvfile)

    @app.teardown_request
    def teardown_request(*args, **kwargs):
        # If we don't do this, the flask-admin view doesn't update sometimes.
        db_session.expire_all()
        db_session.close()


def scheduler_setup(app):
    """Initialize APScheduler and start running jobs."""
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    return scheduler


def log_setup(app, db_session):
    """Set up a database logger for our invoicer system."""
    # Set log level
    logging.basicConfig(level=logging.DEBUG)
    db_logger = logging.getLogger('invoicer_db')
    # Add custom log handler to log directly to DB
    db_logger.addHandler(loghandler.SQLALogHandler(db_session))

    ajax_logger = logging.getLogger('invoicer_ajax')
    ajax_logger.addHandler(loghandler.AJAXLogHandler())
    return db_logger


def init():
    """Initialize application."""
    # Set up Flask app
    app = Flask(__name__)
    Bootstrap(app)
    db_session = admin_setup(app)

    # Give the app a configuration
    app.config.from_object(Config())

    # FLASK_SECRET comes from config.py
    app.secret_key = config.FLASK_SECRET

    # Set up logging - get database session and pass it into the log setup so
    # that logs can go directly to DB
    log_setup(app, db_session)

    # Add page configurations
    app_setup(app, db_session)

    # Start APScheduler jobs
    scheduler = scheduler_setup(app)

    app.run(host='0.0.0.0')
