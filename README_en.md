# PKWwebVideoCaster

Local Python bridge that lets you open streaming catalogs in
**Web Video Caster** without installing Kodi. The project does not provide
any content and does not store any hoster account.

> Strictly personal use, and only for content you are legally allowed to
> access. This project is not affiliated with Web Video Caster, Kodi,
> vStream, or the sites and hosts it queries.

## How it works

The bridge runs vStream scrapers headlessly, renders a minimal web
interface, and relays HLS/MP4 streams to Web Video Caster:

```
iPhone (Web Video Caster)          Mac (this repo)              vStream
┌──────────────────────┐   HTTP   ┌──────────────────────────┐ sources
│ open http://mac:8786 │ ───────► │ bridge/server.py         │ ──────►
│ detect <video>       │ ◄─────── │ runner + shims + proxy   │
│ then cast stream     │          └──────────────────────────┘
└──────────────────────┘
```

The proxy rewrites HLS playlists and relays segments with the required
headers when Web Video Caster cannot send them directly.

## Source and upstream dependency

The catalogs, scrapers, and resolvers are not copied into this repository.
They are loaded at runtime from the original project:

- **Source**: [Kodi-vStream/venom-xbmc-addons](https://github.com/Kodi-vStream/venom-xbmc-addons)
- **Branch used**: `Beta`
- **Expected path**: `venom/plugin.video.vstream`
- **Upstream license**: GNU GPL v3, see the `LICENSE` file from vStream

Prepare the sparse checkout after cloning this repository:

```bash
git clone --filter=blob:none --sparse --branch Beta \
  https://github.com/Kodi-vStream/venom-xbmc-addons.git venom
git -C venom sparse-checkout set plugin.video.vstream
```

The `venom/` directory is an external dependency ignored by the
PKWwebVideoCaster repository; changes to it should be made upstream,
not in this repository.

## Installation and usage

Install Python 3 and the dependencies:

```bash
python3 -m pip install --user -r requirements.txt
./run.sh
```

The server uses `config.json`, listens by default on `0.0.0.0:8786`, and
prints the network address to open in Web Video Caster. The Mac and the
phone must be on the same local network.

## Security

This bridge is a local tool, not a public web service:

- the HTTP server has no authentication and no TLS;
- binding `0.0.0.0` is required for phone access, but port `8786` must
  never be forwarded to the Internet;
- the proxy follows upstream URLs and redirects; it must not be reachable
  by untrusted users;
- `/debug` may expose errors and resolution URLs.

Use a local firewall or private VPN. Public exposure would require at
minimum authentication, strict upstream destination validation, SSRF
protections, TLS, and rate limiting.

## Structure

```
bridge/                 bridge code, Kodi shims, and HLS proxy
config.json             listen host and port
requirements.txt        direct Python dependencies
run.sh                  launcher
venom/                  sparse checkout of the upstream dependency (not tracked)
```

## Limitations

- Results depend on the availability and evolution of upstream sources.
- Premium/debrid resolution is not enabled.
- FlareSolverr is not required by the current configuration.
