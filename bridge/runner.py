# -*- coding: utf-8 -*-
# Executes vStream site functions headlessly: sets sys.argv like Kodi does,
# calls the function, returns the items captured by the fake cGui.

import importlib
import sys
import traceback
from urllib.parse import urlencode

from bridge import shimstate
from bridge.boot import setup

# params réservés au bridge, jamais transmis au code vStream
BRIDGE_PARAMS = ('site', 'function', 'keyboard', 'page', 'back')

_site_modules = {}


def _module(site):
    mod = _site_modules.get(site)
    if mod is None:
        mod = importlib.import_module('resources.sites.' + site)
        _site_modules[site] = mod
    return mod


def call_site(site, function, params=None, keyboard='', page=None):
    """Run <site>.<function> with Kodi-style argv; return dict of captured state."""
    setup()
    shimstate.reset(keyboard=keyboard or '', page_choices=page)

    passthrough = {k: v for k, v in (params or {}).items()
                   if k not in BRIDGE_PARAMS and v not in (None, '')}
    qs = urlencode(passthrough, doseq=True)
    old_argv = sys.argv
    sys.argv = ['plugin://plugin.video.vstream/', '1', ('?' + qs) if qs else '']
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
    setup()
    shimstate.reset()
    try:
        mod = _module(site)
        search = getattr(mod, 'URL_SEARCH_MOVIES', None) or getattr(mod, 'URL_SEARCH', None)
        if not search:
            raise AttributeError('%s n\'expose pas URL_SEARCH' % site)
        fn = getattr(mod, search[1], None)
        if fn is None:
            raise AttributeError('%s n\'expose pas %s()' % (site, search[1]))

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
