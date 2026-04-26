
"""HTML renderer for the standalone menu server.

This module contains the logic previously embedded inside
`src/menu_server/menu_server.py` for generating the full HTML page,
CSS and JS. It exposes a single public function `render_menu_html(tasks)`.
"""
from typing import Dict
import html


def _menu_styles() -> str:
	return (
		"*{box-sizing:border-box;margin:0;padding:0}"
		"body{font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;background:#f5f5f5;"
		"display:flex;align-items:center;justify-content:center;min-height:100vh}"
		".card{background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.1);"
		"padding:32px;width:100%;max-width:480px}"
		"h1{font-size:1.1em;color:#555;margin-bottom:20px;font-weight:500}"
		".btn{display:block;width:100%;padding:14px 16px;margin:8px 0;"
		"border:1px solid #e0e0e0;border-radius:8px;background:#fff;"
		"cursor:pointer;text-align:left;font-size:.95em;transition:.15s}"
		".btn:hover{background:#f0f7ff;border-color:#4a9eff}"
		".btn strong{display:block}"
		".btn span{display:block;font-size:.78em;color:#999;margin-top:3px}"
		".btn.exit{display:block;width:100%;padding:12px 16px;margin-top:16px;"
		"border:1px solid #ffcdd2;border-radius:8px;background:#fff;"
		"cursor:pointer;text-align:center;font-size:.9em;color:#e53935;transition:.15s}"
		".exit-btn:hover{background:#ffebee}"
		"#status{margin-top:16px;font-size:.85em;color:#4a9eff;min-height:1.2em;text-align:center}"
	)


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


def render_menu_html(tasks: Dict[str, str]) -> str:
	"""Public API: render the full HTML page for the given tasks mapping.

	Returns a string (not bytes) — callers can encode it as needed.
	"""
	return _build_html(tasks)


