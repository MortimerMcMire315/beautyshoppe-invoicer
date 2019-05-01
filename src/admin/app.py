from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from ..db import conn, models
from .. import config

import traceback

def init_admin():
    db_sessionmaker = conn.get_db_sessionmaker()
    db_session = db_sessionmaker()

    app = Flask(__name__)
    app.secret_key=config.FLASK_SECRET
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    app.config['ENV'] = 'development'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    admin = Admin(app, url='/', name='Beauty Shoppe ACH Administration', template_mode='bootstrap3')
    admin.add_view(ModelView(models.Member, db_session))

    @app.errorhandler(500)
    def serverError(error):
        print("500 error:")
        print(traceback.format_exc())

    app.run(host='0.0.0.0')
