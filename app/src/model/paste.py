# -*- coding: utf-8 -*-
from __future__ import annotations

import os

import logging
from datetime import datetime
from dataclasses import dataclass
import random
import string
import bcrypt
import MySQLdb

from . import user


CHARACTERS = string.ascii_letters + string.digits
PASTE_ID_LENGTH = int(os.environ.get('PASTE_ID_LENGTH', '4'))
MAX_GENID_COUNT = 100


class PasteNotFound(Exception):
    msg = "past not found"


class NoAvailableID(Exception):
    msg = "no available ID"


@dataclass
class Paste:
    id: int
    token: str
    public: bool
    user_id: typing.Optional[int]
    document: str
    created_at: datetime
    updated_at: datetime
    deleted_at: typing.Optional[datetime] = None

    def __init__(
        self, id, token, user_id, public, document, created_at, updated_at, deleted_at
    ):
        if isinstance(token, bytes):
            token = token.decode()
        if isinstance(document, bytes):
            document = document.decode()

        self.id = id
        self.token = token
        self.user_id = user_id
        self.public = public
        self.document = document
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def __repr__(self):
        token = self.token
        public = "PUBLIC" if self.public else "PRIVATE"
        created_at = self.created_at
        first3lines = "\t" + "\n\t".join(self.document.splitlines()[:3])
        return f" - {token}:  [{created_at}] {public}\n{first3lines}"


def generate_id(length):
    return ''.join([random.choice(CHARACTERS) for _ in range(length)])


def get_pastes_by_userid(db, user_id: int, limit: int) -> typing.List[Paste]:
    c = db.cursor()
    c.execute(
        "SELECT * FROM paste WHERE user_id = %s LIMIT %s",
        (user_id, limit)
    )
    return [Paste(*r) for r in c]


def save(db, document: str, user: typing.Optional[user.User], public: bool) -> Paste:
    user_id = user.id if user else None
    public = True if not user else public
    c = db.cursor()
    for _ in range(MAX_GENID_COUNT):
        token = generate_id(PASTE_ID_LENGTH)
        try:
            c.execute(
                "INSERT INTO paste (token, user_id, public, document, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(6), NOW(6))",
                (token, user_id, public, document)
            )
        except MySQLdb.IntegrityError:
            pass
        else:
            break
    else:
        raise NoAvailableID
    return load(db, token, user)


def load(db, token: str, user: typing.Optional[user.User]) -> Paste:
    c = db.cursor()
    if user:
        c.execute(
            "SELECT * FROM paste WHERE (token = %s) AND (user_id = %s) AND (deleted_at IS NULL)",
            (token, user.id)
        )
    else:
        c.execute(
            "SELECT * FROM paste WHERE public AND (token = %s) AND (deleted_at IS NULL)",
            (token,)
        )
    row = c.fetchone()
    if not row:
        raise PasteNotFound
    return Paste(*row)
