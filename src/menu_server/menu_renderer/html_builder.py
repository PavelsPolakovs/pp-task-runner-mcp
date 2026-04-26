"""HTML-building helpers for the menu renderer.

This module contains the low-level helpers that produce the buttons,
status div, script and the `_build_html` function which composes the
complete HTML page. Extracting these keeps `menu_renderer.py` as a
small public-facing API surface.
"""
from typing import Dict
import html
from .styles import _menu_styles
from .components.button import _render_button


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
        "try{const d=await post({action:'select',name});"
        "if(d.switch){window.location='/?menu='+encodeURIComponent(d.switch);return;}"
        "document.getElementById('status').textContent=d.feedback||'✓ Done';}"
        "catch{document.getElementById('status').textContent='Error';}}"
        "async function doExit(){document.getElementById('status').textContent='Closing…';"
        "try{await post({action:'exit',name:''});}catch{}window.close();}"
        # Do not automatically send a close beacon on beforeunload. Closing
        # the page during in-menu navigation previously caused the server to
        # shutdown prematurely. The server will still stop on explicit
        # exit/close actions posted by the client.
    )


def _build_html(options: Dict[str, str], menu_name: str) -> str:
    buttons = "".join(_render_button(name, desc) for name, desc in options.items())
    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html lang=\"en\">")
    html_parts.append("<head>")
    html_parts.append("<meta charset=\"utf-8\">")
    display = "Main Menu" if menu_name == "main" else menu_name
    html_parts.append(f"<title>PP Task Runner — {display}</title>")
    html_parts.append("<style>")
    html_parts.append(_menu_styles())
    html_parts.append("</style>")
    html_parts.append("</head>")
    html_parts.append("<body>")
    html_parts.append('<div class="card">')
    html_parts.append(f"  <h1>PP Task Runner — {display}</h1>")
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

