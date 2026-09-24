"""Custom Orbit widgets for the demo panel."""

from app.orbit.demo.widgets.dashboard_widgets import (
    CatalogStats,
    FormatsChart,
    PlaysTrendChart,
    RecentAlbumsTable,
    ReleasesChart,
    StreamsChart,
    WelcomeWidget,
)
from app.orbit.demo.widgets.insight_widgets import (
    CountriesPieChart,
    GenreRadarChart,
    PlatformsChart,
    ReleaseChecklistWidget,
    StatusBreakdownChart,
    TopArtistsChart,
    TopTracksTable,
)

__all__ = [
    "WelcomeWidget",
    "CatalogStats",
    "ReleasesChart",
    "PlaysTrendChart",
    "FormatsChart",
    "StreamsChart",
    "RecentAlbumsTable",
    "CountriesPieChart",
    "GenreRadarChart",
    "PlatformsChart",
    "StatusBreakdownChart",
    "TopArtistsChart",
    "TopTracksTable",
    "ReleaseChecklistWidget",
]
