"""Insights dashboard widgets — pie, radar, Apex bar, table, checklist."""

from __future__ import annotations

from almasix.orbit import widgets as orbit_widgets
from almasix.orbit.forms import (
    DatePicker,
    FileUpload,
    Form,
    Select,
    TextInput,
    ToggleButtons,
)
from almasix.orbit.schemas import Callout, Section, Wizard
from almasix.orbit.tables import BadgeColumn, Table, TextColumn

from app.orbit.demo.catalog_metrics import (
    albums_by_status,
    country_breakdown,
    genre_radar_series,
    platform_breakdown,
    top_artists_by_plays,
    top_track_rows,
)


class CountriesPieChart(orbit_widgets.ChartWidget):
    """Artists by country — Chart.js pie."""

    sort = 1
    heading = "Artists by country"
    description = "Roster geography · Chart.js pie"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "countries_pie")
        rows = country_breakdown()
        labels = [name for name, _ in rows]
        data = [count for _, count in rows]
        self.chart_library(orbit_widgets.ChartLibrary.CHARTJS)
        self.chart_type("pie")
        if labels:
            self.labels(labels)
            self.datasets([{"data": data}])
        else:
            self.empty_state_heading("No country data yet")
            self.empty_state_description("Seed artists with countries to populate this chart.")
        self.color("primary")
        self.max_height("300px")


class GenreRadarChart(orbit_widgets.ChartWidget):
    """Genre coverage — Chart.js radar with two datasets."""

    sort = 2
    heading = "Genre coverage"
    description = "Top tags · Chart.js radar"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "genre_radar")
        labels, datasets = genre_radar_series(6)
        self.chart_library(orbit_widgets.ChartLibrary.CHARTJS)
        self.chart_type("radar")
        if labels:
            self.labels(labels)
            self.datasets(datasets)
            self.options(
                {
                    "plugins": {"legend": {"position": "bottom"}},
                    "scales": {"r": {"beginAtZero": True}},
                }
            )
        else:
            self.empty_state_heading("No genre tags yet")
            self.empty_state_description("Add genres on artists to build the radar.")
        self.color("info")
        self.max_height("300px")


class PlatformsChart(orbit_widgets.ChartWidget):
    """Distribution platforms — ApexCharts donut."""

    sort = 3
    heading = "Platforms"
    description = "Artist storefronts · ApexCharts donut"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "platforms_chart")
        labels, data = platform_breakdown()
        self.chart_library(orbit_widgets.ChartLibrary.APEX)
        self.chart_type("doughnut")
        if labels:
            self.labels(labels)
            self.datasets([{"data": data}])
        else:
            self.empty_state_heading("No platforms yet")
            self.empty_state_description("Seed artist platforms to see this breakdown.")
        self.color("success")
        self.max_height("300px")


class StatusBreakdownChart(orbit_widgets.ChartWidget):
    """Album status — Chart.js doughnut."""

    sort = 4
    heading = "Release status"
    description = "Draft vs released · Chart.js doughnut"
    column_span = 1

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "status_breakdown")
        labels, data = albums_by_status()
        self.chart_library(orbit_widgets.ChartLibrary.CHARTJS)
        self.chart_type("doughnut")
        if labels:
            self.labels(labels)
            self.datasets([{"data": data}])
        else:
            self.empty_state_heading("No albums yet")
        self.color("warning")
        self.max_height("300px")


class TopArtistsChart(orbit_widgets.ChartWidget):
    """Top artists by plays — ApexCharts bar."""

    sort = 5
    heading = "Top artists"
    description = "Lifetime plays · ApexCharts bar"
    column_span = "full"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "top_artists_chart")
        labels, data = top_artists_by_plays(10)
        self.chart_library(orbit_widgets.ChartLibrary.APEX)
        self.chart_type("bar")
        self.labels(labels or ["—"])
        self.datasets([{"label": "Plays", "data": data or [0]}])
        self.color("primary")
        self.max_height("320px")
        self.apex_options(
            {
                "chart": {"type": "bar", "toolbar": {"show": False}},
                "plotOptions": {"bar": {"horizontal": True, "borderRadius": 4}},
                "series": [{"name": "Plays", "data": data or [0]}],
                "xaxis": {"categories": labels or ["—"]},
                "dataLabels": {"enabled": False},
            }
        )


class TopTracksTable(orbit_widgets.TableWidget):
    """Highest-play tracks for the Insights page."""

    sort = 10
    heading = "Top tracks"
    description = "By lifetime play count"
    column_span = "full"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "top_tracks_table")
        rows = top_track_rows(10)
        self.table(
            Table.make()
            .columns(
                [
                    TextColumn.make("title").label("Track"),
                    TextColumn.make("album").label("Album"),
                    BadgeColumn.make("status").label("Status"),
                    TextColumn.make("plays").label("Plays"),
                ]
            )
            .records(rows)
            .paginated(False)
        )


class ReleaseChecklistWidget(orbit_widgets.Widget):
    """Schema Wizard checklist hosted as a custom widget."""

    sort = 20
    heading = "New release checklist"
    description = "Wizard on a custom Insights dashboard"
    column_span = "full"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "release_checklist")

    def render_body(self, state=None, **ctx) -> str:  # type: ignore[no-untyped-def]
        form = Form.make("release_checklist").schema(
            [
                Callout.make()
                .info()
                .label("Checklist only")
                .description(
                    "Use Albums → Create to persist a real release. This Wizard "
                    "shows schema steps on an analytics dashboard."
                ),
                Wizard.make("checklist")
                .skippable()
                .steps(
                    (
                        "Details",
                        [
                            Section.make("d")
                            .heading("Basics")
                            .schema(
                                [
                                    TextInput.make("working_title").label(
                                        "Working title"
                                    ),
                                    ToggleButtons.make("status")
                                    .options(
                                        {"draft": "Draft", "released": "Released"}
                                    )
                                    .default("draft"),
                                    DatePicker.make("target_date").label(
                                        "Target date"
                                    ),
                                ]
                            ),
                        ],
                    ),
                    (
                        "Artwork",
                        [
                            FileUpload.make("mock_cover")
                            .label("Draft cover")
                            .image()
                            .directory("insight-covers")
                            .panel_layout()
                            .image_preview_height(160),
                            Select.make("format")
                            .options(
                                {
                                    "digital": "Digital",
                                    "vinyl": "Vinyl",
                                    "cd": "CD",
                                    "streaming": "Streaming",
                                }
                            ),
                        ],
                    ),
                    (
                        "Ready",
                        [
                            Callout.make()
                            .success()
                            .label("Ready to ship")
                            .description(
                                "Create the album under Catalog → Albums, then "
                                "add tracks from the relation manager."
                            ),
                        ],
                    ),
                ),
            ]
        )
        return form.render(**ctx)
