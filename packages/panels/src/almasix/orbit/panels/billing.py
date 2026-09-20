"""Pluggable tenant billing provider (plans, subscribe, portal)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass
class BillingPlan:
    """A price a tenant can subscribe to."""

    id: str
    name: str
    amount: int = 0
    currency: str = "USD"
    interval: str = "month"
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount,
            "currency": self.currency,
            "interval": self.interval,
            "description": self.description,
            "price_label": self.price_label(),
        }

    def price_label(self) -> str:
        if self.amount <= 0:
            return "Free"
        major = self.amount / 100
        return f"{self.currency} {major:.2f}/{self.interval}"


def tenant_key(tenant: Any | None) -> str:
    if tenant is None:
        return "default"
    if isinstance(tenant, dict):
        return str(tenant.get("id") or tenant.get("slug") or "default")
    for attr in ("id", "slug", "pk"):
        value = getattr(tenant, attr, None)
        if value is not None:
            return str(value)
    return str(tenant)


@runtime_checkable
class BillingProvider(Protocol):
    def plans(self, *, tenant: Any = None) -> list[BillingPlan]: ...  # pragma: no cover

    def current_subscription(self, *, tenant: Any = None) -> dict[str, Any] | None: ...  # pragma: no cover

    def subscribe(
        self,
        plan_id: str,
        *,
        tenant: Any = None,
        user: Any = None,
    ) -> dict[str, Any]: ...  # pragma: no cover

    def portal_url(self, *, tenant: Any = None) -> str | None: ...  # pragma: no cover


class MemoryBillingProvider:
    """In-process billing adapter for demos, tests, and local panels."""

    def __init__(
        self,
        plans: list[BillingPlan] | None = None,
        *,
        portal_url: str | None = None,
    ) -> None:
        self._plans = list(
            plans
            or [
                BillingPlan(
                    "starter",
                    "Starter",
                    0,
                    description="Free for small teams.",
                ),
                BillingPlan(
                    "pro",
                    "Pro",
                    2900,
                    description="Unlimited seats and priority support.",
                ),
            ]
        )
        self._subs: dict[str, str] = {}
        self._portal_url = portal_url

    def plans(self, *, tenant: Any = None) -> list[BillingPlan]:
        return list(self._plans)

    def current_subscription(self, *, tenant: Any = None) -> dict[str, Any] | None:
        plan_id = self._subs.get(tenant_key(tenant))
        if not plan_id:
            return None
        plan = next((item for item in self._plans if item.id == plan_id), None)
        if plan is None:
            return None
        return {"plan_id": plan.id, "plan": plan.to_dict(), "status": "active"}

    def subscribe(
        self,
        plan_id: str,
        *,
        tenant: Any = None,
        user: Any = None,
    ) -> dict[str, Any]:
        plan = next((item for item in self._plans if item.id == str(plan_id)), None)
        if plan is None:
            return {"ok": False, "error": "Unknown plan."}
        self._subs[tenant_key(tenant)] = plan.id
        return {"ok": True, "plan_id": plan.id, "user": user}

    def portal_url(self, *, tenant: Any = None) -> str | None:
        return self._portal_url
