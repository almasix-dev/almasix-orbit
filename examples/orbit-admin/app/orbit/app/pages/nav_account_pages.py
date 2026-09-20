"""Parent / child page pair for navigation_parent_item demo."""

from __future__ import annotations

from almasix.orbit import Page


class NavAccountPage(Page):
    slug = "nav-account"
    title = "Account"
    navigation_label = "Account"
    navigation_icon = "heroicon-o-user-circle"
    navigation_group = "Navigation"
    navigation_sort = 10

    @classmethod
    def render(cls, **ctx) -> str:
        return (
            '<div class="or-page">'
            '<h1 class="or-page-title">Account</h1>'
            '<p class="or-muted">Parent nav item — Preferences nests underneath.</p>'
            "</div>"
        )


class NavPreferencesPage(Page):
    slug = "nav-preferences"
    title = "Preferences"
    navigation_label = "Preferences"
    navigation_group = "Navigation"
    navigation_parent_item = "Account"
    navigation_sort = 11

    @classmethod
    def render(cls, **ctx) -> str:
        return (
            '<div class="or-page">'
            '<h1 class="or-page-title">Preferences</h1>'
            '<p class="or-muted">Child item via navigation_parent_item = "Account".</p>'
            "</div>"
        )
