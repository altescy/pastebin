# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass
import bcrypt
import MySQLdb


class AccountIdConflict(Exception):
    msg = "account id conflict"


class UserNotFound(Exception):
    msg = "user not found"


class InvalidAuth(Exception):
    msg = "invalid auth"


@dataclass
class User:
    id: int
    account_id: str
    password: bytes
    created_at: datetime
    updated_at: datetime
    deleted_at: typing.Optional[datetime] = None

    def __init__(self, id, account_id, password, created_at, updated_at, deleted_at):
        if isinstance(account_id, bytes):
            account_id = account_id.decode()

        self.id = id
        self.account_id = account_id
        self.password = password
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def to_json(self):
        return {
            "id": self.id,
            "name": self.account_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def signup(db, account_id: str, password: str):
    hpass = bcrypt.hashpw(password.encode(), bcrypt.gensalt(10))

    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO user (account_id, password, created_at, updated_at) VALUES (%s, %s, NOW(6), NOW(6))",
            (account_id, hpass),
        )
    except MySQLdb.IntegrityError:
        raise AccountIdConflict


def signin(db, account_id: str, password: str) -> User:
    cur = db.cursor()
    cur.execute("SELECT * FROM user WHERE account_id = %s AND (deleted_at IS NULL)", (account_id,))
    row = cur.fetchone()
    if not row:
        raise UserNotFound
    user = User(*row)

    if not bcrypt.checkpw(password.encode(), user.password):
        raise InvalidAuth

    return user


def get_auth(db, account_id: str, password: str) -> User:
    try:
        user = signin(db, account_id, password)
    except UserNotFound:
        signup(db, account_id, password)
        user = signin(db, account_id, password)
    return user
