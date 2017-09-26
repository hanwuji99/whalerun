# -*- coding: utf-8 -*-

from app import create_app
from app.tasks import celery
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth

app = create_app()
oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key='a11a1bda412d928fb39a',
    consumer_secret='92b7cf30bc42c49d589a10372c3f9ff3bb310037',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)
#

@app.route('/index')
def index():
    if 'github_token' in session:
        me = github.get('user')
        return jsonify(me.data)
    return redirect(url_for('github_login'))


@app.route('/users/github_login')
def github_login():
    return github.authorize(callback=url_for('github_authorized', _external=True))


@app.route('/users/github_login/authorized')
def github_authorized():
    resp = github.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['github_token'] = (resp['access_token'], '')
    me = github.get('user')
    return jsonify(me.data)


@app.route('/users/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


if __name__ == '__main__':
    # global App
    # App.set_app(app)
    app.run(debug=True)


 # global github_oauth
    # github_oauth = Oauth(app)
    # github_oauth.set_oauth(app)
    # global makeapp
    # makeapp = App(app)
    # makeapp.set_app(app)
