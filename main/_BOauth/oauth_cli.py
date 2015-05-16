from main.main import app
from flask_oauthlib.client import OAuth

oauth = OAuth(app)

remote = oauth.remote_app(
    'remote',
    request_token_params={},
    base_url='http://127.0.0.1:5000/',
    request_token_url=None,
    access_token_url='http://127.0.0.1:5000/oauth/token',
    authorize_url='http://127.0.0.1:5000/oauth/authorize'
)
