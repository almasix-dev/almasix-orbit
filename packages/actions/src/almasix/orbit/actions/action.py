"""Action objects — button + optional modal form + callback."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon

_TRIGGER_STYLES = frozenset({"button", "link", "icon_button", "badge"})


class Action(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._action: Callable[..., Any] | None = None
        self._color: str | Callable[..., str] = "primary"
        self._icon: str | Callable[..., str] | None = None
        self._requires_confirmation = False
        self._confirmation_forced_off = False
        self._modal_heading: str | Callable[..., str] | None = None
        self._modal_description: str | Callable[..., str] | None = None
        self._form_schema: list[Component] = []
        self._url: str | Callable[..., str] | None = None
        self._authorize: Callable[..., bool] | bool | None = None
        self._success_notification: str | None = None
        self._success_notification_explicit = False
        self._button_group: str = "default"
        self._modal = False
        self._slide_over = False
        self._modal_width: str | Callable[..., str] | None = None

        # Trigger chrome
        self._trigger_style: str = "button"
        self._labeled_from: str | None = None
        self._size: str = "md"
        self._outlined = False
        self._icon_position: str = "before"
        self._tooltip: str | Callable[..., str] | None = None
        self._badge: str | int | Callable[..., Any] | None = None
        self._badge_color: str | Callable[..., str] | None = None
        self._key_bindings: list[str] = []
        self._open_url_in_new_tab = False

        # Schema / form
        self._fill_form: dict[str, Any] | Callable[..., Any] | None = None
        self._disabled_form = False

        # Modal API
        self._modal_submit_action_label: str | Callable[..., str] | None = None
        self._modal_cancel_action_label: str | Callable[..., str] | None = None
        self._sticky_modal_header = False
        self._sticky_modal_footer = False
        self._close_modal_by_clicking_away = True
        self._close_modal_by_escaping = True
        self._modal_close_button = True
        self._modal_icon: str | Callable[..., str] | None = None
        self._modal_icon_color: str | Callable[..., str] | None = None
        self._modal_alignment: str = "start"
        self._modal_autofocus = True
        self._slide_over_position: str = "right"

        # Lifecycle / mutation
        self._before: Callable[..., Any] | None = None
        self._after: Callable[..., Any] | None = None
        self._mutate_data_using: Callable[..., Any] | None = None
        self._mutate_record_data_using: Callable[..., Any] | None = None
        self._using: Callable[..., Any] | None = None
        self._success_redirect_url: str | Callable[..., str] | None = None
        self._success_notification_title: str | None = None
        self._failure_notification: str | None = None
        self._failure_notification_title: str | None = None
        self._halted = False
        self._cancelled = False
        self._arguments: dict[str, Any] = {}

        # Authorization UX
        self._authorization_tooltip: str | None = None
        self._authorization_notification: str | None = None

    # —— Core configurators ————————————————————————————————————————————————

    def action(self, callback: Callable[..., Any]) -> Self:
        self._action = callback
        return self

    def get_action(self) -> Callable[..., Any] | None:
        return self._action

    def color(self, color: str | Callable[..., str]) -> Self:
        self._color = color
        return self

    def get_color(self, **ctx: Any) -> str:
        result = evaluate(self._color, **ctx)
        return "primary" if result is None else str(result)

    def icon(self, name: str | Callable[..., str]) -> Self:
        self._icon = name
        return self

    def get_icon(self, **ctx: Any) -> str | None:
        if self._icon is None:
            return None
        result = evaluate(self._icon, **ctx)
        return None if result is None else str(result)

    def requires_confirmation(self, condition: bool = True) -> Self:
        self._requires_confirmation = condition
        if condition:
            self._confirmation_forced_off = False
        return self

    def without_confirmation(self, condition: bool = True) -> Self:
        """Explicit opt-out — danger actions confirm by default otherwise."""
        self._confirmation_forced_off = condition
        if condition:
            self._requires_confirmation = False
        return self

    def needs_confirmation(self, **ctx: Any) -> bool:
        if self._confirmation_forced_off:
            return False
        if self._requires_confirmation:
            return True
        return self.get_color(**ctx) == "danger"

    def modal(self, condition: bool = True) -> Self:
        """Prefer modal/quick action over URL navigation when both apply."""
        self._modal = condition
        return self

    def is_modal(self) -> bool:
        return (
            self._modal
            or bool(self._form_schema)
            or self._requires_confirmation
            or (not self._confirmation_forced_off and self._color == "danger")
        )

    def slide_over(self, condition: bool = True) -> Self:
        self._slide_over = condition
        self._modal = condition or self._modal
        return self

    def is_slide_over(self) -> bool:
        return self._slide_over

    def slide_over_position(self, position: str) -> Self:
        self._slide_over_position = position if position in {"left", "right"} else "right"
        return self

    def get_slide_over_position(self) -> str:
        return self._slide_over_position

    def modal_width(self, width: str | Callable[..., str]) -> Self:
        self._modal_width = width
        return self

    def get_modal_width(self, **ctx: Any) -> str | None:
        if self._modal_width is None:
            return None
        result = evaluate(self._modal_width, **ctx)
        return None if result is None else str(result)

    def modal_heading(self, text: str | Callable[..., str]) -> Self:
        self._modal_heading = text
        return self

    def modal_description(self, text: str | Callable[..., str]) -> Self:
        self._modal_description = text
        return self

    def form(self, components: Sequence[Component]) -> Self:
        self._form_schema = list(components)
        return self

    def schema(self, components: Sequence[Component]) -> Self:
        """Filament alias of :meth:`form`."""
        return self.form(components)

    def get_form_schema(self) -> list[Component]:
        return list(self._form_schema)

    def fill_form(self, data: dict[str, Any] | Callable[..., Any]) -> Self:
        self._fill_form = data
        return self

    def get_fill_form(self, **ctx: Any) -> dict[str, Any]:
        if self._fill_form is None:
            return {}
        result = evaluate(self._fill_form, **ctx)
        return dict(result) if isinstance(result, dict) else {}

    def disabled_form(self, condition: bool = True) -> Self:
        self._disabled_form = condition
        return self

    def is_disabled_form(self) -> bool:
        return self._disabled_form

    def url(
        self,
        url: str | Callable[..., str],
        *,
        open_in_new_tab: bool | None = None,
    ) -> Self:
        self._url = url
        if open_in_new_tab is not None:
            self._open_url_in_new_tab = open_in_new_tab
        return self

    def get_url(self, **ctx: Any) -> str | None:
        if self._url is None:
            return None
        result = evaluate(self._url, **ctx)
        return None if result is None else str(result)

    def open_url_in_new_tab(self, condition: bool = True) -> Self:
        self._open_url_in_new_tab = condition
        return self

    def opens_url_in_new_tab(self) -> bool:
        return self._open_url_in_new_tab

    def authorize(self, callback: Callable[..., bool] | bool) -> Self:
        self._authorize = callback
        return self

    def authorization_tooltip(self, text: str) -> Self:
        """When unauthorized, render disabled with this tooltip instead of hiding."""
        self._authorization_tooltip = text
        return self

    def authorization_notification(self, text: str) -> Self:
        """When unauthorized, still render and emit notification intent via data attrs."""
        self._authorization_notification = text
        return self

    def success_notification(self, message: str | None) -> Self:
        self._success_notification = message
        self._success_notification_explicit = True
        return self

    def success_notification_title(self, title: str) -> Self:
        self._success_notification_title = title
        return self

    def failure_notification(self, message: str) -> Self:
        self._failure_notification = message
        return self

    def failure_notification_title(self, title: str) -> Self:
        self._failure_notification_title = title
        return self

    def success_redirect_url(self, url: str | Callable[..., str]) -> Self:
        self._success_redirect_url = url
        return self

    def get_success_redirect_url(self, **ctx: Any) -> str | None:
        if self._success_redirect_url is None:
            return None
        result = evaluate(self._success_redirect_url, **ctx)
        return None if result is None else str(result)

    def can(self, **ctx: Any) -> bool:
        auth = self._authorize
        if auth is None:
            return True
        return bool(evaluate(auth, **ctx))

    # —— Trigger chrome ————————————————————————————————————————————————————

    def button(self, condition: bool = True) -> Self:
        if condition:
            self._trigger_style = "button"
        return self

    def link(self, condition: bool = True) -> Self:
        if condition:
            self._trigger_style = "link"
        return self

    def icon_button(self, condition: bool = True) -> Self:
        if condition:
            self._trigger_style = "icon_button"
        return self

    def badge(self, value: bool | str | int | Callable[..., Any] = True) -> Self:
        """Badge trigger style (bool) or count indicator (str/int/callable)."""
        if isinstance(value, bool):
            if value:
                self._trigger_style = "badge"
            elif self._trigger_style == "badge":
                self._trigger_style = "button"
            return self
        self._badge = value
        return self

    def badge_color(self, color: str | Callable[..., str]) -> Self:
        self._badge_color = color
        return self

    def get_badge(self, **ctx: Any) -> str | None:
        if self._badge is None:
            return None
        result = evaluate(self._badge, **ctx)
        return None if result is None else str(result)

    def get_badge_color(self, **ctx: Any) -> str:
        if self._badge_color is None:
            return "primary"
        result = evaluate(self._badge_color, **ctx)
        return "primary" if result is None else str(result)

    def get_trigger_style(self) -> str:
        return self._trigger_style if self._trigger_style in _TRIGGER_STYLES else "button"

    def labeled_from(self, breakpoint: str) -> Self:
        self._labeled_from = breakpoint
        return self

    def size(self, value: str) -> Self:
        self._size = value
        return self

    def get_size(self) -> str:
        return self._size

    def outlined(self, condition: bool = True) -> Self:
        self._outlined = condition
        return self

    def icon_position(self, position: str) -> Self:
        self._icon_position = "after" if position == "after" else "before"
        return self

    def tooltip(self, text: str | Callable[..., str]) -> Self:
        self._tooltip = text
        return self

    def get_tooltip(self, **ctx: Any) -> str | None:
        if self._tooltip is None:
            return None
        result = evaluate(self._tooltip, **ctx)
        return None if result is None else str(result)

    def key_bindings(self, keys: Sequence[str]) -> Self:
        self._key_bindings = list(keys)
        return self

    def get_key_bindings(self) -> list[str]:
        return list(self._key_bindings)

    # —— Modal labels / chrome —————————————————————————————————————————————

    def modal_submit_action_label(self, label: str | Callable[..., str]) -> Self:
        self._modal_submit_action_label = label
        return self

    def modal_cancel_action_label(self, label: str | Callable[..., str]) -> Self:
        self._modal_cancel_action_label = label
        return self

    def get_modal_submit_action_label(self, **ctx: Any) -> str | None:
        if self._modal_submit_action_label is None:
            return None
        result = evaluate(self._modal_submit_action_label, **ctx)
        return None if result is None else str(result)

    def get_modal_cancel_action_label(self, **ctx: Any) -> str | None:
        if self._modal_cancel_action_label is None:
            return None
        result = evaluate(self._modal_cancel_action_label, **ctx)
        return None if result is None else str(result)

    def sticky_modal_header(self, condition: bool = True) -> Self:
        self._sticky_modal_header = condition
        return self

    def sticky_modal_footer(self, condition: bool = True) -> Self:
        self._sticky_modal_footer = condition
        return self

    def close_modal_by_clicking_away(self, condition: bool = True) -> Self:
        self._close_modal_by_clicking_away = condition
        return self

    def close_modal_by_escaping(self, condition: bool = True) -> Self:
        self._close_modal_by_escaping = condition
        return self

    def modal_close_button(self, condition: bool = True) -> Self:
        self._modal_close_button = condition
        return self

    def modal_icon(self, name: str | Callable[..., str]) -> Self:
        self._modal_icon = name
        return self

    def modal_icon_color(self, color: str | Callable[..., str]) -> Self:
        self._modal_icon_color = color
        return self

    def get_modal_icon(self, **ctx: Any) -> str | None:
        if self._modal_icon is None:
            return None
        result = evaluate(self._modal_icon, **ctx)
        return None if result is None else str(result)

    def get_modal_icon_color(self, **ctx: Any) -> str | None:
        if self._modal_icon_color is None:
            return None
        result = evaluate(self._modal_icon_color, **ctx)
        return None if result is None else str(result)

    def modal_alignment(self, alignment: str) -> Self:
        self._modal_alignment = "center" if alignment == "center" else "start"
        return self

    def modal_autofocus(self, condition: bool = True) -> Self:
        self._modal_autofocus = condition
        return self

    # —— Lifecycle / mutation ——————————————————————————————————————————————

    def before(self, callback: Callable[..., Any]) -> Self:
        self._before = callback
        return self

    def after(self, callback: Callable[..., Any]) -> Self:
        self._after = callback
        return self

    def mutate_data_using(self, callback: Callable[..., Any]) -> Self:
        self._mutate_data_using = callback
        return self

    def mutate_record_data_using(self, callback: Callable[..., Any]) -> Self:
        self._mutate_record_data_using = callback
        return self

    def using(self, callback: Callable[..., Any]) -> Self:
        """Custom persist callback — replaces the default ``action()`` body when set."""
        self._using = callback
        return self

    def get_using(self) -> Callable[..., Any] | None:
        return self._using

    def halt(self) -> Self:
        self._halted = True
        return self

    def cancel(self) -> Self:
        self._cancelled = True
        return self

    def is_halted(self) -> bool:
        return self._halted

    def is_cancelled(self) -> bool:
        return self._cancelled

    def arguments(self, args: dict[str, Any]) -> Self:
        self._arguments = dict(args)
        return self

    def get_arguments(self) -> dict[str, Any]:
        return dict(self._arguments)

    def call(self, *args: Any, **kwargs: Any) -> Any:
        self._halted = False
        self._cancelled = False

        if self._before is not None:
            self._before(*args, **kwargs)
        if self._halted or self._cancelled:
            return None

        data = kwargs.get("data")
        if data is not None and self._mutate_data_using is not None:
            rest = {k: v for k, v in kwargs.items() if k != "data"}
            kwargs = {**kwargs, "data": self._mutate_data_using(data, **rest)}

        record = kwargs.get("record")
        if record is not None and self._mutate_record_data_using is not None:
            if isinstance(record, dict):
                rest = {k: v for k, v in kwargs.items() if k not in {"record", "data"}}
                mutated = self._mutate_record_data_using(dict(record), **rest)
                if isinstance(mutated, dict):
                    kwargs = {**kwargs, "record": mutated}
            else:
                rest = {k: v for k, v in kwargs.items() if k not in {"record", "data"}}
                self._mutate_record_data_using(record, **rest)

        result: Any = None
        if self._using is not None:
            result = self._using(*args, **kwargs)
        elif self._action is not None:
            result = self._action(*args, **kwargs)

        if self._halted or self._cancelled:
            return result

        if self._after is not None:
            self._after(*args, **kwargs)
        return result

    # —— Render helpers ————————————————————————————————————————————————————

    def _resolve_fill_state(self, record: Any | None, **ctx: Any) -> dict[str, Any]:
        state: dict[str, Any] = {}
        fill = self.get_fill_form(record=record, **ctx)
        if fill:
            state.update(fill)
        if isinstance(record, dict):
            state.update(record)
        elif record is not None:
            for field in self._form_schema:
                fname = field.get_name()
                if fname:
                    state[fname] = getattr(record, fname, None)
        return state

    def _render_form_fields(self, record: Any | None = None, **ctx: Any) -> str:
        if not self._form_schema:
            return ""
        parts: list[str] = []
        state = self._resolve_fill_state(record, **ctx)
        for field in self._form_schema:
            fname = field.get_name() or ""
            value = state.get(fname) if fname else None
            prev_disabled = field._disabled
            if self._disabled_form:
                field._disabled = True
            try:
                parts.append(
                    field.render(
                        value,
                        record=record,
                        **{k: v for k, v in ctx.items() if k != "state"},
                    )
                )
            finally:
                field._disabled = prev_disabled
        return "".join(parts)

    def _extra_attrs_html(self, **ctx: Any) -> str:
        attrs = self.get_extra_attributes(**ctx)
        if not attrs:
            return ""
        parts: list[str] = []
        for key, val in attrs.items():
            if val is False or val is None:
                continue
            if val is True:
                parts.append(e(str(key)))
            else:
                parts.append(f'{e(str(key))}="{e(val)}"')
        return (" " + " ".join(parts)) if parts else ""

    def _trigger_classes(self, color: str, *, disabled: bool = False) -> str:
        style = self.get_trigger_style()
        size = self._size or "md"
        classes = ["or-btn", f"or-btn-{color}", f"or-btn-{size}"]
        if style == "link":
            classes.append("or-btn-link")
        elif style == "icon_button":
            classes.extend(["or-btn-icon", "or-icon-btn"])
        elif style == "badge":
            classes.extend(["or-btn-badge", "or-badge"])
        if self._outlined:
            classes.append("or-btn-outlined")
        if self._labeled_from:
            classes.append(f"or-btn-labeled-from-{self._labeled_from}")
        if disabled:
            classes.append("or-btn-disabled")
        return " ".join(classes)

    def _inner_label_html(self, label: str, ic: str, *, icon_only: bool) -> str:
        if icon_only:
            return ic or f"<span class=\"or-btn-label\">{label}</span>"
        label_html = f'<span class="or-btn-label">{label}</span>'
        if self._icon_position == "after":
            return f"{label_html}{ic}"
        return f"{ic}{label_html}"

    def _badge_indicator_html(self, **ctx: Any) -> str:
        value = self.get_badge(**ctx)
        if value is None:
            return ""
        color = e(self.get_badge_color(**ctx))
        return f'<span class="or-btn-indicator or-badge or-badge-{color}">{e(value)}</span>'

    def _notification_data_attrs(self) -> str:
        parts: list[str] = []
        if self._success_notification_explicit:
            if self._success_notification is None:
                parts.append(' data-success-notification=""')
            else:
                parts.append(f' data-success-notification="{e(self._success_notification)}"')
        elif self._success_notification:
            parts.append(f' data-success-notification="{e(self._success_notification)}"')
        if self._success_notification_title:
            parts.append(
                f' data-success-notification-title="{e(self._success_notification_title)}"'
            )
        if self._failure_notification:
            parts.append(f' data-failure-notification="{e(self._failure_notification)}"')
        if self._failure_notification_title:
            parts.append(
                f' data-failure-notification-title="{e(self._failure_notification_title)}"'
            )
        redirect = self._success_redirect_url
        if redirect is not None and not callable(redirect):
            parts.append(f' data-success-redirect-url="{e(redirect)}"')
        return "".join(parts)

    def _modal_data_attrs(self, **ctx: Any) -> str:
        parts: list[str] = []
        submit = self.get_modal_submit_action_label(**ctx)
        cancel = self.get_modal_cancel_action_label(**ctx)
        if submit:
            parts.append(f' data-modal-submit-label="{e(submit)}"')
        if cancel:
            parts.append(f' data-modal-cancel-label="{e(cancel)}"')
        if self._sticky_modal_header:
            parts.append(' data-sticky-header="true"')
        if self._sticky_modal_footer:
            parts.append(' data-sticky-footer="true"')
        if not self._close_modal_by_clicking_away:
            parts.append(' data-close-on-click-away="false"')
        if not self._close_modal_by_escaping:
            parts.append(' data-close-on-escape="false"')
        if not self._modal_close_button:
            parts.append(' data-modal-close-button="false"')
        modal_icon = self.get_modal_icon(**ctx)
        if modal_icon:
            parts.append(f' data-modal-icon="{e(modal_icon)}"')
        icon_color = self.get_modal_icon_color(**ctx)
        if icon_color:
            parts.append(f' data-modal-icon-color="{e(icon_color)}"')
        if self._modal_alignment != "start":
            parts.append(f' data-modal-alignment="{e(self._modal_alignment)}"')
        if not self._modal_autofocus:
            parts.append(' data-modal-autofocus="false"')
        if self._slide_over:
            parts.append(' data-slide-over="true"')
            if self._slide_over_position != "right":
                parts.append(f' data-slide-over-position="{e(self._slide_over_position)}"')
        width = self.get_modal_width(**ctx)
        if width:
            parts.append(f' data-modal-width="{e(width)}"')
        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "color": self._color if not callable(self._color) else None,
            "icon": self._icon if not callable(self._icon) else None,
            "requires_confirmation": self._requires_confirmation,
            "modal": self._modal,
            "modal_heading": self._modal_heading if not callable(self._modal_heading) else None,
            "modal_description": (
                self._modal_description if not callable(self._modal_description) else None
            ),
            "has_form": bool(self._form_schema),
            "success_notification": self._success_notification,
            "success_notification_title": self._success_notification_title,
            "failure_notification": self._failure_notification,
            "failure_notification_title": self._failure_notification_title,
            "has_url": self._url is not None,
            "slide_over": self._slide_over,
            "slide_over_position": self._slide_over_position,
            "modal_width": self._modal_width if not callable(self._modal_width) else None,
            "trigger_style": self.get_trigger_style(),
            "size": self._size,
            "outlined": self._outlined,
            "icon_position": self._icon_position,
            "labeled_from": self._labeled_from,
            "disabled_form": self._disabled_form,
            "sticky_modal_header": self._sticky_modal_header,
            "sticky_modal_footer": self._sticky_modal_footer,
            "close_modal_by_clicking_away": self._close_modal_by_clicking_away,
            "close_modal_by_escaping": self._close_modal_by_escaping,
            "modal_close_button": self._modal_close_button,
            "modal_alignment": self._modal_alignment,
            "modal_autofocus": self._modal_autofocus,
            "key_bindings": list(self._key_bindings),
            "open_url_in_new_tab": self._open_url_in_new_tab,
            "arguments": dict(self._arguments),
            "has_using": self._using is not None,
            "create_another": getattr(self, "_create_another", False),
        })
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""

        authorized = self.can(**ctx)
        unauthorized_tooltip = bool(self._authorization_tooltip) and not authorized
        unauthorized_notification = bool(self._authorization_notification) and not authorized
        if not authorized and not unauthorized_tooltip and not unauthorized_notification:
            return ""

        record = ctx.get("record", state if isinstance(state, dict) else None)
        name = e(self.get_name() or "action")
        label = e(
            self.get_label(**ctx) or (self.get_name() or "Action").replace("_", " ").title()
        )
        icon_name = self.get_icon(**ctx)
        ic = render_icon(icon_name) if icon_name else ""
        color = e(self.get_color(**ctx))
        needs_confirm = self.needs_confirmation(**ctx)
        has_form = bool(self._form_schema)
        use_modal = self._modal or has_form or needs_confirm
        disabled = self.is_disabled(**ctx) or unauthorized_tooltip or unauthorized_notification
        tip = self.get_tooltip(**ctx)
        if unauthorized_tooltip:
            tip = self._authorization_tooltip
        title_attr = f' title="{e(tip)}"' if tip else ""
        extra = self._extra_attrs_html(**ctx)
        classes = self._trigger_classes(color, disabled=disabled)
        style = self.get_trigger_style()
        icon_only = style == "icon_button"
        inner = self._inner_label_html(label, ic, icon_only=icon_only)
        badge_html = self._badge_indicator_html(**ctx)
        aria_label = f' aria-label="{label}"' if icon_only else ""
        keys = self.get_key_bindings()
        keys_attr = f' data-key-bindings="{e(",".join(keys))}"' if keys else ""
        notif_attrs = self._notification_data_attrs()
        auth_notif = ""
        if unauthorized_notification:
            auth_notif = (
                f' data-authorization-notification="{e(self._authorization_notification)}"'
            )

        href = None if use_modal else self.get_url(**ctx)
        if href and not disabled:
            target = ' target="_blank" rel="noopener noreferrer"' if self._open_url_in_new_tab else ""
            return (
                f'<a class="{classes}" data-action="{name}" href="{e(href)}"{target}'
                f"{title_attr}{aria_label}{keys_attr}{notif_attrs}{auth_notif}{extra}>"
                f"{inner}{badge_html}</a>"
            )

        confirm = "true" if needs_confirm else "false"
        heading = ""
        if self._modal_heading:
            heading = str(evaluate(self._modal_heading, **ctx) or "")
        elif needs_confirm and not has_form:
            heading = f"{label}?"
        description = ""
        if self._modal_description:
            description = str(evaluate(self._modal_description, **ctx) or "")
        elif needs_confirm and not has_form and color == "danger":
            description = "This action cannot be undone."
        heading_attr = f' data-modal-heading="{e(heading)}"' if heading else ""
        desc_attr = f' data-modal-description="{e(description)}"' if description else ""
        has_form_attr = ' data-has-form="true"' if has_form else ""
        rid = ""
        if isinstance(record, dict) and record.get("id") is not None:
            rid = str(record.get("id"))
        elif record is not None and getattr(record, "id", None) is not None:
            rid = str(record.id)
        rid_attr = f' data-record-id="{e(rid)}"' if rid else ""
        modal_attrs = self._modal_data_attrs(**ctx)
        form_tpl = ""
        if has_form:
            form_record = record if (isinstance(record, dict) or record is not None) else None
            fields = self._render_form_fields(
                form_record, **{k: v for k, v in ctx.items() if k != "record"}
            )
            form_tpl = f'<template class="or-action-form-tpl">{fields}</template>'

        disabled_attr = " disabled" if disabled else ""
        wire = "" if disabled else f' wire:click="mountAction(\'{name}\')"'
        return (
            f'<button type="button" class="{classes}" data-action="{name}" '
            f'data-confirm="{confirm}"{has_form_attr}{rid_attr}{heading_attr}{desc_attr}'
            f"{modal_attrs}{keys_attr}{notif_attrs}{auth_notif}{title_attr}{aria_label}"
            f"{disabled_attr}{extra}{wire}>"
            f"{inner}{badge_html}</button>{form_tpl}"
        )


class CreateAction(Action):
    def __init__(self, name: str | None = "create") -> None:
        super().__init__(name)
        self.label("Create").icon("heroicon-o-plus").color("primary")
        self._create_another = False
        self._preserve_form_data_when_creating_another = False

    def create_another(self, condition: bool = True) -> Self:
        self._create_another = condition
        return self

    def preserve_form_data_when_creating_another(self, condition: bool = True) -> Self:
        self._preserve_form_data_when_creating_another = condition
        return self

    def should_create_another(self) -> bool:
        return self._create_another

    def should_preserve_form_data_when_creating_another(self) -> bool:
        return self._preserve_form_data_when_creating_another

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["create_another"] = self._create_another
        d["preserve_form_data_when_creating_another"] = (
            self._preserve_form_data_when_creating_another
        )
        return d


class EditAction(Action):
    def __init__(self, name: str | None = "edit") -> None:
        super().__init__(name)
        self.label("Edit").icon("heroicon-o-pencil-square").color("primary")


class ViewAction(Action):
    def __init__(self, name: str | None = "view") -> None:
        super().__init__(name)
        self.label("View").icon("heroicon-o-magnifying-glass").color("gray")

    def form(self, components: Sequence[Component]) -> Self:
        super().form(components)
        self._modal = True
        self._disabled_form = True
        return self


class DeleteAction(Action):
    def __init__(self, name: str | None = "delete") -> None:
        super().__init__(name)
        self.label("Delete").icon("heroicon-o-trash").color("danger").requires_confirmation()
        self.modal_heading("Delete?")
        self.modal_description("This permanently removes the record.")


class BulkAction(Action):
    """Generic bulk action with selected-record processing helpers."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._chunk_selected_records: int | None = None
        self._fetch_selected_records = True
        self._authorize_individual_records = False

    def chunk_selected_records(self, size: int) -> Self:
        self._chunk_selected_records = size
        return self

    def get_chunk_selected_records(self) -> int | None:
        return self._chunk_selected_records

    def fetch_selected_records(self, condition: bool = True) -> Self:
        self._fetch_selected_records = condition
        return self

    def should_fetch_selected_records(self) -> bool:
        return self._fetch_selected_records

    def authorize_individual_records(self, condition: bool = True) -> Self:
        self._authorize_individual_records = condition
        return self

    def should_authorize_individual_records(self) -> bool:
        return self._authorize_individual_records

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "chunk_selected_records": self._chunk_selected_records,
                "fetch_selected_records": self._fetch_selected_records,
                "authorize_individual_records": self._authorize_individual_records,
            }
        )
        return d


class DeleteBulkAction(BulkAction):
    def __init__(self, name: str | None = "delete_bulk") -> None:
        super().__init__(name)
        self.label("Delete selected").icon("heroicon-o-trash").color("danger").requires_confirmation()
        self.modal_heading("Delete selected?")
        self.modal_description("This permanently removes the selected records.")
