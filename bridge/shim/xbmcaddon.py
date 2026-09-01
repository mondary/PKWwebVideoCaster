# -*- coding: utf-8 -*-
# Pure-Python stub of the Kodi `xbmcaddon` module (headless bridge).


class Addon(object):
    def __init__(self, id=''):
        self._id = id

    def getSetting(self, key):
        return ''

    def setSetting(self, key, value):
        return True

    def getAddonInfo(self, info):
        return ''

    def openSettings(self):
        pass
