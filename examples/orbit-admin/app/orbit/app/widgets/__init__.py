"""Custom Orbit widgets (auto-discovered by the app panel)."""

from app.orbit.app.widgets.dashboard_widgets import (
    OverviewStats,
    RecentPostsTable,
    RevenueApexChart,
    SignupsChart,
    WelcomeWidget,
)

__all__ = [
    "WelcomeWidget",
    "OverviewStats",
    "SignupsChart",
    "RevenueApexChart",
    "RecentPostsTable",
]
