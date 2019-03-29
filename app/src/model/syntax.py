# -*- coding: utf-8 -*-

from enum import Enum
from pygments import highlight
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.util import ClassNotFound
from pygments.formatters import HtmlFormatter, TerminalFormatter

from ..utils import LexerNotFound


class Formatter(Enum):
    HTML = 0
    TERMINAL = 1


def colorize(text, lexer_name=None, formatter=Formatter.TERMINAL):
    try:
        lexer = get_lexer_by_name(lexer_name) if lexer_name else guess_lexer(text)
    except ClassNotFound:
        lexer = get_lexer_by_name('text')
    if formatter is Formatter.HTML:
        formatter = HtmlFormatter()
        text = highlight(text, lexer, formatter)
        style = formatter.get_style_defs('.highlight')
        return {'text': text, 'style': style}
    text = highlight(text, lexer, TerminalFormatter())
    return {'text': text}
