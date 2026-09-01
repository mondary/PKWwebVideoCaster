# -*- coding: utf-8 -*-
import os

VENDOR_LIB = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..',
    'venom', 'plugin.video.vstream', 'resources', 'lib'))

if VENDOR_LIB not in __path__:
    __path__.append(VENDOR_LIB)
