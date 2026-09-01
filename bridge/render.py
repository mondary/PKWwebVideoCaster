# -*- coding: utf-8 -*-
# Rich mobile-first HTML rendering. Pages are meant to be browsed from
# Web Video Caster: any <video> / media URL that appears gets picked up by
# the WVC drawer.
#
# Visual style: dark cinematic UI inspired by Magic UI (animated gradient
# borders, shimmer, dot patterns, glass surfaces), large poster grid cards
# with gradient overlays, gradient hero header on the home page.

import html
import urllib.parse

BASE_CSS = """
:root{color-scheme:dark;
      --bg:#0a0e17;--bg2:#0d1320;--card:#131a2a;--card2:#182135;
      --line:#1e2a42;--text:#eef1f8;--muted:#8d96ad;--acc:#3b82f6;--acc2:#22d3ee;
      --ok:#3ecf8e;--ko:#ff6b64}
@property --ga{syntax:'<angle>';inherits:false;initial-value:0deg}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:var(--bg);color:var(--text)}
a{color:inherit;text-decoration:none}
a:active{opacity:.8}
a:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
img{display:block}

/* ---------- top bar ---------- */
.topbar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:10px;
        padding:10px 14px;background:rgba(10,14,23,.75);
        -webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);
        border-bottom:1px solid var(--line)}
.topbar .back{width:38px;height:38px;flex:none;display:flex;align-items:center;
              justify-content:center;border-radius:12px;
              background:rgba(19,26,42,.8);border:1px solid var(--line);
              font-size:1.05rem;transition:transform .15s ease,border-color .15s ease}
.topbar .back:active{transform:scale(.92)}
.topbar h1{font-size:1.02rem;font-weight:700;margin:0;flex:1;min-width:0;
           overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* ---------- hero ---------- */
.hero{position:relative;padding:36px 20px 32px;overflow:hidden;
      background:radial-gradient(1100px 380px at 85% -20%,rgba(59,130,246,.30),transparent 60%),
                 radial-gradient(800px 320px at -10% 110%,rgba(34,211,238,.18),transparent 55%),
                 linear-gradient(160deg,#0e1a33 0%,#0a0e17 70%)}
.hero::before{content:'';position:absolute;inset:0;
      background-image:radial-gradient(circle,rgba(255,255,255,.055) 1px,transparent 1px);
      background-size:22px 22px;
      mask-image:linear-gradient(180deg,rgba(0,0,0,.9),transparent 85%);
      -webkit-mask-image:linear-gradient(180deg,rgba(0,0,0,.9),transparent 85%)}
.hero::after{content:'';position:absolute;inset:auto 0 0 0;height:70px;
             background:linear-gradient(180deg,transparent,var(--bg));pointer-events:none}
.hero>*{position:relative;z-index:1}
.hero .brand{font-size:1.7rem;font-weight:800;letter-spacing:-.02em;
             background:linear-gradient(92deg,#fff 20%,#7ab8ff 70%,#22d3ee 105%);
             -webkit-background-clip:text;background-clip:text;
             -webkit-text-fill-color:transparent;color:transparent}
.hero p{margin:6px 0 18px;color:var(--muted);font-size:.9rem}

/* ---------- search ---------- */
.search{display:flex;gap:8px;padding:2px 16px 6px;margin-top:-14px;z-index:2;position:relative}
.search input[type=text]{flex:1;min-width:0;padding:13px 16px;border-radius:14px;
      border:1px solid var(--line);background:rgba(19,26,42,.85);color:var(--text);
      font-size:1rem;margin:0;box-shadow:0 8px 24px rgba(0,0,0,.35);
      -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
      transition:border-color .15s ease}
.search input[type=text]:focus{outline:none;border-color:var(--acc)}
.search button{padding:13px 22px;border-radius:14px;border:0;font-size:.95rem;font-weight:700;
      color:#fff;flex:none;
      background:linear-gradient(110deg,#1d4ed8 20%,var(--acc2) 50%,#1d4ed8 80%);
      background-size:200% 100%;
      box-shadow:0 8px 20px rgba(59,130,246,.35);
      animation:shimmer 3.2s linear infinite;
      transition:transform .15s ease}
.search button:active{transform:scale(.94)}
@keyframes shimmer{to{background-position:-200% 0}}

/* ---------- sections ---------- */
.section{display:flex;align-items:center;justify-content:space-between;
         margin:16px 0 8px;padding:0 16px;font-size:.78rem;font-weight:800;
         letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
.section a{font-size:.72rem;letter-spacing:.05em;color:var(--acc2);font-weight:700}

/* ---------- animated gradient border (Magic UI style) ---------- */
.gborder{position:relative;border-radius:16px;padding:1.5px;
         background:conic-gradient(from var(--ga),#1d4ed8,var(--acc2),#7c3aed,#1d4ed8);
         animation:gaspn 5s linear infinite;
         box-shadow:0 8px 26px rgba(37,99,235,.28)}
@keyframes gaspn{to{--ga:360deg}}
.gborder>a{display:flex;align-items:center;min-height:48px;padding:0 18px;
           border-radius:15px;font-weight:700;font-size:.95rem;
           background:linear-gradient(135deg,#0d1a33,#0a0e17);
           white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (prefers-reduced-motion:reduce){.gborder{animation:none}}

/* ---------- rails / source chips ---------- */
.rail{display:flex;gap:10px;overflow-x:auto;padding:2px 16px 8px;
      scrollbar-width:none;-webkit-overflow-scrolling:touch}
.rail::-webkit-scrollbar{display:none}
.sources{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));
         gap:9px;padding:4px 16px 12px}
.chip{display:flex;align-items:center;gap:8px;min-height:46px;padding:0 14px;
      border-radius:13px;font-weight:600;font-size:.9rem;
      background:linear-gradient(135deg,var(--card),var(--card2));
      border:1px solid var(--line);box-shadow:0 4px 14px rgba(0,0,0,.28);
      transition:transform .15s ease,border-color .15s ease;
      white-space:nowrap;overflow:hidden}
.chip:active{transform:scale(.96);border-color:var(--acc)}
.chip .nm{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis}
.chip .st{flex:none;font-size:.68rem;font-weight:800;letter-spacing:.04em}
.chip .st.ok{color:var(--ok)}
.chip .st.ko{color:var(--ko);background:rgba(255,107,100,.12);
             padding:2px 7px;border-radius:7px}
.chip .st.wait{color:var(--muted)}
.chip.down{opacity:.5}

/* ---------- poster grid ---------- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));
      gap:12px;padding:12px 16px 10px}
.card{position:relative;display:block;border-radius:14px;overflow:hidden;
      background:var(--card);border:1px solid var(--line);
      box-shadow:0 8px 22px rgba(0,0,0,.38);
      transition:transform .18s ease,box-shadow .18s ease}
.card:active{transform:translateY(-2px) scale(.98)}
.card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
      background:var(--card2)}
.card .ph{display:flex;align-items:center;justify-content:center;aspect-ratio:2/3;
      background:linear-gradient(160deg,#1b2947 0%,#111827 60%,#0b0f19 100%);
      color:#5f6c8a;font-size:2.3rem;font-weight:800;user-select:none;
      letter-spacing:.02em}
.card.txt .ph{font-size:1rem;padding:12px;text-align:center;font-weight:600;
      color:#aeb9d6}
.card.badge::after{content:attr(data-badge);position:absolute;top:8px;right:8px;
      padding:3px 8px;border-radius:8px;font-size:.62rem;font-weight:800;
      letter-spacing:.07em;text-transform:uppercase;color:#dff1ff;
      background:linear-gradient(135deg,rgba(37,99,235,.92),rgba(14,165,233,.85));
      box-shadow:0 2px 8px rgba(2,8,20,.5)}

/* ---------- infinite scroll sentinel ---------- */
.sentinel{display:flex;justify-content:center;padding:20px 0 28px}
.sentinel .spin{width:26px;height:26px;border-radius:50%;
      border:3px solid var(--line);border-top-color:var(--acc);
      animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* ---------- list (play links) ---------- */
.list{list-style:none;margin:0;padding:4px 16px 18px;display:flex;flex-direction:column;gap:8px}
.list a{display:flex;gap:10px;align-items:center;min-height:52px;padding:12px 14px;
        border-radius:14px;background:var(--card);border:1px solid var(--line)}
.list .t{flex:1;min-width:0;font-weight:600;font-size:.92rem;word-break:break-all}
.list .t small{color:var(--muted);display:block;font-weight:400;font-size:.74rem;
        overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.list .go{flex:none;color:var(--acc2);font-size:1rem}

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

_INFINITE_SCROLL = """
<script>(function(){var s=document.querySelector('.sentinel');if(!s)return;
var grid=document.querySelector('.grid');
var io=new IntersectionObserver(function(es){es.forEach(function(e){
if(!e.isIntersecting)return;io.disconnect();
fetch(s.dataset.url).then(function(r){return r.text()}).then(function(t){
var tpl=document.createElement('div');tpl.innerHTML=t;
var g=tpl.querySelector('.grid');var ns=tpl.querySelector('.sentinel');
if(!g||!g.children.length){s.remove();return;}
while(g.firstChild)grid.appendChild(g.firstChild);
if(ns){s.dataset.url=ns.dataset.url;io.observe(s);}else{s.remove();}});});
},{rootMargin:'500px'});io.observe(s);})();</script>
"""


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def page(title, body, back=None, hero=False, no_nav=False):
    if hero or no_nav:
        nav = ''
    else:
        home = '<a class="back" href="/" aria-label="Accueil">&#8962;</a>'
        backbtn = ('<a class="back" href="%s" aria-label="Retour">&#8592;</a>'
                   % esc(back)) if back else ''
        nav = ('<div class="topbar">%s%s<h1>%s</h1></div>'
               % (backbtn, home, esc(title)))
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


def render_sources(sites, statuses):
    """sites: site_manager list; statuses: {id: {'ok': bool} | None}."""
    out = ['<div class="sources">']
    for s in sites:
        st = statuses.get(s['id'])
        if st is None:
            st_cls, st_lbl, down = 'wait', '&#8987;', ''
        elif st.get('ok'):
            st_cls, st_lbl, down = 'ok', '&#9679;', ''
        else:
            st_cls, st_lbl, down = 'ko', 'KO', ' down'
        out.append('<a class="chip src%s" href="/nav?site=%s&function=load">'
                   '<span class="nm">%s</span>'
                   '<span class="st %s">%s</span></a>'
                   % (down, urllib.parse.quote(s['id']),
                      esc(s['label']), st_cls, st_lbl))
    out.append('</div>')
    return ''.join(out)


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


def render_items(base_path, data, site, back=None, next_url=None,
                 with_script=True):
    """data: runner.call_site result -> poster grid HTML.

    next_url: URL of the following page; when set, an infinite-scroll
    sentinel is appended (plus the loader script unless with_script=False,
    as inside AJAX fragments)."""
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
    if next_url:
        out.append('<div class="sentinel" data-url="%s"><span class="spin">'
                   '</span></div>' % esc(next_url))
        if with_script:
            out.append(_INFINITE_SCROLL)
    return ''.join(out)


def render_play(title, result, base_url, back):
    """result: guihoster.resolve_media output dict."""
    from bridge import m3u8proxy
    raw = result['url']
    base, headers = m3u8proxy.split_pipe(raw)
    token = m3u8proxy.register(raw)
    proxied = base_url + m3u8proxy.proxy_url(token, base)

    body = ['<div class="topbar">'
            '<a class="back" href="%s" aria-label="Retour">&#8592;</a>'
            '<a class="back" href="/" aria-label="Accueil">&#8962;</a>'
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
    return page(title, ''.join(body), no_nav=True)
