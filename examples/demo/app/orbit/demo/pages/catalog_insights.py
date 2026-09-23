"""Catalog Insights — custom page with rollups and a release checklist wizard."""

from __future__ import annotations

from almasix.orbit import Page
from almasix.orbit.forms import (
    DatePicker,
    FileUpload,
    Form,
    Select,
    TextInput,
    ToggleButtons,
)
from almasix.orbit.schemas import Callout, Section, Wizard
from almasix.orbit.support.html import e

from app.orbit.demo.catalog_metrics import (
    catalog_counts,
    country_breakdown,
    format_counts,
)


def _card(*, title: str | None = None, body: str, extra_class: str = "") -> str:
    """Orbit ``.or-card`` chrome with optional heading."""
    cls = f"or-card{(' ' + extra_class) if extra_class else ''}"
    heading = (
        f'<header class="or-widget-header"><h3>{e(title)}</h3></header>'
        if title
        else ""
    )
    return (
        f'<section class="{cls}">'
        f"{heading}"
        f'<div class="or-widget-body">{body}</div>'
        f"</section>"
    )


class CatalogInsightsPage(Page):
    slug = "catalog-insights"
    title = "Insights"
    navigation_label = "Insights"
    navigation_icon = "heroicon-o-chart-bar"
    navigation_group = "Catalog"
    navigation_sort = 10

    @classmethod
    def _checklist_form(cls) -> Form:
        return Form.make("release_checklist").schema(
            [
                Callout.make()
                .info()
                .label("New release checklist")
                .description(
                    "A schema Wizard on a custom page — use Albums → Create to "
                    "persist a real release."
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

    @classmethod
    def render(cls, **ctx) -> str:
        counts = catalog_counts()
        formats = format_counts()
        countries = country_breakdown()

        format_rows = "".join(
            f"<tr><td>{e(name)}</td><td>{n}</td></tr>" for name, n in formats
        ) or "<tr><td colspan='2'>No format data yet.</td></tr>"
        country_rows = "".join(
            f"<tr><td>{e(name)}</td><td>{n}</td></tr>" for name, n in countries
        ) or "<tr><td colspan='2'>No country data yet.</td></tr>"

        stats_body = (
            '<div style="display:grid;'
            'grid-template-columns:repeat(auto-fit,minmax(10rem,1fr));gap:1.25rem;">'
            f'<div><div class="or-muted" style="font-size:0.85rem;">Artists</div>'
            f'<div class="or-stat-value">{counts["artists"]}</div></div>'
            f'<div><div class="or-muted" style="font-size:0.85rem;">Albums</div>'
            f'<div class="or-stat-value">{counts["albums"]}</div></div>'
            f'<div><div class="or-muted" style="font-size:0.85rem;">Tracks</div>'
            f'<div class="or-stat-value">{counts["tracks"]}</div></div>'
            f'<div><div class="or-muted" style="font-size:0.85rem;">Plays</div>'
            f'<div class="or-stat-value">{counts["plays"]:,}</div></div>'
            "</div>"
        )

        formats_body = (
            '<table class="or-table"><thead><tr><th>Format</th><th>Albums</th>'
            f"</tr></thead><tbody>{format_rows}</tbody></table>"
        )
        countries_body = (
            '<table class="or-table"><thead><tr><th>Country</th><th>Artists</th>'
            f"</tr></thead><tbody>{country_rows}</tbody></table>"
        )
        checklist = cls._checklist_form().render(**ctx)

        return (
            '<div class="or-page">'
            '<h1 class="or-page-title">Catalog insights</h1>'
            '<p class="or-muted">Rollups from the SQLite catalog plus a Wizard '
            "checklist (custom page — not a resource).</p>"
            '<div style="display:flex;flex-direction:column;gap:1.25rem;margin-top:1.25rem;">'
            f"{_card(title='Catalog overview', body=stats_body)}"
            '<div style="display:grid;grid-template-columns:repeat(auto-fit,'
            'minmax(16rem,1fr));gap:1.25rem;">'
            f"{_card(title='Formats', body=formats_body)}"
            f"{_card(title='Artists by country', body=countries_body)}"
            "</div>"
            f"{_card(title='New release checklist', body=checklist)}"
            "</div>"
            "</div>"
        )
