"""Shared button rendering helpers used by both web UI and standalone renderer.

This module provides a minimal, dependency-free `_render_button` and
`_render_exit_button` so both `menu_mcp` and `menu_server` can import the
same implementation (one-way dependency on `menu_mcp`).
"""
from typing import Optional
import html


def _render_button(name: str, description: str, *, onclick: str = "pick(this.dataset.name)", css_class: str = "btn", include_data_name: bool = True) -> str:
    label_html = html.escape(name)
    desc_html = html.escape(description)
    parts = [f'<button class="{css_class}"']
    if include_data_name:
        data_name = html.escape(name, quote=True)
        parts.append(f' data-name="{data_name}"')
    parts.append(f' onclick="{onclick}">')
    parts.append(f"<strong>{label_html}</strong>")
    if desc_html:
        parts.append(f"<span>{desc_html}</span>")
    parts.append("</button>")
    return "".join(parts)


def _render_exit_button() -> str:
    # Use the generic button renderer for consistent markup across UIs.
    # Do not include a data-name for the exit control.
    return _render_button("Exit", "", onclick="doExit()", css_class="btn exit", include_data_name=False)

