# -*- coding: utf-8 -*-
# Thread-local state shared by the shims and the HTTP handlers:
# collected GUI items, dialog messages, keyboard input, and a small log ring.

import collections
import threading

_local = threading.local()
_logring = collections.deque(maxlen=400)
_loglock = threading.Lock()


def _state():
    try:
        return _local.s
    except AttributeError:
        s = {
            'items': [],
            'messages': [],
            'errors': [],
            'keyboard': '',
            'page_choices': None,
        }
        _local.s = s
        return s


def reset(keyboard='', page_choices=None):
    s = _state()
    s['items'] = []
    s['messages'] = []
    s['errors'] = []
    s['keyboard'] = keyboard or ''
    s['page_choices'] = page_choices


def items():
    return _state()['items']


def messages():
    return _state()['messages']


def errors():
    return _state()['errors']


def keyboard_text():
    return _state()['keyboard']


def page_choices():
    return _state()['page_choices']


def add_item(item):
    _state()['items'].append(item)


def message(text):
    m = str(text)
    _state()['messages'].append(m)
    log('message: ' + m)


def error(text):
    e = str(text)
    _state()['errors'].append(e)
    log('error: ' + e)


def log(text):
    with _loglock:
        _logring.append(text[:500])


def recent_logs(n=200):
    with _loglock:
        return list(_logring)[-n:]
