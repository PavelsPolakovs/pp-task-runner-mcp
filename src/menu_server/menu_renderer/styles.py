"""CSS styles used by the menu renderer.

This module extracts the large `_menu_styles` function out of
`menu_renderer.py` so the renderer module stays focused on HTML
generation.
"""

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

