"""Dashboard widgets for the Orbit Admin sample panel."""

from __future__ import annotations

from typing import Any

from almasix.orbit import widgets as orbit_widgets
from almasix.orbit.tables import BadgeColumn, Table, TextColumn


def _tenant_slug(ctx: dict[str, Any]) -> str:
    tenant = ctx.get("tenant")
    return str(getattr(tenant, "slug", "") or "acme")


def _tenant_name(ctx: dict[str, Any]) -> str:
    tenant = ctx.get("tenant")
    return str(getattr(tenant, "name", "") or "Acme Corp")


def _overview_stats(**ctx: Any) -> list[orbit_widgets.Stat]:
    """KPI cards for the current team. Beta Labs is a smaller sample set."""
    name = _tenant_name(ctx)
    if _tenant_slug(ctx) == "beta":
        return [
            orbit_widgets.Stat.make("Users")
            .value(86)
            .description(f"{name} · +1% this week")
            .description_icon("heroicon-m-arrow-trending-up")
            .color("success")
            .icon("heroicon-o-users")
            .chart([40, 48, 52, 61, 70, 86]),
            orbit_widgets.Stat.make("Posts")
            .value(14)
            .description(f"{name} · 3 drafts")
            .color("primary")
            .icon("heroicon-o-document-text")
            .chart([4, 6, 8, 9, 11, 14]),
            orbit_widgets.Stat.make("Revenue")
            .value("$1.8k")
            .description(f"{name} · MRR")
            .color("warning")
            .icon("heroicon-o-banknotes")
            .chart([0.8, 0.9, 1.1, 1.3, 1.5, 1.8]),
        ]
    return [
        orbit_widgets.Stat.make("Users")
        .value(1280)
        .description(f"{name} · +4% this week")
        .description_icon("heroicon-m-arrow-trending-up")
        .color("success")
        .icon("heroicon-o-users")
        .chart([820, 932, 901, 1034, 1190, 1280]),
        orbit_widgets.Stat.make("Posts")
        .value(342)
        .description(f"{name} · 12 drafts")
        .color("primary")
        .icon("heroicon-o-document-text")
        .chart([210, 240, 280, 310, 330, 342]),
        orbit_widgets.Stat.make("Revenue")
        .value("$12.4k")
        .description(f"{name} · MRR")
        .color("warning")
        .icon("heroicon-o-banknotes")
        .chart([8.1, 9.2, 9.8, 10.4, 11.2, 12.4]),
    ]


class OverviewStats(orbit_widgets.StatsOverviewWidget):
    """KPI strip with sparklines."""

    sort = 1
    heading = "Overview"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "overview_stats")
        self.stats([_overview_stats])


class SignupsChart(orbit_widgets.ChartWidget):
    """Chart.js line chart (default library)."""

    sort = 10
    heading = "Signups"
    description = "Last 7 days · Chart.js"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "signups_chart")
        self.chart_library(orbit_widgets.ChartLibrary.CHARTJS)
        self.chart_type("line")
        self.labels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        self.datasets([{"label": "Users", "data": [12, 19, 14, 22, 18, 25, 30]}])
        self.color("primary")
        self.max_height("280px")

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        if _tenant_slug(ctx) == "beta":
            self.datasets([{"label": "Users", "data": [2, 3, 2, 4, 3, 5, 6]}])
        else:
            self.datasets([{"label": "Users", "data": [12, 19, 14, 22, 18, 25, 30]}])
        return super().render_body(state, **ctx)


class RevenueApexChart(orbit_widgets.ChartWidget):
    """ApexCharts area chart via ``.chart_library``."""

    sort = 11
    heading = "Revenue"
    description = "Monthly · ApexCharts"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "revenue_apex")
        self.chart_library(orbit_widgets.ChartLibrary.APEX)
        self.chart_type("area")
        self.labels(["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
        self.datasets([{"label": "MRR ($k)", "data": [12, 15, 14, 18, 22, 26]}])
        self.color("success")
        self.max_height("280px")

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        if _tenant_slug(ctx) == "beta":
            self.datasets([{"label": "MRR ($k)", "data": [1, 1, 1, 2, 2, 2]}])
        else:
            self.datasets([{"label": "MRR ($k)", "data": [12, 15, 14, 18, 22, 26]}])
        return super().render_body(state, **ctx)


class RecentPostsTable(orbit_widgets.TableWidget):
    """Small table widget for the home dashboard."""

    sort = 20
    heading = "Recent posts"
    description = "Latest drafts and publications"
    column_span = "full"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "recent_posts")
        self.table(
            Table.make()
            .columns(
                [
                    TextColumn.make("title").label("Title"),
                    BadgeColumn.make("status").label("Status"),
                    TextColumn.make("author").label("Author"),
                ]
            )
            .records(
                [
                    {
                        "title": "Launch Orbit",
                        "status": "published",
                        "author": "Ada",
                    },
                    {
                        "title": "Conduit hosts",
                        "status": "draft",
                        "author": "Grace",
                    },
                    {
                        "title": "Widget polish",
                        "status": "published",
                        "author": "Ada",
                    },
                ]
            )
            .paginated(False)
        )

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        if self._table is not None:
            if _tenant_slug(ctx) == "beta":
                rows = [
                    {"title": "Beta onboarding", "status": "published", "author": "Sam"},
                    {"title": "API sandbox", "status": "draft", "author": "Riley"},
                ]
            else:
                rows = [
                    {"title": "Launch Orbit", "status": "published", "author": "Ada"},
                    {"title": "Conduit hosts", "status": "draft", "author": "Grace"},
                    {"title": "Widget polish", "status": "published", "author": "Ada"},
                ]
            self._table.records(rows)
        return super().render_body(state, **ctx)


class WelcomeWidget(orbit_widgets.Widget):
    """Optional custom widget demonstrating ``render_body``."""

    sort = 0
    heading = "Welcome"
    description = "Custom widget on the app dashboard"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "welcome")

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        brand = str(ctx.get("brand") or "Orbit Admin")
        team = _tenant_name(ctx)
        return (
            f'<p class="or-muted">You are viewing <strong>{team}</strong> in '
            f"<strong>{brand}</strong>. Switch teams in the topbar — the stats, "
            "charts, and recent posts on this dashboard follow the current team.</p>"
        )
