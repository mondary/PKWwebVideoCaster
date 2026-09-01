# PKWwebVideoCaster

Bridge local en Python qui permet d'ouvrir des catalogues de streaming dans
**Web Video Caster**, sans installer Kodi. Le projet ne fournit aucun contenu
et ne stocke aucun compte d'hébergeur.

> Usage strictement personnel et uniquement pour des contenus auxquels vous
> avez légalement accès. Ce projet n'est pas affilié à Web Video Caster, Kodi,
> vStream, ni aux sites ou hébergeurs consultés.

## Fonctionnement

Le bridge exécute les scrapers vStream en mode headless, rend une interface
web minimale et relaie les flux HLS/MP4 vers Web Video Caster :

```
iPhone (Web Video Caster)          Mac (ce dépôt)                 vStream
┌──────────────────────┐   HTTP   ┌──────────────────────────┐   sources
│ ouvre http://mac:8786│ ───────► │ bridge/server.py         │ ────────►
│ détecte le <video>   │ ◄─────── │ runner + shims + proxy   │
│ puis caste le flux   │          └──────────────────────────┘
└──────────────────────┘
```

Le proxy réécrit les playlists HLS et relaie les segments avec les en-têtes
nécessaires quand Web Video Caster ne peut pas les envoyer directement.

## Source et dépendance upstream

Les catalogues, scrapers et résolveurs ne sont pas recopiés dans ce dépôt.
Ils sont chargés à l'exécution depuis le projet d'origine :

- **Source** : [Kodi-vStream/venom-xbmc-addons](https://github.com/Kodi-vStream/venom-xbmc-addons)
- **Branche utilisée** : `Beta`
- **Chemin attendu** : `venom/plugin.video.vstream`
- **Licence upstream** : GNU GPL v3, voir le fichier `LICENSE` de vStream

Préparer le checkout sparse après avoir cloné ce dépôt :

```bash
git clone --filter=blob:none --sparse --branch Beta \
  https://github.com/Kodi-vStream/venom-xbmc-addons.git venom
git -C venom sparse-checkout set plugin.video.vstream
```

Le dossier `venom/` est une dépendance externe ignorée par le dépôt
PKWwebVideoCaster ; ses modifications doivent être faites dans le projet
upstream, pas dans ce dépôt.

## Installation et lancement

Installer Python 3 et les dépendances :

```bash
python3 -m pip install --user -r requirements.txt
./run.sh
```

Le serveur utilise `config.json`, écoute par défaut sur `0.0.0.0:8786` et
affiche l'adresse réseau à ouvrir dans Web Video Caster. Le Mac et le
téléphone doivent être sur le même réseau local.

## Sécurité

Ce bridge est un outil local, pas un service web public :

- le serveur HTTP n'a ni authentification ni TLS ;
- le bind `0.0.0.0` est nécessaire pour l'accès depuis le téléphone, mais le
  port `8786` ne doit jamais être redirigé sur Internet ;
- le proxy suit des URLs et des redirections upstream ; il ne doit pas être
  accessible à des utilisateurs non fiables ;
- `/debug` peut afficher des erreurs et des URLs de résolution.

Utiliser un pare-feu local ou un VPN privé. Une exposition publique nécessiterait
au minimum une authentification, une validation stricte des destinations
upstream, des protections SSRF, du TLS et des limites de débit.

## Structure

```
bridge/                 code du bridge, shims Kodi et proxy HLS
config.json             hôte et port d'écoute
requirements.txt        dépendances Python directes
run.sh                  lanceur
venom/                  checkout sparse de la dépendance upstream (non suivi)
```

## Limites

- Le résultat dépend de la disponibilité et de l'évolution des sources
  upstream.
- La résolution premium/debrid n'est pas activée.
- FlareSolverr n'est pas requis par la configuration actuelle.
