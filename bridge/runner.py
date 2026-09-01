# -*- coding: utf-8 -*-
# Executes vStream site functions headlessly: sets sys.argv like Kodi does,
# calls the function, returns the items captured by the fake cGui.

import importlib
import sys
import threading
import time
import traceback
from urllib.parse import urlencode

from bridge import shimstate
from bridge.boot import setup

# params réservés au bridge, jamais transmis au code vStream
BRIDGE_PARAMS = ('site', 'function', 'keyboard', 'page', 'back',
                 'pages', 'fragment')

# sys.argv est un global : les exécutions (utilisateur + health-check en
# fond) doivent être sérialisées, sinon les params se corrompent.
argv_lock = threading.RLock()

# timestamp de la dernière requête pilotée par l'utilisateur (pour laisser
# la priorité au trafic réel avant un probe de health-check)
_last_user_activity = 0.0

_site_modules = {}


def _module(site):
    mod = _site_modules.get(site)
    if mod is None:
        mod = importlib.import_module('resources.sites.' + site)
        _site_modules[site] = mod
    return mod


def mark_user_activity():
    """Appelé par le serveur à chaque requête réelle de l'utilisateur."""
    global _last_user_activity
    _last_user_activity = time.time()


def user_idle_seconds():
    return time.time() - _last_user_activity


def call_site(site, function, params=None, keyboard='', page=None,
              background=False):
    """Run <site>.<function> with Kodi-style argv; return dict of captured state.

    background=True (health-check) : cède la place aux requêtes utilisateur
    récentes avant de prendre le verrou argv."""
    if background:
        while user_idle_seconds() < 30:
            time.sleep(5)
    with argv_lock:
        setup()
        shimstate.reset(keyboard=keyboard or '', page_choices=page)

        passthrough = {k: v for k, v in (params or {}).items()
                       if k not in BRIDGE_PARAMS and v not in (None, '')}
        qs = urlencode(passthrough, doseq=True)
        old_argv = sys.argv
        sys.argv = ['plugin://plugin.video.vstream/', '1',
                    ('?' + qs) if qs else '']
        try:
            mod = _module(site)
            fn = getattr(mod, function or 'load', None)
            if fn is None:
                raise AttributeError('%s n\'expose pas %s()' % (site, function))
            fn()
            return {
                'ok': True,
                'items': list(shimstate.items()),
                'messages': list(shimstate.messages()),
                'errors': list(shimstate.errors()),
            }
        except Exception:
            return {
                'ok': False,
                'items': list(shimstate.items()),
                'messages': list(shimstate.messages()),
                'errors': list(shimstate.errors()) + [traceback.format_exc()],
            }
        finally:
            sys.argv = old_argv

def run_search(site, q):
    """Recherche par site : portage de default.py::_pluginSearch.

    Protocole vStream : window(10101).setProperty('search','true') puis appel
    direct de la fonction URL_SEARCH[1] avec URL_SEARCH[0] + texte quoté.
    """
    with argv_lock:
        setup()
        shimstate.reset()
        try:
            mod = _module(site)
            search = getattr(mod, 'URL_SEARCH_MOVIES', None) or getattr(
                mod, 'URL_SEARCH', None)
            if not search:
                raise AttributeError('%s n\'expose pas URL_SEARCH' % site)
            fn = getattr(mod, search[1], None)
            if fn is None:
                raise AttributeError('%s n\'expose pas %s()'
                                     % (site, search[1]))

            from bridge.shim.comaddon import window
            from resources.lib.util import Quote
            window(10101).setProperty('search', 'true')
            old_argv = sys.argv
            sys.argv = ['plugin://plugin.video.vstream/', '1', '']
            try:
                fn(search[0] + str(Quote(q)))
                return {
                    'ok': True,
                    'items': list(shimstate.items()),
                    'messages': list(shimstate.messages()),
                    'errors': list(shimstate.errors()),
                }
            finally:
                window(10101).setProperty('search', 'false')
                sys.argv = old_argv
        except Exception:
            return {
                'ok': False,
                'items': list(shimstate.items()),
                'messages': list(shimstate.messages()),
                'errors': list(shimstate.errors()) + [traceback.format_exc()],
            }
