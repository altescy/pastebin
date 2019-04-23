# -*- coding: utf-8 -*-

import os

import contextlib
from functools import wraps
from flask import Flask, request, render_template, redirect
import MySQLdb

from . import highlight
from . import model


MANUAL = "TL;DR: curl -F 'f=<-' {}"
MANUAL_PASTES = """TL;DR: curl -F 'f=<-' {}

YOUR PASTES:
{}
"""


dbhost = os.environ.get("PB_DB_HOST", "127.0.0.1")
dbport = os.environ.get("PB_DB_PORT", "13306")
dbuser = os.environ.get("PB_DB_USER", "root")
dbpass = os.environ.get("PB_DB_PASSWORD", "root")
dbname = os.environ.get("PB_DB_NAME", "pastebin")


app = Flask(__name__)


_dbconn = None


def is_from_browser():
    user_agent = request.headers.get('User-Agent', '')
    if user_agent.startswith("Mozilla"):
        return True
    return False


def get_host():
    return request.host


def get_paste_url(token):
    proto = request.headers.get('X-Forwarded-Proto', 'http')
    host = get_host()
    return f"{proto}://{host}/{token}"


def get_dbconn():
    # NOTE: get_dbconn() is not thread safe.  Don't use threaded server.
    global _dbconn

    if _dbconn is None:
        _dbconn = MySQLdb.connect(
            host=dbhost,
            port=int(dbport),
            user=dbuser,
            password=dbpass,
            database=dbname,
            charset="utf8mb4",
            autocommit=True,
        )

    return _dbconn


@contextlib.contextmanager
def writedb():
    conn = get_dbconn()
    conn.begin()
    try:
        yield conn
    except:
        conn.rollback()
        raise
    else:
        conn.commit()


def check_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = None
        auth = request.authorization
        if auth:
            with writedb() as db:
                try:
                    user = model.get_auth(db, auth.username, auth.password)
                except model.InvalidAuth as e:
                    return e.msg, 400
        return f(*args, **kwargs, user=user)
    return decorated


@app.errorhandler(Exception)
def errohandler(err):
    app.logger.exception("FAIL")
    return err, 500


@app.route('/', methods=["GET"])
@check_auth
def index(user):
    if user:
        db = get_dbconn()
        pastes = model.get_pastes_by_userid(db, user.id, limit=10)
        return MANUAL_PASTES.format(
            get_host(),
            "\n".join("{}".format(p) for p in pastes)
        )
    if is_from_browser():
        return render_template('index.html', host=get_host())
    return MANUAL.format(get_host())


@app.route('/', methods=["POST"])
@check_auth
def save_paste(user):
    text = request.form.get('f')
    public = bool(request.form.get('public'))
    if not text:
        return "form parameter `f` is required", 400
    with writedb() as db:
        paste = model.save(db, text, user, public)
    if is_from_browser():
        return redirect(f'/{paste.token}', code=302)
    return get_paste_url(paste.token)


@app.route('/<string:token>', methods=['GET'])
@check_auth
def load_paste(token, user):
    db = get_dbconn()
    try:
        paste = model.load(db, token, user)
    except model.PasteNotFound:
        return "no such paste", 404
    if is_from_browser():
        rendered = highlight.colorize(paste.document, 'text', formatter=highlight.Formatter.HTML)
        return render_template('paste.html', rendered=rendered)
    return paste.document


@app.route('/<string:token>/', methods=['GET'])
@check_auth
def read_with_guessed_highlignt(token, user):
    db = get_dbconn()
    try:
        paste = model.load(db, token, user)
    except model.PasteNotFound as e:
        return e.msg, 404
    if is_from_browser():
        rendered = highlight.colorize(paste.document, formatter=highlight.Formatter.HTML)
        return render_template('paste.html', rendered=rendered)
    rendered = highlight.colorize(paste.document, formatter=highlight.Formatter.TERMINAL)
    return rendered['text']


@app.route('/<string:token>/<string:lexer_name>', methods=['GET'])
@check_auth
def read_with_highlight(token, lexer_name, user):
    db = get_dbconn()
    try:
        paste = model.load(db, token, user)
    except model.PasteNotFound:
        return "no such paste", 404
    is_html = is_from_browser()
    formatter = highlight.Formatter.HTML if is_html else highlight.Formatter.TERMINAL
    rendered = highlight.colorize(paste.document, lexer_name, formatter)
    if is_html:
        return render_template('paste.html', rendered=rendered)
    return rendered['text']
