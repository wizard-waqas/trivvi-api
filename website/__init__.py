""" website package initializer  """

from flask import Flask
from flask_cors import CORS

from .parsepdf import parsepdf
from .youtube import youtube
from .openai import generate_quiz


def create_app():
    """ create a flask app  """
    app = Flask(__name__)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.secret_key = 'ib90rcf42r768bxf67g8t6kn907v0k9n34x'

    app.register_blueprint(youtube, url_prefix="/api/youtube")
    app.register_blueprint(parsepdf, url_prefix="/api/parsepdf")
    app.register_blueprint(generate_quiz, url_prefix="/api/ai-generate")

    return app