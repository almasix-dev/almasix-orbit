(function () {
  function readSchedule(html) {
    var mark = html.indexOf('class="or-schedule-data"');
    var open = mark < 0 ? -1 : html.indexOf(">", mark);
    var close = open < 0 ? -1 : html.indexOf("<" + "/script>", open);
    if (close < 0) return null;
    try {
      return JSON.parse(html.slice(open + 1, close));
    } catch (error) {
      return null;
    }
  }

  function addDays(iso, count) {
    var parts = String(iso || "").split("-");
    var day = new Date(Date.UTC(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])));
    day.setUTCDate(day.getUTCDate() + count);
    var month = String(day.getUTCMonth() + 1).padStart(2, "0");
    var date = String(day.getUTCDate()).padStart(2, "0");
    return day.getUTCFullYear() + "-" + month + "-" + date;
  }

  function register(Alpine) {
    Alpine.data("orbitSchedule", function () {
      return {
        view: "week",
        date: "",
        readonly: true,
        events: [],
        range: null,
        navigate: "",
        schedule: null,
        picker: null,
        init: function () {
          var node = this.$el.querySelector(".or-schedule-data");
          var config = JSON.parse((node && node.textContent) || "{}");
          this.view = config.view || "week";
          this.date = config.date;
          this.readonly = config.readonly !== false;
          this.events = config.events || [];
          this.range = config.range || null;
          this.navigate = config.navigate || "";
          var self = this;
          this.$el.addEventListener("click", function (event) {
            if (event.target.closest(".or-schedule-toolbar")) {
              var viewButton = event.target.closest("[data-view]");
              if (viewButton) {
                self.setView(viewButton.getAttribute("data-view"));
                return;
              }
              var shiftButton = event.target.closest("[data-shift]");
              if (shiftButton) self.shift(Number(shiftButton.getAttribute("data-shift")));
              return;
            }
            if (event.target.closest(".or-schedule-picker")) {
              window.setTimeout(function () {
                self.followPicker();
              }, 0);
            }
          });
          var picker = this.$el.querySelector(".or-schedule-picker");
          if (picker) {
            picker.addEventListener(
              "wheel",
              function () {
                window.setTimeout(function () {
                  self.followPicker();
                }, 0);
              },
              { passive: true }
            );
          }
          this.mount();
        },
        mount: function () {
          var lib = window.calendarjs;
          var board = this.$el.querySelector(".or-schedule-board");
          var pickerBoard = this.$el.querySelector(".or-schedule-picker-board");
          var month = this.$el.querySelector(".or-schedule-month");
          board.innerHTML = "";
          if (pickerBoard) pickerBoard.innerHTML = "";
          if (!lib || typeof lib.Schedule !== "function" || typeof lib.Calendar !== "function") {
            board.textContent = "The schedule library has not loaded yet.";
            return;
          }
          if (month) month.hidden = true;
          var self = this;
          var block = function () {
            if (self.readonly) return false;
          };
          var marks = this.events.map(function (event) {
            return { date: event.date };
          });
          this.picker = lib.Calendar(pickerBoard, {
            type: "inline",
            value: this.date,
            footer: false,
            data: marks,
            onchange: function (_picker, value) {
              self.goTo(String(value || "").slice(0, 10));
            },
          });
          this.schedule = lib.Schedule(board, {
            type: this.view,
            value: this.date,
            data: this.events,
            overlap: true,
            readOnlyRange: [
              ["00:00", "08:00"],
              ["17:00", "24:00"],
            ],
            onbeforecreate: block,
            onbeforeinsert: block,
            onbeforechangeevent: block,
          });
        },
        loadedMonth: function () {
          if (this.range && this.range[0]) return this.range[0].slice(0, 7);
          return String(this.date || "").slice(0, 7);
        },
        showDate: function (iso) {
          this.date = iso;
          if (!this.schedule) return;
          this.schedule.value = iso;
          if (typeof this.schedule.render === "function") this.schedule.render();
        },
        followPicker: function () {
          if (this._applying || !this.picker || !this.navigate) return;
          var names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
          ];
          var index = names.indexOf(this.picker.month);
          if (index < 0 || !this.picker.year) return;
          var month = this.picker.year + "-" + String(index + 1).padStart(2, "0");
          if (month === this.loadedMonth()) return;
          var value = String(this.picker.value || "");
          var iso = value.slice(0, 7) === month ? value.slice(0, 10) : month + "-01";
          this.openMonth(iso);
        },
        goTo: function (iso) {
          if (this._applying || !/^\d{4}-\d{2}-\d{2}$/.test(iso) || iso === this.date) return;
          if (!this.navigate || iso.slice(0, 7) === this.loadedMonth()) {
            this.showDate(iso);
            return;
          }
          this.openMonth(iso);
        },
        openMonth: function (iso) {
          var self = this;
          window.clearTimeout(this._queueTimer);
          this._loadId = (this._loadId || 0) + 1;
          var loadId = this._loadId;
          if (!/^\d{4}-\d{2}-\d{2}$/.test(iso) || !this.navigate || iso.slice(0, 7) === this.loadedMonth()) {
            if (/^\d{4}-\d{2}-\d{2}$/.test(iso)) this.showDate(iso);
            return;
          }
          this._queued = iso;
          this._queueTimer = window.setTimeout(function () {
            if (loadId !== self._loadId) return;
            var requested = self._queued;
            var month = requested.slice(0, 7);
            var url = self.navigate.replace("{date}", requested).replace("{month}", month);
            window.fetch(url, { credentials: "same-origin" }).then(function (response) {
              return response.text();
            }).then(function (html) {
              if (loadId !== self._loadId) return;
              var config = readSchedule(html);
              if (!config) return;
              self.applyLoaded(config, requested, url);
            }).catch(function () {});
          }, 40);
        },
        applyLoaded: function (config, iso, url) {
          var day = iso;
          if (config.range && (iso < config.range[0] || iso > config.range[1])) day = config.date || iso;
          config.date = day;
          this._applying = true;
          this.events = config.events || [];
          this.range = config.range || this.range;
          this.date = day;
          if (this.schedule) {
            this.schedule.value = day;
            if (typeof this.schedule.setData === "function") this.schedule.setData(this.events);
            else this.schedule.data = this.events;
          }
          if (this.picker) {
            this.picker.data = this.events.map(function (event) {
              return { date: event.date };
            });
            if (typeof this.picker.setValue === "function") this.picker.setValue(day);
          }
          var node = this.$el.querySelector(".or-schedule-data");
          if (node) node.textContent = JSON.stringify(config).replace(/</g, "\\u003c");
          document.querySelectorAll('input[name="month"]').forEach(function (field) {
            field.value = day.slice(0, 7);
          });
          if (window.history && typeof window.history.replaceState === "function") {
            window.history.replaceState(null, "", url);
          }
          this._applying = false;
        },
        setView: function (view) {
          if (view !== "day" && view !== "week" && view !== "weekdays") return;
          this.view = view;
          var buttons = this.$el.querySelectorAll(".or-schedule-toolbar [data-view]");
          buttons.forEach(function (button) {
            button.classList.toggle("is-active", button.getAttribute("data-view") === view);
          });
          if (!this.schedule) {
            this.mount();
            return;
          }
          this.schedule.type = view;
          if (typeof this.schedule.render === "function") this.schedule.render();
        },
        shift: function (step) {
          var days = this.view === "day" ? step : step * 7;
          var next = addDays(this.date, days);
          var outside = this.range && (next < this.range[0] || next > this.range[1]);
          if (outside && this.navigate) {
            this.openMonth(next);
            return;
          }
          this.date = next;
          if (this.picker && typeof this.picker.setValue === "function") this.picker.setValue(next);
          if (this.schedule) {
            this.schedule.value = next;
            if (typeof this.schedule.render === "function") this.schedule.render();
          }
        },
      };
    });
  }

  document.addEventListener("alpine:init", function () {
    register(window.Alpine);
  });
})();
