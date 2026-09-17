(() => {
  const register = () => {
    if (typeof window === "undefined" || !window.Alpine) {
      return;
    }
    window.Alpine.data("orbitNotifications", () => ({
      init() {},
      dismiss(id) {
        const el = this.$el?.querySelector?.(`[data-id="${id}"]`);
        if (el) {
          el.remove();
        }
      },
    }));

    window.Alpine.data("orbitActionModal", () => ({
      open: false,
      name: "",
      heading: "",
      description: "",
      needsConfirm: false,
      init() {
        window.addEventListener("orbit:mount-action", (event) => {
          const detail = event.detail || {};
          this.name = detail.name || "";
          this.heading = detail.heading || detail.name || "Confirm";
          this.description = detail.description || "";
          this.needsConfirm = Boolean(detail.confirm);
          this.open = true;
        });
      },
      close() {
        this.open = false;
      },
      confirm() {
        this.$dispatch("orbit:action-confirmed", { name: this.name });
        this.close();
      },
    }));

    // Bridge wire:click mountAction buttons when Conduit is not hosting yet.
    document.addEventListener(
      "click",
      (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const btn = target.closest("[data-action][wire\\:click], [data-action][data-confirm]");
        if (!(btn instanceof HTMLElement)) return;
        const click = btn.getAttribute("wire:click") || "";
        if (!click.includes("mountAction") && btn.getAttribute("data-confirm") !== "true") {
          return;
        }
        if (window.Livewire || window.Conduit) {
          return;
        }
        event.preventDefault();
        const name = btn.getAttribute("data-action") || "";
        window.dispatchEvent(
          new CustomEvent("orbit:mount-action", {
            detail: {
              name,
              heading: btn.getAttribute("data-modal-heading") || name,
              description: btn.getAttribute("data-modal-description") || "",
              confirm: btn.getAttribute("data-confirm") === "true",
            },
          }),
        );
      },
      true,
    );
  };

  if (typeof window !== "undefined" && window.Alpine) {
    register();
  } else if (typeof document !== "undefined") {
    document.addEventListener("alpine:init", register);
  }
})();
