"""
Safe HTML helpers. All dynamic values MUST pass through esc() before
interpolation into any HTML string.
"""
from __future__ import annotations

import html
from typing import Any, Mapping


def esc(value: Any) -> str:
    """Escape for HTML text content / attributes. Never skip this."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def attr(name: str, value: Any) -> str:
    """Build a single HTML attribute safely. Empty value → omitted."""
    if value is None or value is False:
        return ""
    if value is True:
        return f" {esc(name)}"
    return f' {esc(name)}="{esc(value)}"'


def class_names(*parts: Any, **flags: bool) -> str:
    """Join class names; truthy flags include the key as a class."""
    classes: list[str] = []
    for p in parts:
        if not p:
            continue
        if isinstance(p, (list, tuple)):
            classes.extend(str(x) for x in p if x)
        else:
            classes.append(str(p))
    for key, on in flags.items():
        if on:
            classes.append(key.replace("_", "-"))
    return " ".join(classes)


def html_block(tag: str, content: str = "", *, attrs: Mapping[str, Any] | None = None, self_closing: bool = False) -> str:
    """Minimal element builder. `content` is assumed already escaped or trusted static."""
    attr_str = ""
    if attrs:
        attr_str = "".join(attr(k, v) for k, v in attrs.items())
    if self_closing:
        return f"<{tag}{attr_str} />"
    return f"<{tag}{attr_str}>{content}</{tag}>"
