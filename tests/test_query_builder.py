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
