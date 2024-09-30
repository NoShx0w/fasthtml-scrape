from fasthtml.common import *
from fasthtml.svg import Polyline

hdrs = [SortableJS(),StyleX("apps/nav/nav.css")]

app,rt = fast_app(hdrs=hdrs)

app_list = ["scrape","h2f"]

def navigation_bar(navigation_items: list[str]):
    return Nav(
        Ul(
            *[
                Li(Button(item, hx_get=f"/{item}/", hx_trigger="click", hx_target="#page-content", hx_swap="outerHTML", cls="primary-button"), cls="button-borders")
                for item in navigation_items
            ]
        ),
    )


@rt("/")
def index():
    return Div(
        Main(id="page-content", cls="content"),
        navigation_bar(app_list),
        cls="container",
        style="max-width: 100vw"
    )
