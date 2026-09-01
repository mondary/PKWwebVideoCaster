# -*- coding: utf-8 -*-
# Pure-Python stub of the Kodi `xbmc` module (headless bridge).
LOGDEBUG = 0
LOGINFO = 1
LOGWARNING = 2
LOGERROR = 3
LOGFATAL = 4


def log(msg, level=LOGDEBUG):
    pass


def sleep(ms):
    import time
    time.sleep(ms / 1000.0)


def executebuiltin(statement, wait=False):
    pass


def executeJSONRPC(statement):
    return '{"id":1,"jsonrpc":"2.0","result":"OK"}'


def getCondVisibility(condition):
    return 0


def getInfoLabel(infotag):
    return ''


def getRegion(id):
    return ''


def getLanguage(fmt=0, region=True):
    return 'fr_FR'


def getSkinDir():
    return ''


def translatePath(path):
    from bridge.shim.comaddon import VSPath
    return VSPath(path)


def getLocalizedString(id):
    return str(id)


def makeLegalFilename(filename):
    return filename


class Monitor(object):
    def __init__(self):
        pass

    def waitForAbort(self, timeout=0.1):
        import time
        time.sleep(timeout)
        return False

    def abortRequested(self):
        return False


class Keyboard(object):
    def __init__(self, line='', heading=''):
        self._line = line

    def doModal(self):
        pass

    def isConfirmed(self):
        return bool(self._line)

    def getText(self):
        return self._line
