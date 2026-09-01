# -*- coding: utf-8 -*-
# Headless replacement for vStream's resources.lib.gui.hoster (cHosterGui).
# checkHoster/getHoster are ported from the original; showHoster captures a
# "play" item instead of building Kodi GUI elements. Debrid paths are dropped
# (guest resolution only) — see README.

import importlib

from bridge import shimstate
from bridge.shim.comaddon import addon, dialog, VSlog


class cHosterGui(object):
    SITE_NAME = 'cHosterGui'
    ADDON = addon()

    # ------------------------------------------------------------------ #

    def getHoster(self, sHosterFileName):
        mod = importlib.import_module('resources.hosters.' + sHosterFileName)
        klass = getattr(mod, 'cHoster')
        return klass()

    def showHoster(self, oGui, oHoster, sMediaUrl, sThumbnail='',
                   bGetRedirectUrl=False):
        oHoster.setUrl(sMediaUrl)
        import re
        title = re.sub(r'\[/?COLOR[^]]*\]', '', oHoster.getDisplayName() or '')
        shimstate.add_item({
            'kind': 'play',
            'hoster': oHoster.getPluginIdentifier(),
            'url': sMediaUrl,
            'title': title.strip(),
            'file': oHoster.getFileName() or '',
            'thumb': sThumbnail or '',
            'redirect': bool(bGetRedirectUrl),
        })

    # ------------------------------------------------------------------ #
    # checkHoster : portage fidèle de la version Kodi (sans debrid).
    # Entrée : nom d'hébergeur OU url ; sortie : instance de cHoster ou False.

    def checkHoster(self, sHosterUrl, debrid=True, tried_urls=None,
                    depth=0, max_depth=3):
        if not sHosterUrl:
            return False

        if tried_urls is None:
            tried_urls = set()
        if sHosterUrl in tried_urls or depth > max_depth:
            VSlog('Boucle évitée ou profondeur max atteinte pour %s' % sHosterUrl)
            return False
        tried_urls.add(sHosterUrl)

        fullURL = sHosterUrl

        # lien direct ?
        if any(x in sHosterUrl for x in ['.mp4', '.avi', '.flv', '.m3u8',
                                         '.webm', '.mkv', '.mpd']):
            return self.getHoster('lien_direct')

        sHosterUrl = sHosterUrl.split('|')[0]
        sHosterUrl = sHosterUrl.split('?')[0]
        sHosterUrl = sHosterUrl.lower()

        from urllib.parse import urlparse
        try:
            sHostName = urlparse(sHosterUrl).hostname or sHosterUrl
        except Exception:
            sHostName = sHosterUrl

        supported_player = ['streamz', 'streamax', 'gounlimited', 'xdrive', 'facebook', 'mixdrop', 'mixloads', 'vidoza',
                            'rutube', 'megawatch', 'vidzi', 'vidzy', 'filetrip', 'speedvid', 'letsupload', 'fsvid', 'sendvid',
                            'onevideo', 'playreplay', 'vimeo', 'prostream', 'vidfast', 'uqload', 'letwatch', 'mail.ru',
                            'filepup', 'vimple', 'wstream', 'watchvideo', 'vidwatch', 'up2stream', 'tune', 'playtube',
                            'vidup', 'vidbull', 'vidlox', 'megaup', '33player' 'easyload', 'ninjastream', 'cloudhost',
                            'videobin', 'stagevu', 'gorillavid', 'daclips', 'hdvid', 'vshare', 'streamlare', 'vidload',
                            'giga', 'vidbom', 'cloudvid', 'megadrive', 'downace', 'clickopen', 'supervideo', 'turbovid',
                            'jawcloud', 'kvid', 'soundcloud', 'mixcloud', 'ddlfr', 'vupload', 'dwfull', 'vidzstore',
                            'pdj', 'rapidstream', 'archive', 'dustreaming', 'viki', 'flix555', 'onlystream', 'filemoon',
                            'upstream', 'pstream', 'vudeo', 'vidia', 'streamtape', 'vidbem', 'uplea', 'vido', 'vidmoly', 'vidsonic',
                            'sibnet', 'vidplayer', 'userload', 'aparat', 'evoload', 'vidshar', 'abcvideo', 'plynow', 'smoothpre',
                            'tomacloud', 'videovard', 'viewsb', 'yourvid', 'vf-manga', 'darkibox', 'mustardshock', 'lulustream',
                            'daisukianime', 'xtremestream', 'gofile']

        val = next((x for x in supported_player if x in sHostName), None)
        if val:
            return self.getHoster(val.replace('.', ''))

        if ('vidbm' in sHostName) or ('vedbom' in sHostName):
            return self.getHoster('vidbm')

        if ('embedwish' in sHostName) or ('streamwish' in sHostName) or ('warda' in sHostName):
            return self.getHoster('streamwish')

        if ('guccihide' in sHostName) or ('streamhide' in sHostName) or ('wishonly' in sHostName):
            return self.getHoster('streamhide')

        if ('oneupload' in sHostName) or ('tipfly' in sHostName):
            return self.getHoster('oneupload')

        if ('vk.com' in sHostName) or ('vkontakte' in sHostName) or ('vkcom' in sHostName):
            return self.getHoster('vk')

        if ('vidguard' in sHostName) or ('fertoto' in sHostName) or ('vgembed' in sHostName) or ('vgfplay' in sHostName) or ('jetload' in sHostName):
            return self.getHoster('vidguard')

        if ('vidara' in sHostName) or ('vidarax' in sHostName) or ('vidaarax' in sHostName) or ('streamix' in sHostName) or ('stmix' in sHostName):
            return self.getHoster('vidara')

        if ('filelions' in sHostName) or ('shoooot' in sHostName) or ('vidhide' in sHostName) or ('nejma' in sHostName) or ('earnvids' in sHostName) or ('minochinos' in sHostName):
            return self.getHoster('filelions')

        if ('lulustream' in sHostName) or ('luluvid' in sHostName) or ('luluvdo' in sHostName) or ('lulu.st' in sHostName) or ('streamhihi' in sHostName):
            return self.getHoster('lulustream')

        if ('savefiles' in sHostName) or ('streamhls' in sHostName):
            return self.getHoster('savefiles')

        if ('swish' in sHostName) or ('hanerix' in sHostName) or ('hgcloud' in sHostName):
            return self.getHoster('swish')

        if ('playvidto' in sHostName):
            return self.getHoster('vidto')

        if ('hd-stream' in sHostName):
            return self.getHoster('hd_stream')

        if ('vcstream' in sHostName):
            return self.getHoster('vidcloud')

        # Hosts utilisant lien_direct
        if any(x in sHostName for x in ['livestream', 'mustardshock']):
            return self.getHoster('lien_direct')

        # vidtodo et clone
        val = next((x for x in ['vidtodo', 'vixtodo', 'viddoto', 'vidstodo']
                    if x in sHostName), None)
        if val:
            return self.getHoster('vidtodo')

        if ('dailymotion' in sHostName) or ('dai.ly' in sHostName):
            try:
                if 'stream' in sHosterUrl:
                    return self.getHoster('lien_direct')
            except Exception:
                pass
            else:
                return self.getHoster('dailymotion')

        if ('flashx' in sHostName) or ('filez' in sHostName):
            return self.getHoster('flashx')

        if ('xcoic' in sHostName) or ('filmoon' in sHostName):
            return self.getHoster('filemoon')

        if ('mystream' in sHostName) or ('mstream' in sHostName):
            return self.getHoster('mystream')

        if ('streamingentiercom/videophp' in sHosterUrl) or ('speedvideo' in sHostName):
            return self.getHoster('speedvideo')

        if ('googlevideo' in sHostName) or ('picasaweb' in sHostName) or ('googleusercontent' in sHostName):
            return self.getHoster('googlevideo')

        if ('ok.ru' in sHostName) or ('odnoklassniki' in sHostName):
            return self.getHoster('ok_ru')

        if ('iframe-secured' in sHostName):
            return self.getHoster('iframe_secured')

        if ('iframe-secure' in sHostName):
            return self.getHoster('iframe_secure')

        if ('thevideo' in sHostName) or ('video.tt' in sHostName) or ('vev.io' in sHostName):
            return self.getHoster('thevideo_me')

        if ('drive.google.com' in sHostName) or ('docs.google.com' in sHostName):
            return self.getHoster('googledrive')

        if ('movshare' in sHostName) or ('wholecloud' in sHostName):
            return self.getHoster('wholecloud')

        if ('moacloud' in sHostName) or ('duxcloud' in sHostName):
            return self.getHoster('vidzstore')

        if ('upvideo' in sHostName) or ('streamon' in sHostName):
            return self.getHoster('upvideo')

        if ('upvid' in sHostName) or ('opvid' in sHostName) or ('illvid' in sHostName) or ('golvid' in sHostName):
            return self.getHoster('upvid')

        if ('estream' in sHostName) and not ('widestream' in sHostName):
            return self.getHoster('estream')

        if ('clipwatching' in sHostName) or ('highstream' in sHostName):
            return self.getHoster('clipwatching')

        if ('kokoflix' in sHostName):
            return self.getHoster('allow_redirects')

        if ('bigwarp' in sHostName):
            return self.getHoster('flix555')

        if sHostName.replace('o', '').replace('0', '').replace('stream', '').split('.')[0] == 'dd':
            return self.getHoster('dood')
        if ('dsvplay' in sHostName) or ('ds2play' in sHostName) or ('ds2video' in sHostName) or ('dooodster' in sHostName) or ('vidply' in sHostName):
            return self.getHoster('dood')

        if ('voe' in sHostName) or ('jamessoundcost' in sHostName) or ('magasavor' in sHostName) or ('sandratableother' in sHostName) or ('alejandrocenturyoil' in sHostName):
            return self.getHoster('voe')

        if ('goo.gl' in sHostName) or ('bit.ly' in sHostName) or ('streamcrypt' in sHostName) or ('opsktp' in sHosterUrl):
            return self.getHoster('allow_redirects')

        # le captcha ne fonctionne pas
        if ('netu' in sHostName) or ('waaw' in sHostName) or ('hqq' in sHostName) or ('doplay' in sHostName) or ('vizplay' in sHostName) or ('netzues' in sHostName):
            return self.getHoster('netu')

        if ('tapepops' in sHostName):
            return self.getHoster('streamtape')

        # frenchvid et clone
        val = next((x for x in ['french-vid', 'yggseries', 'fembed', 'fem.tohds', 'feurl', 'fsimg', 'core1player',
                                'vfsplayer', 'gotochus', 'femax'] if x in sHostName), None)
        if val:
            return self.getHoster('frenchvid')

        if ('directmoviedl' in sHostName) or ('moviesroot' in sHostName):
            return self.getHoster('directmoviedl')

        # Lien telechargeable a convertir en stream
        if ('1fichier' in sHostName):
            return self.getHoster('1fichier')

        if ('uploaded' in sHostName) or ('ul.to' in sHostName):
            if ('/file/forbidden' in sHosterUrl):
                return False
            return self.getHoster('uploaded')

        if ('myfiles.alldebrid.com' in sHostName):
            return self.getHoster('lien_direct')

        # Si on n'a rien trouvé mais que le lien semble valide (ex: /e/)
        if ('/e/' in fullURL) or ('/v/' in fullURL):
            try:
                from resources.lib.handler.requestHandler import cRequestHandler
                oRequest = cRequestHandler(fullURL)
                html = oRequest.request()
                sHosterUrl2 = None
                import re
                if 'content="VOE">' in html or re.search(r'voe', html, re.I):
                    sHosterUrl2 = 'https://voe.com/%s' % (fullURL.split('/e/', 1)[1])
                elif 'filemoon' in html or 'filmoon' in html or 'Byse' in html:
                    sHosterUrl2 = 'https://filemoon.com/%s' % (fullURL.split('/e/', 1)[1])
                elif 'vidhide' in html:
                    sHosterUrl2 = 'https://earnvids.com/%s' % (fullURL.split('/v/', 1)[1])
                elif 'guardstorage' in html:
                    sHosterUrl2 = 'https://vidguard.com/%s' % (fullURL.split('/e/', 1)[1])
                elif 'Redirecting...' in html:
                    urlMatch = re.search(r"window\.location\.href\s*=\s*'([^']+)", html)
                    if urlMatch:
                        sHosterUrl2 = urlMatch.group(1)
                elif '.doodcdn' in html:
                    sHosterUrl2 = 'https://dood.com/%s' % (fullURL.split('/e/', 1)[1])

                if sHosterUrl2:
                    return self.checkHoster(sHosterUrl2, debrid, tried_urls,
                                            depth + 1, max_depth)
            except Exception:
                pass

        # a la fin, pour éviter d'attraper avant ce qui commence par myvi...
        if ('myvi' in sHostName):
            return self.getHoster('myvi')

        return False


class ResolveError(Exception):
    pass


def resolve_media(hosterIdentifier, mediaUrl, fileName='', title=''):
    """Portage headless de cHosterGui.play() : renvoie 'url[|Headers]'."""
    from bridge.runner import argv_lock
    with argv_lock:  # les hébergeurs lisent sys.argv via leurs helpers
        return _resolve_media(hosterIdentifier, mediaUrl, fileName, title)


def _resolve_media(hosterIdentifier, mediaUrl, fileName='', title=''):
    oHosterGui = cHosterGui()
    sFileName = fileName or title or ''

    if not hosterIdentifier:
        # pas d'identifiant connu : tenter la détection par l'URL
        oHoster = oHosterGui.checkHoster(mediaUrl)
        if not oHoster:
            raise ResolveError('Hébergeur inconnu pour ' + mediaUrl)
    else:
        oHoster = oHosterGui.getHoster(hosterIdentifier)

    oHoster.setFileName(sFileName)
    dialog().VSinfo(oHoster.getDisplayName(), 'Résolution')

    try:
        oHoster.setUrl(mediaUrl)
        aLink = oHoster.getMediaLink()
    except Exception as e:
        VSlog('Hoster exception: %r' % e)
        raise ResolveError('Erreur hébergeur %s: %s' % (hosterIdentifier, e))

    if aLink and (aLink[0] or aLink[1]):
        if not aLink[0]:
            # l'hébergeur redirige vers un autre hébergeur
            oHoster2 = oHosterGui.checkHoster(aLink[1], debrid=False)
            if oHoster2:
                oHoster2.setFileName(sFileName)
                dialog().VSinfo(oHoster2.getDisplayName(), 'Résolution')
                oHoster2.setUrl(aLink[1])
                aLink = oHoster2.getMediaLink()

        if aLink and aLink[0]:
            subtitles = aLink[2] if len(aLink) > 2 else ''
            return {'url': aLink[1], 'subtitles': subtitles,
                    'title': title or sFileName,
                    'hoster': oHoster.getPluginIdentifier()}

    errs = shimstate.errors() or ['Aucun flux trouvé']
    raise ResolveError(' ; '.join(errs))
