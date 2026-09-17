(() => {
  const register = () => {
    if (typeof window === "undefined" || !window.Alpine) {
      return;
    }

    window.Alpine.data("orbitShell", () => ({
      collapsed: false,
      drawerOpen: false,
      theme: "system",
      _mq: null,
      init() {
        try {
          const stored = localStorage.getItem("orbit-theme");
          if (stored === "dark" || stored === "light" || stored === "system") {
            this.theme = stored;
          } else {
            this.theme = "system";
          }
        } catch (_) {
          /* ignore */
        }
        this.applyTheme();
        try {
          this._mq = window.matchMedia("(prefers-color-scheme: dark)");
          this._mq.addEventListener("change", () => {
            if (this.theme === "system") {
              this.applyTheme();
            }
          });
        } catch (_) {
          /* ignore */
        }
        this.$watch("drawerOpen", (open) => {
          document.documentElement.classList.toggle("or-scroll-lock", Boolean(open));
        });
        try {
          if (sessionStorage.getItem("orbit-sidebar-collapsed") === "1") {
            this.collapsed = true;
          }
        } catch (_) {
          /* ignore */
        }
      },
      resolvedTheme() {
        if (this.theme === "dark") return "dark";
        if (this.theme === "light") return "light";
        try {
          return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        } catch (_) {
          return "light";
        }
      },
      applyTheme() {
        const root = document.documentElement;
        const resolved = this.resolvedTheme();
        root.setAttribute("data-theme", resolved);
        root.setAttribute("data-theme-preference", this.theme);
        root.classList.toggle("dark", resolved === "dark");
        try {
          localStorage.setItem("orbit-theme", this.theme);
        } catch (_) {
          /* ignore */
        }
      },
      cycleTheme() {
        const order = ["light", "dark", "system"];
        const idx = order.indexOf(this.theme);
        this.theme = order[(idx + 1) % order.length];
        this.applyTheme();
      },
      toggleTheme() {
        this.cycleTheme();
      },
      toggleCollapse() {
        this.collapsed = !this.collapsed;
        try {
          sessionStorage.setItem("orbit-sidebar-collapsed", this.collapsed ? "1" : "0");
        } catch (_) {
          /* ignore */
        }
      },
      openDrawer() {
        this.drawerOpen = true;
      },
      closeDrawer() {
        this.drawerOpen = false;
      },
    }));

    window.Alpine.data("orbitTableSelection", () => ({
      selected: [],
      init() {
        const initial = this.$el?.getAttribute?.("data-selected");
        if (initial) {
          try {
            const parsed = JSON.parse(initial);
            if (Array.isArray(parsed)) {
              this.selected = parsed.map(String);
            }
          } catch (_) {
            /* ignore bad JSON */
          }
        }
      },
      syncHost() {
        const root = this.$el?.closest?.("[wire\\:id], [conduit\\:id], [data-conduit-id]");
        const wire = this.$wire || root?.__conduit || root?.__livewire;
        if (wire && typeof wire.set === "function") {
          wire.set("selected", this.selected);
        } else if (typeof window.Conduit !== "undefined" && window.Conduit.find) {
          try {
            window.Conduit.find(this.$el)?.set?.("selected", this.selected);
          } catch (_) {
            /* optional Conduit bridge */
          }
        }
      },
      toggle(id, checked) {
        const key = String(id);
        if (checked) {
          if (!this.selected.includes(key)) {
            this.selected = [...this.selected, key];
          }
        } else {
          this.selected = this.selected.filter((x) => x !== key);
        }
        this.syncHost();
      },
      toggleAll(checked) {
        const boxes = this.$el.querySelectorAll('input.or-row-check[data-record-id]');
        const ids = [];
        boxes.forEach((box) => {
          box.checked = checked;
          if (checked) {
            ids.push(String(box.getAttribute("data-record-id")));
          }
        });
        this.selected = ids;
        this.syncHost();
      },
      get pageFullySelected() {
        const boxes = this.$el.querySelectorAll('input.or-row-check[data-record-id]');
        return boxes.length > 0 && this.selected.length === boxes.length;
      },
      clear() {
        this.toggleAll(false);
      },
    }));

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
        this.$el.classList.add("or-alpine-ready");
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

    window.Alpine.data("orbitSearchableSelect", () => ({
      q: "",
      filter() {
        const select = this.$refs.select;
        if (!(select instanceof HTMLSelectElement)) return;
        const q = (this.q || "").toLowerCase();
        Array.from(select.options).forEach((opt) => {
          if (!opt.value) {
            opt.hidden = false;
            return;
          }
          const label = (opt.dataset.label || opt.textContent || "").toLowerCase();
          opt.hidden = Boolean(q) && !label.includes(q);
        });
      },
    }));

    window.Alpine.data("orbitMorphToSelect", () => ({
      init() {
        const typeSelect = this.$el.querySelector("[data-morph-type]");
        if (typeSelect) {
          typeSelect.addEventListener("change", () => {
            this.$dispatch("orbit:morph-type-changed", {
              type: typeSelect.value,
              field: this.$el.getAttribute("data-field"),
            });
          });
        }
      },
    }));

    const bootTipTap = () => {
      const nodes = document.querySelectorAll(".or-editor-rich[data-tiptap]");
      if (!nodes.length) return;

      const initEditor = (root) => {
        if (root.dataset.tiptapBound === "1") return;
        const input =
          root.querySelector("[data-tiptap-input]") ||
          document.getElementById(root.getAttribute("data-input") || "");
        const surface =
          root.querySelector("[data-tiptap-surface]") ||
          (() => {
            const el = document.createElement("div");
            el.className = "or-tiptap-surface";
            el.setAttribute("contenteditable", "true");
            el.dataset.tiptapSurface = "1";
            root.appendChild(el);
            return el;
          })();
        root.dataset.tiptapBound = "1";

        const toolbar = root.parentElement?.querySelector(".or-editor-toolbar");
        if (toolbar) {
          toolbar.addEventListener("click", (event) => {
            const btn = event.target instanceof Element ? event.target.closest("[data-tool]") : null;
            if (!(btn instanceof HTMLElement)) return;
            event.preventDefault();
            const tool = btn.getAttribute("data-tool");
            const cmd = {
              bold: "bold",
              italic: "italic",
              underline: "underline",
              strike: "strikeThrough",
              link: "createLink",
            }[tool || ""];
            if (cmd === "createLink") {
              const url = window.prompt("URL");
              if (url) document.execCommand(cmd, false, url);
            } else if (cmd) {
              document.execCommand(cmd, false);
            }
            sync();
          });
        }

        const sync = () => {
          if (input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement) {
            input.value = surface.innerHTML;
            input.dispatchEvent(new Event("input", { bubbles: true }));
          }
        };
        surface.addEventListener("input", sync);
        if (input && !surface.innerHTML) {
          surface.innerHTML = input.value || "";
        }
      };

      nodes.forEach(initEditor);
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

  // Floating tooltips for the collapsed sidebar rail. CSS ::after tooltips are
  // clipped by overflow:auto on .or-sidebar-nav, so we portal to <body>.
  const bootCollapsedTooltips = () => {
    if (typeof document === "undefined") return;
    let tip = document.getElementById("or-floating-tooltip");
    if (!tip) {
      tip = document.createElement("div");
      tip.id = "or-floating-tooltip";
      tip.className = "or-floating-tooltip";
      tip.setAttribute("role", "tooltip");
      tip.hidden = true;
      document.body.appendChild(tip);
    }

    const hide = () => {
      tip.hidden = true;
      tip.textContent = "";
    };

    const show = (el) => {
      const app = el.closest(".or-app");
      if (!app || !app.classList.contains("is-collapsed")) {
        hide();
        return;
      }
      const text = el.getAttribute("data-tooltip");
      if (!text) {
        hide();
        return;
      }
      tip.textContent = text;
      tip.hidden = false;
      const rect = el.getBoundingClientRect();
      const tipRect = tip.getBoundingClientRect();
      let top = rect.top + rect.height / 2 - tipRect.height / 2;
      let left = rect.right + 10;
      top = Math.max(8, Math.min(top, window.innerHeight - tipRect.height - 8));
      if (left + tipRect.width > window.innerWidth - 8) {
        left = Math.max(8, rect.left - tipRect.width - 10);
      }
      tip.style.top = `${Math.round(top)}px`;
      tip.style.left = `${Math.round(left)}px`;
    };

    document.addEventListener(
      "pointerover",
      (event) => {
        const el =
          event.target instanceof Element
            ? event.target.closest(".or-app.is-collapsed [data-tooltip]")
            : null;
        if (el) show(el);
      },
      true
    );
    document.addEventListener(
      "pointerout",
      (event) => {
        const el =
          event.target instanceof Element
            ? event.target.closest(".or-app.is-collapsed [data-tooltip]")
            : null;
        if (!el) return;
        const related =
          event.relatedTarget instanceof Element ? event.relatedTarget.closest(".or-app.is-collapsed [data-tooltip]") : null;
        if (related === el) return;
        hide();
      },
      true
    );
    document.addEventListener("scroll", hide, true);
    window.addEventListener("resize", hide);
  };

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bootCollapsedTooltips);
    } else {
      bootCollapsedTooltips();
    }
  }
})();
