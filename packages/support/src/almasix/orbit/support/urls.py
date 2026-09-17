"""Public URL helpers for shell assets (logos, etc.)."""

from __future__ import annotations

from urllib.parse import urlparse


def resolve_public_url(value: str | None) -> str | None:
    """Normalize a configured public URL for ``src`` / ``href``.

    - Absolute ``http(s)://``, protocol-relative ``//``, ``data:``, and ``blob:``
      values are returned unchanged (including the result of ``asset(...)`` when
      it already produced an absolute URL).
    - Bare relatives (``images/logo.svg`` or ``/images/logo.svg``) resolve to a
      **root-relative** path (``/images/logo.svg``). We deliberately drop the
      ``APP_URL`` host so logos load from whatever host the browser used — an
      absolute ``http://lan-ip/...`` logo while you browse via ``localhost``
      (or the reverse) leaves the tab spinner spinning until that fetch 404s.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    lower = text.lower()
    if lower.startswith(("http://", "https://", "//", "data:", "blob:")):
        return text
    try:
        from almasix.routing.url import url as make_url

        resolved = str(make_url(text))
    except Exception:
        return text if text.startswith("/") else f"/{text}"
    if resolved.startswith(("http://", "https://")):
        parsed = urlparse(resolved)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        return path
    if resolved.startswith("//"):
        # Protocol-relative from url() — treat as absolute CDN-style.
        return resolved
    return resolved if resolved.startswith("/") else f"/{resolved}"
