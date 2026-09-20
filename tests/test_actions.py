"""Tests for almasix.orbit.actions — Filament 5 Actions parity."""

from __future__ import annotations

from typing import Any

from almasix.orbit.actions import (
    Action,
    ActionGroup,
    BulkAction,
    BulkActionGroup,
    CreateAction,
    DeleteAction,
    DeleteBulkAction,
    EditAction,
    ExportAction,
    Exporter,
    ForceDeleteAction,
    ForceDeleteBulkAction,
    ImportAction,
    Importer,
    ReplicateAction,
    RestoreAction,
    RestoreBulkAction,
    ViewAction,
)
from almasix.orbit.forms.components import TextInput


def test_action_authorize_call_and_render() -> None:
    called: list[int] = []
    action = (
        Action.make("save")
        .label("Save")
        .color("primary")
        .icon("heroicon-o-check")
        .requires_confirmation()
        .modal_heading("Confirm")
        .modal_description("Sure?")
        .form([TextInput.make("reason")])
        .url("/go")
        .authorize(lambda user=None: user == "admin")
        .success_notification("Saved")
        .action(lambda *a, **k: called.append(1) or "ok")
    )
    assert not action.can(user="guest")
    assert action.can(user="admin")
    assert action.call() == "ok"
    assert called == [1]
    assert Action.make("noop").get_action() is None
    assert action.get_action() is not None
    assert Action.make("open").authorize(True).can()
    assert not Action.make("closed").authorize(False).can()
    d = action.to_dict()
    assert d["requires_confirmation"] is True
    assert d["has_form"] is True
    html = action.render(user="admin")
    assert "or-btn-primary" in html and 'data-confirm="true"' in html
    assert action.render(user="guest") == ""
    assert Action.make("h").hidden().render() == ""
    assert Action.make("noicon").label("X").render()  # no icon branch


def test_preset_actions() -> None:
    create = CreateAction.make()
    assert create.get_label() == "Create"
    assert create._color == "primary"
    edit = EditAction.make()
    assert edit.get_label() == "Edit"
    view = ViewAction.make()
    assert view._color == "gray"
    delete = DeleteAction.make()
    assert delete._requires_confirmation is True
    assert delete._color == "danger"
    bulk = DeleteBulkAction.make()
    assert bulk.get_label() == "Delete selected"
    assert "or-btn" in create.render()


def test_trigger_chrome_variants() -> None:
    link = Action.make("a").label("Go").link().size("lg").outlined()
    html = link.render()
    assert "or-btn-link" in html and "or-btn-lg" in html and "or-btn-outlined" in html

    icon_btn = Action.make("b").label("More").icon("heroicon-o-check").icon_button()
    ih = icon_btn.render()
    assert "or-btn-icon" in ih and 'aria-label="More"' in ih

    badge_style = Action.make("c").label("New").badge()
    assert "or-btn-badge" in badge_style.render()
    assert badge_style.badge(False).get_trigger_style() == "button"

    counted = (
        Action.make("d")
        .label("Inbox")
        .button()
        .badge(3)
        .badge_color("danger")
        .labeled_from("md")
        .icon("heroicon-o-bell")
        .icon_position("after")
        .tooltip("Open inbox")
        .key_bindings(["mod+i"])
        .extra_attributes({"data-test": "yes"})
    )
    ch = counted.render()
    assert "or-btn-indicator" in ch and "or-badge-danger" in ch
    assert "or-btn-labeled-from-md" in ch
    assert 'title="Open inbox"' in ch
    assert 'data-key-bindings="mod+i"' in ch
    assert 'data-test="yes"' in ch
    assert ch.index("or-btn-label") < ch.index("<svg")

    assert counted.get_badge() == "3"
    assert counted.get_badge_color() == "danger"
    assert counted.get_key_bindings() == ["mod+i"]
    assert Action.make("e").badge(lambda **_: None).get_badge() is None
    assert Action.make("f").badge_color(lambda **_: None).get_badge_color() == "primary"
    assert Action.make("g").tooltip(lambda **_: None).get_tooltip() is None
    assert Action.make("h").button(False).get_trigger_style() == "button"
    assert Action.make("i").link(False).get_trigger_style() == "button"
    assert Action.make("j").icon_button(False).get_trigger_style() == "button"


def test_url_new_tab_and_disabled() -> None:
    link = Action.make("open").label("Docs").url("/docs", open_in_new_tab=True)
    html = link.render()
    assert 'href="/docs"' in html and 'target="_blank"' in html

    toggled = Action.make("x").url("/x").open_url_in_new_tab()
    assert toggled.opens_url_in_new_tab() is True
    assert 'target="_blank"' in toggled.render()

    disabled = Action.make("d").label("Nope").disabled().action(lambda: 1)
    dh = disabled.render()
    assert "disabled" in dh and "or-btn-disabled" in dh
    assert "wire:click" not in dh


def test_schema_fill_and_disabled_form() -> None:
    action = (
        Action.make("edit")
        .schema([TextInput.make("title")])
        .fill_form({"title": "Draft"})
        .disabled_form()
    )
    assert action.get_form_schema()[0].get_name() == "title"
    assert action.is_disabled_form() is True
    html = action.render()
    assert "Draft" in html and "disabled" in html
    assert action.get_fill_form()["title"] == "Draft"
    assert Action.make("x").get_fill_form() == {}
    assert Action.make("y").fill_form(lambda **_: "nope").get_fill_form() == {}


def test_modal_api_data_attrs() -> None:
    action = (
        Action.make("wipe")
        .label("Wipe")
        .requires_confirmation()
        .modal_submit_action_label("Wipe it")
        .modal_cancel_action_label("Never mind")
        .sticky_modal_header()
        .sticky_modal_footer()
        .close_modal_by_clicking_away(False)
        .close_modal_by_escaping(False)
        .modal_close_button(False)
        .modal_icon("heroicon-o-trash")
        .modal_icon_color("danger")
        .modal_alignment("center")
        .modal_autofocus(False)
        .slide_over()
        .slide_over_position("left")
        .modal_width("2xl")
        .success_notification("Done")
        .success_notification_title("Success")
        .failure_notification("Failed")
        .failure_notification_title("Error")
        .success_redirect_url("/done")
    )
    html = action.render()
    assert 'data-modal-submit-label="Wipe it"' in html
    assert 'data-modal-cancel-label="Never mind"' in html
    assert 'data-sticky-header="true"' in html
    assert 'data-sticky-footer="true"' in html
    assert 'data-close-on-click-away="false"' in html
    assert 'data-close-on-escape="false"' in html
    assert 'data-modal-close-button="false"' in html
    assert 'data-modal-icon="heroicon-o-trash"' in html
    assert 'data-modal-icon-color="danger"' in html
    assert 'data-modal-alignment="center"' in html
    assert 'data-modal-autofocus="false"' in html
    assert 'data-slide-over="true"' in html
    assert 'data-slide-over-position="left"' in html
    assert 'data-modal-width="2xl"' in html
    assert 'data-success-notification="Done"' in html
    assert 'data-success-notification-title="Success"' in html
    assert 'data-failure-notification="Failed"' in html
    assert 'data-failure-notification-title="Error"' in html
    assert 'data-success-redirect-url="/done"' in html
    assert action.get_slide_over_position() == "left"
    assert action.slide_over_position("nope").get_slide_over_position() == "right"
    assert action.get_modal_submit_action_label() == "Wipe it"
    assert action.get_modal_cancel_action_label() == "Never mind"
    assert action.get_modal_icon() == "heroicon-o-trash"
    assert action.get_modal_icon_color() == "danger"
    assert Action.make("z").get_modal_submit_action_label() is None
    assert Action.make("z").get_modal_cancel_action_label() is None
    assert Action.make("z").get_modal_icon() is None
    assert Action.make("z").get_modal_icon_color() is None
    assert Action.make("z").modal_icon(lambda **_: None).get_modal_icon() is None
    assert Action.make("z").modal_icon_color(lambda **_: None).get_modal_icon_color() is None
    assert (
        Action.make("z")
        .modal_submit_action_label(lambda **_: None)
        .get_modal_submit_action_label()
        is None
    )
    assert (
        Action.make("z")
        .modal_cancel_action_label(lambda **_: None)
        .get_modal_cancel_action_label()
        is None
    )
    assert Action.make("z").modal_alignment("start").to_dict()["modal_alignment"] == "start"


def test_lifecycle_halt_cancel_using_mutate() -> None:
    events: list[str] = []
    action = (
        Action.make("save")
        .before(lambda **_: events.append("before"))
        .mutate_data_using(lambda data, **_: {**data, "x": 1})
        .mutate_record_data_using(lambda data, **_: {**data, "y": 2})
        .using(lambda **kwargs: events.append(f"using:{kwargs['data']}") or "ok")
        .after(lambda **_: events.append("after"))
        .arguments({"mode": "quick"})
    )
    assert action.get_arguments() == {"mode": "quick"}
    assert action.get_using() is not None
    result = action.call(data={"a": 1}, record={"id": 1})
    assert result == "ok"
    assert events[0] == "before"
    assert any(e.startswith("using:") for e in events)
    assert events[-1] == "after"

    a = Action.make("halt")
    a.before(lambda **_: a.halt()).action(lambda: "nope")
    assert a.call() is None and a.is_halted()

    b = Action.make("cancel")
    b.before(lambda **_: b.cancel()).action(lambda: "nope")
    assert b.call() is None and b.is_cancelled()

    c = Action.make("after-halt")

    def _halt_body() -> str:
        c.halt()
        return "x"

    c.action(_halt_body).after(lambda **_: events.append("should-not"))
    before_len = len(events)
    assert c.call() == "x"
    assert len(events) == before_len

    obj = type("R", (), {"id": 1})()
    seen: list[Any] = []
    Action.make("m").mutate_record_data_using(lambda r, **_: seen.append(r)).action(
        lambda **_: 1
    ).call(record=obj)
    assert seen == [obj]

    mutated_rec = (
        Action.make("n")
        .mutate_record_data_using(lambda data, **_: {**data, "y": 2})
        .action(lambda **k: k["record"])
        .call(record={"id": 2})
    )
    assert mutated_rec == {"id": 2, "y": 2}

    Action.make("n2").mutate_record_data_using(lambda data, **_: None).action(
        lambda **k: k["record"]
    ).call(record={"id": 3})

    assert Action.make("plain").action(lambda: 7).call() == 7
    assert Action.make("empty").call() is None

    d = Action.make("d")

    def _cancel_body() -> int:
        d.cancel()
        return 1

    d.action(_cancel_body).after(lambda **_: events.append("no"))
    before = len(events)
    assert d.call() == 1
    assert len(events) == before

    assert Action.make("slide").slide_over().is_slide_over() is True
    assert Action.make("bc").get_badge_color() == "primary"
    assert Action.make("bg").get_badge() is None

    # legacy success notification attr without explicit flag
    legacy = Action.make("leg").label("L")
    legacy._success_notification = "Hi"
    legacy._success_notification_explicit = False
    assert 'data-success-notification="Hi"' in legacy.render()

    # slide over default position omits left attr
    so = Action.make("so").requires_confirmation().slide_over().render()
    assert 'data-slide-over="true"' in so and "slide-over-position" not in so

    # requires_confirmation(False) / without_confirmation(False) branches
    Action.make("rc").requires_confirmation(False)
    Action.make("wc").without_confirmation(False)


def test_success_notification_none_disables() -> None:
    html = Action.make("x").label("X").success_notification(None).render()
    assert 'data-success-notification=""' in html
    assert Action.make("y").success_redirect_url(lambda **_: None).get_success_redirect_url() is None
    assert Action.make("z").success_redirect_url("/a").get_success_redirect_url() == "/a"
    assert Action.make("w").get_success_redirect_url() is None


def test_authorization_tooltip_and_notification() -> None:
    tip = (
        Action.make("a")
        .label("Secret")
        .authorize(False)
        .authorization_tooltip("No access")
    )
    html = tip.render()
    assert "or-btn-disabled" in html and 'title="No access"' in html
    assert "wire:click" not in html

    note = (
        Action.make("b")
        .label("Secret")
        .authorize(False)
        .authorization_notification("Denied")
    )
    nh = note.render()
    assert 'data-authorization-notification="Denied"' in nh
    assert "or-btn-disabled" in nh


def test_create_view_bulk_extras() -> None:
    create = (
        CreateAction.make()
        .create_another()
        .preserve_form_data_when_creating_another()
    )
    assert create.should_create_another() is True
    assert create.should_preserve_form_data_when_creating_another() is True
    assert create.to_dict()["create_another"] is True

    view = ViewAction.make().form([TextInput.make("title")])
    assert view.is_modal() is True
    assert view.is_disabled_form() is True
    assert "disabled" in view.render({"title": "Hi"}, record={"title": "Hi"})

    bulk = (
        BulkAction.make("bulk")
        .chunk_selected_records(50)
        .fetch_selected_records(False)
        .authorize_individual_records()
    )
    assert bulk.get_chunk_selected_records() == 50
    assert bulk.should_fetch_selected_records() is False
    assert bulk.should_authorize_individual_records() is True
    assert bulk.to_dict()["chunk_selected_records"] == 50

    assert DeleteBulkAction.make().get_label() == "Delete selected"
    assert ForceDeleteBulkAction.make().should_fetch_selected_records() is True
    assert RestoreBulkAction.make()._requires_confirmation is True


def test_replicate_action() -> None:
    saved: list[dict] = []
    hooks: list[str] = []
    action = (
        ReplicateAction.make()
        .exclude_attributes(["slug", "id"])
        .before_replica_saved(lambda replica, **_: hooks.append("before"))
        .after_replica_saved(lambda replica, **_: hooks.append("after"))
        .using(lambda replica, **_: saved.append(replica) or replica)
    )
    result = action.call(record={"id": 1, "title": "A", "slug": "a"})
    assert result == {"title": "A"}
    assert saved == [{"title": "A"}]
    assert hooks == ["before", "after"]

    custom = (
        ReplicateAction.make()
        .replicate_using(lambda record, **_: {"t": "x"})
        .action(lambda replica, **_: replica)
    )
    assert custom.call(record={"id": 1}) == {"t": "x"}
    assert custom.to_dict()["has_replicate_using"] is True

    obj = type("R", (), {})()
    obj.id = 9
    obj.title = "Obj"
    obj._private = 1
    assert ReplicateAction.make().exclude_attributes([])._default_replica(obj) == {"title": "Obj"}

    class Slot:
        __slots__ = ()

    assert ReplicateAction.make()._default_replica(Slot()) == {}

    # action (not using) path + after_replica then after
    acted: list[Any] = []
    ReplicateAction.make().action(lambda replica, **_: acted.append(replica) or replica).call(
        record={"id": 1, "name": "n"}
    )
    assert acted == [{"name": "n"}]

    # after_replica then after both run
    order: list[str] = []
    (
        ReplicateAction.make()
        .using(lambda replica, **_: replica)
        .after_replica_saved(lambda **_: order.append("ar"))
        .after(lambda **_: order.append("a"))
        .call(record={"id": 1, "z": 1})
    )
    assert order == ["ar", "a"]

    # get_exclude_attributes
    assert ReplicateAction.make().exclude_attributes(["a"]).get_exclude_attributes() == ["a"]

    h = ReplicateAction.make()
    h.before(lambda **_: h.halt()).using(lambda **k: "no")
    assert h.call(record={"id": 1, "t": 1}) is None

    h2 = ReplicateAction.make()
    h2.before_replica_saved(lambda **k: h2.cancel()).using(lambda **k: "no")
    assert h2.call(record={"id": 1, "t": 1}) is None

    assert ReplicateAction.make().action(lambda: "x").call() == "x"

    after_called: list[int] = []
    h3 = ReplicateAction.make()

    def _halt_use(**k: Any) -> str:
        h3.halt()
        return "x"

    h3.using(_halt_use).after(lambda **_: after_called.append(1))
    assert h3.call(record={"id": 1, "t": 1}) == "x"
    assert after_called == []

    h4 = ReplicateAction.make()

    def _cancel_after(**k: Any) -> None:
        h4.cancel()

    h4.using(lambda **k: "x").after_replica_saved(_cancel_after).after(
        lambda **_: after_called.append(2)
    )
    assert h4.call(record={"id": 1, "t": 1}) == "x"
    assert 2 not in after_called

    assert (
        ReplicateAction.make()
        .using(lambda replica, **_: replica["title"])
        .call({"id": 1, "title": "Pos"})
        == "Pos"
    )

    # no using/action still returns None after hooks
    assert ReplicateAction.make().call(record={"id": 1, "a": 1}) is None


def test_force_delete_restore_confirm() -> None:
    force = ForceDeleteAction.make().render()
    assert 'data-confirm="true"' in force
    restore = RestoreAction.make().render()
    assert 'data-confirm="true"' in restore
    assert "Restore" in RestoreBulkAction.make().render()


def test_action_group_depth() -> None:
    group = (
        ActionGroup.make([EditAction.make(), DeleteAction.make()])
        .label("More")
        .tooltip("More actions")
        .dropdown_placement("bottom-end")
        .dropdown_width("xs")
        .dropdown_offset(8)
        .dropdown_max_height(240)
        .link()
    )
    html = group.render()
    assert "or-dropdown" in html and 'title="More actions"' in html
    assert 'data-dropdown-placement="bottom-end"' in html
    assert 'data-dropdown-width="xs"' in html
    assert 'data-dropdown-offset="8"' in html
    assert 'data-dropdown-max-height="240"' in html
    assert "or-btn-link" in html

    icon_g = (
        ActionGroup.make([EditAction.make()])
        .icon_button()
        .icon("heroicon-o-ellipsis-vertical")
    )
    assert "or-btn-icon" in icon_g.render() and "or-dropdown-menu-end" in icon_g.render()

    after = ActionGroup.make([EditAction.make()]).icon("heroicon-o-check").icon_position("after")
    ah = after.render()
    assert ah.index("</span>") < ah.index("<svg")

    badge_g = ActionGroup.make([EditAction.make()]).badge().outlined()
    assert "or-btn-badge" in badge_g.render() and "or-btn-outlined" in badge_g.render()

    nested = ActionGroup.make(
        [
            ActionGroup.make([EditAction.make()]).label("Edit group").dropdown(False),
            DeleteAction.make(),
        ]
    ).button_group()
    nh = nested.render()
    assert "or-action-section" in nh and "Edit group" in nh

    empty_section = ActionGroup.make(
        [ActionGroup.make([EditAction.make().hidden()]).label("Empty").dropdown(False)]
    ).button_group()
    assert empty_section.render() == ""

    btn = ActionGroup.make("g").actions([EditAction.make()]).button_group()
    assert "or-btn-group" in btn.render()
    assert (
        ActionGroup.make([EditAction.make()]).button_group().dropdown().to_dict()["dropdown"]
        is True
    )
    assert ActionGroup.make([EditAction.make()]).authorize(False).render() == ""
    assert ActionGroup.make().hidden().render() == ""
    assert ActionGroup.make([EditAction.make().hidden()]).render() == ""
    assert BulkActionGroup.make().get_label() == "Bulk actions"

    assert ActionGroup.make([EditAction.make()]).get_actions()[0].get_name() == "edit"
    nested_flat = ActionGroup.make(
        [ActionGroup.make([EditAction.make()]), DeleteAction.make()]
    )
    assert len(nested_flat.flat_actions()) == 2
    assert nested_flat.to_dict()["dropdown"] is True

    bare = ActionGroup.make([EditAction.make()]).icon_button()
    bare._icon = None
    assert "<span>" in bare.render()


def test_import_export_parity() -> None:
    imp = (
        ImportAction.make()
        .importer(lambda path, **_: path)
        .options_form([TextInput.make("delimiter")])
        .options({"header": True})
        .accepted_file_types([".csv"])
        .column_map({"a": "A"})
        .chunk_size(10)
        .max_rows(100)
    )
    assert imp.get_options_form()[0].get_name() == "delimiter"
    assert imp.get_column_map()["a"] == "A"
    assert imp.get_chunk_size() == 10
    assert imp.get_max_rows() == 100
    assert 'data-import="true"' in imp.render()
    assert "arrow-up-tray" in (imp.get_icon() or "")
    assert imp.to_dict()["has_options_form"] is True
    assert imp.call("/tmp/a.csv") == "/tmp/a.csv"

    assert ImportAction.make().action(lambda: "via").call() == "via"
    assert ImportAction.make().using(lambda: "via-using").call() == "via-using"
    assert ImportAction.make().call() is None

    halted = ImportAction.make().importer(lambda *a, **k: "x")
    halted.before(lambda **_: halted.halt())
    assert halted.call() is None

    after_imp: list[str] = []
    ImportAction.make().importer(lambda *a, **k: "x").after(
        lambda **_: after_imp.append("a")
    ).call()
    assert after_imp == ["a"]

    exp = (
        ExportAction.make()
        .exporter(lambda **_: "bytes")
        .formats(["csv"])
        .columns(["name"])
        .column_map({"n": "N"})
        .chunk_size(5)
        .max_rows(50)
        .filename("out")
    )
    assert exp.get_column_map()["n"] == "N"
    assert exp.get_chunk_size() == 5
    assert exp.get_max_rows() == 50
    assert exp.get_filename() == "out"
    assert "arrow-down-tray" in (exp.get_icon() or "")
    assert 'data-export="true"' in exp.render()
    assert exp.call() == "bytes"
    assert ExportAction.make().action(lambda: "via").call() == "via"
    assert ExportAction.make().using(lambda: "u").call() == "u"
    assert ExportAction.make().call() is None
    assert ExportAction.make().filename(lambda **_: None).get_filename() == "export"

    halted_e = ExportAction.make().exporter(lambda **_: "x")
    halted_e.before(lambda **_: halted_e.halt())
    assert halted_e.call() is None

    after_exp: list[str] = []
    ExportAction.make().exporter(lambda **_: "x").after(
        lambda **_: after_exp.append("a")
    ).call()
    assert after_exp == ["a"]

    assert imp.get_importer() is not None
    assert exp.get_exporter() is not None
    assert exp.to_dict()["has_exporter"] is True
    assert exp.to_dict()["formats"] == ["csv"]

    # cancel after importer skips after
    skip_after: list[str] = []
    cancel_imp = ImportAction.make()

    def _imp_cancel(*a: Any, **k: Any) -> str:
        cancel_imp.cancel()
        return "x"

    cancel_imp.importer(_imp_cancel).after(lambda **_: skip_after.append("a"))
    assert cancel_imp.call() == "x"
    assert skip_after == []

    cancel_exp = ExportAction.make()

    def _exp_cancel(*a: Any, **k: Any) -> str:
        cancel_exp.cancel()
        return "x"

    cancel_exp.exporter(_exp_cancel).after(lambda **_: skip_after.append("b"))
    assert cancel_exp.call() == "x"
    assert "b" not in skip_after

    assert ImportAction.make().hidden().render() == ""
    assert ExportAction.make().authorize(False).render() == ""

    try:
        Importer()("/x")
    except NotImplementedError:
        pass
    try:
        Exporter()()
    except NotImplementedError:
        pass

    class MyImp(Importer):
        def __call__(
            self, path: str, *, options: dict[str, Any] | None = None, **kwargs: Any
        ) -> str:
            return path

    class MyExp(Exporter):
        def __call__(self, records: list | None = None, **kwargs: Any) -> str:
            return "ok"

    assert MyImp()("/f") == "/f"
    assert MyExp()() == "ok"


def test_form_fields_from_object_record() -> None:
    obj = type("R", (), {"id": 5, "title": "Obj"})()
    html = Action.make("e").form([TextInput.make("title")]).render(obj, record=obj)
    assert "Obj" in html and 'data-record-id="5"' in html

    html2 = (
        Action.make("f")
        .form([TextInput.make("title")])
        .fill_form({"title": "fill"})
        .render({"id": 1, "title": "rec"}, record={"id": 1, "title": "rec"})
    )
    assert "rec" in html2

    a = (
        Action.make("c")
        .color(lambda **_: None)
        .icon(lambda **_: None)
        .modal_heading(lambda **_: None)
        .modal_description(lambda **_: None)
        .requires_confirmation()
    )
    assert a.get_color() == "primary"
    assert a.get_icon() is None
    assert "data-confirm" in a.render()

    danger = Action.make("wipe").label("Wipe").color("danger").render()
    assert "cannot be undone" in danger

    assert Action.make("w").color("danger").without_confirmation().needs_confirmation() is False

    html3 = Action.make("x").extra_attributes({"flag": True, "skip": None, "no": False}).render()
    assert "flag" in html3 and "skip" not in html3 and "no=" not in html3

    assert Action.make("b").button().badge(False).get_trigger_style() == "button"

    assert "or-btn-label" in Action.make("io").label("Only").icon_button().render()

    weird = Action.make("w")
    weird._trigger_style = "nope"
    assert weird.get_trigger_style() == "button"

    conf = Action.make("del").label("Delete").requires_confirmation().render()
    assert 'data-modal-heading="Delete?"' in conf

    assert "href=" not in Action.make("m").url("/x").modal().render()

    assert 'data-record-id="' not in Action.make("r").requires_confirmation().render(
        {"name": "a"}, record={"name": "a"}
    )

    assert Action.make("x")._render_form_fields({"a": 1}) == ""

    nameless = TextInput.make("t")
    nameless._name = None
    Action.make("f2").form([nameless]).fill_form({})._render_form_fields(type("R", (), {})())
