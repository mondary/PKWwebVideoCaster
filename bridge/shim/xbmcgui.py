# -*- coding: utf-8 -*-
# Pure-Python stub of the Kodi `xbmcgui` module (headless bridge).
# Everything is a permissive no-op: enough for imports and light attribute
# access, never for real GUI work (the bridge replaces the GUI layer).


class _Noop(object):
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        def _f(*args, **kwargs):
            return None
        return _f


ACTION_NONE = 0
ACTION_SELECT_ITEM = 7
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_BACKSPACE = 110
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_PLAYER_STOPPED = 13
ACTION_PLAYER_STARTED = 78

ICON_IMAGE_FOV = ''


class ListItem(_Noop):
    pass


class Window(_Noop):
    pass


class WindowDialog(_Noop):
    pass


class WindowXML(_Noop):
    pass


class WindowXMLDialog(_Noop):
    pass


class Control(_Noop):
    pass


class ControlLabel(Control):
    pass


class ControlButton(Control):
    pass


class ControlList(Control):
    pass


class ControlImage(Control):
    pass


class ControlTextBox(Control):
    pass


class ControlProgress(Control):
    pass


class ControlGroup(Control):
    pass


class Dialog(_Noop):
    def ok(self, *args, **kwargs):
        return True

    def yesno(self, *args, **kwargs):
        return False

    def select(self, *args, **kwargs):
        return 0

    def input(self, *args, **kwargs):
        return ''

    def browse(self, *args, **kwargs):
        return ''

    def notification(self, *args, **kwargs):
        return None


class DialogProgress(_Noop):
    def isCanceled(self):
        return False

    def create(self, *args, **kwargs):
        return None

    def update(self, *args, **kwargs):
        return None

    def close(self, *args, **kwargs):
        return None


class DialogProgressBG(_Noop):
    pass


class DialogBusy(_Noop):
    pass


def getCurrentWindowId():
    return 0


def getCurrentWindowDialogId():
    return 0
