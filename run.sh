#!/bin/bash
# Lance le bridge PKWwebVideoCaster.
cd "$(dirname "$0")"
if [ ! -d "venom/plugin.video.vstream" ]; then
  echo "Dépendance upstream manquante : lance d'abord les commandes README (clone sparse de venom-xbmc-addons)." >&2
  exit 1
fi
exec python3 -m bridge.server
