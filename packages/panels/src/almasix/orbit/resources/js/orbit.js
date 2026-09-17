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
      slideOver: false,
      modalWidth: "md",
      stickyHeader: false,
      stickyFooter: false,
      closeOnEscape: true,
      closeOnClickAway: true,
      init() {
        window.addEventListener("orbit:mount-action", (event) => {
          const detail = event.detail || {};
          this.name = detail.name || "";
          this.heading = detail.heading || detail.name || "Confirm";
          this.description = detail.description || "";
          this.needsConfirm = Boolean(detail.confirm);
          this.slideOver = Boolean(detail.slideOver);
          this.modalWidth = detail.modalWidth || "md";
          this.stickyHeader = Boolean(detail.stickyHeader);
          this.stickyFooter = Boolean(detail.stickyFooter);
          this.closeOnEscape = detail.closeOnEscape !== false;
          this.closeOnClickAway = detail.closeOnClickAway !== false;
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
              slideOver: btn.getAttribute("data-slide-over") === "true",
              modalWidth: btn.getAttribute("data-modal-width") || "md",
              stickyHeader: btn.getAttribute("data-sticky-header") === "true",
              stickyFooter: btn.getAttribute("data-sticky-footer") === "true",
              closeOnEscape: btn.getAttribute("data-close-on-escape") !== "false",
              closeOnClickAway: btn.getAttribute("data-close-on-click-away") !== "false",
            },
          }),
        );
      },
      true,
    );

    // TipTap host for RichEditor (.or-editor-rich[data-tiptap])
    const bootTipTap = () => {
      const nodes = document.querySelectorAll(".or-editor-rich[data-tiptap]");
      if (!nodes.length) return;
      const ensure = () => {
        if (!window.tipTapOrbitReady) {
          const s = document.createElement("script");
          s.src = "https://cdn.jsdelivr.net/npm/@tiptap/core@2/dist/index.umd.min.js";
          s.onload = () => {
            window.tipTapOrbitReady = true;
            nodes.forEach(initEditor);
          };
          document.head.appendChild(s);
          return;
        }
        nodes.forEach(initEditor);
      };
      const initEditor = (root) => {
        if (root.dataset.tiptapBound === "1") return;
        const input = root.querySelector("[data-tiptap-input]");
        const surface = root.querySelector("[data-tiptap-surface]") || root;
        root.dataset.tiptapBound = "1";
        root.addEventListener("input", () => {
          if (input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement) {
            input.value = surface.innerHTML;
            input.dispatchEvent(new Event("input", { bubbles: true }));
          }
        });
        if (input && !surface.innerHTML) {
          surface.innerHTML = input.value || "";
        }
      };
      ensure();
    };
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bootTipTap);
    } else {
      bootTipTap();
    }
  };

  if (typeof window !== "undefined" && window.Alpine) {
    register();
  } else if (typeof document !== "undefined") {
    document.addEventListener("alpine:init", register);
  }
})();
