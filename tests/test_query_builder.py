"""Tests for almasix.orbit.query_builder."""

from __future__ import annotations

from almasix.orbit.query_builder.builder import (
    BooleanConstraint,
    Constraint,
    DateConstraint,
    NumberConstraint,
    Operator,
    QueryBuilder,
    SelectConstraint,
    TextConstraint,
)


def test_constraint_operators_apply() -> None:
    records = [
        {"name": "Ada", "age": 30, "role": "admin", "bio": "hi"},
        {"name": "Bob", "age": 20, "role": "user", "bio": ""},
        {"name": "Cid", "age": None, "role": "user", "bio": None},
    ]
    c = Constraint.make("name").attribute("name").operators(Operator.EQUALS, Operator.CONTAINS)
    assert c.get_attribute() == "name"
    assert len(c.apply(records, Operator.EQUALS, "Ada")) == 1
    assert len(c.apply(records, Operator.NOT_EQUALS, "Ada")) == 2
    assert len(c.apply(records, Operator.CONTAINS, "a")) == 1  # Ada only (casefold)
    assert len(c.apply(records, Operator.CONTAINS, "A")) == 1
    assert len(TextConstraint.make("name").apply(records, Operator.STARTS_WITH, "B")) == 1
    assert len(TextConstraint.make("name").apply(records, Operator.ENDS_WITH, "b")) == 1

    age = NumberConstraint.make("age")
    assert len(age.apply(records, Operator.GREATER_THAN, 25)) == 1
    assert len(age.apply(records, Operator.LESS_THAN, 25)) == 1
    assert len(age.apply(records, Operator.EQUALS, 30)) == 1
    assert len(age.apply(records, Operator.NOT_EQUALS, 30)) == 2

    bio = TextConstraint.make("bio")
    assert len(bio.apply(records, Operator.IS_SET, None)) == 1
    assert len(bio.apply(records, Operator.IS_NOT_SET, None)) == 2

    role = SelectConstraint.make("role").options({"admin": "Admin"})
    assert len(role.apply(records, Operator.IN, ["admin"])) == 1
    assert SelectConstraint.make("role").options({"a": "A"})._options == {"a": "A"}
    assert Operator.EQUALS in BooleanConstraint.make("flag")._operators
    assert Operator.GREATER_THAN in DateConstraint.make("created")._operators
    assert Operator.LESS_THAN in NumberConstraint.make("n")._operators
    # IS_SET / IS_NOT_SET / LESS on numbers already covered; hit remaining branches
    assert TextConstraint.make("bio").apply(records, Operator.IS_SET, None)
    assert TextConstraint.make("bio").apply(records, Operator.IS_NOT_SET, None)
    assert NumberConstraint.make("age").apply(records, Operator.LESS_THAN, 25)
    assert NumberConstraint.make("age").apply(records, Operator.GREATER_THAN, 100) == []

    obj = type("R", (), {"name": "Z"})()
    assert Constraint.make("name").apply([obj], Operator.EQUALS, "Z")


def test_query_builder_rules() -> None:
    records = [
        {"name": "Ada", "age": 30},
        {"name": "Bob", "age": 20},
    ]
    qb = (
        QueryBuilder.make()
        .constraints([TextConstraint.make("name"), NumberConstraint.make("age")])
        .rules(
            [
                {"constraint": "name", "operator": "contains", "value": "a"},
                {"constraint": "age", "operator": "greater_than", "value": 25},
                {"constraint": "missing", "operator": "equals", "value": 1},
            ]
        )
    )
    assert len(qb.get_constraints()) == 2
    result = qb.apply(records)
    assert result == [{"name": "Ada", "age": 30}]
    d = qb.to_dict()
    assert "rules" in d and len(d["constraints"]) == 2


def test_query_builder_or_logic_and_add_rule() -> None:
    records = [
        {"name": "Ada", "age": 30},
        {"name": "Bob", "age": 20},
    ]
    qb = (
        QueryBuilder.make()
        .constraints([TextConstraint.make("name"), NumberConstraint.make("age")])
        .logic("or")
        .add_rule("name", Operator.EQUALS, "Bob")
        .add_rule("age", "greater_than", 25)
    )
    assert qb.get_logic() == "or"
    names = {row["name"] for row in qb.apply(records)}
    assert names == {"Ada", "Bob"}
    assert qb.to_dict()["logic"] == "or"
    # Duplicate OR match does not duplicate the row.
    twice = QueryBuilder.make().constraints([TextConstraint.make("name")]).logic("OR")
    twice.add_rule("name", "contains", "a").add_rule("name", "contains", "A")
    assert twice.apply([{"name": "Ada"}]) == [{"name": "Ada"}]
    skipped = (
        QueryBuilder.make()
        .constraints([TextConstraint.make("name")])
        .logic("or")
        .rules([{"constraint": "missing", "operator": "equals", "value": 1}])
    )
    assert skipped.apply(records) == []


def test_query_builder_renders_typed_value_inputs() -> None:
    html = (
        QueryBuilder.make()
        .constraints(
            [
                TextConstraint.make("title").label("Title"),
                NumberConstraint.make("views").label("Views"),
                DateConstraint.make("published_at").label("Published"),
                BooleanConstraint.make("featured").label("Featured"),
                SelectConstraint.make("status").label("Status").options({"draft": "Draft"}),
            ]
        )
        .logic("and")
        .render()
    )
    assert 'data-logic="and"' in html
    assert 'type="number"' in html
    assert 'type="date"' in html
    assert 'type="checkbox"' in html
    assert "Draft" in html
    assert QueryBuilder.make().hidden().render() == ""
    assert "or-qb-logic" in html
    assert 'value="and" selected' in html


def test_query_builder_serializes_and_hydrates_rules() -> None:
    title = TextConstraint.make("title").label("Title")
    assert "contains" in title.to_dict()["operators"]
    assert title.get_operators()
    status = SelectConstraint.make("status").options({"draft": "Draft"})
    assert status.get_options() == {"draft": "Draft"}
    assert status.to_dict()["options"] == {"draft": "Draft"}

    qb = (
        QueryBuilder.make()
        .constraints([title, status, BooleanConstraint.make("featured"), DateConstraint.make("when")])
        .add_rule("title", "contains", "orbit")
        .add_rule("featured", Operator.EQUALS, True)
        .add_rule("when", "equals", "2026-01-01")
    )
    assert qb.get_rules()[0]["constraint"] == "title"
    payload = qb.to_dict()
    assert payload["logic"] == "and"
    html = qb.render()
    assert 'value="orbit"' in html
    assert "checked" in html
    assert 'value="2026-01-01"' in html
    assert 'value="contains" selected' in html

    presence = (
        QueryBuilder.make()
        .constraints([TextConstraint.make("bio")])
        .add_rule("bio", Operator.IS_SET)
        .render()
    )
    assert 'name="bio_value"' not in presence
    assert 'value="is_set" selected' in presence

    hydrated = QueryBuilder.make().constraints([TextConstraint.make("title")])
    html_or = hydrated.render(
        {"logic": "or", "rules": [{"constraint": "title", "operator": "equals", "value": "Ada"}]}
    )
    assert 'data-logic="or"' in html_or
    assert 'value="Ada"' in html_or
    listed = QueryBuilder.make().constraints([TextConstraint.make("title")])
    listed.render([{"constraint": "title", "operator": "contains", "value": "x"}])
    assert listed.get_rules()[0]["value"] == "x"
    QueryBuilder.make().constraints([TextConstraint.make("title")]).render({})
    QueryBuilder.make().constraints([TextConstraint.make("title")]).render({"rules": "nope"})

    cleared = qb.clear_rules()
    assert cleared.get_rules() == []
    assert cleared.apply([{"title": "Ada"}]) == [{"title": "Ada"}]


def test_query_builder_filter_dict_value_and_indicator() -> None:
    from almasix.orbit.tables import QueryBuilderFilter

    records = [{"name": "Ada"}, {"name": "Bob"}]
    builder = QueryBuilder.make().constraints([TextConstraint.make("name")])
    qf = QueryBuilderFilter.make().builder(builder)
    matched = qf.apply(
        records,
        {
            "logic": "or",
            "rules": [
                {"constraint": "name", "operator": "equals", "value": "Ada"},
                {"constraint": "name", "operator": "equals", "value": "Bob"},
            ],
        },
    )
    assert {row["name"] for row in matched} == {"Ada", "Bob"}
    assert qf.resolve_indicator([]) is None
    assert qf.resolve_indicator({"rules": []}) is None
    assert qf.resolve_indicator([{"constraint": "name"}]) == "1 rule"
    assert qf.resolve_indicator({"logic": "or", "rules": [{}, {}]}) == "2 rules (or)"
    labeled = QueryBuilderFilter.make().indicate_using(lambda value, **_: f"custom:{value}")
    assert labeled.resolve_indicator("x") == "custom:x"
    assert QueryBuilderFilter.make().resolve_indicator("open") == "open"
    assert qf.resolve_indicator({"rules": "nope"}) is None
    assert QueryBuilderFilter.make().builder(
        QueryBuilder.make().constraints([TextConstraint.make("name")])
    ).apply(records, {"logic": "and"}) == records

    class _NoLogic:
        def rules(self, value):
            self._saved = value

        def apply(self, query):
            return query

    assert QueryBuilderFilter.make().builder(_NoLogic()).apply([1], {"logic": "or", "rules": []}) == [1]

    views = (
        QueryBuilder.make()
        .constraints(
            [
                NumberConstraint.make("views").label("Views"),
                SelectConstraint.make("status").options({"draft": "Draft", "live": "Live"}),
            ]
        )
        .add_rule("views", "greater_than", 10)
        .add_rule("status", "equals", "draft")
        .render()
    )
    assert 'value="10"' in views
    assert 'value="draft" selected' in views
