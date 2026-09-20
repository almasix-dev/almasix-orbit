"""Small Settings Hub cluster for the Navigation showcase."""

from __future__ import annotations

from almasix.orbit.panels import Cluster


class SettingsHubCluster(Cluster):
    """Cluster entry under the Navigation group — Colors + Fonts as members."""

    navigation_icon = "heroicon-o-cog-6-tooth"
    navigation_label = "Settings Hub"
    navigation_group = "Navigation"
    navigation_sort = 20
    sub_navigation_position = "start"
    cluster_breadcrumb = "Settings Hub"
