"""Security and observability basics with the standard library.

Run:
    python 15-security-observability/logging_security.py
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse


SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_-]{6,}|Bearer\s+[A-Za-z0-9._-]+)")


def redact(text: str) -> str:
    return SECRET_RE.sub("[REDACTED]", text)


def validate_public_http_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL must use http or https")
    if not parsed.netloc:
        raise ValueError("URL must include a host")
    return url


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    logger = logging.getLogger("security-demo")

    raw_message = "calling API with token Bearer abc.def.ghi and key sk-test123456"
    logger.info("outbound_request %s", redact(raw_message))

    try:
        validate_public_http_url("file:///etc/passwd")
    except ValueError as exc:
        logger.warning("blocked_url reason=%s", exc)


if __name__ == "__main__":
    main()
