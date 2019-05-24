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

from wtforms import form, fields, validators
from flask import url_for, redirect, render_template, request
from flask_admin import AdminIndexView, expose, helpers

from ..invoicer import nexudus
from ..db import models

import flask_login as login

'''
This file is largely plagiarized from
https://github.com/flask-admin/flask-admin/blob/master/examples/auth-flask-login/app.py
'''


def init_login(db_session, app):
    """Create login manager and add user loader function."""
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return models.AuthUser(user_id)


class MyAdminIndexView(AdminIndexView):
    """Override default admin view to redirect to login page if not authenticated."""

    @expose('/')
    def index(self):
        """Define site index page (simple redirect)."""
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        """Site login view."""
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))

        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

    @expose('/logout')
    def logout_view(self):
        """Site logout."""
        login.logout_user()
        return redirect(url_for('.index'))


class LoginForm(form.Form):
    """Simple login form calling nexudus.authAPIUser."""

    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        """Check the user's credentials."""
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

    def get_user(self):
        """Try authenticating the user."""
        return nexudus.authAPIUser(self.login.data, self.password.data)
