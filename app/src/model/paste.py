# -*- coding: utf-8 -*-

import os
import random
import string

from ..utils import PasteNotFound, NoAvailableID

CHARACTERS = string.ascii_letters + string.digits
PASTE_PATH = os.environ.get('PASTE_PATH', '/tmp/pastes')
PASTE_ID_LENGTH = int(os.environ.get('PASTE_ID_LENGTH', '4'))
MAX_GENID_COUNT = 100

os.makedirs(PASTE_PATH, exist_ok=True)

def generate_id(length):
    return ''.join([random.choice(CHARACTERS) for _ in range(length)])

def save(text):
    cnt = 0
    paste_id = generate_id(PASTE_ID_LENGTH)
    file_path = os.path.join(PASTE_PATH, paste_id)
    while os.path.exists(file_path):
        if cnt > MAX_GENID_COUNT:
            raise NoAvailableID
        cnt += 1
        paste_id = generate_id(PASTE_ID_LENGTH)
        file_path = os.path.join(PASTE_PATH, paste_id)
    with open(file_path, 'w') as f:
        f.write(text)
    return paste_id

def load(paste_id):
    file_path = os.path.join(PASTE_PATH, paste_id)
    try:
        with open(file_path, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        raise PasteNotFound
    return text
