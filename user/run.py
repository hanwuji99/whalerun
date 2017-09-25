# -*- coding: utf-8 -*-

from app import create_app
from app.tasks import celery
from app.blueprints.api import App

app = create_app()
if __name__ == '__main__':
    App.set_app(app)
    app.run(debug=True)


 # global github_oauth
    # github_oauth = Oauth(app)
    # github_oauth.set_oauth(app)
    # global makeapp
    # makeapp = App(app)
    # makeapp.set_app(app)
