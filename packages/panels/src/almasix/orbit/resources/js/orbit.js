(() => {
  window.orbitWire = (el) => {
    const node = el?.closest?.("[wire\\:id], [conduit\\:id], [data-conduit-id]") || el;
    return (
      (typeof window !== "undefined" && window.Livewire && node?.id && window.Livewire.find?.(node.id)) ||
      node?.__conduit ||
      node?.__livewire ||
      node?.__wire ||
      null
    );
  };

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

    window.Alpine.data("orbitTableFilters", () => ({
      filtersOpen: false,
      defer: false,
      activeCount: 0,
      pending: {},
      init() {
        const el = this.$el;
        this.defer = el?.hasAttribute?.("data-defer-filters") || false;
        const count = el?.getAttribute?.("data-active-count");
        if (count != null) {
          this.activeCount = Number(count) || 0;
        }
        const pending = el?.getAttribute?.("data-pending");
        if (pending) {
          try {
            const parsed = JSON.parse(pending);
            if (parsed && typeof parsed === "object") {
              this.pending = { ...parsed };
            }
          } catch (_) {
            /* ignore */
          }
        }
        this._onCloseOthers = (event) => {
          if (event?.detail?.except === "filters") {
            return;
          }
          this.filtersOpen = false;
        };
        window.addEventListener("orbit:close-dropdowns", this._onCloseOthers);
      },
      destroy() {
        if (this._onCloseOthers) {
          window.removeEventListener("orbit:close-dropdowns", this._onCloseOthers);
        }
      },
      toggleFilters(event) {
        event?.stopPropagation?.();
        this.filtersOpen = !this.filtersOpen;
        if (this.filtersOpen) {
          window.dispatchEvent(
            new CustomEvent("orbit:close-dropdowns", { detail: { except: "filters" } })
          );
        }
      },
      closeFilters() {
        this.filtersOpen = false;
      },
      applyDeferred() {
        const wire = window.orbitWire?.(this.$el);
        const payload = { ...this.pending };
        Object.keys(payload).forEach((key) => {
          if (payload[key] === "" || payload[key] == null) {
            delete payload[key];
          }
        });
        if (wire && typeof wire.applyTableFilters === "function") {
          wire.applyTableFilters(payload);
        } else if (wire && typeof wire.$set === "function") {
          wire.$set("table_filters", payload);
        }
        this.filtersOpen = false;
      },
    }));

    window.Alpine.data("orbitDropdown", () => ({
      menuOpen: false,
      init() {
        this._menu =
          this.$el?.querySelector?.(
            ":scope > .or-dropdown-menu, :scope > .or-columns-panel, :scope > .or-filters-panel"
          ) || null;
        this._trigger =
          this.$el?.querySelector?.(":scope > .or-btn, :scope > button") || null;
        this._onCloseOthers = (event) => {
          if (event?.detail?.except === "dropdown") {
            return;
          }
          this.menuOpen = false;
        };
        window.addEventListener("orbit:close-dropdowns", this._onCloseOthers);
        this.$watch("menuOpen", (open) => {
          if (open) {
            this._positionMenu();
          } else {
            this._clearMenuPosition();
          }
        });
      },
      destroy() {
        this._clearMenuPosition();
        if (this._onCloseOthers) {
          window.removeEventListener("orbit:close-dropdowns", this._onCloseOthers);
        }
      },
      _selectionRoot() {
        return this.$el?.closest?.(".or-table-wrap, .or-list-card") || null;
      },
      syncSelection() {
        const root = this._selectionRoot();
        if (!root || typeof window.Alpine === "undefined") {
          return;
        }
        try {
          const data = window.Alpine.$data(root);
          if (data && typeof data.syncHost === "function") {
            data.syncHost();
          }
        } catch (_) {
          /* selection root may not be Alpine-bound yet */
        }
      },
      _positionMenu() {
        const menu = this._menu;
        const trigger = this._trigger;
        if (!menu || !trigger) {
          return;
        }
        const place = () => {
          menu.classList.add("or-dropdown-menu-fixed");
          const rect = trigger.getBoundingClientRect();
          const preferEnd =
            menu.classList.contains("or-dropdown-menu-end") ||
            !!trigger.closest(".or-td-actions, .or-row-actions, .or-page-actions");
          const mw = menu.offsetWidth || 192;
          const mh = menu.offsetHeight || 0;
          let top = rect.bottom + 6;
          let left = preferEnd ? rect.right - mw : rect.left;
          if (top + mh > window.innerHeight - 8 && rect.top - mh - 6 > 8) {
            top = rect.top - mh - 6;
          }
          left = Math.max(8, Math.min(left, window.innerWidth - mw - 8));
          menu.style.top = `${Math.round(top)}px`;
          menu.style.left = `${Math.round(left)}px`;
          menu.style.right = "auto";
        };
        // x-show applies display after this tick — measure once visible.
        if (typeof this.$nextTick === "function") {
          this.$nextTick(place);
        } else {
          requestAnimationFrame(place);
        }
        if (!this._onReposition) {
          this._onReposition = () => {
            if (this.menuOpen) {
              place();
            }
          };
          window.addEventListener("scroll", this._onReposition, true);
          window.addEventListener("resize", this._onReposition);
        }
      },
      _clearMenuPosition() {
        const menu = this._menu;
        if (menu) {
          menu.classList.remove("or-dropdown-menu-fixed");
          menu.style.top = "";
          menu.style.left = "";
          menu.style.right = "";
        }
        if (this._onReposition) {
          window.removeEventListener("scroll", this._onReposition, true);
          window.removeEventListener("resize", this._onReposition);
          this._onReposition = null;
        }
      },
      toggleMenu(event) {
        event?.preventDefault?.();
        event?.stopPropagation?.();
        this.menuOpen = !this.menuOpen;
        if (this.menuOpen) {
          window.dispatchEvent(
            new CustomEvent("orbit:close-dropdowns", { detail: { except: "dropdown" } })
          );
          // Do not syncHost here: $set(selected) remorphs the Conduit root and
          // used to un-hide Filters/bulk via stripped Alpine styles. Selection is
          // pushed on bulk action click (capture) instead.
        }
      },
      closeMenu() {
        this.menuOpen = false;
      },
    }));

    window.Alpine.data("orbitTableSelection", () => ({
      selected: [],
      total: 0,
      allResultsSelected: false,
      init() {
        // Capture the x-data root once. Alpine's `$el` inside child `@click`
        // handlers is the child node (e.g. Clear button), not the wrap.
        this._rootEl = this.$el;
        const initial = this._rootEl?.getAttribute?.("data-selected");
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
        const totalAttr = this._rootEl?.getAttribute?.("data-total");
        if (totalAttr != null) {
          this.total = Number(totalAttr) || 0;
        }
        if (this._rootEl?.getAttribute?.("data-select-all") === "true") {
          this.allResultsSelected = true;
        }
        // Alpine @change/@click on thead checkboxes is unreliable (handler never
        // fires alongside :checked). Bind select-all imperatively instead.
        this._onSelectAllChange = (event) => {
          const target = event.target;
          if (!(target instanceof HTMLInputElement)) {
            return;
          }
          if (!target.classList.contains("or-select-all")) {
            return;
          }
          this.toggleAll(target.checked);
        };
        this._rootEl.addEventListener("change", this._onSelectAllChange);
        this._syncHeaderCheck();
        // Sync to host immediately before a bulk action Conduit call (capture phase).
        this._onBulkActionClick = (event) => {
          const target = event.target;
          if (!(target instanceof Element)) {
            return;
          }
          const bulk = this._rootEl.querySelector(
            ".or-table-bulk-trigger, .or-list-bulk-actions"
          );
          if (!bulk || !bulk.contains(target)) {
            return;
          }
          if (target.closest("[wire\\:click], [conduit\\:click], [data-action]")) {
            this.syncHost();
          }
        };
        this._rootEl.addEventListener("click", this._onBulkActionClick, true);
      },
      destroy() {
        if (this._onSelectAllChange && this._rootEl) {
          this._rootEl.removeEventListener("change", this._onSelectAllChange);
        }
        if (this._onBulkActionClick && this._rootEl) {
          this._rootEl.removeEventListener("click", this._onBulkActionClick, true);
        }
      },
      _root() {
        return this._rootEl || this.$el;
      },
      _host() {
        const root = this._root()?.closest?.("[wire\\:id], [conduit\\:id], [data-conduit-id]");
        return this.$wire || root?.__conduit || root?.__livewire || null;
      },
      syncHost() {
        const wire = window.orbitWire?.(this._root()) || this._host();
        if (!wire) {
          return;
        }
        const next = this.selected.map(String);
        const selectAll = !!this.allResultsSelected;
        const prev = this._lastSynced;
        const prevAll = this._lastSyncedSelectAll;
        if (
          Array.isArray(prev) &&
          prev.length === next.length &&
          prev.every((value, index) => value === next[index]) &&
          prevAll === selectAll
        ) {
          return;
        }
        this._lastSynced = next;
        this._lastSyncedSelectAll = selectAll;
        if (typeof wire.$set === "function") {
          wire.$set("selected", next);
          wire.$set("select_all", selectAll);
          return;
        }
        if (typeof wire.set === "function") {
          wire.set("selected", next);
          wire.set("select_all", selectAll);
        }
      },
      pageIds() {
        const boxes = this._root().querySelectorAll("input.or-row-check[data-record-id]");
        return Array.from(boxes).map((box) => String(box.getAttribute("data-record-id")));
      },
      _syncHeaderCheck() {
        const header = this._root().querySelector(
          "th.or-th-select input.or-row-check, .or-select-all"
        );
        if (header) {
          header.checked = this.pageFullySelected;
        }
      },
      toggle(id, checked) {
        const key = String(id);
        if (this.allResultsSelected && !checked) {
          // Leave "all matching" mode: keep only this page, minus the unchecked row.
          this.allResultsSelected = false;
          this.selected = this.pageIds().filter((x) => x !== key);
        } else if (checked) {
          this.allResultsSelected = false;
          if (!this.selected.includes(key)) {
            this.selected = [...this.selected, key];
          }
        } else {
          this.allResultsSelected = false;
          this.selected = this.selected.filter((x) => x !== key);
        }
        this._syncHeaderCheck();
        // Keep selection Alpine-only while picking rows. Syncing on every toggle
        // remorphs the Conduit host and remounts dropdowns (filters/Actions fight).
        window.dispatchEvent(new CustomEvent("orbit:close-dropdowns", { detail: {} }));
      },
      toggleAll(checked) {
        this.allResultsSelected = false;
        const ids = this.pageIds();
        if (checked) {
          const set = new Set(this.selected);
          ids.forEach((id) => set.add(id));
          this.selected = Array.from(set);
        } else {
          const drop = new Set(ids);
          this.selected = this.selected.filter((id) => !drop.has(id));
        }
        this._root().querySelectorAll("input.or-row-check[data-record-id]").forEach((box) => {
          box.checked = checked;
        });
        this._syncHeaderCheck();
        window.dispatchEvent(new CustomEvent("orbit:close-dropdowns", { detail: {} }));
      },
      get pageFullySelected() {
        if (this.allResultsSelected) {
          return this.pageIds().length > 0;
        }
        const ids = this.pageIds();
        return ids.length > 0 && ids.every((id) => this.selected.includes(id));
      },
      get selectionCount() {
        return this.allResultsSelected ? this.total : this.selected.length;
      },
      get showSelectAllResults() {
        const pageCount = this.pageIds().length;
        return (
          !this.allResultsSelected &&
          this.pageFullySelected &&
          this.total > pageCount &&
          pageCount > 0
        );
      },
      get showSelectPageOnly() {
        return this.allResultsSelected && this.total > this.pageIds().length;
      },
      selectAllResults() {
        this.allResultsSelected = true;
        const ids = this.pageIds();
        const set = new Set(this.selected);
        ids.forEach((id) => set.add(id));
        this.selected = Array.from(set);
        this._root().querySelectorAll("input.or-row-check[data-record-id]").forEach((box) => {
          box.checked = true;
        });
        this._syncHeaderCheck();
      },
      selectPageOnly() {
        this.allResultsSelected = false;
        this.selected = this.pageIds();
        this._root().querySelectorAll("input.or-row-check[data-record-id]").forEach((box) => {
          box.checked = true;
        });
        this._syncHeaderCheck();
      },
      togglePage() {
        this.toggleAll(!this.pageFullySelected);
      },
      clear() {
        this.allResultsSelected = false;
        this.selected = [];
        this._root().querySelectorAll("input.or-row-check[data-record-id]").forEach((box) => {
          box.checked = false;
        });
        this._syncHeaderCheck();
        window.dispatchEvent(new CustomEvent("orbit:close-dropdowns", { detail: {} }));
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
      hasForm: false,
      formHtml: "",
      recordId: "",
      pendingEl: null,
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
          this.hasForm = Boolean(detail.hasForm);
          this.formHtml = detail.formHtml || "";
          this.recordId = detail.recordId || "";
          this.pendingEl = detail.pendingEl || null;
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
        this.formHtml = "";
        this.pendingEl = null;
      },
      _formData() {
        const root = this.$refs.actionForm;
        if (!root) return {};
        const data = {};
        root.querySelectorAll("input[name], select[name], textarea[name]").forEach((el) => {
          const name = el.getAttribute("name");
          if (!name) return;
          if (el.type === "checkbox") {
            data[name] = el.checked;
          } else {
            data[name] = el.value;
          }
        });
        return data;
      },
      confirm() {
        const payload = {
          name: this.name,
          recordId: this.recordId,
          data: this.hasForm ? this._formData() : {},
        };
        const el = this.pendingEl;
        const wire = el ? window.orbitWire?.(el) : null;
        if (wire && typeof wire.mountAction === "function") {
          wire.mountAction(payload.name, payload.recordId || null, { data: payload.data });
        } else if (wire && typeof wire.$call === "function") {
          wire.$call("mountAction", payload.name, payload.recordId || null, { data: payload.data });
        }
        this.$dispatch("orbit:action-confirmed", payload);
        this.close();
      },
    }));

    document.addEventListener(
      "click",
      (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const btn = target.closest("[data-action]");
        if (!(btn instanceof HTMLElement)) return;
        const needsConfirm = btn.getAttribute("data-confirm") === "true";
        const hasForm = btn.getAttribute("data-has-form") === "true";
        const click = btn.getAttribute("wire:click") || "";
        if (!needsConfirm && !hasForm) {
          return;
        }
        if (!click.includes("mountAction") && !needsConfirm && !hasForm) {
          return;
        }
        // Intercept before Conduit/Livewire so confirm / modal form always shows.
        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === "function") {
          event.stopImmediatePropagation();
        }
        const name = btn.getAttribute("data-action") || "";
        let formHtml = "";
        const tpl =
          btn.querySelector("template.or-action-form-tpl") ||
          btn.parentElement?.querySelector(`template.or-action-form-tpl`);
        // Prefer sibling template immediately after the button.
        const next = btn.nextElementSibling;
        if (next && next.matches?.("template.or-action-form-tpl")) {
          formHtml = next.innerHTML;
        } else if (tpl) {
          formHtml = tpl.innerHTML;
        }
        window.dispatchEvent(
          new CustomEvent("orbit:mount-action", {
            detail: {
              name,
              heading: btn.getAttribute("data-modal-heading") || name,
              description: btn.getAttribute("data-modal-description") || "",
              confirm: needsConfirm,
              hasForm,
              formHtml,
              recordId: btn.getAttribute("data-record-id") || "",
              pendingEl: btn,
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

    // Inline editable columns (Select / Toggle / TextInput / Checkbox).
    const emitColumnEdit = (el) => {
      if (!(el instanceof HTMLElement)) return;
      const kind = el.getAttribute("data-orbit-column-edit");
      if (!kind) return;
      const recordId = el.getAttribute("data-record-id") || "";
      const column = el.getAttribute("data-column") || "";
      let value;
      if (kind === "checkbox" || kind === "toggle") {
        value = el.checked;
      } else {
        value = el.value;
      }
      const wire = window.orbitWire?.(el);
      if (wire && typeof wire.updateColumnState === "function") {
        wire.updateColumnState(recordId, column, value);
      } else if (wire && typeof wire.update_column_state === "function") {
        wire.update_column_state(recordId, column, value);
      } else if (wire && typeof wire.$call === "function") {
        wire.$call("updateColumnState", recordId, column, value);
      }
    };
    document.addEventListener(
      "change",
      (event) => {
        const el = event.target;
        if (!(el instanceof HTMLElement)) return;
        if (!el.getAttribute("data-orbit-column-edit")) return;
        const kind = el.getAttribute("data-orbit-column-edit");
        if (kind === "text") return; // blur only
        emitColumnEdit(el);
      },
      true,
    );
    document.addEventListener(
      "blur",
      (event) => {
        const el = event.target;
        if (!(el instanceof HTMLElement)) return;
        if (el.getAttribute("data-orbit-column-edit") !== "text") return;
        emitColumnEdit(el);
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

  // Collapsible table group headers (Filament-style).
  if (typeof document !== "undefined") {
    document.addEventListener("click", (event) => {
      const header = event.target?.closest?.(
        "tr.or-group-header[data-collapsible='true']"
      );
      if (!header) {
        return;
      }
      if (event.target?.closest?.("a,button,input,label,select")) {
        return;
      }
      const key = header.getAttribute("data-group-key");
      if (key == null) {
        return;
      }
      const collapsed = header.getAttribute("data-collapsed") === "true";
      const next = !collapsed;
      header.setAttribute("data-collapsed", next ? "true" : "false");
      const tbody = header.closest("tbody");
      if (!tbody) {
        return;
      }
      tbody.querySelectorAll("tr.or-group-member").forEach((row) => {
        if (row.getAttribute("data-group-key") !== key) {
          return;
        }
        if (next) {
          row.setAttribute("hidden", "hidden");
        } else {
          row.removeAttribute("hidden");
        }
      });
    });
  }
})();
