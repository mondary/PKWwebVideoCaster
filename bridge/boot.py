# -*- coding: utf-8 -*-
# Wires the vendored vStream code to the headless shims.
#
# Mechanism: `bridge/shim_overlay/resources` is a shadow `resources` package
# placed ahead of the vendored tree on sys.path. Its `__init__`s extend
# `__path__` with the vendored dirs, so the four replaced modules
# (comaddon, gui.gui, gui.hoster, player) resolve to the shim, while every
# other module (handler, sites, hosters, parser, util, cloudscraper, ...)
# resolves to the vendored file. xbmc/xbmcgui/... stubs live in bridge/shim,
# also on sys.path. Must run once before any site import.

import os
import sys

BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BRIDGE_DIR)
VENDOR_ADDON_DIR = os.path.join(ROOT_DIR, 'venom', 'plugin.video.vstream')
SHIM_DIR = os.path.join(BRIDGE_DIR, 'shim')
OVERLAY_DIR = os.path.join(BRIDGE_DIR, 'shim_overlay')

_booted = False


def setup():
    global _booted
    if _booted:
        return

    # priorité finale : OVERLAY > SHIM > VENDOR > ROOT
    for p in (ROOT_DIR, VENDOR_ADDON_DIR, SHIM_DIR, OVERLAY_DIR):
        if p not in sys.path:
            sys.path.insert(0, p)
    # Équivalent hors Kodi de script.module.dnspython : contourne les
    # réponses DNS empoisonnées par certains FAI (dood.to -> ::1).
    from bridge.dns import install_public_dns_fallback
    install_public_dns_fallback()


    # garantit que cRequestHandler.request() renvoie toujours str :
    # certains upstream renvoient parfois du bytes, ce qui casse les regex.
    import resources.lib.handler.requestHandler as rh
    _orig_request = rh.cRequestHandler.request

    def _request_str(self, jsonDecode=False):
        r = _orig_request(self, jsonDecode)
        if isinstance(r, bytes):
            r = r.decode('utf-8', errors='replace')
        return r

    rh.cRequestHandler.request = _request_str

    # contrôle: cGui et siteManager doivent être les shims
    from resources.lib.gui.gui import cGui
    from bridge.shim.gui import cGui as _ShimGui
    if cGui is not _ShimGui:
        raise ImportError('overlay resources/lib/gui/gui.py non actif')

    _booted = True


def site_manager():
    setup()
    from bridge.shim.comaddon import siteManager
    return siteManager()
