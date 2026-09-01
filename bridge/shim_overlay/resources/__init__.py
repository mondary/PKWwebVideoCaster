# -*- coding: utf-8 -*-
# Shadow package: this `resources` package wins over the vendored one, then
# extends its search path with the vendored tree so every non-shadowed
# submodule (lib.handler, sites, hosters, ...) resolves from the vendor.
import os

VENDOR_RESOURCES = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'venom',
    'plugin.video.vstream', 'resources'))

if VENDOR_RESOURCES not in __path__:
    __path__.append(VENDOR_RESOURCES)
