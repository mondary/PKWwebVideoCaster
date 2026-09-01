# -*- coding: utf-8 -*-
# Headless replacement for vStream's resources.lib.comaddon.
# Same public surface used by sites/hosters/lib, zero Kodi.

import json
import os
import threading

from bridge import shimstate

VENDOR_ADDON_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'venom', 'plugin.video.vstream')
VENDOR_ADDON_DIR = os.path.normpath(VENDOR_ADDON_DIR)

SITES_JSON = os.path.join(VENDOR_ADDON_DIR, 'resources', 'sites.json')
LANG_PO = os.path.join(VENDOR_ADDON_DIR, 'resources', 'language',
                       'resource.language.fr_fr', 'strings.po')

# Settings vStream utilsés par les chemins de code que le bridge exécute.
# Tout ce qui ne figure pas ici répond 'false' (désactivé).
DEFAULT_SETTINGS = {
    'premium': 'false',
    'hoster_alldebrid_premium': 'false',
    'hoster_realdebrid_premium': 'false',
    'hoster_debridlink_premium': 'false',
    'hoster_uptobox_premium': 'false',
    'hoster_onefichier_premium': 'false',
    'use_flaresolverr': 'false',
    'ipaddress': '',
    'display_info_file': 'false',
}

_STRINGS = None


def _load_strings():
    global _STRINGS
    if _STRINGS is not None:
        return _STRINGS
    _STRINGS = {}
    try:
        ctxt = None
        with open(LANG_PO, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if line.startswith('msgctxt'):
                    ctxt = line.split('"')[1] if '"' in line else None
                elif line.startswith('msgstr') and ctxt:
                    msgstr = line[len('msgstr'):].strip().strip('"')
                    if msgstr:
                        _STRINGS[ctxt.lstrip('#')] = msgstr
                    ctxt = None
    except OSError:
        pass
    return _STRINGS



def VSlog(e, level=0):
    shimstate.log(str(e))


def VSPath(pathSpecial):
    """Map special:// home paths onto the vendored addon tree."""
    if not isinstance(pathSpecial, str):
        return pathSpecial
    prefix = 'special://home/addons/plugin.video.vstream/'
    if pathSpecial.startswith(prefix):
        return os.path.join(VENDOR_ADDON_DIR, pathSpecial[len(prefix):])
    if pathSpecial.startswith('special://'):
        return pathSpecial.replace('special://', '/tmp/')
    return pathSpecial


def VSProfil():
    return 'Master user'


def isKrypton():
    return False


def isMatrix():
    return True


def isNexus():
    return True


class addon(object):
    def __init__(self, addonId=None):
        pass

    def openSettings(self):
        pass

    def getSetting(self, key):
        return DEFAULT_SETTINGS.get(key, 'false')

    def setSetting(self, key, value):
        return True

    def getAddonInfo(self, info):
        if info == 'path':
            return VENDOR_ADDON_DIR
        if info == 'profile':
            return VENDOR_ADDON_DIR
        return ''

    def VSlang(self, lang):
        strings = _load_strings()
        return strings.get(str(lang).lstrip('#'), str(lang))


class dialog(object):
    def VSok(self, desc, title='vStream'):
        shimstate.message(str(desc))
        return True

    def VSyesno(self, desc, title='vStream'):
        shimstate.message('yesno: %s -> Non' % desc)
        return False

    def VSselect(self, desc, title='vStream'):
        shimstate.message('select: %s -> 0' % desc)
        return 0

    def numeric(self, dialogType, heading, defaultt=''):
        return str(defaultt)

    def VSbrowse(self, type, heading, shares):
        return ''

    def VSselectqual(self, list_qual, list_url):
        # Première qualité proposée (comportement "invité" par défaut).
        return 0

    def VSinfo(self, desc, title='vStream', iseconds=1, sound=False):
        shimstate.message(str(desc))
        return True

    def VSerror(self, e):
        shimstate.error(str(e))
        return True

    def VStextView(self, desc, title='vStream'):
        shimstate.message(str(desc))
        return True


class progress(object):
    def __init__(self):
        self._canceled = False

    def VScreate(self, title='', desc='', large=False):
        return self

    def VSupdate(self, dialog, total, text='', search=False):
        return self

    def iscanceled(self):
        return self._canceled

    def VSclose(self, dialog=None):
        return self

    def getProgress(self):
        return 0


class window(object):
    _store = {}

    def __init__(self, winID=None):
        pass

    def setProperty(self, key, value):
        window._store[str(key)] = str(value)

    def getProperty(self, key):
        return window._store.get(str(key), '')

    def clearProperty(self, key):
        window._store.pop(str(key), None)


class listitem(object):
    def __init__(self, label='', label2=''):
        self._label = label
        self._label2 = label2

    def addMenu(self, sFile, sFunction, sTitle, oOutputParameterHandler=False):
        pass

    def getLabel(self):
        return self._label


class siteManager(object):
    SITES = 'sites'
    ACTIVE = 'active'
    CLOUDFLARE = 'cloudflare'
    LABEL = 'label'
    URL_MAIN = 'url'

    def __init__(self):
        with open(SITES_JSON, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def isEnable(self, sourceName):
        return self.getDefaultProperty(sourceName, self.ACTIVE) == 'True'

    def isCloudFlare(self, sourceName):
        return self.getDefaultProperty(sourceName, self.CLOUDFLARE) == 'True'

    def isActive(self, sourceName):
        return self.getDefaultProperty(sourceName, self.ACTIVE) == 'True'

    def setActive(self, sourceName, state):
        pass

    def getUrlMain(self, sourceName):
        return str(self.getDefaultProperty(sourceName, self.URL_MAIN))

    def disableAll(self):
        pass

    def enableAll(self):
        pass

    def getDefaultProperty(self, sourceName, propName):
        sourceData = self.data[self.SITES].get(sourceName)
        if not sourceData:
            return False
        if propName not in sourceData:
            return False
        return sourceData.get(propName)

    def getProperty(self, sourceName, propName):
        return self.getDefaultProperty(sourceName, propName)

    def setProperty(self, sourceName, propName, value):
        pass

    def listActive(self):
        out = []
        for name, props in sorted(self.data[self.SITES].items(),
                                  key=lambda kv: kv[1].get('label', kv[0]).lower()):
            if props.get(self.ACTIVE) != 'True':
                continue
            if name.startswith(('alldebrid', 'debrid_link', 'realdebrid',
                                'direct_stream', 'freebox', 'pastebin', 'themoviedb_org',
                                'topimdb', 'siteonefichier', 'kepliz_com', 'wawacity',
                                'extreme_down', 'free_telechargement_org',
                                'sitedarkibox', 'netu', 'cloudproxy', 'dnspython',
                                'livetv')):
                continue  # sources non "catalogue web" ou liées à un compte
            out.append({'id': name, 'label': props.get(self.LABEL, name),
                        'url': props.get(self.URL_MAIN, '')})
        return out
