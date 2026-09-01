# -*- coding: utf-8 -*-
# Pure-Python stub of the Kodi `xbmcvfs` module (headless bridge).


def exists(path):
    # requestHandler utilise ce test avant d'activer son fallback DNS Kodi.
    # dnspython est installé dans le Python du bridge.
    return 'script.module.dnspython' in str(path)


def copy(source, destination):
    return False


def delete(path):
    return False


def listdir(path):
    return ([], [])


def mkdir(path):
    return False


def translatePath(path):
    from bridge.shim.comaddon import VSPath
    return VSPath(path)


class File(object):
    def __init__(self, path, mode='r'):
        pass

    def read(self, n=-1):
        return ''

    def write(self, data):
        return 0

    def size(self):
        return 0

    def seek(self, pos, whence=0):
        return 0

    def close(self):
        pass
