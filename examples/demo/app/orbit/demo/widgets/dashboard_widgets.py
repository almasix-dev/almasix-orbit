"""Dashboard widgets for the Orbit Records demo home."""

from __future__ import annotations

from almasix.orbit import widgets as orbit_widgets
from almasix.orbit.tables import BadgeColumn, Table, TextColumn

from app.orbit.demo.catalog_metrics import (
    albums_by_year,
    catalog_counts,
    format_counts,
    plays_by_week,
    recent_albums,
    sparkline_from_plays,
    top_tracks_by_plays,
)


class WelcomeWidget(orbit_widgets.Widget):
    """Intro card for the Orbit Records demo."""

    sort = 0
    heading = "Orbit Records"
    description = "Public music catalog demo"
    column_span = "full"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "welcome")

    def render_body(self, state=None, **ctx) -> str:  # type: ignore[no-untyped-def]
        brand = str(ctx.get("brand") or "Orbit Demo")
        return (
            f'<p class="or-muted">Welcome to <strong>{brand}</strong> — a full '
            "Orbit showcase on SQLite. Explore Artists, Albums, and Tracks; open "
            "Insights for pie, radar, and Apex breakdowns of the same catalog.</p>"
        )


class CatalogStats(orbit_widgets.StatsOverviewWidget):
    """KPI strip computed from the SQLite catalog."""

    sort = 1
    heading = "Catalog"
    column_span = "full"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "catalog_stats")
        counts = catalog_counts()
        spark = sparkline_from_plays()
        self.stats(
            [
                orbit_widgets.Stat.make("Artists")
                .value(counts["artists"])
                .description(f'{counts["released"]} released albums')
                .description_icon("heroicon-m-musical-note")
                .color("primary")
                .icon("heroicon-o-user-group")
                .chart(spark)
                .url("/artists"),
                orbit_widgets.Stat.make("Albums")
                .value(counts["albums"])
                .description(f'{counts["draft"]} drafts · {counts["featured"]} featured')
                .color("success")
                .icon("heroicon-o-rectangle-stack")
                .chart(spark[::-1] if spark else [])
                .url("/albums"),
                orbit_widgets.Stat.make("Tracks")
                .value(counts["tracks"])
                .description(
                    f'{counts["trashed"]} soft-deleted'
                    if counts["trashed"]
                    else "Soft-deletes supported"
                )
                .color("info")
                .icon("heroicon-o-queue-list")
                .chart(spark)
                .url("/tracks"),
                orbit_widgets.Stat.make("Plays")
                .value(f'{counts["plays"]:,}')
                .description("Lifetime stream counts")
                .color("warning")
                .icon("heroicon-o-speaker-wave")
                .chart(spark),
            ]
        )


class ReleasesChart(orbit_widgets.ChartWidget):
    """Albums by year — Chart.js bar."""

    sort = 10
    heading = "Releases by year"
    description = "Album count · Chart.js bar"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "releases_chart")
        labels, data = albums_by_year()
        self.chart_library(orbit_widgets.ChartLibrary.CHARTJS)
        self.chart_type("bar")
        self.labels(labels or ["—"])
        self.datasets([{"label": "Albums", "data": data or [0]}])
        self.color("primary")
        self.max_height("280px")


class PlaysTrendChart(orbit_widgets.ChartWidget):
    """Multi-dataset weekly plays — Chart.js line with range filter tabs."""

    sort = 11
    heading = "Play trend"
    description = "Streams vs discovery · Chart.js line"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "plays_trend")
        labels, datasets = plays_by_week("30d")
        self.chart_library(orbit_widgets.ChartLibrary.CHARTJS)
        self.chart_type("line")
        self.filters({"7d": "7 days", "30d": "30 days", "90d": "90 days"})
        self.filter("30d")
        self.labels(labels or ["—"])
        self.datasets(datasets or [{"label": "Streams", "data": [0]}])
        self.color("info")
        self.max_height("280px")
        self.options({"plugins": {"legend": {"position": "bottom"}}})


class FormatsChart(orbit_widgets.ChartWidget):
    """Album formats — Chart.js doughnut."""

    sort = 12
    heading = "Formats"
    description = "Album share · Chart.js doughnut"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "formats_chart")
        rows = format_counts()
        labels = [name.title() for name, _ in rows]
        data = [count for _, count in rows]
        self.chart_library(orbit_widgets.ChartLibrary.CHARTJS)
        self.chart_type("doughnut")
        if labels:
            self.labels(labels)
            self.datasets([{"data": data}])
        else:
            self.empty_state_heading("No format data yet")
            self.empty_state_description("Seed the catalog to see format share.")
        self.color("success")
        self.max_height("280px")


class StreamsChart(orbit_widgets.ChartWidget):
    """Top tracks by play count — ApexCharts area."""

    sort = 13
    heading = "Top streams"
    description = "Play counts · ApexCharts area"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "streams_chart")
        labels, data = top_tracks_by_plays(8)
        self.chart_library(orbit_widgets.ChartLibrary.APEX)
        self.chart_type("area")
        self.labels(labels or ["—"])
        self.datasets([{"label": "Plays", "data": data or [0]}])
        self.color("warning")
        self.max_height("280px")
        self.collapsible()


class RecentAlbumsTable(orbit_widgets.TableWidget):
    """Recent albums on the home dashboard."""

    sort = 20
    heading = "Recent albums"
    description = "Latest rows in the catalog"
    column_span = "full"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "recent_albums")
        rows = recent_albums(8)
        self.table(
            Table.make()
            .columns(
                [
                    TextColumn.make("title").label("Title"),
                    TextColumn.make("artist").label("Artist"),
                    BadgeColumn.make("status").label("Status"),
                    TextColumn.make("year").label("Year"),
                ]
            )
            .records(rows)
            .paginated(False)
        )
