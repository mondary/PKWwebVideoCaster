# -*- coding: utf-8 -*-
# PKWwebVideoCaster — local bridge server.
# Browse vStream catalogs (fs16.lol & co) from Web Video Caster.

import json
import os
import socket
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from bridge import m3u8proxy, render, runner
from bridge.shim.guihoster import ResolveError, resolve_media

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.json')

DEFAULT_SEARCH = {
    'french_stream': [('Films', 'showSearchMovie'), ('Séries', 'showSearchSerie')],
}


def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    # ------------------------------------------------------------------ #

    def log_message(self, fmt, *args):
        try:
            sys.stderr.write('%s %s\n' % (self.address_string(), fmt % args))
        except Exception:
            pass  # requêtes binaires (handshake TLS sur le port HTTP, etc.)

    def _send(self, code, body, ctype='text/html; charset=utf-8', extra=None):
        payload = body if isinstance(body, bytes) else body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _query(self):
        parsed = urllib.parse.urlsplit(self.path)
        qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        return {k: v[0] for k, v in qs.items()}

    def _base_url(self):
        host = self.headers.get('Host')
        if not host:
            host = '%s:%d' % (self.server.server_address[0],
                              self.server.server_address[1])
        return 'http://%s' % host
    def _current_path(self):
        """Return this request as a local path for child-page links."""
        parsed = urllib.parse.urlsplit(self.path)
        path = parsed.path or '/'
        return path + (('?' + parsed.query) if parsed.query else '')

    @staticmethod
    def _local_path(value):
        """Accept only a local return path, never an external URL."""
        parsed = urllib.parse.urlsplit(value or '')
        if parsed.scheme or parsed.netloc or not parsed.path.startswith('/'):
            return None
        return parsed.path + (('?' + parsed.query) if parsed.query else '')


    # ------------------------------------------------------------------ #

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        route = parsed.path.rstrip('/') or '/'
        try:
            if route == '/':
                self._home()
            elif route == '/nav':
                self._nav(self._query())
            elif route == '/search':
                self._search(self._query())
            elif route == '/play':
                self._play(self._query())
            elif route == '/stream':
                self._stream(self._query())
            elif route == '/debug':
                self._debug()
            else:
                self._send(404, render.page('404', '<p>Inconnu.</p>'))
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            import traceback
            from bridge import shimstate
            shimstate.log(traceback.format_exc())
            self._send(500, render.page(
                'Erreur', '<div class="msg err">%s</div>'
                '<p><a href="/debug">Voir /debug</a></p>' % render.esc(e)))

    # ------------------------------------------------------------------ #

    def _home(self):
        from bridge.boot import site_manager
        sites = site_manager().listActive()
        cur = self._query().get('site', 'french_stream')
        # recherche générique : chaque source avec URL_SEARCH (protocole vStream)
        options = ''.join(
            '<option value="%s"%s>%s</option>'
            % (render.esc(s['id']),
               ' selected' if s['id'] == cur else '',
               render.esc(s['label']))
            for s in sites)
        parts = [render.hero('PKWwebVideoCaster',
                             'Cast vStream vers Web Video Caster, sans Kodi'),
                 '<form class="search" method="get" action="/search">',
                 '<select name="site">%s</select>' % options,
                 '<input type="text" name="q" '
                 'placeholder="Titre, s&eacute;rie, anime&hellip;">',
                 '<button type="submit">OK</button></form>',
                 '<p class="section">Catalogue principal</p>',
                 '<div class="rail"><a class="chip main" '
                 'href="/nav?site=%s&function=showMenuMovies">'
                 'Films &amp; s&eacute;ries &#183; fs16.lol &#8594;</a></div>'
                 % urllib.parse.quote('french_stream'),
                 '<p class="section">Autres sources</p>',
                 '<div class="rail">']
        for s in sites:
            if s['id'] == 'french_stream':
                continue
            parts.append('<a class="chip" href="/nav?site=%s&function=load">%s</a>'
                         % (urllib.parse.quote(s['id']), render.esc(s['label'])))
        parts.append('</div>')
        self._send(200, render.page('PKWwebVideoCaster', ''.join(parts), hero=True))

    def _nav(self, q):
        site = q.get('site') or 'french_stream'
        function = q.get('function') or 'load'
        result = runner.call_site(site, function, params=q,
                                  keyboard=q.get('keyboard', ''),
                                  page=q.get('page'))
        body = render.render_items('', result, site, back=self._current_path())
        fallback = '/' if function == 'load' else (
            '/nav?site=%s&function=load' % urllib.parse.quote(site))
        back = self._local_path(q.get('back')) or fallback
        self._send(200, render.page(
            '%s · %s' % (site, function), body, back=back))

    def _search(self, q):
        site = q.get('site') or 'french_stream'
        query = (q.get('q') or q.get('keyboard') or '').strip()
        if not query:
            self._redirect('/')
            return
        result = runner.run_search(site, query)
        body = render.render_items('', result, site, back=self._current_path())
        self._send(200, render.page(
            'Recherche « %s » · %s' % (query, site), body,
            back='/'))

    def _play(self, q):
        url = q.get('url') or ''
        hoster = q.get('hoster') or ''
        name = q.get('name') or q.get('file') or 'Lecture'
        if not url:
            self._send(400, render.page('Lecture', '<div class="msg err">URL manquante.</div>'))
            return
        try:
            result = resolve_media(hoster, url,
                                   fileName=q.get('file', ''), title=name)
        except ResolveError as e:
            body = '<div class="msg err">R&eacute;solution impossible : %s</div>' % render.esc(e)
            body += '<p><a href="/debug">Journaux</a></p>'
            self._send(200, render.page(name, body))
            return
        back = (self._local_path(q.get('back')) or
                self._local_path(self.headers.get('Referer')) or '/')
        self._send(200, render.render_play(name, result, self._base_url(),
                                           back=back))


    def _stream(self, q):
        token = q.get('t') or ''
        target = q.get('u') or ''
        if not token or not target:
            self._send(400, 'token/url manquants', 'text/plain')
            return
        entry = m3u8proxy.get_entry(token)
        if not entry:
            self._send(404, 'token inconnu', 'text/plain')
            return
        try:
            resp = m3u8proxy.open_stream(token, target,
                                         range_header=self.headers.get('Range'))
        except m3u8proxy.ProxyFetchError as e:
            self._send(502, str(e), 'text/plain')
            return

        ctype = resp.headers.get('Content-Type', '')
        first_chunk = b''
        is_playlist = m3u8proxy.looks_like_playlist(target, ctype, None)
        if not is_playlist:
            # sonde les premiers octets pour détecter un manifeste sans extension
            try:
                first_chunk = next(resp.iter_content(512), b'')
            except StopIteration:
                first_chunk = b''
            if first_chunk[:7].lstrip().startswith(b'#EXTM3U'):
                is_playlist = True

        if is_playlist:
            body = first_chunk + resp.content
            text = body.decode('utf-8', errors='replace')
            rewritten = m3u8proxy.rewrite_playlist(text, target, token)
            resp.close()
            self._send(200, rewritten,
                       ctype='application/vnd.apple.mpegurl')
            return

        passthrough = {}
        for h in ('Content-Type', 'Content-Length', 'Content-Range',
                  'Accept-Ranges', 'Content-Encoding'):
            if h in resp.headers:
                passthrough[h] = resp.headers[h]
        if 'Content-Type' not in passthrough:
            passthrough['Content-Type'] = ctype or 'application/octet-stream'
        self.send_response(resp.status_code)
        self.send_header('Cache-Control', 'no-store')
        for k, v in passthrough.items():
            self.send_header(k, v)
        if 'Accept-Ranges' not in passthrough:
            self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        try:
            if first_chunk:
                self.wfile.write(first_chunk)
            for chunk in resp.iter_content(64 * 1024):
                if chunk:
                    self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            resp.close()

    def _debug(self):
        from bridge import shimstate
        logs = shimstate.recent_logs(200)
        body = '<pre>%s</pre>' % render.esc('\n'.join(logs) or '(vide)')
        self._send(200, render.page('Debug', body))


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except OSError:
        return '127.0.0.1'
    finally:
        s.close()


def main():
    cfg = load_config()
    host = cfg.get('host', '0.0.0.0')
    port = int(cfg.get('port', 8786))

    runner.setup()  # boot the shims before the first request

    class Server(ThreadingHTTPServer):
        daemon_threads = True

    httpd = Server((host, port), Handler)
    print('PKWwebVideoCaster prêt.')
    print('  - Sur ce Mac : http://127.0.0.1:%d' % port)
    print('  - Sur le réseau (à ouvrir dans Web Video Caster) : http://%s:%d'
          % (lan_ip(), port))
    try:
        while True:
            try:
                # une exception sur le socket d'écoute ne doit pas tuer le serveur
                httpd.serve_forever(poll_interval=0.5)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                import traceback
                traceback.print_exc()
                print('Boucle d\'écoute réinitialisée après : %r' % e)
                import time
                time.sleep(1)
    except KeyboardInterrupt:
        print('\nArrêt.')


if __name__ == '__main__':
    main()
