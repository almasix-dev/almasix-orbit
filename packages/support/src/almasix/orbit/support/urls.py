"""Public URL helpers for shell assets (logos, etc.)."""

from __future__ import annotations


def resolve_public_url(value: str | None) -> str | None:
    """Normalize a configured public URL for ``src`` / ``href``.

    - Absolute ``http(s)://``, protocol-relative ``//``, ``data:``, and ``blob:``
      values are returned unchanged (including the result of ``asset(...)`` when
      it already produced an absolute URL).
    - Bare relatives (``images/logo.svg`` or ``/images/logo.svg``) are passed
      through Almasix ``url()`` so ``APP_URL`` / base path apply.
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

        return str(make_url(text))
    except Exception:
        return text if text.startswith("/") else f"/{text}"
