"""Configura certificados SSL antes de llamadas a Google APIs."""

from __future__ import annotations

import os
import sys


def configure_ssl() -> None:
    try:
        import truststore

        truststore.inject_into_ssl()
        return
    except ImportError:
        pass

    try:
        import certifi

        ca_bundle = certifi.where()
        os.environ.setdefault("SSL_CERT_FILE", ca_bundle)
        os.environ.setdefault("REQUESTS_CA_BUNDLE", ca_bundle)
    except ImportError:
        pass

    if sys.platform == "win32":
        try:
            import certifi_win32  # noqa: F401
        except ImportError:
            pass


configure_ssl()
