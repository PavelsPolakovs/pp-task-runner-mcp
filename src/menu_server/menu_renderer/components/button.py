
"""Button rendering helpers.

Contains the `_render_button` helper extracted from `html_builder.py` so
that button-specific rendering can live in its own module.
"""
import html


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




