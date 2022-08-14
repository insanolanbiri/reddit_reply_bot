# wsgi file for hosting on pythonanywhere
# symlink this file to the path of wsgi file

import sys, os

path = f'{os.environ["HOME"]}/reddit_reply_bot'
if path not in sys.path:
    sys.path.append(path)


# fake app
from flask import Flask

app = Flask(__name__)


@app.route("/")
def root():
    return "hello"
# end fake app

from main import main

main()
