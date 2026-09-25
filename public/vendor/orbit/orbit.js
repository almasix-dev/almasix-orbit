(() => {
  window.orbitWire = (el) => {
    let node =
      el?.closest?.("[wire\\:id], [conduit\\:id], [data-conduit-id]") || null;
    if (!node) {
      const menu = el?.closest?.(".or-dropdown-menu, .or-columns-panel");
      node = menu?._orbitHostEl || null;
    }
    if (!node && typeof document !== "undefined") {
      node =
        document.querySelector("[conduit\\:id], [data-conduit-id], [wire\\:id]") ||
        null;
    }
    node = node || el;
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
        if (this.collapsed) this.expandSidebarNav();
        this._initSpa();
      },
      destroy() {
        if (this._spaClick) {
          document.removeEventListener("click", this._spaClick);
        }
        if (this._spaPop) {
          window.removeEventListener("popstate", this._spaPop);
        }
      },
      _initSpa() {
        const rootEl = document.documentElement;
        if (rootEl.getAttribute("data-orbit-spa") !== "true") return;
        this._spaRoot = rootEl.getAttribute("data-orbit-spa-root") || "/";
        this._spaExceptions = (rootEl.getAttribute("data-orbit-spa-exceptions") || "")
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);
        this._spaClick = (event) => this._onSpaClick(event);
        this._spaPop = () => this._spaLoad(location.href, false);
        document.addEventListener("click", this._spaClick);
        window.addEventListener("popstate", this._spaPop);
      },
      _spaShouldHandle(anchor) {
        if (!anchor || !anchor.getAttribute) return false;
        if (anchor.target === "_blank" || anchor.hasAttribute("download")) return false;
        if (anchor.getAttribute("data-orbit-spa") === "false") return false;
        let url;
        try {
          url = new URL(anchor.href, location.origin);
        } catch (_) {
          return false;
        }
        if (url.origin !== location.origin) return false;
        if (url.pathname === location.pathname && url.search === location.search) return false;
        const path = url.pathname;
        const root = this._spaRoot === "/" ? "" : String(this._spaRoot).replace(/\/$/, "");
        if (root && path !== root && !path.startsWith(`${root}/`)) return false;
        return !this._spaExceptions.some(
          (ex) => path === ex || path.endsWith(ex) || path.includes(ex),
        );
      },
      _onSpaClick(event) {
        if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
          return;
        }
        const anchor = event.target?.closest?.("a[href]");
        if (!this._spaShouldHandle(anchor)) return;
        event.preventDefault();
        this._spaLoad(anchor.href, true);
      },
      async _spaLoad(href, push) {
        try {
          const res = await fetch(href, {
            headers: { "X-Orbit-Spa": "1", Accept: "text/html" },
            credentials: "same-origin",
          });
          if (!res.ok) {
            location.href = href;
            return;
          }
          const html = await res.text();
          const doc = new DOMParser().parseFromString(html, "text/html");
          const nextMain = doc.querySelector("main.or-content");
          const curMain = document.querySelector("main.or-content");
          if (!nextMain || !curMain) {
            location.href = href;
            return;
          }
          curMain.replaceWith(nextMain);
          this._spaSwapNav(doc);
          if (this.collapsed) this.expandSidebarNav();
          // Re-bind Alpine + Conduit on the swapped main (list tabs, tables, forms).
          try {
            window.Alpine?.initTree?.(nextMain);
          } catch (_) {
            /* ignore */
          }
          try {
            window.Conduit?.boot?.(nextMain);
          } catch (_) {
            /* ignore */
          }
          document.title = doc.title;
          if (push) history.pushState({}, "", href);
          window.dispatchEvent(new CustomEvent("orbit:spa-navigated", { detail: { href } }));
        } catch (_) {
          location.href = href;
        }
      },
      _spaSwapNav(doc) {
        // Sidebar + topbar carry active states; swap them with the fetched shell.
        const selectors = [
          "nav.or-sidebar-nav",
          "nav.or-topnav",
          ".or-topbar-active-root",
        ];
        for (const selector of selectors) {
          const nextNodes = doc.querySelectorAll(selector);
          const curNodes = document.querySelectorAll(selector);
          if (!nextNodes.length || curNodes.length !== nextNodes.length) continue;
          curNodes.forEach((el, i) => {
            const replacement = nextNodes[i].cloneNode(true);
            el.replaceWith(replacement);
            try {
              window.Alpine?.initTree?.(replacement);
            } catch (_) {
              /* ignore */
            }
          });
        }
        // Breadcrumbs sit outside main.or-content — swap/insert/remove them too.
        this._spaSwapBreadcrumbs(doc);
      },
      _spaSwapBreadcrumbs(doc) {
        const next = doc.querySelector("nav.or-breadcrumbs");
        const cur = document.querySelector("nav.or-breadcrumbs");
        const main = document.querySelector("main.or-content");
        if (next && cur) {
          cur.replaceWith(next.cloneNode(true));
          return;
        }
        if (next && !cur && main) {
          main.insertAdjacentElement("beforebegin", next.cloneNode(true));
          return;
        }
        if (!next && cur) {
          cur.remove();
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
        if (this.collapsed) this.expandSidebarNav();
      },
      expandSidebarNav() {
        // Collapsed rail shows every link — force groups/subgroups open.
        this.$nextTick?.(() => {
          const root = this.$el?.querySelector?.(".or-sidebar") || document;
          root
            .querySelectorAll?.(
              ".or-nav-group-collapsible[x-data], .or-nav-accordion[x-data]"
            )
            ?.forEach((el) => {
              try {
                const data = window.Alpine?.$data?.(el);
                if (data && Object.prototype.hasOwnProperty.call(data, "open")) {
                  data.open = true;
                }
              } catch (_) {
                /* ignore */
              }
            });
        });
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
      sessionKey: null,
      init() {
        const el = this.$el;
        this.defer = el?.hasAttribute?.("data-defer-filters") || false;
        this.sessionKey = el?.getAttribute?.("data-filters-session") || null;
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
        if (this.sessionKey) {
          this._restoreSession();
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
      _storageKey() {
        return this.sessionKey ? `orbit-table-filters:${this.sessionKey}` : null;
      },
      _restoreSession() {
        const key = this._storageKey();
        if (!key) {
          return;
        }
        try {
          const raw = sessionStorage.getItem(key);
          if (!raw) {
            return;
          }
          const parsed = JSON.parse(raw);
          if (!parsed || typeof parsed !== "object") {
            return;
          }
          const wire = window.orbitWire?.(this.$el);
          const current = wire?.table_filters;
          const empty =
            !current ||
            (typeof current === "object" && Object.keys(current).length === 0);
          if (empty && wire && typeof wire.applyTableFilters === "function") {
            wire.applyTableFilters(parsed);
            this.pending = { ...parsed };
            this.activeCount = Object.keys(parsed).length;
          }
        } catch (_) {
          /* ignore */
        }
      },
      _persistSession(payload) {
        const key = this._storageKey();
        if (!key) {
          return;
        }
        try {
          sessionStorage.setItem(key, JSON.stringify(payload || {}));
        } catch (_) {
          /* ignore */
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
          if (payload[key] === "" || payload[key] == null || payload[key] === false) {
            delete payload[key];
          }
          if (Array.isArray(payload[key]) && payload[key].length === 0) {
            delete payload[key];
          }
        });
        if (wire && typeof wire.applyTableFilters === "function") {
          wire.applyTableFilters(payload);
        } else if (wire && typeof wire.$set === "function") {
          wire.$set("table_filters", payload);
        }
        this._persistSession(payload);
        this.activeCount = Object.keys(payload).length;
        this.filtersOpen = false;
      },
    }));

    window.Alpine.data("orbitColumnReorder", () => ({
      dragging: null,
      onDragStart(event) {
        const item = event.target?.closest?.("[data-column-name]");
        if (!item) {
          return;
        }
        this.dragging = item;
        event.dataTransfer.effectAllowed = "move";
        try {
          event.dataTransfer.setData("text/plain", item.dataset.columnName || "");
        } catch (_) {
          /* ignore */
        }
      },
      onDrop(event) {
        const list = this.$el;
        const target = event.target?.closest?.("[data-column-name]");
        if (!list || !this.dragging || !target || this.dragging === target) {
          this.dragging = null;
          return;
        }
        const rect = target.getBoundingClientRect();
        const before = event.clientY < rect.top + rect.height / 2;
        if (before) {
          list.insertBefore(this.dragging, target);
        } else {
          list.insertBefore(this.dragging, target.nextSibling);
        }
        this.dragging = null;
        const order = Array.from(list.querySelectorAll("[data-column-name]")).map(
          (el) => el.dataset.columnName,
        );
        const wire = typeof orbitWire === "function" ? orbitWire(list) : null;
        if (wire && typeof wire.reorderColumns === "function") {
          wire.reorderColumns(order);
        }
      },
    }));

    window.Alpine.data("orbitDropdown", () => ({
      menuOpen: false,
      init() {
        // Alpine rebinds `$el` to the event target inside @click handlers; keep the
        // x-data root so portal/querySelector always run against the dropdown wrap.
        this._rootEl = this.$el;
        this._menuPlaceholder = null;
        this._onCloseOthers = (event) => {
          if (event?.detail?.except === "dropdown") {
            return;
          }
          this.closeMenu();
        };
        window.addEventListener("orbit:close-dropdowns", this._onCloseOthers);
        // Portaled menus leave the Alpine root, so @click.outside alone is not enough.
        this._onDocPointer = (event) => {
          if (!this.menuOpen) {
            return;
          }
          const target = event.target;
          if (!(target instanceof Element)) {
            return;
          }
          const root = this._dropdownRoot();
          if (root?.contains(target) || this._menu?.contains(target)) {
            return;
          }
          this.closeMenu();
        };
        document.addEventListener("pointerdown", this._onDocPointer, true);
      },
      destroy() {
        this.closeMenu();
        if (this._onCloseOthers) {
          window.removeEventListener("orbit:close-dropdowns", this._onCloseOthers);
        }
        if (this._onDocPointer) {
          document.removeEventListener("pointerdown", this._onDocPointer, true);
        }
      },
      _dropdownRoot() {
        // Prefer Alpine's live `$root`. Cached `_rootEl` goes stale when Conduit
        // morphs the table; `$el` is the event target inside @click handlers.
        if (this.$root?.isConnected) {
          return this.$root;
        }
        if (this._rootEl?.isConnected) {
          return this._rootEl;
        }
        const el = this.$el;
        if (el?.isConnected && el.hasAttribute?.("x-data")) {
          return el;
        }
        return el?.closest?.("[data-dropdown], .or-dropdown, .or-table-columns") || el || null;
      },
      _selectionRoot() {
        return this._dropdownRoot()?.closest?.(".or-table-wrap, .or-list-card") || null;
      },
      syncSelection() {
        const root = this._selectionRoot();
        if (!root || typeof window.Alpine === "undefined") {
          return;
        }
        try {
          const stack = root._x_dataStack || [];
          const data =
            stack.find((entry) => typeof entry?.syncHost === "function") ||
            window.Alpine.$data(root);
          if (data && typeof data.syncHost === "function") {
            data.syncHost();
          }
        } catch (_) {
          /* selection root may not be Alpine-bound yet */
        }
      },
      _resolveParts() {
        const root = this._dropdownRoot();
        if (root && root !== this._rootEl) {
          this._rootEl = root;
        }
        // Prefer direct children; fall back after portal restore / nested markup.
        const menu =
          root?.querySelector?.(
            ":scope > .or-dropdown-menu, :scope > .or-columns-panel"
          ) || root?.querySelector?.(".or-dropdown-menu, .or-columns-panel");
        // Keep a previously portaled menu reference if it's still live on <body>.
        if (menu) {
          this._menu = menu;
        } else if (!this._menu?.isConnected) {
          this._menu = null;
        }
        const trigger =
          root?.querySelector?.(":scope > .or-btn, :scope > button") ||
          root?.querySelector?.(":scope > .or-icon-btn, :scope > .or-columns-trigger") ||
          root?.querySelector?.("button, .or-btn");
        if (trigger) {
          this._trigger = trigger;
        } else if (!this._trigger?.isConnected) {
          this._trigger = null;
        }
        return Boolean(this._menu && this._trigger);
      },
      _portalMenu() {
        const menu = this._menu;
        if (!menu || menu.parentElement === document.body) {
          return;
        }
        const hostEl =
          menu.closest?.("[wire\\:id], [conduit\\:id], [data-conduit-id]") ||
          this._dropdownRoot()?.closest?.(
            "[wire\\:id], [conduit\\:id], [data-conduit-id]"
          ) ||
          null;
        if (hostEl) {
          menu._orbitHostEl = hostEl;
        }
        this._menuPlaceholder = document.createComment("or-dropdown-portal");
        menu.parentNode?.insertBefore(this._menuPlaceholder, menu);
        document.body.appendChild(menu);
      },
      _restoreMenu() {
        const menu = this._menu;
        const placeholder = this._menuPlaceholder;
        if (menu && placeholder?.parentNode) {
          placeholder.parentNode.insertBefore(menu, placeholder);
          placeholder.remove();
        } else if (menu && menu.parentElement === document.body && this._rootEl?.isConnected) {
          this._rootEl.appendChild(menu);
        }
        this._menuPlaceholder = null;
      },
      _positionMenu(retries = 0) {
        if (!this.menuOpen || !this._resolveParts()) {
          return;
        }
        const menu = this._menu;
        const trigger = this._trigger;
        // Wait until Alpine x-show has made the panel measurable.
        if (getComputedStyle(menu).display === "none") {
          if (retries < 20) {
            requestAnimationFrame(() => this._positionMenu(retries + 1));
          }
          return;
        }
        this._portalMenu();
        menu.classList.add("or-dropdown-menu-fixed");
        menu.hidden = false;
        menu.style.display = "flex";
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
        if (!this._onReposition) {
          this._onReposition = () => {
            if (this.menuOpen) {
              this._positionMenu();
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
          menu.style.display = "";
        }
        this._restoreMenu();
        if (this._onReposition) {
          window.removeEventListener("scroll", this._onReposition, true);
          window.removeEventListener("resize", this._onReposition);
          this._onReposition = null;
        }
      },
      toggleMenu(event) {
        event?.preventDefault?.();
        event?.stopPropagation?.();
        if (this.menuOpen) {
          this.closeMenu();
          return;
        }
        this.menuOpen = true;
        window.dispatchEvent(
          new CustomEvent("orbit:close-dropdowns", { detail: { except: "dropdown" } })
        );
        // Position after x-show paints; rAF covers Conduit/Alpine timing.
        requestAnimationFrame(() => this._positionMenu());
        requestAnimationFrame(() =>
          requestAnimationFrame(() => this._positionMenu())
        );
      },
      closeMenu() {
        if (!this.menuOpen && !this._menuPlaceholder) {
          return;
        }
        this.menuOpen = false;
        this._clearMenuPosition();
      },
    }));

    window.Alpine.data("orbitTableSelection", () => ({
      selected: [],
      total: 0,
      allResultsSelected: false,
      init() {
        // Alpine rebinds `$el` inside nested @click handlers; keep the wrap.
        this._rootEl = this.$el;
        const boot = () => {
          const root = this._root();
          this._rootEl = root;
          const initial = root?.getAttribute?.("data-selected");
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
          const totalAttr = root?.getAttribute?.("data-total");
          if (totalAttr != null) {
            this.total = Number(totalAttr) || 0;
          }
          if (root?.getAttribute?.("data-select-all") === "true") {
            this.allResultsSelected = true;
          }
          if (this._onSelectAllChange && this._boundSelectRoot) {
            this._boundSelectRoot.removeEventListener("change", this._onSelectAllChange);
          }
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
          this._boundSelectRoot = root;
          root?.addEventListener("change", this._onSelectAllChange);
          this._syncHeaderCheck();
          if (this._onBulkActionClick && this._boundBulkRoot) {
            this._boundBulkRoot.removeEventListener("click", this._onBulkActionClick, true);
          }
          // Sync to host immediately before a bulk action Conduit call (capture phase).
          this._onBulkActionClick = (event) => {
            const target = event.target;
            if (!(target instanceof Element)) {
              return;
            }
            const inBulkUi =
              target.closest(".or-table-bulk-trigger, .or-list-bulk-actions") ||
              (target.closest(".or-dropdown-menu") &&
                /delete_bulk|bulk/i.test(
                  target.closest("[data-action]")?.getAttribute("data-action") || ""
                ));
            if (!inBulkUi) {
              return;
            }
            if (target.closest("[wire\\:click], [conduit\\:click], [data-action]")) {
              this.syncHost();
            }
          };
          this._boundBulkRoot = document;
          document.addEventListener("click", this._onBulkActionClick, true);
        };
        boot();
        this.$nextTick?.(() => boot());
      },
      destroy() {
        if (this._onSelectAllChange && this._boundSelectRoot) {
          this._boundSelectRoot.removeEventListener("change", this._onSelectAllChange);
        }
        if (this._onBulkActionClick && this._boundBulkRoot) {
          this._boundBulkRoot.removeEventListener("click", this._onBulkActionClick, true);
        }
      },
      _root() {
        const live = this.$root || this.$el;
        if (live?.classList?.contains("or-table-wrap")) {
          return live;
        }
        if (this._rootEl?.isConnected && this._rootEl.classList?.contains("or-table-wrap")) {
          return this._rootEl;
        }
        return (
          live?.closest?.(".or-table-wrap") ||
          this._rootEl?.closest?.(".or-table-wrap") ||
          this._rootEl ||
          live
        );
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
      notifications: [],
      _timers: {},
      init() {
        const seed = Array.from(this.$el.querySelectorAll(".or-notification[data-id]"));
        seed.forEach((el) => {
          const id = el.getAttribute("data-id");
          if (!id) return;
          this.notifications.push({
            id,
            title: el.querySelector(".or-notification-title")?.textContent || "",
            body: el.querySelector(".or-notification-body")?.textContent || "",
            status: (el.className.match(/or-notification-(success|warning|danger|info)/) || [])[1] || "info",
            duration: Number(el.getAttribute("data-duration")) || 6000,
            persistent: el.getAttribute("data-persistent") === "true",
            html: el.outerHTML,
          });
          el.remove();
        });
        this.notifications.forEach((n) => this._schedule(n));

        const onNotify = (event) => {
          const detail = event.detail || {};
          this.push(detail);
        };
        const onClose = (event) => {
          const id = event.detail?.id;
          if (id) this.dismiss(id);
        };
        window.addEventListener("orbit:notify", onNotify);
        window.addEventListener("close-notification", onClose);
        this.$el.addEventListener("close-notification", onClose);
        this._cleanup = () => {
          window.removeEventListener("orbit:notify", onNotify);
          window.removeEventListener("close-notification", onClose);
        };
      },
      destroy() {
        this._cleanup?.();
        Object.values(this._timers).forEach((t) => clearTimeout(t));
      },
      push(detail) {
        const id = detail.id || `n-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        const item = {
          id,
          title: detail.title || "",
          body: detail.body || "",
          status: detail.status || "info",
          icon: detail.icon || "",
          iconColor: detail.iconColor || detail.icon_color || detail.status || "info",
          color: detail.color || detail.status || "",
          duration: detail.persistent ? 0 : Number(detail.duration ?? 6000),
          persistent: Boolean(detail.persistent),
          actions: detail.actions || [],
        };
        this.notifications = [...this.notifications.filter((n) => n.id !== id), item];
        this._schedule(item);
      },
      dismiss(id) {
        if (this._timers[id]) {
          clearTimeout(this._timers[id]);
          delete this._timers[id];
        }
        this.notifications = this.notifications.filter((n) => n.id !== id);
      },
      _schedule(item) {
        if (item.persistent || !item.duration) return;
        if (this._timers[item.id]) clearTimeout(this._timers[item.id]);
        this._timers[item.id] = setTimeout(() => this.dismiss(item.id), item.duration);
      },
      runAction(notificationId, action) {
        if (action?.url) {
          if (action.openUrlInNewTab || action.open_url_in_new_tab) {
            window.open(action.url, "_blank", "noopener,noreferrer");
          } else {
            window.location.href = action.url;
          }
        }
        if (action?.dispatch) {
          window.dispatchEvent(
            new CustomEvent(action.dispatch, { detail: action.dispatchPayload || action.dispatch_payload || [] })
          );
        }
        if (action?.close) this.dismiss(notificationId);
      },
    }));

    window.Alpine.data("orbitLiveNotifications", () => ({
      channels: [],
      cursor: 0,
      _pollTimer: null,
      init() {
        const raw = this.$el.getAttribute("data-channels") || "";
        this.channels = raw
          .split(",")
          .map((c) => c.trim())
          .filter(Boolean);
        this.cursor = Number(this.$el.getAttribute("data-cursor") || 0) || 0;
        window.addEventListener("orbit:broadcast", (event) => {
          const detail = event.detail || {};
          const channel = detail.channel;
          if (channel && this.channels.length && !this.channels.includes(channel)) {
            return;
          }
          window.dispatchEvent(new CustomEvent("orbit:notify", { detail }));
        });
        const url = this.$el.getAttribute("data-orbit-live-url") || "";
        const polling = Number(this.$el.getAttribute("data-polling") || 0);
        if (url && polling > 0) {
          this.pollLive(url);
          this._pollTimer = setInterval(() => this.pollLive(url), polling);
        }
      },
      destroy() {
        if (this._pollTimer) clearInterval(this._pollTimer);
      },
      async pollLive(url) {
        try {
          const sep = url.includes("?") ? "&" : "?";
          const res = await fetch(`${url}${sep}since=${this.cursor}`, {
            headers: { Accept: "application/json" },
            credentials: "same-origin",
          });
          if (!res.ok) return;
          const data = await res.json();
          const events = Array.isArray(data.events) ? data.events : [];
          if (typeof data.cursor === "number") this.cursor = data.cursor;
          else this.cursor += events.length;
          for (const detail of events) {
            window.dispatchEvent(new CustomEvent("orbit:broadcast", { detail }));
          }
        } catch (_) {}
      },
    }));

    window.Alpine.data("orbitDatabaseNotifications", () => ({
      open: false,
      deckOpen: false,
      detailOpen: false,
      selected: null,
      detailTitleId: "or-notify-detail-title",
      notifications: [],
      unreadList: [],
      deckList: [],
      deckPageSize: 20,
      deckVisibleCount: 20,
      _pollTimer: null,
      get unreadCount() {
        return this.unreadList.length;
      },
      get deckHasMore() {
        return this.deckVisibleCount < this.notifications.length;
      },
      init() {
        try {
          const raw = this.$el.getAttribute("data-notifications") || "[]";
          this.notifications = this._sortLatest(JSON.parse(raw));
        } catch (_) {
          this.notifications = [];
        }
        this._syncLists();
        // Keep list mirrors in sync — Alpine x-for is more reliable on
        // plain arrays than on filtered getters after poll()/init().
        this.$watch("notifications", () => this._syncLists());
        this.$watch("deckVisibleCount", () => this._syncLists());
        const polling = Number(this.$el.getAttribute("data-polling") || 0);
        if (polling > 0) {
          this._pollTimer = setInterval(() => this.poll(), polling);
        }
        window.addEventListener("orbit:database-notifications-refresh", () => this.poll());
        window.addEventListener("open-modal", (event) => {
          if (event.detail?.id === "database-notifications") this.openDeck();
        });
      },
      destroy() {
        if (this._pollTimer) clearInterval(this._pollTimer);
      },
      _isRead(note) {
        const value = note?.read;
        return value === true || value === 1 || value === "1" || value === "true";
      },
      _syncLists() {
        const list = Array.isArray(this.notifications) ? this.notifications : [];
        this.unreadList = list.filter((n) => !this._isRead(n));
        this.deckList = list.slice(0, this.deckVisibleCount);
      },
      toggle() {
        this.open = !this.open;
        if (this.open) this.deckOpen = false;
      },
      openDeck() {
        this.open = false;
        this.deckVisibleCount = this.deckPageSize;
        this.deckOpen = true;
        this._syncLists();
        this.$nextTick?.(() => {
          const list = this.$refs?.deckList;
          if (list) list.scrollTop = 0;
        });
      },
      closeDeck() {
        this.deckOpen = false;
      },
      onDeckScroll(event) {
        const el = event?.target;
        if (!el || !this.deckHasMore) return;
        const remaining = el.scrollHeight - el.scrollTop - el.clientHeight;
        if (remaining < 120) this.loadMoreDeck();
      },
      loadMoreDeck() {
        if (!this.deckHasMore) return;
        this.deckVisibleCount = Math.min(
          this.notifications.length,
          this.deckVisibleCount + this.deckPageSize
        );
      },
      openDetail(note) {
        if (!note) return;
        this.selected = { ...note };
        this.detailOpen = true;
        this.open = false;
        if (!this._isRead(note)) this.markRead(note.id);
      },
      closeDetail() {
        this.detailOpen = false;
        this.selected = null;
      },
      onEscape() {
        if (this.detailOpen) {
          this.closeDetail();
          return;
        }
        if (this.deckOpen) {
          this.closeDeck();
          return;
        }
        this.open = false;
      },
      formatTime(value) {
        if (!value) return "";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return String(value);
        const diffMs = Date.now() - date.getTime();
        const sec = Math.round(diffMs / 1000);
        if (sec < 45) return "just now";
        const min = Math.round(sec / 60);
        if (min < 60) return `${min}m ago`;
        const hr = Math.round(min / 60);
        if (hr < 24) return `${hr}h ago`;
        const day = Math.round(hr / 24);
        if (day < 7) return `${day}d ago`;
        try {
          return date.toLocaleString(undefined, {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          });
        } catch (_) {
          return date.toISOString();
        }
      },
      _sortLatest(list) {
        if (!Array.isArray(list)) return [];
        return [...list].sort((a, b) => {
          const ac = String(a?.created_at || "");
          const bc = String(b?.created_at || "");
          if (ac === bc) return String(b?.id || "").localeCompare(String(a?.id || ""));
          return bc.localeCompare(ac);
        });
      },
      markRead(id) {
        this.notifications = this.notifications.map((n) =>
          n.id === id ? { ...n, read: true } : n
        );
        if (this.selected?.id === id) this.selected = { ...this.selected, read: true };
        this._syncLists();
        this._sync({ id, read: true });
      },
      markUnread(id) {
        this.notifications = this.notifications.map((n) =>
          n.id === id ? { ...n, read: false } : n
        );
        if (this.selected?.id === id) this.selected = { ...this.selected, read: false };
        this._syncLists();
        this._sync({ id, read: false });
      },
      markAllRead() {
        this.notifications = this.notifications.map((n) => ({ ...n, read: true }));
        if (this.selected) this.selected = { ...this.selected, read: true };
        this._syncLists();
        this._sync({ all: true });
      },
      async _sync(payload) {
        const url = this.$el.getAttribute("data-orbit-notifications-url");
        if (!url) return;
        try {
          await fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
              "Content-Type": "application/json",
              Accept: "application/json",
            },
            body: JSON.stringify(payload),
          });
        } catch (_) {}
      },
      async poll() {
        const url = this.$el.getAttribute("data-orbit-notifications-url");
        if (url) {
          try {
            const res = await fetch(url, {
              credentials: "same-origin",
              headers: { Accept: "application/json" },
            });
            if (res.ok) {
              const data = await res.json();
              if (Array.isArray(data.notifications)) {
                this.notifications = this._sortLatest(data.notifications);
                if (this.deckVisibleCount > this.notifications.length) {
                  this.deckVisibleCount = Math.max(
                    this.deckPageSize,
                    this.notifications.length
                  );
                }
                this._syncLists();
              }
            }
          } catch (_) {}
        }
        window.dispatchEvent(
          new CustomEvent("orbit:database-notifications-poll", {
            detail: { notifications: this.notifications },
          })
        );
      },
    }));

    // Filament-style JS client
    class OrbitNotificationAction {
      constructor(name) {
        this._name = name || "action";
        this._label = null;
        this._button = false;
        this._url = null;
        this._openUrlInNewTab = false;
        this._dispatch = null;
        this._dispatchPayload = [];
        this._close = false;
        this._color = null;
      }
      button(v = true) {
        this._button = Boolean(v);
        return this;
      }
      label(v) {
        this._label = v;
        return this;
      }
      url(v) {
        this._url = v;
        return this;
      }
      openUrlInNewTab(v = true) {
        this._openUrlInNewTab = Boolean(v);
        return this;
      }
      dispatch(event, payload = []) {
        this._dispatch = event;
        this._dispatchPayload = payload;
        return this;
      }
      close(v = true) {
        this._close = Boolean(v);
        return this;
      }
      color(v) {
        this._color = v;
        return this;
      }
      toJSON() {
        return {
          name: this._name,
          label: this._label || this._name,
          button: this._button,
          url: this._url,
          openUrlInNewTab: this._openUrlInNewTab,
          dispatch: this._dispatch,
          dispatchPayload: this._dispatchPayload,
          close: this._close,
          color: this._color,
        };
      }
    }

    class OrbitNotification {
      constructor(id) {
        this._id = id || null;
        this._title = "";
        this._body = "";
        this._status = "info";
        this._icon = null;
        this._iconColor = null;
        this._color = null;
        this._duration = 6000;
        this._persistent = false;
        this._actions = [];
      }
      title(v) {
        this._title = v;
        return this;
      }
      body(v) {
        this._body = v;
        return this;
      }
      icon(v) {
        this._icon = v;
        return this;
      }
      iconColor(v) {
        this._iconColor = v;
        return this;
      }
      color(v) {
        this._color = v;
        return this;
      }
      status(v) {
        this._status = v;
        return this;
      }
      success() {
        return this.status("success");
      }
      warning() {
        return this.status("warning");
      }
      danger() {
        return this.status("danger");
      }
      info() {
        return this.status("info");
      }
      duration(ms) {
        this._duration = Number(ms);
        return this;
      }
      seconds(n) {
        this._duration = Number(n) * 1000;
        return this;
      }
      persistent(v = true) {
        this._persistent = Boolean(v);
        return this;
      }
      actions(list) {
        this._actions = (list || []).map((a) =>
          a && typeof a.toJSON === "function" ? a.toJSON() : a
        );
        return this;
      }
      getId() {
        return this._id;
      }
      send() {
        const id = this._id || `n-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        this._id = id;
        window.dispatchEvent(
          new CustomEvent("orbit:notify", {
            detail: {
              id,
              title: this._title,
              body: this._body,
              status: this._status,
              icon: this._icon,
              iconColor: this._iconColor,
              color: this._color,
              duration: this._duration,
              persistent: this._persistent,
              actions: this._actions,
            },
          })
        );
        return this;
      }
    }

    window.OrbitNotification = OrbitNotification;
    window.OrbitNotificationAction = OrbitNotificationAction;

    const toastFromActionEl = (el) => {
      if (!(el instanceof HTMLElement)) return;
      if (!el.hasAttribute("data-success-notification")) return;
      const body = el.getAttribute("data-success-notification");
      if (body === "") return; // explicitly disabled
      const title = el.getAttribute("data-success-notification-title") || body || "Success";
      const note = new OrbitNotification().title(title).success();
      if (body && body !== title) note.body(body);
      note.send();
    };

    const toastFailureFromActionEl = (el) => {
      if (!(el instanceof HTMLElement)) return;
      if (!el.hasAttribute("data-failure-notification")) return;
      const body = el.getAttribute("data-failure-notification");
      if (!body) return;
      const title = el.getAttribute("data-failure-notification-title") || body || "Error";
      const note = new OrbitNotification().title(title).danger();
      if (body && body !== title) note.body(body);
      note.send();
    };

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
      slideOverPosition: "right",
      modalWidth: "md",
      stickyHeader: false,
      stickyFooter: false,
      closeOnEscape: true,
      closeOnClickAway: true,
      showCloseButton: true,
      modalIcon: "",
      modalIconColor: "",
      modalIconHtml: "",
      modalAlignment: "start",
      modalAutofocus: true,
      submitLabel: "Confirm",
      cancelLabel: "Cancel",
      get confirmOnly() {
        return this.needsConfirm && !this.hasForm;
      },
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
          this.slideOverPosition = detail.slideOverPosition || "right";
          this.modalWidth = detail.modalWidth || "md";
          this.stickyHeader = Boolean(detail.stickyHeader);
          this.stickyFooter = Boolean(detail.stickyFooter);
          this.closeOnEscape = detail.closeOnEscape !== false;
          this.closeOnClickAway = detail.closeOnClickAway !== false;
          this.showCloseButton = detail.showCloseButton !== false;
          this.modalIcon = detail.modalIcon || "";
          this.modalIconColor = detail.modalIconColor || "";
          this.modalIconHtml = detail.modalIconHtml || "";
          this.modalAlignment = detail.modalAlignment || "start";
          this.modalAutofocus = detail.modalAutofocus !== false;
          this.submitLabel =
            detail.submitLabel ||
            (this.hasForm ? (this.needsConfirm ? "Confirm" : "Save") : "Confirm");
          this.cancelLabel = detail.cancelLabel || "Cancel";
          this.open = true;
          if (this.modalAutofocus) {
            this.$nextTick?.(() => {
              const root = this.$refs.actionForm || this.$el;
              const focusable = root?.querySelector?.(
                "input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button.or-btn-primary",
              );
              focusable?.focus?.();
            });
          }
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
        // Portaled bulk menus live on <body>; sync Alpine selection before delete_bulk.
        try {
          const wrap = document.querySelector(".or-table-wrap[x-data]");
          const stack = wrap?._x_dataStack || [];
          const sel =
            stack.find((entry) => typeof entry?.syncHost === "function") || null;
          sel?.syncHost?.();
        } catch (_) {
          /* ignore */
        }
        const el = this.pendingEl;
        const wire = el ? window.orbitWire?.(el) : null;
        if (wire && typeof wire.mountAction === "function") {
          wire.mountAction(payload.name, payload.recordId || null, { data: payload.data });
        } else if (wire && typeof wire.$call === "function") {
          wire.$call("mountAction", payload.name, payload.recordId || null, { data: payload.data });
        }
        this.$dispatch("orbit:action-confirmed", payload);
        toastFromActionEl(el);
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
        if (btn.hasAttribute("disabled") || btn.classList.contains("or-btn-disabled")) {
          return;
        }
        const needsConfirm = btn.getAttribute("data-confirm") === "true";
        const hasForm = btn.getAttribute("data-has-form") === "true";
        // Immediate actions (no modal): toast success notification after click.
        if (!needsConfirm && !hasForm && btn.hasAttribute("data-success-notification")) {
          queueMicrotask(() => toastFromActionEl(btn));
        }
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
        const iconName = btn.getAttribute("data-modal-icon") || "";
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
              slideOverPosition: btn.getAttribute("data-slide-over-position") || "right",
              modalWidth: btn.getAttribute("data-modal-width") || "md",
              stickyHeader: btn.getAttribute("data-sticky-header") === "true",
              stickyFooter: btn.getAttribute("data-sticky-footer") === "true",
              closeOnEscape: btn.getAttribute("data-close-on-escape") !== "false",
              closeOnClickAway: btn.getAttribute("data-close-on-click-away") !== "false",
              showCloseButton: btn.getAttribute("data-modal-close-button") !== "false",
              modalIcon: iconName,
              modalIconColor: btn.getAttribute("data-modal-icon-color") || "",
              modalIconHtml: "",
              modalAlignment: btn.getAttribute("data-modal-alignment") || "start",
              modalAutofocus: btn.getAttribute("data-modal-autofocus") !== "false",
              submitLabel: btn.getAttribute("data-modal-submit-label") || "",
              cancelLabel: btn.getAttribute("data-modal-cancel-label") || "",
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

    const orbitCombobox = () => ({
      open: false,
      q: "",
      options: [],
      state: null,
      activeIndex: -1,
      searching: false,
      multiple: false,
      searchable: false,
      ajax: false,
      allowHtml: false,
      wrapLabels: false,
      disabled: false,
      placeholder: "—",
      searchPrompt: "Search…",
      noResults: "No options match your search.",
      searchingMsg: "Searching…",
      loadingMsg: "Loading…",
      maxItems: null,
      fieldName: "",

      init() {
        const root = this.$el;
        this.multiple = root.getAttribute("data-multiple") === "true";
        this.searchable = root.hasAttribute("data-searchable");
        this.ajax = root.getAttribute("data-ajax-search") === "true";
        this.allowHtml = root.getAttribute("data-allow-html") === "true";
        this.wrapLabels = root.hasAttribute("data-wrap-labels");
        this.placeholder = root.getAttribute("data-placeholder") || "—";
        this.searchPrompt = root.getAttribute("data-search-prompt") || "Search…";
        this.noResults = root.getAttribute("data-no-results") || this.noResults;
        this.searchingMsg = root.getAttribute("data-searching") || this.searchingMsg;
        this.loadingMsg = root.getAttribute("data-loading") || this.loadingMsg;
        const max = root.getAttribute("data-max-items");
        this.maxItems = max != null && max !== "" ? Number(max) : null;
        this.fieldName =
          root.closest("[data-field]")?.getAttribute("data-field") ||
          root.getAttribute("data-field") ||
          "";
        const search = this.$refs.search;
        if (search instanceof HTMLInputElement && search.value) {
          this.q = search.value;
        }
        this.readFromSelect();
        this.$watch("open", (value) => {
          if (value) {
            this.$nextTick(() => {
              if (this.searchable && this.$refs.search) this.$refs.search.focus();
            });
          }
        });
      },

      get selectedItems() {
        return this.selectedValues.map((value) => {
          const opt = this.options.find((o) => o.value === value);
          return {
            value,
            label: opt ? opt.label : value,
            labelHtml: opt ? opt.labelHtml : value,
          };
        });
      },

      get selectedValues() {
        if (this.multiple) {
          return Array.isArray(this.state) ? this.state.map(String) : [];
        }
        return this.state != null && this.state !== "" ? [String(this.state)] : [];
      },

      get selectedLabel() {
        if (this.multiple) return "";
        const item = this.selectedItems[0];
        return item ? item.label : "";
      },

      get hasValue() {
        return this.selectedValues.length > 0;
      },

      get visibleOptions() {
        const opts = this.options.filter((o) => o.value !== "");
        if (this.ajax || !this.searchable) return opts;
        const needle = (this.q || "").toLowerCase().trim();
        if (!needle) return opts;
        return opts.filter(
          (o) =>
            o.label.toLowerCase().includes(needle) ||
            o.value.toLowerCase().includes(needle),
        );
      },

      get statusMessage() {
        if (this.searching) {
          return this.ajax ? this.searchingMsg : this.loadingMsg;
        }
        if (this.open && this.visibleOptions.length === 0) {
          return this.noResults;
        }
        return "";
      },

      get activeId() {
        if (this.activeIndex < 0 || !this.fieldName) return null;
        return `or-${this.fieldName}-opt-${this.activeIndex}`;
      },

      readFromSelect() {
        const select = this.$refs.select;
        if (!(select instanceof HTMLSelectElement)) return;
        this.disabled = select.disabled;
        this.options = Array.from(select.options).map((opt) => ({
          value: String(opt.value),
          label: String(opt.dataset.label || opt.textContent || "").trim(),
          labelHtml: opt.innerHTML,
          disabled: Boolean(opt.disabled),
          group: opt.dataset.group || "",
        }));
        if (this.multiple) {
          this.state = Array.from(select.selectedOptions)
            .map((o) => String(o.value))
            .filter((v) => v !== "");
        } else {
          this.state = select.value || "";
        }
      },

      isSelected(value) {
        return this.selectedValues.includes(String(value));
      },

      toggle() {
        if (this.disabled) return;
        if (this.open) this.close();
        else this.openPanel();
      },

      openPanel() {
        if (this.disabled) return;
        this.open = true;
        this.activeIndex = this.visibleOptions.findIndex((o) => this.isSelected(o.value));
        if (this.activeIndex < 0 && this.visibleOptions.length) this.activeIndex = 0;
      },

      close() {
        this.open = false;
        this.activeIndex = -1;
        if (!this.multiple) this.q = "";
      },

      move(delta) {
        this.openPanel();
        const len = this.visibleOptions.length;
        if (!len) return;
        this.activeIndex = (this.activeIndex + delta + len) % len;
        const el = this.activeId ? document.getElementById(this.activeId) : null;
        if (el) el.scrollIntoView({ block: "nearest" });
      },

      chooseActive() {
        const opt = this.visibleOptions[this.activeIndex];
        if (opt) this.choose(opt);
      },

      choose(opt) {
        if (!opt || opt.disabled) return;
        if (this.multiple) {
          const value = String(opt.value);
          const current = [...this.selectedValues];
          const idx = current.indexOf(value);
          if (idx >= 0) current.splice(idx, 1);
          else {
            if (this.maxItems != null && current.length >= this.maxItems) return;
            current.push(value);
          }
          this.state = current;
          this.q = "";
          this.syncSelect();
          return;
        }
        this.state = String(opt.value);
        this.syncSelect();
        this.close();
      },

      deselect(value) {
        if (!this.multiple) return;
        this.state = this.selectedValues.filter((v) => v !== String(value));
        this.syncSelect();
      },

      clear() {
        this.state = this.multiple ? [] : "";
        this.q = "";
        this.syncSelect();
        this.close();
      },

      onBackspace(event) {
        if (!this.multiple) return;
        if ((this.q || "") !== "") return;
        const values = this.selectedValues;
        if (!values.length) return;
        event.preventDefault();
        this.deselect(values[values.length - 1]);
      },

      onSearch() {
        if (this.ajax) {
          this.searching = true;
          const wireRoot = this.$el.closest(
            "[wire\\:id], [conduit\\:id], [data-conduit]",
          );
          const wire = wireRoot && (wireRoot.__wire || wireRoot.__conduit);
          if (wire && typeof wire.searchSelectOptions === "function") {
            wire.searchSelectOptions(this.fieldName, this.q || "");
            return;
          }
          this.searching = false;
        }
        this.openPanel();
        this.activeIndex = this.visibleOptions.length ? 0 : -1;
      },

      syncSelect() {
        const select = this.$refs.select;
        if (!(select instanceof HTMLSelectElement)) return;
        if (this.multiple) {
          const selected = new Set(this.selectedValues);
          Array.from(select.options).forEach((opt) => {
            opt.selected = selected.has(String(opt.value));
          });
        } else {
          select.value = this.state == null ? "" : String(this.state);
        }
        select.dispatchEvent(new Event("input", { bubbles: true }));
        select.dispatchEvent(new Event("change", { bubbles: true }));
      },
    });

    window.Alpine.data("orbitCombobox", orbitCombobox);
    window.Alpine.data("orbitSearchableSelect", orbitCombobox);


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

    const parseJsonAttr = (el, name) => {
      const raw = el.getAttribute(name);
      if (!raw) return null;
      try {
        return JSON.parse(raw);
      } catch (_) {
        return null;
      }
    };

    const chartCssColor = (token) => {
      try {
        const styles = getComputedStyle(document.documentElement);
        return (
          styles.getPropertyValue(`--or-chart-${token}`).trim() ||
          styles.getPropertyValue(`--or-${token}`).trim() ||
          styles.getPropertyValue("--or-primary").trim() ||
          "#f1511b"
        );
      } catch (_) {
        return "#f1511b";
      }
    };

    const chartThemeTokens = () => ["primary", "success", "warning", "info", "danger"];

    const chartThemePalette = () => chartThemeTokens().map((token) => chartCssColor(token));

    const chartTokenFromEl = (el) => {
      const match = [...(el?.classList || [])].find((c) => c.startsWith("or-color-"));
      return match ? match.slice("or-color-".length) : "primary";
    };

    const chartColorWithAlpha = (color, alpha) => {
      const raw = String(color || "").trim();
      if (/^#([0-9a-f]{6})$/i.test(raw)) {
        const hex = raw.slice(1);
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
      }
      if (/^#([0-9a-f]{3})$/i.test(raw)) {
        const hex = raw.slice(1);
        const r = parseInt(hex[0] + hex[0], 16);
        const g = parseInt(hex[1] + hex[1], 16);
        const b = parseInt(hex[2] + hex[2], 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
      }
      const rgb = raw.match(
        /^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?\s*\)$/i,
      );
      if (rgb) {
        return `rgba(${rgb[1]}, ${rgb[2]}, ${rgb[3]}, ${alpha})`;
      }
      return raw;
    };

    const applyThemeToChartJsDatasets = (type, datasets, accent, palette) => {
      const series = Array.isArray(datasets) ? datasets : [];
      return series.map((ds, index) => {
        const next = { ...ds };
        const seriesColor = palette[index % palette.length] || accent;
        const pointCount = Array.isArray(next.data) ? next.data.length : 0;
        const multiPoint =
          series.length === 1 &&
          pointCount > 1 &&
          (type === "bar" || type === "pie" || type === "doughnut" || type === "polarArea");

        if (multiPoint) {
          if (next.backgroundColor == null) {
            next.backgroundColor = Array.from(
              { length: pointCount },
              (_, i) => palette[i % palette.length] || seriesColor,
            );
          }
          if (next.borderColor == null) {
            next.borderColor = Array.isArray(next.backgroundColor)
              ? next.backgroundColor
              : seriesColor;
          }
          if (next.borderWidth == null) next.borderWidth = 1;
          return next;
        }

        if (next.borderColor == null) next.borderColor = seriesColor;
        if (next.backgroundColor == null) {
          next.backgroundColor =
            type === "line" || type === "radar"
              ? chartColorWithAlpha(seriesColor, 0.18)
              : seriesColor;
        }
        if (next.fill == null && (type === "line" || type === "radar")) next.fill = true;
        if (next.tension == null && type === "line") next.tension = 0.35;
        return next;
      });
    };

    const applyThemeToApexOptions = (options, accent, palette) => {
      const next = { ...options };
      if (!next.colors || !next.colors.length) {
        next.colors = palette.length ? palette : [accent];
      }
      if (!next.stroke) next.stroke = {};
      if (next.stroke.curve == null) next.stroke.curve = "smooth";
      if (!next.fill) next.fill = {};
      if (next.fill.type == null && (next.chart?.type === "area" || next.chart?.type === "line")) {
        next.fill.type = "gradient";
        next.fill.gradient = {
          shadeIntensity: 0.35,
          opacityFrom: 0.45,
          opacityTo: 0.05,
          stops: [0, 90, 100],
          ...(next.fill.gradient || {}),
        };
      }
      return next;
    };

    window.Alpine.data("orbitChart", () => ({
      chart: null,
      init() {
        const el = this.$el;
        const library = (el.getAttribute("data-chart-library") || "chartjs").toLowerCase();
        const payload = parseJsonAttr(el, "data-chart");
        if (!payload) return;
        const token = chartTokenFromEl(el);
        const accent = chartCssColor(token);
        const palette = chartThemePalette();

        if (library === "apex") {
          if (typeof window.ApexCharts === "undefined") return;
          const options = applyThemeToApexOptions({ ...payload }, accent, palette);
          if (!options.chart) options.chart = {};
          options.chart.height = options.chart.height || el.style.maxHeight || 300;
          this.chart = new window.ApexCharts(el, options);
          this.chart.render();
          return;
        }

        if (typeof window.Chart === "undefined") return;
        let canvas = el.querySelector("canvas");
        if (!canvas) {
          canvas = document.createElement("canvas");
          el.appendChild(canvas);
        }
        const type = payload.type || "line";
        const data = {
          labels: payload.labels || [],
          datasets: applyThemeToChartJsDatasets(
            type,
            payload.datasets || [],
            accent,
            palette,
          ),
        };
        this.chart = new window.Chart(canvas.getContext("2d"), {
          type,
          data,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            ...(payload.options || {}),
          },
        });
      },
      destroy() {
        if (this.chart && typeof this.chart.destroy === "function") {
          this.chart.destroy();
        }
        this.chart = null;
      },
    }));

    window.Alpine.data("orbitSparkline", () => ({
      chart: null,
      init() {
        const el = this.$el;
        if (typeof window.Chart === "undefined") return;
        const payload = parseJsonAttr(el, "data-sparkline") || {};
        const values = payload.values || [];
        if (!values.length) return;

        let canvas = el.querySelector("canvas");
        if (!canvas) {
          canvas = document.createElement("canvas");
          el.appendChild(canvas);
        }

        const borderEl = el.querySelector(".or-stat-chart-border");
        const bgEl = el.querySelector(".or-stat-chart-bg");
        const fallback = chartCssColor(payload.color || "primary");
        let borderColor = fallback;
        let fillBase = chartColorWithAlpha(fallback, 0.35);
        try {
          if (borderEl) {
            const c = getComputedStyle(borderEl).color;
            if (c && c !== "rgba(0, 0, 0, 0)") borderColor = c;
          }
          if (bgEl) {
            const c = getComputedStyle(bgEl).color;
            if (c && c !== "rgba(0, 0, 0, 0)") fillBase = c;
          }
        } catch (_) {
          /* ignore */
        }

        const styles = getComputedStyle(el.closest(".or-stat") || el);
        const readNum = (name, fallbackVal) => {
          const raw = styles.getPropertyValue(name).trim();
          const n = Number(raw);
          return Number.isFinite(n) ? n : fallbackVal;
        };
        const fillMode = (styles.getPropertyValue("--or-stat-chart-fill").trim() || "start").toLowerCase();
        const fill =
          fillMode === "none" || fillMode === "false" ? false : fillMode === "origin" ? "origin" : "start";
        const tension = readNum("--or-stat-chart-line-tension", 0.4);
        const borderWidth = readNum("--or-stat-chart-border-width", 2);

        const ctx = canvas.getContext("2d");
        const height = el.clientHeight || 60;
        let backgroundColor = fillBase;
        if (fill && ctx) {
          const gradient = ctx.createLinearGradient(0, 0, 0, height);
          gradient.addColorStop(0, fillBase);
          gradient.addColorStop(1, chartColorWithAlpha(borderColor, 0));
          backgroundColor = gradient;
        }

        this.chart = new window.Chart(ctx, {
          type: "line",
          data: {
            labels: values.map((_, i) => String(i)),
            datasets: [
              {
                data: values,
                borderColor,
                backgroundColor,
                fill,
                tension,
                pointRadius: 0,
                borderWidth,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            layout: { padding: 0 },
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
            scales: {
              x: { display: false, grid: { display: false }, border: { display: false } },
              y: {
                display: false,
                grid: { display: false },
                border: { display: false },
                // Leave a little headroom so the stroke isn't clipped at the top.
                suggestedMin: Math.min(...values) * 0.92,
                suggestedMax: Math.max(...values) * 1.05,
              },
            },
            elements: { line: { borderJoinStyle: "round", borderCapStyle: "round" } },
          },
        });
      },
      destroy() {
        if (this.chart && typeof this.chart.destroy === "function") {
          this.chart.destroy();
        }
        this.chart = null;
      },
    }));

    const parseJsonDataset = (el, key, fallback) => {
      try {
        const raw = el?.getAttribute?.(`data-${key}`);
        if (!raw) return fallback;
        return JSON.parse(raw);
      } catch (_) {
        return fallback;
      }
    };

    const syncWirePath = (el, path, value) => {
      if (!path) return;
      const wire = window.orbitWire?.(el);
      if (!wire) return;
      // Prefer renderless host sync — `$set` remorphs the form and can wipe Alpine
      // state inside TagsInput / CheckboxList even with wire:ignore.
      if (typeof wire.sync_data_path === "function") {
        wire.sync_data_path(path, value);
        return;
      }
      if (typeof wire.$set === "function") {
        wire.$set(path, value);
        return;
      }
      if (typeof wire.set === "function") {
        wire.set(path, value);
      }
    };

    // Before Conduit submit, flush Alpine list fields so Save sees latest chips/checks
    // even if a coalesce timer hasn't fired yet.
    if (typeof document !== "undefined" && !window.__orbitAlpineFormFlush) {
      window.__orbitAlpineFormFlush = true;
      document.addEventListener(
        "submit",
        (event) => {
          const form = event.target;
          if (!(form instanceof HTMLFormElement)) return;
          const hasSubmit =
            form.hasAttribute("conduit:submit") || form.hasAttribute("wire:submit");
          if (!hasSubmit) return;
          form
            .querySelectorAll(".or-field-TagsInput, .or-field-CheckboxList")
            .forEach((root) => {
              try {
                const data = window.Alpine?.$data?.(root);
                if (data && typeof data.sync === "function") data.sync();
              } catch (_) {
                /* ignore */
              }
            });
        },
        true
      );
    }

    window.Alpine.data("orbitCheckboxList", () => ({
      selected: [],
      options: [],
      path: "",
      _syncing: false,
      init() {
        const el = this.$el;
        this.path = el.getAttribute("data-path") || "";
        this.options = parseJsonDataset(el, "options", []).map(String);
        this.selected = parseJsonDataset(el, "state", []).map(String);
        // x-model on checkboxes mutates ``selected``; push to Conduit after Alpine settles.
        this.$watch("selected", () => {
          if (this._syncing) return;
          this.$nextTick(() => this.sync());
        });
      },
      selectAll() {
        this.selected = [...this.options];
      },
      deselectAll() {
        this.selected = [];
      },
      sync() {
        this._syncing = true;
        try {
          syncWirePath(this.$el, this.path, [...this.selected]);
        } finally {
          // Allow the next user gesture to sync again after Conduit settles.
          this.$nextTick(() => {
            this._syncing = false;
          });
        }
      },
    }));

    window.Alpine.data("orbitTagsInput", () => ({
      state: [],
      newTag: "",
      path: "",
      splitKeys: [],
      tagPrefix: "",
      tagSuffix: "",
      disabled: false,
      _syncing: false,
      init() {
        const el = this.$el;
        this.path = el.getAttribute("data-path") || "";
        this.state = parseJsonDataset(el, "state", []).map(String);
        this.splitKeys = parseJsonDataset(el, "split-keys", [",", "Tab"]).map(String);
        this.tagPrefix = el.getAttribute("data-tag-prefix") || "";
        this.tagSuffix = el.getAttribute("data-tag-suffix") || "";
        this.disabled = Boolean(el.querySelector("input.or-tags-input[disabled]"));
        this.$watch("state", () => {
          if (this._syncing) return;
          this.sync();
        });
      },
      createTag() {
        const tag = String(this.newTag || "").trim();
        this.newTag = "";
        if (!tag || this.disabled) return;
        if (this.state.includes(tag)) return;
        this.state = [...this.state, tag];
      },
      deleteTag(tag) {
        if (this.disabled) return;
        this.state = this.state.filter((t) => t !== tag);
      },
      onKeydown(event) {
        // Enter / Tab are handled by Alpine `.prevent` modifiers on the input.
        if (event.key === "Enter" || event.key === "Tab") return;
        if (this.splitKeys.includes(event.key)) {
          event.preventDefault();
          event.stopPropagation();
          this.createTag();
          return;
        }
        if (event.key === "Backspace" && !this.newTag && this.state.length) {
          this.deleteTag(this.state[this.state.length - 1]);
        }
      },
      onPaste(event) {
        this.$nextTick?.(() => {
          if (!this.splitKeys.length) {
            this.createTag();
            return;
          }
          // Split only on single-character keys ("," etc.) — never on "Tab"/"Enter" literals.
          const seps = this.splitKeys.filter((k) => k.length === 1);
          if (!seps.length) {
            this.createTag();
            return;
          }
          const escaped = seps
            .map((k) => k.replace(/[/\-\\^$*+?.()|[\]{}]/g, "\\$&"))
            .join("|");
          const parts = String(this.newTag || "").split(new RegExp(escaped, "g"));
          parts.forEach((part) => {
            this.newTag = part;
            this.createTag();
          });
        });
      },
      sync() {
        this._syncing = true;
        try {
          syncWirePath(this.$el, this.path, [...this.state]);
        } finally {
          this.$nextTick(() => {
            this._syncing = false;
          });
        }
      },
    }));

    window.Alpine.data("orbitWizard", () => ({
      step: 0,
      maxReached: 0,
      total: 1,
      linear: true,
      init() {
        const el = this.$el;
        this.total = Math.max(1, Number(el.getAttribute("data-steps") || 1));
        this.linear = el.getAttribute("data-linear") !== "false";
        const start = Math.min(
          Math.max(0, Number(el.getAttribute("data-start") || 0)),
          this.total - 1,
        );
        this.step = start;
        this.maxReached = start;
      },
      validateStep() {
        const pane = this.$el.querySelector(
          `.or-wizard-step[data-step="${this.step}"]`,
        );
        if (!pane) return true;
        const fields = pane.querySelectorAll("input, select, textarea");
        for (const field of fields) {
          if (field.disabled || field.type === "hidden") continue;
          if (typeof field.checkValidity === "function" && !field.checkValidity()) {
            field.reportValidity();
            return false;
          }
        }
        return true;
      },
      go(index) {
        const i = Number(index);
        if (Number.isNaN(i) || i < 0 || i >= this.total) return;
        if (this.linear && i > this.maxReached) return;
        this.step = i;
      },
      back() {
        this.go(Math.max(this.step - 1, 0));
      },
      next() {
        if (this.linear && !this.validateStep()) return;
        const n = Math.min(this.step + 1, this.total - 1);
        this.maxReached = Math.max(this.maxReached, n);
        this.step = n;
      },
      skip() {
        const n = Math.min(this.step + 1, this.total - 1);
        this.maxReached = Math.max(this.maxReached, n);
        this.step = n;
      },
    }));

    const bootFileUploads = () => {
      const FilePond = window.FilePond;
      if (!FilePond) return;

      const register = [
        window.FilePondPluginFileValidateType,
        window.FilePondPluginFileValidateSize,
        window.FilePondPluginImageExifOrientation,
        window.FilePondPluginFilePoster,
        window.FilePondPluginImagePreview,
        window.FilePondPluginImageCrop,
        window.FilePondPluginImageResize,
        window.FilePondPluginImageTransform,
      ].filter(Boolean);
      if (register.length && !window.__orbitFilePondPlugins) {
        FilePond.registerPlugin(...register);
        window.__orbitFilePondPlugins = true;
      }

      const csrfHeader = () => {
        const meta = document.querySelector('meta[name="csrf-token"]');
        const token = meta?.getAttribute?.("content");
        return token ? { "X-CSRF-TOKEN": token } : {};
      };

      const parseExisting = (root) => {
        const raw = root.getAttribute("data-existing");
        if (!raw) return [];
        try {
          const list = JSON.parse(raw);
          return Array.isArray(list) ? list : [];
        } catch (_) {
          return [];
        }
      };

      const initField = (root) => {
        // Morph may have wiped FilePond while leaving the bound flag — allow re-init.
        if (root.dataset.uploadBound === "1" && !root.querySelector(".filepond--root")) {
          delete root.dataset.uploadBound;
          try {
            root._orbitFilePond?.destroy?.();
          } catch (_) {
            /* ignore */
          }
          root._orbitFilePond = null;
        }
        if (root.dataset.uploadBound === "1") return;
        const input = root.querySelector("input.or-file");
        const endpoint = root.getAttribute("data-upload-url");
        const field = root.getAttribute("data-upload-field") || "";
        const statePath =
          root.getAttribute("data-upload-path") ||
          (field && !String(field).startsWith("data.") ? `data.${field}` : field);
        const resource = root.getAttribute("data-upload-resource") || "";
        if (!input || !endpoint) return;
        root.dataset.uploadBound = "1";

        // FilePond owns the chrome — hide progressive-enhancement cards.
        root.querySelectorAll(".or-file-preview-fallback").forEach((el) => {
          el.setAttribute("hidden", "hidden");
        });

        const multiple = Boolean(input.multiple);
        const maxFilesAttr = Number(root.getAttribute("data-max-files") || 0);
        const maxSizeKb = Number(root.getAttribute("data-max-size") || 0);
        const minSizeKb = Number(root.getAttribute("data-min-size") || 0);
        const accepted = (input.getAttribute("accept") || "")
          .split(",")
          .map((part) => part.trim())
          .filter(Boolean);
        const imagePreview = root.getAttribute("data-image-preview") === "true";
        const reorderable = root.getAttribute("data-reorderable") === "true";
        const avatar = root.getAttribute("data-avatar") === "true";
        const imageEditor = root.getAttribute("data-image-editor") === "true";
        const previewHeight = root.getAttribute("data-preview-height");
        const aspectRaw = root.getAttribute("data-aspect-ratios") || "";
        const aspect = aspectRaw
          .split(",")
          .map((part) => part.trim())
          .filter(Boolean)[0];

        const pushState = (pond) => {
          const wire = window.orbitWire?.(root);
          if (!wire || !statePath) return;
          const paths = pond
            .getFiles()
            .map((item) => item.serverId || (typeof item.source === "string" ? item.source : null))
            .filter(Boolean);
          const value = multiple || maxFilesAttr > 1 ? paths : paths[0] || null;
          // Prefer renderless sync_data_path (no remorph); fall back to $set.
          if (typeof wire.sync_data_path === "function") {
            wire.sync_data_path(statePath, value);
          } else if (typeof wire.$set === "function") {
            wire.$set(statePath, value);
          } else if (typeof wire.set_property === "function") {
            wire.set_property(statePath, value);
          }
        };

        root._orbitUploadUrls = root._orbitUploadUrls || {};
        const existing = parseExisting(root).map((file) => {
          const path = file.path;
          const url = file.url || root._orbitUploadUrls[path] || path;
          if (path && url) root._orbitUploadUrls[path] = url;
          return {
            source: path,
            options: {
              type: "local",
              file: {
                name: file.name || String(path).split("/").pop(),
                type: file.mime || undefined,
                size: undefined,
              },
              metadata: {
                poster: url,
              },
            },
          };
        });

        let stylePanelLayout = null;
        if (avatar) stylePanelLayout = "circle";
        // panel_layout uses Orbit CSS grid widths on .filepond--item (not FilePond compact).

        const options = {
          credits: false,
          allowMultiple: multiple || maxFilesAttr > 1,
          maxFiles: maxFilesAttr > 0 ? maxFilesAttr : avatar ? 1 : null,
          maxFileSize: maxSizeKb > 0 ? `${maxSizeKb}KB` : null,
          minFileSize: minSizeKb > 0 ? `${minSizeKb}KB` : null,
          acceptedFileTypes: accepted.length ? accepted : null,
          allowReorder: reorderable,
          allowPaste: true,
          allowDrop: true,
          allowBrowse: true,
          allowReplace: !(multiple || maxFilesAttr > 1),
          instantUpload: true,
          stylePanelLayout,
          stylePanelAspectRatio: avatar ? "1:1" : null,
          imagePreviewHeight: previewHeight
            ? Number(previewHeight)
            : avatar
              ? 170
              : imagePreview
                ? 160
                : null,
          allowImagePreview: imagePreview || avatar,
          allowFilePoster: true,
          // Skip client transforms for already-stored locals — ImageTransform can
          // throw (e.g. M_ID) when remorphing after save with incomplete metadata.
          imageTransformImageFilter: (file) => {
            try {
              const origin = file?.origin ?? file?.file?.origin;
              const localOrigin =
                (window.FilePond && window.FilePond.FileOrigin?.LOCAL) ?? 3;
              if (origin === localOrigin) return false;
            } catch (_) {
              /* ignore */
            }
            return true;
          },
          files: existing,
          labelIdle: avatar
            ? '<span class="filepond--label-action">Upload avatar</span>'
            : 'Drag & drop files, or <span class="filepond--label-action">Browse</span>',
          server: {
            process: (_fieldName, file, _metadata, load, error, progress, abort) => {
              const body = new FormData();
              body.append("file", file, file.name);
              body.append("field", field);
              body.append("resource", resource);
              const request = new XMLHttpRequest();
              request.open("POST", endpoint);
              Object.entries(csrfHeader()).forEach(([key, value]) => {
                request.setRequestHeader(key, value);
              });
              request.upload.onprogress = (event) => {
                progress(event.lengthComputable, event.loaded, event.total || 0);
              };
              request.onload = () => {
                try {
                  const result = JSON.parse(request.responseText || "{}");
                  if (result.ok && result.file?.path) {
                    if (result.file.url) {
                      root._orbitUploadUrls[result.file.path] = result.file.url;
                    }
                    load(result.file.path);
                  } else {
                    error(result.error || "Upload failed.");
                  }
                } catch (_) {
                  error("Upload failed.");
                }
              };
              request.onerror = () => error("Upload failed.");
              request.send(body);
              return {
                abort: () => {
                  request.abort();
                  abort();
                },
              };
            },
            revert: (uniqueFileId, load, error) => {
              const body = new FormData();
              body.append("intent", "delete");
              body.append("path", uniqueFileId);
              body.append("field", field);
              body.append("resource", resource);
              fetch(endpoint, {
                method: "POST",
                body,
                headers: csrfHeader(),
                credentials: "same-origin",
              })
                .then((res) => (res.ok ? load() : error("Could not remove file.")))
                .catch(() => error("Could not remove file."));
            },
            remove: (source, load, error) => {
              const body = new FormData();
              body.append("intent", "delete");
              body.append("path", source);
              body.append("field", field);
              body.append("resource", resource);
              fetch(endpoint, {
                method: "POST",
                body,
                headers: csrfHeader(),
                credentials: "same-origin",
              })
                .then((res) => (res.ok ? load() : error("Could not remove file.")))
                .catch(() => error("Could not remove file."));
            },
            load: (source, load, error, progress, abort) => {
              const match = parseExisting(root).find((file) => file.path === source);
              const url =
                match?.url || root._orbitUploadUrls?.[source] || source;
              // Absolute path required — relative URLs resolve against the edit page.
              const resolved =
                typeof url === "string" &&
                url &&
                !url.startsWith("/") &&
                !/^https?:/i.test(url) &&
                !url.startsWith("data:")
                  ? `/storage/${url.replace(/^\/+/, "")}`
                  : url;
              const controller =
                typeof AbortController !== "undefined" ? new AbortController() : null;
              fetch(resolved, {
                credentials: "same-origin",
                signal: controller?.signal,
              })
                .then((res) => {
                  if (!res.ok) throw new Error("load failed");
                  return res.blob();
                })
                .then((blob) => {
                  progress(true, blob.size, blob.size);
                  load(blob);
                })
                .catch(() => {
                  try {
                    error("Could not load file.");
                  } catch (_) {
                    /* FilePond may reject after destroy during morph */
                  }
                });
              return {
                abort: () => {
                  controller?.abort();
                  abort();
                },
              };
            },
          },
        };

        if (imageEditor) {
          options.allowImageCrop = true;
          options.allowImageResize = true;
          options.allowImageTransform = true;
          if (aspect) {
            // "16:9" → 16/9
            const parts = aspect.split(":").map(Number);
            if (parts.length === 2 && parts[0] > 0 && parts[1] > 0) {
              options.imageCropAspectRatio = parts[0] / parts[1];
            }
          } else if (avatar) {
            options.imageCropAspectRatio = 1;
          }
        }

        try {
          const pond = FilePond.create(input, options);
          root._orbitFilePond = pond;
          const sync = () => pushState(pond);
          pond.on("processfile", sync);
          pond.on("removefile", sync);
          pond.on("reorderfiles", sync);
          // Do not sync on every updatefiles — that fires before upload completes
          // and can push null into form state while FilePond is still processing.
        } catch (err) {
          delete root.dataset.uploadBound;
          console.error("[orbit] FilePond init failed", err);
        }
      };

      document.querySelectorAll("[data-upload-field]").forEach(initField);
    };
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bootFileUploads);
    } else {
      bootFileUploads();
    }
    // SPA navigations remount form hosts — rebind FilePond on new fields.
    window.addEventListener("orbit:spa-navigated", () => bootFileUploads());
    // Conduit morphs can wipe FilePond; rebind any field that lost its chrome.
    if (!window.__orbitFilePondObserver) {
      let pondBootTimer = null;
      const scheduleBoot = () => {
        clearTimeout(pondBootTimer);
        pondBootTimer = setTimeout(() => bootFileUploads(), 40);
      };
      window.__orbitFilePondObserver = new MutationObserver(scheduleBoot);
      window.__orbitFilePondObserver.observe(document.documentElement, {
        childList: true,
        subtree: true,
      });
    }

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
            const tool = btn.getAttribute("data-tool") || "";
            const block = {
              h1: "<h1>",
              h2: "<h2>",
              h3: "<h3>",
              heading: "<h2>",
              paragraph: "<p>",
              blockquote: "<blockquote>",
              codeBlock: "<pre>",
            }[tool];
            const cmd = {
              bold: "bold",
              italic: "italic",
              underline: "underline",
              strike: "strikeThrough",
              link: "createLink",
              unlink: "unlink",
              bulletList: "insertUnorderedList",
              orderedList: "insertOrderedList",
              alignStart: "justifyLeft",
              alignCenter: "justifyCenter",
              alignEnd: "justifyRight",
              undo: "undo",
              redo: "redo",
              clearFormat: "removeFormat",
              horizontalRule: "insertHorizontalRule",
            }[tool];
            surface.focus();
            if (block) {
              document.execCommand("formatBlock", false, block);
            } else if (cmd === "createLink") {
              const url = window.prompt("URL");
              if (url) document.execCommand(cmd, false, url);
            } else if (tool === "image") {
              const src = window.prompt("Image URL");
              if (src) document.execCommand("insertImage", false, src);
            } else if (tool.startsWith("mergeTag:")) {
              document.execCommand("insertText", false, `{{ ${tool.slice(9)} }}`);
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
        const placeholder = root.getAttribute("data-placeholder");
        if (placeholder) {
          surface.setAttribute("data-placeholder", placeholder);
        }
        if (root.getAttribute("data-editor-disabled") === "true") {
          surface.setAttribute("contenteditable", "false");
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

  // Copy-message toast for `.copyable().copyMessage(...)` columns. The Alpine
  // `@click.stop` on `.or-copy-btn` already writes to the clipboard; this just
  // surfaces an optional confirmation toast next to the button.
  const bootCopyToast = () => {
    if (typeof document === "undefined") return;
    let toast = document.getElementById("or-copy-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "or-copy-toast";
      toast.className = "or-copy-toast";
      toast.setAttribute("role", "status");
      document.body.appendChild(toast);
    }
    let hideTimer = null;
    document.addEventListener(
      "click",
      (event) => {
        const btn = event.target?.closest?.(".or-copy-btn");
        if (!btn) return;
        const wrap = btn.closest("[data-copy]");
        const message = wrap?.getAttribute("data-copy-message");
        if (!message) return;
        const duration = Number(wrap.getAttribute("data-copy-message-duration")) || 2000;
        toast.textContent = message;
        const rect = btn.getBoundingClientRect();
        toast.style.top = `${Math.round(rect.top - 36)}px`;
        toast.style.left = `${Math.round(rect.left)}px`;
        toast.classList.add("is-visible");
        if (hideTimer) clearTimeout(hideTimer);
        hideTimer = setTimeout(() => {
          toast.classList.remove("is-visible");
        }, duration);
      },
      true,
    );
  };
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bootCopyToast);
    } else {
      bootCopyToast();
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

  if (typeof window !== "undefined") {
    window.addEventListener("orbit-export-ready", (event) => {
      const detail = event.detail || {};
      const content = detail.content;
      if (content == null || content === "") return;
      const mime = detail.mime || "text/csv";
      const filename = detail.filename || "export.csv";
      const blob = new Blob([content], { type: mime });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    });
  }
})();
