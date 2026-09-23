"""Application shell: sidebar, header, page frame."""

def __getattr__(name: str):
    if name in ("NAV_BY_ROLE", "nav_items_for_role"):
        from ui.shell.nav import NAV_BY_ROLE, nav_items_for_role
        return NAV_BY_ROLE if name == "NAV_BY_ROLE" else nav_items_for_role
    if name == "render_sidebar":
        from ui.shell.sidebar import render_sidebar
        return render_sidebar
    if name == "render_header":
        from ui.shell.header import render_header
        return render_header
    if name in ("page_frame", "render_shell"):
        from ui.shell.frame import page_frame, render_shell
        return page_frame if name == "page_frame" else render_shell
    raise AttributeError(name)

__all__ = [
    "NAV_BY_ROLE",
    "nav_items_for_role",
    "render_sidebar",
    "render_header",
    "page_frame",
    "render_shell",
]
