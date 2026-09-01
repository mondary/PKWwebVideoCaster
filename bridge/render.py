# -*- coding: utf-8 -*-
# Minimal mobile-first HTML rendering. Pages are meant to be browsed from
# Web Video Caster: any <video> / media URL that appears gets picked up by
# the WVC drawer.

import html
import urllib.parse

BASE_CSS = """
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;font:16px/1.45 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:#101418;color:#e8eaed;padding:14px;max-width:760px;margin-inline:auto}
a{color:#7ab8ff;text-decoration:none}
a:active{opacity:.7}
h1{font-size:1.25rem;margin:.2rem 0 .8rem}
h1 small{display:block;color:#9aa0a6;font-weight:400;font-size:.8rem}
.list{list-style:none;margin:0;padding:0}
.list li{border-bottom:1px solid #23282e}
.list a{display:flex;gap:10px;align-items:center;padding:11px 2px}
.list img{width:56px;height:84px;object-fit:cover;border-radius:4px;flex:none;background:#23282e}
.list .t{flex:1;min-width:0}
.list .t small{color:#9aa0a6;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.badge{font-size:.72rem;background:#23282e;border-radius:4px;padding:2px 6px;color:#c3c8cd;flex:none}
video{width:100%;border-radius:8px;background:#000;margin:10px 0}
input[type=text],select{width:100%;padding:11px;border-radius:8px;border:1px solid #2c333a;
     background:#191f26;color:#e8eaed;font-size:1rem;margin:4px 0 10px}
button{padding:11px 18px;border-radius:8px;border:0;background:#2f6fed;color:#fff;font-size:1rem}
.msg{background:#1d2733;border-left:3px solid #2f6fed;padding:8px 10px;border-radius:4px;
     margin:6px 0;font-size:.85rem;color:#b9c4cf}
.err{background:#2b1d1f;border-left-color:#e2574c;color:#f0b9b4}
pre{white-space:pre-wrap;font-size:.75rem;color:#9aa0a6}
.footer{margin-top:18px;color:#5f666d;font-size:.78rem}
"""


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def page(title, body, back=None):
    nav = '<p><a href="%s">&#8592; Retour</a></p>' % esc(back) if back else ''
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><style>%s</style></head><body>%s<h1>%s</h1>%s'
            '<p class="footer">PKWwebVideoCaster &#183; bridge vStream &#8594; Web Video Caster</p>'
            '</body></html>') % (esc(title), BASE_CSS, nav, esc(title), body)


def render_messages(messages, errors):
    out = []
    for m in messages or []:
        out.append('<div class="msg">%s</div>' % esc(m))
    for e in errors or []:
        out.append('<div class="msg err">%s</div>' % esc(e))
    return ''.join(out)


def render_items(base_path, data, site, back=None):
    """data: runner.call_site result -> list HTML."""
    out = [render_messages(data.get('messages'), data.get('errors'))]
    if not data['items'] and data['ok']:
        out.append('<div class="msg">Aucun r&eacute;sultat.</div>')
    if not data['ok'] and not data['items']:
        out.append('<div class="msg err">Erreur du site (voir /debug).</div>')

    out.append('<ul class="list">')
    for it in data['items']:
        kind = it.get('kind')
        if kind == 'text':
            out.append('<li><div class="t">%s</div></li>' % esc(it.get('label')))
            continue
        if kind == 'play':
            play_params = {
                'hoster': it.get('hoster', ''),
                'url': it.get('url', ''),
                'name': it.get('title', ''),
                'file': it.get('file', ''),
            }
            if back:
                play_params['back'] = back
            qs = urllib.parse.urlencode(play_params, doseq=True)
            label = it.get('title') or it.get('file') or 'Lecture'
            out.append(_li('%s/play?%s' % (base_path, qs), label,
                           it.get('thumb'), badge=it.get('hoster', '')))
            continue
        # Preserve the page containing this directory item. WVC can omit the
        # Referer header when it opens a playback page.
        params = dict(it.get('params') or {})
        if back:
            params['back'] = back
        qs = urllib.parse.urlencode(params, doseq=True)
        href = '%s/nav?site=%s&function=%s' % (
            base_path, urllib.parse.quote(it.get('site') or site),
            urllib.parse.quote(it.get('function') or 'load'))
        if qs:
            href += '&' + qs
        badge = {'episode': 'EP', 'season': 'SAISON', 'next': 'SUIVANT'}.get(kind, '')
        out.append(_li(href, it.get('label'), it.get('thumb'), badge=badge))
    out.append('</ul>')
    return ''.join(out)


def _li(href, label, thumb, badge=''):
    img = ('<img loading="lazy" src="%s" onerror="this.style.visibility=\'hidden\'">'
           % esc(thumb)) if thumb else ''
    b = '<span class="badge">%s</span>' % esc(badge) if badge else ''
    return ('<li><a href="%s">%s<span class="t">%s</span>%s</a></li>'
            % (esc(href), img, esc(label), b))


def render_play(title, result, base_url, back):
    """result: guihoster.resolve_media output dict."""
    from bridge import m3u8proxy
    raw = result['url']
    base, headers = m3u8proxy.split_pipe(raw)
    token = m3u8proxy.register(raw)
    proxied = base_url + m3u8proxy.proxy_url(token, base)

    body = []
    body.append('<video controls autoplay muted playsinline preload="auto" '
                'src="%s"></video>' % esc(proxied))
    body.append('<ul class="list">'
                '<li><a href="%s"><span class="t">Flux via proxy (WVC) '
                '<small>%s</small></span></a></li>'
                '<li><a href="%s"><span class="t">URL brute (sans header) '
                '<small>%s</small></span></a></li></ul>'
                % (esc(proxied), esc(base), esc(base), esc(base)))
    if headers:
        body.append('<p class="msg">Headers appliqu&eacute;s par le proxy : %s</p>'
                    % esc(', '.join(sorted(headers))))
    if result.get('subtitles'):
        body.append('<p class="msg">Sous-titres : %s</p>' % esc(result['subtitles']))
    return page(title, ''.join(body), back=back)
