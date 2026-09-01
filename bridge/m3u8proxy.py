# -*- coding: utf-8 -*-
# Header-aware stream proxy.
#
# vStream resolvers return "url|Header=Value&Header=Value" (Kodi convention).
# WVC/Chromecast cannot send custom headers, so the bridge re-serves the
# stream itself: HLS playlists are rewritten so every URI goes back through
# this proxy, and segments/files are fetched with the stored headers.

import re
import secrets
import threading

import requests

from bridge.boot import setup

_lock = threading.Lock()
_tokens = {}

DEFAULT_UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36')


def split_pipe(url):
    """'http://x/f.m3u8|Referer=http://a&User-Agent=U' -> (url, headers)."""
    if '|' not in url:
        return url, {}
    base, hs = url.split('|', 1)
    headers = {}
    for kv in hs.split('&'):
        if '=' in kv:
            k, v = kv.split('=', 1)
            headers[k.strip()] = v
    return base, headers


def register(url_with_headers):
    setup()
    base, headers = split_pipe(url_with_headers)
    token = secrets.token_urlsafe(9)
    with _lock:
        _tokens[token] = {'url': base, 'headers': headers}
    return token


def get_entry(token):
    with _lock:
        return _tokens.get(token)


def proxy_url(token, absolute_url):
    from urllib.parse import quote
    return '/stream?t=%s&u=%s' % (token, quote(absolute_url, safe=''))


PLAYLIST_HINTS = ('.m3u8', 'm3u8')


def looks_like_playlist(url, content_type, head):
    if head is not None:
        return head.lstrip().startswith('#EXTM3U')
    low = url.split('?')[0].lower()
    if any(h in low for h in PLAYLIST_HINTS):
        return True
    ct = (content_type or '').lower()
    return 'mpegurl' in ct


_URI_ATTR = re.compile(r'URI="([^"]+)"')


def rewrite_playlist(text, base_url, token):
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            out.append(line)
            continue
        if s.startswith('#'):
            if 'URI="' in s:
                def _sub(m):
                    return 'URI="%s"' % proxy_url(token, _join(base_url, m.group(1)))
                s = _URI_ATTR.sub(_sub, s)
            out.append(s)
        else:
            out.append(proxy_url(token, _join(base_url, s)))
    return '\n'.join(out) + '\n'


def _join(base, ref):
    from urllib.parse import urljoin
    return urljoin(base, ref)


class ProxyFetchError(Exception):
    pass


def open_stream(token, target_url, range_header=None, timeout=20):
    """Fetch a proxied URL; returns a requests.Response (stream=True)."""
    entry = get_entry(token)
    if not entry:
        raise ProxyFetchError('token inconnu ou expiré')
    headers = dict(entry['headers'])
    headers.setdefault('User-Agent', DEFAULT_UA)
    if range_header:
        headers['Range'] = range_header
    try:
        resp = requests.get(target_url, headers=headers, timeout=timeout,
                            stream=True, allow_redirects=True)
    except requests.RequestException as e:
        raise ProxyFetchError('upstream: %s' % e)
    return resp
