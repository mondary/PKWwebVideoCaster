# -*- coding: utf-8 -*-
"""DNS fallback for hosters blocked by the local ISP resolver.

French ISP DNS filtering commonly maps blocked streaming hosters to ::1 instead
of returning NXDOMAIN. Kodi/vStream normally solves this with its optional
script.module.dnspython addon. This bridge runs outside Kodi, so it installs
the equivalent process-wide getaddrinfo fallback: preserve normal DNS answers;
only query public resolvers when lookup fails or yields only loopback/unspecified
addresses for a real domain.
"""

import ipaddress
import socket
import threading

PUBLIC_NAMESERVERS = ('1.1.1.1', '80.67.169.40', '9.9.9.9')

_original_getaddrinfo = socket.getaddrinfo
_lock = threading.Lock()
_installed = False
_resolver = None


def _is_domain(host):
    if not isinstance(host, str) or not host or host.lower() == 'localhost':
        return False
    try:
        ipaddress.ip_address(host)
        return False
    except ValueError:
        return True


def _only_poisoned_addresses(infos):
    if not infos:
        return False
    for info in infos:
        try:
            address = ipaddress.ip_address(info[4][0])
        except (IndexError, ValueError):
            return False
        if not (address.is_loopback or address.is_unspecified):
            return False
    return True


def _port_number(port):
    if port is None:
        return 0
    try:
        return int(port)
    except (TypeError, ValueError):
        return socket.getservbyname(str(port))


def _resolver_instance():
    global _resolver
    with _lock:
        if _resolver is None:
            import dns.resolver
            resolver = dns.resolver.Resolver(configure=False)
            resolver.nameservers = list(PUBLIC_NAMESERVERS)
            resolver.timeout = 2
            resolver.lifetime = 5
            _resolver = resolver
        return _resolver


def _public_lookup(host, port, family, socktype, proto):
    resolver = _resolver_instance()
    record_types = ('A', 'AAAA')
    if family == socket.AF_INET:
        record_types = ('A',)
    elif family == socket.AF_INET6:
        record_types = ('AAAA',)

    last_error = None
    for record_type in record_types:
        try:
            answer = resolver.resolve(host, record_type)
            address = str(answer[0])
            numeric_port = _port_number(port)
            if record_type == 'A':
                return [(socket.AF_INET, socktype or socket.SOCK_STREAM,
                         proto or socket.IPPROTO_TCP, '', (address, numeric_port))]
            return [(socket.AF_INET6, socktype or socket.SOCK_STREAM,
                     proto or socket.IPPROTO_TCP, '', (address, numeric_port, 0, 0))]
        except Exception as e:
            last_error = e
    raise socket.gaierror(-2, 'DNS public failed for %s: %s' % (host, last_error))


def install_public_dns_fallback():
    """Install an idempotent getaddrinfo fallback; return True if available."""
    global _installed
    if _installed:
        return True
    try:
        import dns.resolver  # noqa: F401 — dependency probe
    except ImportError:
        return False

    def getaddrinfo(host, port, family=0, socktype=0, proto=0, flags=0):
        infos = None
        try:
            infos = _original_getaddrinfo(host, port, family, socktype, proto, flags)
        except socket.gaierror:
            pass

        if infos is not None and (not _is_domain(host) or not _only_poisoned_addresses(infos)):
            return infos

        if _is_domain(host):
            try:
                return _public_lookup(host, port, family, socktype, proto)
            except socket.gaierror:
                pass

        if infos is not None:
            return infos
        return _original_getaddrinfo(host, port, family, socktype, proto, flags)

    socket.getaddrinfo = getaddrinfo
    _installed = True
    return True
