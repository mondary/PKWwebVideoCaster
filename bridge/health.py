# -*- coding: utf-8 -*-
# Source health checks: lazily probes each vStream source in a background
# thread, caches the result in memory and in a JSON file so the home page
# can flag dead sources with a KO badge.

import json
import os
import threading
import time

from bridge.boot import setup

CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'status_cache.json')
MAX_AGE = 3600   # re-check a source after one hour

_lock = threading.Lock()
_status = {}      # id -> {'ok': bool, 'ts': float}
_pending = set()
_thread = None


def _load_cache():
    global _status
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        _status = {k: v for k, v in data.items()
                   if isinstance(v, dict) and 'ts' in v}
    except (OSError, ValueError):
        _status = {}


def _save_cache():
    try:
        with open(CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(_status, f)
    except OSError:
        pass


def _probe(site):
    from bridge import runner
    result = runner.call_site(site, 'load')
    # un site qui ne produit aucune entree est considere mort
    return bool(result.get('ok')) and bool(result.get('items'))


def _worker(sites):
    for site in sites:
        with _lock:
            if site in _pending:
                continue
            _pending.add(site)
        try:
            ok = _probe(site)
        except Exception:
            ok = False
        with _lock:
            _status[site] = {'ok': ok, 'ts': time.time()}
            _pending.discard(site)
            _save_cache()


def ensure_fresh(sites):
    """Kick a background re-check for missing/stale sources. Non-blocking."""
    global _thread
    setup()
    with _lock:
        if not _status and os.path.exists(CACHE_PATH):
            _load_cache()
        now = time.time()
        todo = [s['id'] for s in sites
                if s['id'] not in _status
                or now - _status[s['id']]['ts'] > MAX_AGE]
        if not todo or (_thread is not None and _thread.is_alive()):
            return
        _thread = threading.Thread(target=_worker, args=(todo,), daemon=True)
        _thread.start()


def refresh(sites):
    """Kick a re-check of every source right now (non-blocking)."""
    global _thread
    setup()
    with _lock:
        ids = [s['id'] for s in sites]
        _thread = threading.Thread(target=_worker, args=(ids,), daemon=True)
        _thread.start()


def get(site):
    """Status dict or None when not probed yet."""
    with _lock:
        return _status.get(site)
