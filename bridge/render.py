# -*- coding: utf-8 -*-
# Rich mobile-first HTML rendering. Pages are meant to be browsed from
# Web Video Caster: any <video> / media URL that appears gets picked up by
# the WVC drawer.
#
# Visual style: dark cinematic UI, large poster grid cards with gradient
# overlays, gradient hero header on the home page.

import html
import urllib.parse

BASE_CSS = """
:root{color-scheme:dark;
      --bg:#0a0e17;--bg2:#0d1320;--card:#131a2a;--card2:#182135;
      --line:#1e2a42;--text:#eef1f8;--muted:#8d96ad;--acc:#3b82f6;--acc2:#22d3ee}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:var(--bg);color:var(--text)}
a{color:inherit;text-decoration:none}
a:active{opacity:.75}
a:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
img{display:block}

/* ---------- top bar ---------- */
.topbar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:10px;
        padding:10px 14px;background:rgba(10,14,23,.82);
        -webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);
        border-bottom:1px solid var(--line)}
.topbar .back{width:38px;height:38px;flex:none;display:flex;align-items:center;
              justify-content:center;border-radius:12px;
              background:var(--card);border:1px solid var(--line);font-size:1.05rem}
.topbar h1{font-size:1.02rem;font-weight:700;margin:0;flex:1;min-width:0;
           overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* ---------- hero ---------- */
.hero{position:relative;padding:34px 20px 30px;overflow:hidden;
      background:radial-gradient(1100px 380px at 85% -20%,rgba(59,130,246,.28),transparent 60%),
                 radial-gradient(800px 320px at -10% 110%,rgba(34,211,238,.16),transparent 55%),
                 linear-gradient(160deg,#0e1a33 0%,#0a0e17 70%)}
.hero::after{content:'';position:absolute;inset:auto 0 0 0;height:70px;
             background:linear-gradient(180deg,transparent,var(--bg));pointer-events:none}
.hero>*{position:relative;z-index:1}
.hero .brand{font-size:1.65rem;font-weight:800;letter-spacing:-.02em;
             background:linear-gradient(92deg,#fff 20%,#7ab8ff 70%,#22d3ee 105%);
             -webkit-background-clip:text;background-clip:text;
             -webkit-text-fill-color:transparent;color:transparent}
.hero p{margin:6px 0 18px;color:var(--muted);font-size:.9rem}

/* ---------- search ---------- */
.search{display:flex;gap:8px;padding:2px 16px 6px;margin-top:-14px;z-index:2;position:relative}
.search select{flex:1;min-width:0}
.search input[type=text]{flex:1.4;min-width:0}
.search select,.search input[type=text]{padding:13px;border-radius:14px;
      border:1px solid var(--line);background:var(--card);color:var(--text);font-size:1rem;
      box-shadow:0 8px 24px rgba(0,0,0,.35);margin:0}
.search button{padding:13px 20px;border-radius:14px;border:0;font-size:.95rem;font-weight:700;
      color:#fff;background:linear-gradient(135deg,var(--acc),var(--acc2));
      box-shadow:0 8px 20px rgba(59,130,246,.35);flex:none}

/* ---------- rails (home sources) ---------- */
.rail{display:flex;gap:10px;overflow-x:auto;padding:4px 16px 8px;
      scrollbar-width:none;-webkit-overflow-scrolling:touch}
.rail::-webkit-scrollbar{display:none}
.chip{flex:none;display:flex;align-items:center;min-height:46px;padding:0 18px;
      border-radius:14px;font-weight:600;font-size:.92rem;max-width:220px;
      background:linear-gradient(135deg,var(--card),var(--card2));
      border:1px solid var(--line);box-shadow:0 4px 14px rgba(0,0,0,.28);
      white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chip.main{color:#fff;background:linear-gradient(135deg,#1d4ed8,#38bdf8);
           border-color:transparent;box-shadow:0 6px 18px rgba(56,189,248,.30)}
.section{margin:14px 0 6px;padding:0 16px;font-size:.78rem;font-weight:800;
         letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}

/* ---------- poster grid ---------- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));
      gap:12px;padding:12px 16px 22px}
.card{position:relative;display:block;border-radius:14px;overflow:hidden;
      background:var(--card);border:1px solid var(--line);
      box-shadow:0 8px 22px rgba(0,0,0,.38);min-height:100px}
.card img{width:100%;aspect-ratio:2/3;object-fit:cover;background:var(--card2)}
.card .ph{display:flex;align-items:center;justify-content:center;aspect-ratio:2/3;
      background:linear-gradient(160deg,#1b2947 0%,#111827 60%,#0b0f19 100%);
      color:#5f6c8a;font-size:2.3rem;font-weight:800;user-select:none;
      letter-spacing:.02em}
.card .ov{position:absolute;inset:auto 0 0 0;padding:26px 10px 10px;
      background:linear-gradient(180deg,transparent,rgba(6,9,15,.88) 68%)}
.card .ov .t{font-weight:600;font-size:.86rem;line-height:1.3;
      display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
      overflow:hidden;text-shadow:0 1px 3px rgba(0,0,0,.7);word-break:break-word}
.card .ov .s{display:block;margin-top:3px;font-size:.68rem;font-weight:700;
      letter-spacing:.06em;text-transform:uppercase;
      background:linear-gradient(92deg,var(--acc2),var(--acc));
      -webkit-background-clip:text;background-clip:text;
      -webkit-text-fill-color:transparent;color:transparent}
.card.badge::after{content:attr(data-badge);position:absolute;top:8px;right:8px;
      padding:3px 8px;border-radius:8px;font-size:.62rem;font-weight:800;
      letter-spacing:.07em;text-transform:uppercase;color:#dff1ff;
      background:linear-gradient(135deg,rgba(37,99,235,.92),rgba(14,165,233,.85));
      box-shadow:0 2px 8px rgba(2,8,20,.5)}
.card{position:relative;display:block;border-radius:14px;overflow:hidden;
      background:var(--card);border:1px solid var(--line);
      box-shadow:0 8px 22px rgba(0,0,0,.38)}
.card .ph{display:flex;align-items:center;justify-content:center;aspect-ratio:2/3;
      background:linear-gradient(160deg,#1b2947 0%,#111827 60%,#0b0f19 100%);
      color:#5f6c8a;font-size:2.3rem;font-weight:800;user-select:none;
      letter-spacing:.02em}
.card.txt .ph{font-size:1rem;padding:12px;text-align:center;font-weight:600;
      color:#aeb9d6}
.card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
      background:var(--card2)}

/* ---------- player / misc ---------- */
video{width:100%;border-radius:12px;background:#000;margin:12px 0 6px;
      box-shadow:0 12px 34px rgba(0,0,0,.5)}
.msg{background:var(--card);border-left:3px solid var(--acc);padding:10px 12px;
     border-radius:10px;margin:8px 16px;font-size:.84rem;color:#c3cdda}
.msg.err{background:#2a161c;border-left-color:#f0625d;color:#f6c3c0}
pre{white-space:pre-wrap;font-size:.74rem;color:var(--muted);padding:0 16px}
.footer{padding:18px 16px 26px;color:#525b6e;font-size:.75rem;text-align:center}
.empty{padding:34px 16px;text-align:center;color:var(--muted);font-size:.9rem}
"""

_LOGO_LETTERS = {}


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def page(title, body, back=None, hero=False):
    if back:
        nav = ('<div class="topbar"><a class="back" href="%s">&#8592;</a>'
               '<h1>%s</h1></div>' % (esc(back), esc(title)))
    elif hero:
        nav = ''
    else:
        nav = '<div class="topbar"><h1>%s</h1></div>' % esc(title)
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,'
            'viewport-fit=cover">'
            '<title>%s</title><style>%s</style></head><body>%s%s'
            '<p class="footer">PKWwebVideoCaster &#183; bridge vStream &#8594; '
            'Web Video Caster</p></body></html>'
            ) % (esc(title), BASE_CSS, nav, body)


def hero(title, subtitle):
    return ('<div class="hero"><div class="brand">%s</div><p>%s</p></div>'
            % (esc(title), esc(subtitle)))


def render_messages(messages, errors):
    out = []
    for m in messages or []:
        out.append('<div class="msg">%s</div>' % esc(m))
    for e in errors or []:
        out.append('<div class="msg err">%s</div>' % esc(e))
    return ''.join(out)


def _placeholder(label):
    text = (label or '').strip()
    letter = text[0].upper() if text else '&#9654;'
    return '<div class="ph">%s</div>' % esc(letter)


def _card(href, label, thumb, sub='', badge=''):
    cls = 'card' + (' badge" data-badge="%s' % esc(badge) if badge else '')
    img = ('<img loading="lazy" src="%s" alt="" onerror="this.remove()">'
           % esc(thumb)) if thumb else ''
    sub_html = '<span class="s">%s</span>' % esc(sub) if sub else ''
    return ('<a class="%s" href="%s">%s%s<div class="ov">'
            '<div class="t">%s</div>%s</div></a>'
            % (cls, esc(href), _placeholder(label), img, esc(label), sub_html))

def render_items(base_path, data, site, back=None):
    """data: runner.call_site result -> poster grid HTML."""
    out = [render_messages(data.get('messages'), data.get('errors'))]
    if not data['items'] and data['ok']:
        out.append('<div class="empty">Aucun r&eacute;sultat.</div>')
    if not data['ok'] and not data['items']:
        out.append('<div class="msg err">Erreur du site (voir /debug).</div>')

    out.append('<div class="grid">')
    for it in data['items']:
        kind = it.get('kind')
        if kind == 'text':
            label = it.get('label') or ''
            out.append('<div class="card txt"><div class="ph">%s</div></div>'
                       % esc(label))
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
            out.append(_card('%s/play?%s' % (base_path, qs), label,
                             it.get('thumb'), sub=it.get('hoster', '')))
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
        out.append(_card(href, it.get('label'), it.get('thumb'), badge=badge))
    out.append('</div>')
    return ''.join(out)


def render_play(title, result, base_url, back):
    """result: guihoster.resolve_media output dict."""
    from bridge import m3u8proxy
    raw = result['url']
    base, headers = m3u8proxy.split_pipe(raw)
    token = m3u8proxy.register(raw)
    proxied = base_url + m3u8proxy.proxy_url(token, base)

    body = ['<div class="topbar"><a class="back" href="%s">&#8592;</a>'
            '<h1>%s</h1></div>' % (esc(back), esc(title))]
    body.append('<video controls autoplay muted playsinline preload="auto" '
                'src="%s"></video>' % esc(proxied))
    body.append('<ul class="list">'
                '<li><a href="%s"><span class="go">&#9654;</span>'
                '<span class="t">Flux via proxy (WVC)<small>%s</small></span></a></li>'
                '<li><a href="%s"><span class="go">&#128279;</span>'
                '<span class="t">URL brute (sans header)<small>%s</small></span></a></li>'
                '</ul>'
                % (esc(proxied), esc(base), esc(base), esc(base)))
    if headers:
        body.append('<p class="msg">Headers appliqu&eacute;s par le proxy : %s</p>'
                    % esc(', '.join(sorted(headers))))
    if result.get('subtitles'):
        body.append('<p class="msg">Sous-titres : %s</p>' % esc(result['subtitles']))
    return page(title, ''.join(body), back=back)
