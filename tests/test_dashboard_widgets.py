"""Dashboard widget mounting and Filament-parity APIs."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from almasix.orbit.panels.pages.dashboard import Dashboard
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.routing import mount_orbit_assets, mount_panel
from almasix.orbit.widgets import (
    ChartWidget,
    Stat,
    StatsOverviewWidget,
    Widget,
)
from almasix.routing.router import Router


class _HiddenWidget(Widget):
    @classmethod
    def can_view(cls, **ctx: object) -> bool:
        return False

    def render_body(self, state=None, **ctx):  # type: ignore[no-untyped-def]
        return "HIDDEN"


class _SortedB(Widget):
    sort = 20

    def render_body(self, state=None, **ctx):  # type: ignore[no-untyped-def]
        return "WIDGET-B"


class _SortedA(Widget):
    sort = 5

    def render_body(self, state=None, **ctx):  # type: ignore[no-untyped-def]
        return "WIDGET-A"


class _SpanWidget(Widget):
    column_span = "full"

    def render_body(self, state=None, **ctx):  # type: ignore[no-untyped-def]
        return "SPAN"


class CustomDash(Dashboard):
    title = "Analytics"

    @classmethod
    def get_columns(cls) -> int:
        return 3

    @classmethod
    def get_widgets(cls, panel=None):  # type: ignore[no-untyped-def]
        return [
            StatsOverviewWidget.make("stats")
            .heading("Overview")
            .stats([Stat.make("Users").value(12)]),
            _SortedB,
            _SortedA,
            _HiddenWidget,
            _SpanWidget.make().column_span({"md": 2}),
        ]


class FilteredDash(Dashboard):
    persists_filters_in_session = True

    @classmethod
    def get_widgets(cls, panel=None):  # type: ignore[no-untyped-def]
        return [Widget.make("w").heading("W")]


FilteredDash.filters_form(
    SimpleNamespace(render=lambda state=None, **ctx: f'<form data-f="{state}"></form>')
)
FilteredDash.header_filter_actions(
    [SimpleNamespace(render=lambda **ctx: '<button type="button">Filter</button>')]
)


def test_dashboard_mounts_panel_widgets_sorted() -> None:
    panel = (
        Panel.make("admin")
        .path("admin")
        .login(False)
        .widgets([_SortedB, _SortedA, _HiddenWidget])
    )
    html = Dashboard.render(panel=panel, brand="Orbit")
    assert "WIDGET-A" in html and "WIDGET-B" in html
    assert "HIDDEN" not in html
    assert html.index("WIDGET-A") < html.index("WIDGET-B")
    assert 'style="--or-dashboard-cols: 2"' in html
    assert 'data-cols="2"' in html


def test_custom_dashboard_get_widgets_and_columns() -> None:
    html = CustomDash.render(brand="X")
    assert "Analytics" in html
    assert "--or-dashboard-cols: 3" in html
    assert "Overview" in html and "Users" in html
    assert "or-col-span-md-2" in html
    assert "HIDDEN" not in html


def test_dashboard_filters_form_and_header_actions() -> None:
    html = FilteredDash.render(page_filters={"q": "1"}, brand="X")
    assert "or-dashboard-filters" in html
    assert 'data-f=' in html
    assert "or-dashboard-header-actions" in html
    assert "Filter" in html


def test_dashboard_responsive_columns_dict() -> None:
    class Wide(Dashboard):
        @classmethod
        def get_columns(cls):
            return {"md": 2, "xl": 4}

    html = Wide.render(widgets=["<div>w</div>"])
    assert "--or-dashboard-cols:" in html
    assert "or-dashboard-widgets" in html


def test_dashboard_html_string_widgets_compat() -> None:
    html = Dashboard.render(widgets=["<b>w1</b>", 123, "<i>w2</i>"], brand="X")
    assert "or-dashboard-widgets" in html and "w1" in html and "w2" in html


def test_dashboard_welcome_without_widgets() -> None:
    html = Dashboard.render(brand="Acme")
    assert "Welcome to Acme" in html


def test_dashboard_mount_widgets_helper() -> None:
    panel = Panel.make("a").widgets([_SortedA])
    widgets = Dashboard.mount_widgets(panel)
    assert len(widgets) == 1
    assert widgets[0].get_sort() == 5


def test_routing_passes_widgets_into_dashboard() -> None:
    router = Router()
    panel = (
        Panel.make("admin")
        .path("admin")
        .login(False)
        .widgets([_SortedA, ChartWidget.make().labels(["a"]).datasets([{"data": [1]}])])
    )
    mount_panel(router, panel)
    home = next(
        r
        for r in router.routes
        if getattr(r, "route_name", None) == "orbit.admin.home"
        or str(getattr(r, "route_name", "") or "").endswith(".home")
    )
    request = SimpleNamespace(
        url=SimpleNamespace(path="/admin", query=""),
        query_params={"period": "week"},
        session={},
    )
    result = asyncio.run(home.action(request))
    body = getattr(result, "body", None) or getattr(result, "content", b"")
    if isinstance(body, bytes):
        text = body.decode()
    else:
        text = str(body)
    assert "WIDGET-A" in text
    assert "data-chart-library" in text or "or-chart" in text
    assert "chart.umd.min.js" in text
    assert "apexcharts.min.js" in text


def test_chart_assets_mounted() -> None:
    router = Router()
    mount_orbit_assets(router)
    uris = {getattr(r, "uri", None) for r in router.routes}
    assert "/vendor/orbit/chart.umd.min.js" in uris
    assert "/vendor/orbit/apexcharts.min.js" in uris
    chart_route = next(r for r in router.routes if r.uri.endswith("chart.umd.min.js"))
    resp = asyncio.run(chart_route.action())
    body = getattr(resp, "body", None) or getattr(resp, "content", b"")
    assert body


def test_page_filters_session_merge() -> None:
    from almasix.orbit.panels.routing import _dashboard_page_filters

    class Persist(Dashboard):
        persists_filters_in_session = True

    class Multi(SimpleNamespace):
        def multi_items(self):
            return [("a", "1"), ("b", "2")]

    request = SimpleNamespace(
        query_params={"b": "2"},
        session={"orbit_dashboard_filters": {"a": "1"}},
    )
    filters = _dashboard_page_filters(request, Persist)
    assert filters["a"] == "1" and filters["b"] == "2"

    multi_req = SimpleNamespace(query_params=Multi(), session=None)
    assert _dashboard_page_filters(multi_req, Dashboard) == {"a": "1", "b": "2"}

    class BoomSession(dict):
        def get(self, *a, **k):  # type: ignore[no-untyped-def]
            raise RuntimeError("session boom")

    class Persist2(Dashboard):
        persists_filters_in_session = True

    boom = SimpleNamespace(query_params={}, session=BoomSession())
    assert _dashboard_page_filters(boom, Persist2) == {}

    class BadQP:
        def items(self):
            raise RuntimeError("qp boom")

    assert _dashboard_page_filters(SimpleNamespace(query_params=BadQP()), Dashboard) == {}

    # session present but no stored filters / non-dict stored
    empty_sess = SimpleNamespace(query_params={"x": "1"}, session={})
    assert _dashboard_page_filters(empty_sess, Persist) == {"x": "1"}
    nondict = SimpleNamespace(
        query_params={},
        session={"orbit_dashboard_filters": "nope"},
    )
    assert _dashboard_page_filters(nondict, Persist) == {}
    no_session = SimpleNamespace(query_params={"z": "9"}, session=None)
    assert _dashboard_page_filters(no_session, Persist) == {"z": "9"}


def test_dashboard_filter_schema_variants_and_route_path() -> None:
    class SeqDash(Dashboard):
        route_path = "analytics"

    assert SeqDash.get_route_path() == "analytics"

    class Comp:
        def render(self, state=None, **ctx):  # type: ignore[no-untyped-def]
            return f"<em>{state}</em>"

    SeqDash.filters_form([Comp(), "plain"])
    html = SeqDash.render(page_filters={"q": "1"}, widgets=["<b>w</b>"])
    assert "<em>" in html and "plain" in html

    class StrDash(Dashboard):
        pass

    StrDash.filters_form("filters-only")
    html2 = StrDash.render(page_filters={})
    assert "filters-only" in html2 and "or-dashboard-filters" in html2

    class HeaderOnly(Dashboard):
        filters_in_header = True

    HeaderOnly.header_filter_actions(["raw-action"])
    html3 = HeaderOnly.render(widgets=["<i>x</i>"])
    assert "raw-action" in html3

    class EmptyHeader(Dashboard):
        filters_in_header = True

    assert "or-dashboard-header-actions" not in EmptyHeader.render()

    class DefaultCols(Dashboard):
        @classmethod
        def get_columns(cls):
            return {"default": 2, "md": 3}

    html4 = DefaultCols.render(widgets=["<b>1</b>"], columns={"default": 2, "md": 3})
    assert "--or-dashboard-cols: 2" in html4
    assert "--or-dashboard-cols-md: 3" in html4
