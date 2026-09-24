"""Catalog Insights — analytics dashboard with Orbit widgets + release checklist."""

from __future__ import annotations

from typing import Any

from almasix.orbit.panels.pages import Dashboard

from app.orbit.demo.widgets.insight_widgets import (
    CountriesPieChart,
    GenreRadarChart,
    PlatformsChart,
    ReleaseChecklistWidget,
    StatusBreakdownChart,
    TopArtistsChart,
    TopTracksTable,
)


class CatalogInsightsPage(Dashboard):
    """Second dashboard: pie / radar / Apex analytics for the catalog."""

    slug = "catalog-insights"
    title = "Insights"
    navigation_label = "Insights"
    navigation_icon = "heroicon-o-chart-bar"
    navigation_group = "Catalog"
    navigation_sort = 10
    route_path = "catalog-insights"

    @classmethod
    def get_columns(cls) -> int | dict[str, int]:
        return {"default": 1, "md": 2}

    @classmethod
    def get_widgets(cls, panel: Any = None) -> list[Any]:
        return [
            CountriesPieChart,
            GenreRadarChart,
            PlatformsChart,
            StatusBreakdownChart,
            TopArtistsChart,
            TopTracksTable,
            ReleaseChecklistWidget,
        ]
