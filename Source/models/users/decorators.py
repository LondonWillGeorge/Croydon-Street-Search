# Decorators are extremely powerful Python constructs, might need one of these files
# for either of main object classes in this model.
# So far, copied this file from other Python web app
# by jslvtr

from functools import wraps

from flask import session, flash, redirect, url_for, request

__author__ = 'jslvtr'


def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session.keys() or session['email'] is None:
            flash(u'You need to be signed in for this page.')
            return redirect(url_for('users.login_user', next=request.path))
        return f(*args, **kwargs)

    return decorated_function
