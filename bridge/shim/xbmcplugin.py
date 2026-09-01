# -*- coding: utf-8 -*-
# Pure-Python stub of the Kodi `xbmcplugin` module (headless bridge).

PLUGIN_SORT_METHOD_NONE = 0
SORT_METHOD_NONE = 0
SORT_METHOD_LABEL = 1
SORT_METHOD_TITLE = 2
SORT_METHOD_UNSORTED = 3

RESPOND_OK = 0


def addDirectoryItem(handle, url, listitem, isFolder=False):
    return True


def addSortMethod(handle, sortMethod):
    pass


def endOfDirectory(handle, succeeded=True, updateListing=True, cacheToDisc=True):
    pass


def setResolvedUrl(handle, succeeded, listitem):
    pass


def setContent(handle, content):
    pass


def setPluginCategory(handle, category):
    pass


def sortedDirectoryContent(folder):
    return []
