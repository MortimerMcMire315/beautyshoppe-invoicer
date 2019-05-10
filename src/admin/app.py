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
    admin.add_view(ModelView(models.Invoice, db_session))
    admin.add_view(ModelView(models.Log, db_session))

    @app.errorhandler(500)
    def serverError(error):
        print("500 error:")
        print(traceback.format_exc())

    app.run(host='0.0.0.0')
