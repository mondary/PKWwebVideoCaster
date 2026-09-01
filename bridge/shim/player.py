# -*- coding: utf-8 -*-
# Headless replacement for vStream's resources.lib.player (cPlayer).
# The bridge never calls Kodi's player: runner intercepts resolution and
# renders a play page. This stub only exists to keep imports alive.


class cPlayer(object):
    def __init__(self):
        pass

    def run(self, oGuiElement, sUrl, subtitles=''):
        raise RuntimeError('cPlayer.run should never be called in the bridge')

    def AddSubtitles(self, sUrl):
        pass

    def addItemToPlaylist(self, oGuiElement):
        pass
