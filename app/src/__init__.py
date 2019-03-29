# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, redirect

from .model.paste import save, load
from .model.syntax import colorize, Formatter
from .utils import LexerNotFound, PasteNotFound, NoAvailableID


app = Flask(__name__)


def is_from_browser(req):
    user_agent = req.headers.get('User-Agent', '')
    if user_agent.startswith("Mozilla"):
        return True
    return False

def get_host(req):
    return req.host

def get_paste_url(req, paste_id):
    proto = req.headers.get('X-Forwarded-Proto', 'http')
    host = get_host(req)
    return f"{proto}://{host}/{paste_id}"


@app.route('/', methods=["GET"])
def index():
    if is_from_browser(request):
        return render_template('index.html', host=get_host(request))
    return "TL;DR: curl -F 'f=<-' {}".format(get_host(request))


@app.route('/', methods=["POST"])
def paste():
    text = request.args.get('f') or request.form.get('f')
    if not text:
        return ""
    paste_id = save(text)
    if is_from_browser(request):
        return redirect(f'/{paste_id}', code=302)
    return get_paste_url(request, paste_id)


@app.route('/<paste_id>', methods=['GET'])
def read(paste_id):
    try:
        text = load(paste_id)
    except PasteNotFound:
        return "no such paste", 404
    except NoAvailableID:
        return "no available id: please access later", 503
    if is_from_browser(request):
        rendered = colorize(text, formatter=Formatter.HTML)
        return render_template('paste.html', rendered=rendered)
    return text


@app.route('/<paste_id>/', methods=['GET'])
def read_with_guessed_highlignt(paste_id):
    try:
        text = load(paste_id)
    except PasteNotFound:
        return "no such paste", 404
    except NoAvailableID:
        return "no available id: please access later", 503
    if is_from_browser(request):
        rendered = colorize(text, formatter=Formatter.HTML)
        return render_template('paste.html', rendered=rendered)
    rendered = colorize(text, formatter=Formatter.TERMINAL)
    return rendered['text']


@app.route('/<paste_id>/<lexer_name>', methods=['GET'])
def read_with_highlight(paste_id, lexer_name):
    try:
        text = load(paste_id)
    except PasteNotFound:
        return "no such paste", 404
    except NoAvailableID:
        return "no available id: please access later", 503
    is_html = is_from_browser(request)
    formatter = Formatter.HTML if is_html else Formatter.TERMINAL
    rendered = colorize(text, lexer_name, formatter)
    if is_html:
        return render_template('paste.html', rendered=rendered)
    return rendered['text']
