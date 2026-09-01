# -*- coding: utf-8 -*-
# Headless replacement for vStream's resources.lib.gui.gui (cGui).
# Instead of building Kodi list items, every add* call is captured as a plain
# dict in bridge.shimstate; the HTTP layer renders them.

from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from bridge import shimstate


def _params(oOutputParameterHandler):
    if not oOutputParameterHandler:
        return {}
    try:
        uri = oOutputParameterHandler.getParameterAsUri()
        return _parse_uri(uri)
    except Exception:
        return {}


def _parse_uri(uri):
    out = {}
    if not uri or uri == 'params=0':
        return out
    from urllib.parse import unquote_plus
    for part in uri.split('&'):
        if '=' in part:
            k, v = part.split('=', 1)
            out[k] = unquote_plus(v)
    return out

def _strip_color(label):
    # Kodi [COLOR x]yy[/COLOR] -> yy
    import re
    return re.sub(r'\[/?COLOR[^]]*\]', '', label or '')


class cGui(object):

    def __init__(self):
        self.items = shimstate.items()
        self.end_of_directory = False

    # ---- capture primitifs ---------------------------------------------

    def _addItem(self, item):
        self.items.append(item)
        return item

    def addNewDir(self, Type, sId, sFunction, sLabel, sIcon, sThumbnail='',
                  sDesc='', oOutputParameterHandler=cOutputParameterHandler(),
                  sMeta=0, sCat=None):
        return self._addItem({
            'kind': 'dir', 'cat': Type, 'site': sId, 'function': sFunction,
            'label': _strip_color(sLabel), 'thumb': sThumbnail or sIcon or '',
            'desc': sDesc or '', 'params': _params(oOutputParameterHandler),
        })

    def addDir(self, sId, sFunction, sLabel, sIcon,
               oOutputParameterHandler=cOutputParameterHandler(), sDesc=''):
        return self.addNewDir('dir', sId, sFunction, sLabel, sIcon, '', sDesc,
                              oOutputParameterHandler)

    def addMovie(self, sId, sFunction, sLabel, sIcon, sThumbnail, sDesc,
                 oOutputParameterHandler=''):
        return self.addNewDir('movie', sId, sFunction, sLabel, sIcon,
                              sThumbnail, sDesc, oOutputParameterHandler)

    def addTV(self, sId, sFunction, sLabel, sIcon, sThumbnail, sDesc,
              oOutputParameterHandler=''):
        return self.addNewDir('tv', sId, sFunction, sLabel, sIcon,
                              sThumbnail, sDesc, oOutputParameterHandler)

    def addAnime(self, sId, sFunction, sLabel, sIcon, sThumbnail, sDesc,
                 oOutputParameterHandler=''):
        return self.addNewDir('anime', sId, sFunction, sLabel, sIcon,
                              sThumbnail, sDesc, oOutputParameterHandler)

    def addDrama(self, sId, sFunction, sLabel, sIcon, sThumbnail, sDesc,
                 oOutputParameterHandler=''):
        return self.addNewDir('drama', sId, sFunction, sLabel, sIcon,
                              sThumbnail, sDesc, oOutputParameterHandler)

    def addMisc(self, sId, sFunction, sLabel, sIcon, sThumbnail, sDesc,
                oOutputParameterHandler=''):
        return self.addNewDir('misc', sId, sFunction, sLabel, sIcon,
                              sThumbnail, sDesc, oOutputParameterHandler)

    def addMoviePack(self, sId, sFunction, sLabel, sThumbnail, sDesc,
                     oOutputParameterHandler=''):
        return self.addNewDir('movie', sId, sFunction, sLabel, '', sThumbnail,
                              sDesc, oOutputParameterHandler)

    def addGenre(self, sId, sFunction, sLabel, oOutputParameterHandler='',
                 sDesc=''):
        return self.addNewDir('genre', sId, sFunction, sLabel, '', '', sDesc,
                              oOutputParameterHandler)

    def addSeason(self, sId, sFunction, sLabel, sIcon, sThumbnail, sDesc,
                  oOutputParameterHandler=''):
        return self.addNewDir('season', sId, sFunction, sLabel, sIcon,
                              sThumbnail, sDesc, oOutputParameterHandler)

    def addEpisode(self, sId, sFunction, sLabel, sIcon, sThumbnail, sDesc,
                   oOutputParameterHandler=''):
        return self.addNewDir('episode', sId, sFunction, sLabel, sIcon,
                              sThumbnail, sDesc, oOutputParameterHandler)

    def addPerson(self, sId, sFunction, sLabel, sIcon, sThumbnail,
                  oOutputParameterHandler=''):
        return self.addNewDir('person', sId, sFunction, sLabel, sIcon,
                              sThumbnail, '', oOutputParameterHandler)

    def addNetwork(self, sId, sFunction, sLabel, sIcon,
                   oOutputParameterHandler=''):
        return self.addNewDir('network', sId, sFunction, sLabel, sIcon, '',
                              '', oOutputParameterHandler)

    def addLink(self, sId, sFunction, sLabel, sThumbnail, sDesc,
                oOutputParameterHandler=''):
        return self.addNewDir('link', sId, sFunction, sLabel, '', sThumbnail,
                              sDesc, oOutputParameterHandler)

    def addNext(self, sId, sFunction, sLabel, oOutputParameterHandler):
        return self.addNewDir('next', sId, sFunction, sLabel, '', '', '',
                              oOutputParameterHandler)

    def addNone(self, sId):
        return None

    def addText(self, sId, sLabel='', sIcon='none.png'):
        return self._addItem({'kind': 'text', 'label': _strip_color(sLabel)})

    # ---- lecture (cHosterGui.showHoster passe par ici) ------------------

    def addFolder(self, oGuiElement, oOutputParameterHandler='', _isFolder=True):
        # Le vrai flux "play" construit un GuiElement ; dans le bridge, le
        # cHosterGui headless ajoute directement ses items et ne passe jamais ici.
        return None

    # ---- clôtures / vues ------------------------------------------------

    def setEndOfDirectory(self, forceViewMode=False):
        self.end_of_directory = True

    def updateDirectory(self):
        pass

    def viewBA(self):
        pass

    def viewBack(self):
        pass

    def viewInfo(self):
        pass

    def viewSimil(self):
        pass

    # ---- interactions ---------------------------------------------------

    def selectPage(self):
        choices = shimstate.page_choices()
        if choices:
            return str(choices)
        return '1'

    def selectPage2(self):
        return self.selectPage()

    def showKeyBoard(self, sDefaultText='', heading=''):
        return shimstate.keyboard_text() or sDefaultText or ''

    def showNumBoard(self, sTitle='', sDefaultNum=''):
        return shimstate.keyboard_text() or sDefaultNum or ''

    def openSettings(self):
        pass

    def showNofication(self, sDesc, sTitle='vStream', iSeconds=3):
        shimstate.message(sDesc)

    def showError(self, sTitle, sDescription, iSeconds=0):
        shimstate.error('%s: %s' % (sTitle, sDescription))

    def showInfo(self, sTitle, sDescription, iSeconds=0):
        shimstate.message('%s: %s' % (sTitle, sDescription))

    # ---- recherche globale (no-op, le bridge ne s'en sert pas) ----------

    def getSearchResult(self):
        return []

    def addSearchResult(self, oGuiElement, oOutputParameterHandler):
        pass

    def resetSearchResult(self):
        pass

    # Accès aux paramètres d'entrée, pratique pour certains sites qui
    # instancient cInputParameterHandler tardivement.
    def inputParameterHandler(self):
        return cInputParameterHandler()
