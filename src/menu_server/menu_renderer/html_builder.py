"""HTML-building helpers for the menu renderer.

This module contains the low-level helpers that produce the buttons,
status div, script and the `_build_html` function which composes the
complete HTML page. Extracting these keeps `menu_renderer.py` as a
small public-facing API surface.
"""
from typing import Dict
import html
from .styles import _menu_styles


def _render_button(name: str, description: str, *, onclick: str = "pick(this.dataset.name)", css_class: str = "btn", include_data_name: bool = True) -> str:
    """Render a generic button for the menu.

    Caller may override `onclick`, `css_class` and whether to include the `data-name` attribute.
    """
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
    # Use the generic button renderer so the exit button markup is produced
    # in a single place. Do not include a data-name for the exit control.
    return _render_button("Exit", "", onclick="doExit()", css_class="btn exit", include_data_name=False)


def _render_status_div() -> str:
    return '<div id="status"></div>'


def _render_script() -> str:
    return (
        "async function post(body){"
        "const r=await fetch('/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});"
        "return r.json();}"
        "async function pick(name){"
        "document.getElementById('status').textContent='Running '+name+'…';"
        "try{const d=await post({action:'select',name});document.getElementById('status').textContent=d.feedback||'✓ Done';}"
        "catch{document.getElementById('status').textContent='Error';}}"
        "async function doExit(){document.getElementById('status').textContent='Closing…';"
        "try{await post({action:'exit',name:''});}catch{}window.close();}"
        "window.addEventListener('beforeunload',()=>navigator.sendBeacon('/action',JSON.stringify({action:'close',name:''})));"
    )


def _build_html(options: Dict[str, str]) -> str:
    buttons = "".join(_render_button(name, desc) for name, desc in options.items())
    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html lang=\"en\">")
    html_parts.append("<head>")
    html_parts.append("<meta charset=\"utf-8\">")
    html_parts.append("<title>PP Task Runner — Main Menu</title>")
    html_parts.append("<style>")
    html_parts.append(_menu_styles())
    html_parts.append("</style>")
    html_parts.append("</head>")
    html_parts.append("<body>")
    html_parts.append('<div class="card">')
    html_parts.append("  <h1>PP Task Runner — Main Menu</h1>")
    html_parts.append(buttons)
    html_parts.append(_render_exit_button())
    html_parts.append(_render_status_div())
    html_parts.append("</div>")
    html_parts.append("<script>")
    html_parts.append(_render_script())
    html_parts.append("</script>")
    html_parts.append("</body>")
    html_parts.append("</html>")
    return "\n".join(html_parts)

