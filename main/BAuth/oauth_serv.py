from main.main import app
from flask import Blueprint
from .models import Client, Grant, Token, db_session
from flask_oauthlib.provider import OAuth2Provider
from datetime import datetime, timedelta

oauth = OAuth2Provider(app)

bp_oauth = Blueprint('bp_oauth', __name__, url_prefix='/oauth')

@oauth.clientgetter
def load_client(client_id):
    return db_session.query(Client).filter_by(client_id=client_id).first()

@oauth.grantgetter
def load_grant(client_id, code):
    return db_session.query(Grant).filter_by(client_id=client_id, code=code).first()

@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=get_current_user(),
        expires=expires
    )
    db_session.add(grant)
    db_session.commit()
    return grant

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return db_session.query(Token).filter_by(access_token=access_token).first()
    elif refresh_token:
        return db_session.query(Token).filter_by(refresh_token=refresh_token).first()

@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = db_session.query(Token).filter_by(client_id=request.client.client_id,
                                 user_id=request.user.id)
    # make sure that every client has only one token connected to a user
    for t in toks:
        db_session.delete(t)

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db_session.add(tok)
    db_session.commit()
    return tok

@oauth.usergetter
def get_user(username, password, *args, **kwargs):
    user = db_session.query(User).filter_by(username=username).first()
    if user.check_password(password):
        return user
    return None


@bp_oauth.route('/token')
@oauth.token_handler
def access_token():
    return None


@bp_oauth.route('/authorize', methods=['GET', 'POST'])
# @require_login
@oauth.authorize_handler
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.query.filter_by(client_id=client_id).first()
        kwargs['client'] = client
        return render_template('oauthorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'
