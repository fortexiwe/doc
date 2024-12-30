import flask

def authorized_required(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in flask.session:
            return flask.redirect(flask.url_for('login'))
        return func(*args, **kwargs)
    return wrapper
