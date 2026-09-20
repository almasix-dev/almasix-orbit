"""Dashboard widgets for the Orbit Admin sample panel."""

from __future__ import annotations

from almasix.orbit import widgets as orbit_widgets
from almasix.orbit.tables import BadgeColumn, Table, TextColumn


class OverviewStats(orbit_widgets.StatsOverviewWidget):
    """KPI strip with sparklines."""

    sort = 1
    heading = "Overview"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "overview_stats")
        self.stats(
            [
                orbit_widgets.Stat.make("Users")
                .value(1280)
                .description("+4% this week")
                .description_icon("heroicon-m-arrow-trending-up")
                .color("success")
                .icon("heroicon-o-users")
                .chart([820, 932, 901, 1034, 1190, 1280]),
                orbit_widgets.Stat.make("Posts")
                .value(342)
                .description("12 drafts")
                .color("primary")
                .icon("heroicon-o-document-text")
                .chart([210, 240, 280, 310, 330, 342]),
                orbit_widgets.Stat.make("Revenue")
                .value("$12.4k")
                .description("MRR")
                .color("warning")
                .icon("heroicon-o-banknotes")
                .chart([8.1, 9.2, 9.8, 10.4, 11.2, 12.4]),
            ]
        )


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


class WelcomeWidget(orbit_widgets.Widget):
    """Optional custom widget demonstrating ``render_body``."""

    sort = 0
    heading = "Welcome"
    description = "Custom widget on the app dashboard"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "welcome")

    def render_body(self, state=None, **ctx) -> str:  # type: ignore[no-untyped-def]
        brand = str(ctx.get("brand") or "Orbit Admin")
        return (
            f'<p class="or-muted">Widgets + Dashboard sample for '
            f"<strong>{brand}</strong>. Stats, Chart.js, ApexCharts, and a table "
            "are registered on this panel.</p>"
        )
