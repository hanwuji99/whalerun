# -*- coding: utf-8 -*-

from app import create_app
from app.tasks import celery
# from app.blueprints.api import Oauth

app = create_app()

if __name__ == '__main__':

    # global github_oauth
    # github_oauth = Oauth(app)
    # github_oauth.set_oauth(app)
    # global app
    app.run(debug=True)



