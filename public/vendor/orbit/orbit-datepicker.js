/** Orbit Flowbite date/time picker — Alpine host (ported from Shamar). */
(function () {
  "use strict";

let flowbiteDatepickerReady = null;
function loadFlowbiteDatepicker() {
  if (typeof window.Datepicker === 'function') return Promise.resolve();
  if (!flowbiteDatepickerReady) {
    flowbiteDatepickerReady = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = '/vendor/orbit/flowbite-datepicker.min.js';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Flowbite datepicker'));
      document.head.appendChild(script);
    });
  }
  return flowbiteDatepickerReady;
}

function pad2(n) {
  return String(n).padStart(2, '0');
}

function parsePickerBounds(raw) {
  if (raw == null || raw === '') return null;
  const str = String(raw).trim();
  const yearOnly = /^(\d{4})$/.exec(str);
  if (yearOnly) return new Date(Number(yearOnly[1]), 0, 1);
  const ym = /^(\d{4})-(\d{2})$/.exec(str);
  if (ym) return new Date(Number(ym[1]), Number(ym[2]) - 1, 1);
  const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(str);
  if (dateOnly) {
    return new Date(Number(dateOnly[1]), Number(dateOnly[2]) - 1, Number(dateOnly[3]));
  }
  const dt = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?/.exec(str);
  if (dt) {
    return new Date(
      Number(dt[1]),
      Number(dt[2]) - 1,
      Number(dt[3]),
      Number(dt[4]),
      Number(dt[5]),
      dt[6] != null ? Number(dt[6]) : 0,
    );
  }
  const timeOnly = /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/.exec(str);
  if (timeOnly) {
    const d = new Date();
    d.setHours(Number(timeOnly[1]), Number(timeOnly[2]), timeOnly[3] != null ? Number(timeOnly[3]) : 0, 0);
    return d;
  }
  const parsed = new Date(str);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function parsePickerValue(raw, mode) {
  if (raw == null || raw === '') return null;
  const str = String(raw).trim();
  if (mode === 'time') {
    const m = /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/.exec(str);
    if (!m) return null;
    return {
      year: null,
      month: null,
      day: null,
      hour: Number(m[1]),
      minute: Number(m[2]),
      second: m[3] != null ? Number(m[3]) : 0,
    };
  }
  const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(str);
  if (dateOnly) {
    return {
      year: Number(dateOnly[1]),
      month: Number(dateOnly[2]),
      day: Number(dateOnly[3]),
      hour: 0,
      minute: 0,
      second: 0,
    };
  }
  const dt = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?/.exec(str);
  if (dt) {
    return {
      year: Number(dt[1]),
      month: Number(dt[2]),
      day: Number(dt[3]),
      hour: Number(dt[4]),
      minute: Number(dt[5]),
      second: dt[6] != null ? Number(dt[6]) : 0,
    };
  }
  const parsed = parsePickerBounds(str);
  if (!parsed) return null;
  return {
    year: parsed.getFullYear(),
    month: parsed.getMonth() + 1,
    day: parsed.getDate(),
    hour: parsed.getHours(),
    minute: parsed.getMinutes(),
    second: parsed.getSeconds(),
  };
}

function formatPickerState(parts, mode, withSeconds) {
  if (!parts) return '';
  if (mode === 'time') {
    return withSeconds
      ? `${pad2(parts.hour)}:${pad2(parts.minute)}:${pad2(parts.second)}`
      : `${pad2(parts.hour)}:${pad2(parts.minute)}`;
  }
  if (mode === 'year') {
    return parts.year == null ? '' : String(parts.year);
  }
  const date = `${parts.year}-${pad2(parts.month)}-${pad2(parts.day)}`;
  if (mode === 'date' || mode === 'week' || mode === 'month') return date;
  const time = withSeconds
    ? `T${pad2(parts.hour)}:${pad2(parts.minute)}:${pad2(parts.second)}`
    : `T${pad2(parts.hour)}:${pad2(parts.minute)}`;
  return date + time;
}

function dateOnlyStamp(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
}

function isoWeekStart(date, weekStart = 1) {
  const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const diff = (d.getDay() - weekStart + 7) % 7;
  d.setDate(d.getDate() - diff);
  return d;
}

function isoWeekNumber(date) {
  const d = new Date(date.getTime());
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() + 3 - ((d.getDay() + 6) % 7));
  const week1 = new Date(d.getFullYear(), 0, 4);
  return (
    1 +
    Math.round(
      ((d.getTime() - week1.getTime()) / 86400000 - 3 + ((week1.getDay() + 6) % 7)) / 7,
    )
  );
}

function resolveTimeDisplayFormat(preferred) {
  if (preferred === '12' || preferred === '24') return preferred;
  try {
    return new Intl.DateTimeFormat(undefined, { hour: 'numeric' }).resolvedOptions().hour12
      ? '12'
      : '24';
  } catch {
    return '24';
  }
}

function resolveMinuteStep(cfg, withSeconds) {
  if (cfg.minuteStep != null && Number.isFinite(Number(cfg.minuteStep))) {
    return Math.max(1, Math.min(30, Math.floor(Number(cfg.minuteStep))));
  }
  return withSeconds ? 1 : 5;
}

function formatTimeDisplay(parts, format, withSeconds) {
  if (!parts) return '';
  const minute = pad2(parts.minute);
  const second = pad2(parts.second ?? 0);
  if (format === '24') {
    const base = `${pad2(parts.hour)}:${minute}`;
    return withSeconds ? `${base}:${second}` : base;
  }
  const hour24 = ((parts.hour % 24) + 24) % 24;
  const meridiem = hour24 >= 12 ? 'PM' : 'AM';
  const hour12 = hour24 % 12 === 0 ? 12 : hour24 % 12;
  const base = `${pad2(hour12)}:${minute}`;
  return withSeconds ? `${base}:${second} ${meridiem}` : `${base} ${meridiem}`;
}

function timeMaskDigitCapacity(withSeconds) {
  return withSeconds ? 6 : 4;
}

function formatTimeMaskDraft(digits, meridiem, format, withSeconds) {
  const raw = String(digits || '').replace(/\D/g, '');
  let result = '';
  if (raw.length <= 2) {
    result = raw;
  } else if (raw.length <= 4) {
    result = `${raw.slice(0, 2)}:${raw.slice(2)}`;
  } else {
    const capped = raw.slice(0, timeMaskDigitCapacity(withSeconds));
    result = `${capped.slice(0, 2)}:${capped.slice(2, 4)}:${capped.slice(4)}`;
  }
  if (format === '12' && meridiem) {
    return result ? `${result} ${meridiem}` : meridiem;
  }
  return result;
}

function timeMaskFromParts(parts, format, withSeconds) {
  const hour24 = ((parts.hour % 24) + 24) % 24;
  const hour = format === '12' ? (hour24 % 12 === 0 ? 12 : hour24 % 12) : hour24;
  let digits = `${pad2(hour)}${pad2(parts.minute)}`;
  if (withSeconds) digits += pad2(parts.second ?? 0);
  const meridiem = format === '12' ? (hour24 >= 12 ? 'PM' : 'AM') : '';
  return { digits, meridiem };
}

function parseTimeMaskState(state, format, withSeconds) {
  const need = timeMaskDigitCapacity(withSeconds);
  const digits = String(state.digits || '').replace(/\D/g, '');
  if (digits.length < need) return null;
  if (format === '12' && !state.meridiem) return null;
  const hour = Number(digits.slice(0, 2));
  const minute = Number(digits.slice(2, 4));
  const second = withSeconds ? Number(digits.slice(4, 6)) : 0;
  if (!Number.isFinite(hour) || !Number.isFinite(minute) || !Number.isFinite(second)) {
    return null;
  }
  if (minute > 59 || second > 59) return null;
  if (format === '12') {
    if (hour < 1 || hour > 12) return null;
    const meridiem = state.meridiem;
    const hour24 =
      meridiem === 'AM' ? (hour === 12 ? 0 : hour) : hour === 12 ? 12 : hour + 12;
    return { hour: hour24, minute, second };
  }
  if (hour > 23) return null;
  return { hour, minute, second };
}

function applyTimeMaskKey(state, key, format, withSeconds) {
  const max = timeMaskDigitCapacity(withSeconds);
  const digits = String(state.digits || '').replace(/\D/g, '').slice(0, max);
  let meridiem = state.meridiem || '';
  const draftOf = (nextDigits, nextMeridiem) =>
    formatTimeMaskDraft(nextDigits, nextMeridiem, format, withSeconds);

  if (/^[0-9]$/.test(key)) {
    if (digits.length >= max) {
      return { digits, meridiem, draft: draftOf(digits, meridiem), handled: true };
    }
    const pos = digits.length;
    const d = Number(key);
    let next = digits;

    if (pos === 0) {
      if (format === '24' && d > 2) next = `0${key}`;
      else if (format === '12' && d > 1) next = `0${key}`;
      else next = key;
    } else if (pos === 1) {
      const hour = Number(`${digits[0]}${key}`);
      if (format === '24' && hour > 23) {
        return { digits, meridiem, draft: draftOf(digits, meridiem), handled: true };
      }
      if (format === '12' && (hour > 12 || hour === 0)) {
        if (digits.length + 2 > max) {
          return { digits, meridiem, draft: draftOf(digits, meridiem), handled: true };
        }
        next = `0${digits[0]}${key}`;
      } else {
        next = `${digits}${key}`;
      }
    } else if (pos === 2 || pos === 4) {
      if (d > 5) {
        if (digits.length + 2 > max) {
          return { digits, meridiem, draft: draftOf(digits, meridiem), handled: true };
        }
        next = `${digits}0${key}`;
      } else {
        next = `${digits}${key}`;
      }
    } else {
      next = `${digits}${key}`;
    }

    next = next.slice(0, max);
    return { digits: next, meridiem, draft: draftOf(next, meridiem), handled: true };
  }

  if (format === '12' && (key === 'a' || key === 'A' || key === 'p' || key === 'P')) {
    meridiem = key === 'a' || key === 'A' ? 'AM' : 'PM';
    return { digits, meridiem, draft: draftOf(digits, meridiem), handled: true };
  }

  if (key === 'Backspace' || key === 'Delete') {
    if (format === '12' && meridiem) {
      meridiem = '';
      return { digits, meridiem, draft: draftOf(digits, meridiem), handled: true };
    }
    const next = digits.slice(0, -1);
    return { digits: next, meridiem, draft: draftOf(next, meridiem), handled: true };
  }

  if (key === ':' || key === ' ') {
    return { digits, meridiem, draft: draftOf(digits, meridiem), handled: true };
  }

  if (key.length === 1) {
    return { digits, meridiem, draft: draftOf(digits, meridiem), handled: true };
  }

  return { digits, meridiem, draft: draftOf(digits, meridiem), handled: false };
}

function parseFlexibleTimeInput(raw, format = '24') {
  const str = String(raw || '').trim();
  if (!str) return null;
  const meridiemMatch = /(a\.?m\.?|p\.?m\.?|[ap])\s*$/i.exec(str);
  const meridiemToken = meridiemMatch ? meridiemMatch[1].toLowerCase().replace(/\./g, '') : null;
  const meridiem =
    meridiemToken == null ? null : meridiemToken.startsWith('a') ? 'am' : 'pm';
  const cleaned = str
    .replace(/(a\.?m\.?|p\.?m\.?|[ap])\s*$/i, '')
    .replace(/\s+/g, '')
    .replace(/\./g, '');
  let hour = 0;
  let minute = 0;
  let second = 0;
  const colon = /^(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?$/.exec(cleaned);
  if (colon) {
    hour = Number(colon[1]);
    minute = Number(colon[2]);
    second = colon[3] != null ? Number(colon[3]) : 0;
  } else if (/^\d{3,6}$/.test(cleaned)) {
    if (cleaned.length <= 4) {
      const padded = cleaned.padStart(4, '0');
      hour = Number(padded.slice(0, 2));
      minute = Number(padded.slice(2, 4));
    } else {
      const padded = cleaned.padStart(6, '0');
      hour = Number(padded.slice(0, 2));
      minute = Number(padded.slice(2, 4));
      second = Number(padded.slice(4, 6));
    }
  } else {
    return null;
  }
  if (minute > 59 || second > 59) return null;
  if (meridiem || format === '12') {
    if (hour < 0 || hour > 12) return null;
    let hour24;
    if (meridiem === 'am') hour24 = hour === 12 ? 0 : hour;
    else if (meridiem === 'pm') hour24 = hour === 12 ? 12 : hour + 12;
    else hour24 = hour === 12 ? 12 : hour;
    return { hour: hour24, minute, second };
  }
  if (hour > 23) return null;
  return { hour, minute, second };
}

function nudgeTimePart(parts, unit, delta, minuteStep = 5) {
  let { hour, minute, second } = parts;
  if (unit === 'meridiem') return { hour: (hour + 12) % 24, minute, second };
  if (unit === 'hour') return { hour: (hour + delta + 24) % 24, minute, second };
  if (unit === 'second') return { hour, minute, second: (second + delta + 60) % 60 };
  const step = Math.max(1, minuteStep);
  const next = minute + delta * step;
  if (next >= 60) {
    return { hour: (hour + Math.floor(next / 60)) % 24, minute: next % 60, second };
  }
  if (next < 0) {
    const borrow = Math.ceil(-next / 60);
    return {
      hour: (hour - borrow + 240) % 24,
      minute: ((next % 60) + 60) % 60,
      second,
    };
  }
  return { hour, minute: next, second };
}

function createOrbitDatePicker(cfg = {}) {
  const mode = cfg.mode || 'date';
  const withSeconds = !!cfg.seconds;
  const timeFormat = resolveTimeDisplayFormat(cfg.timeFormat);
  const minuteStep = resolveMinuteStep(cfg, withSeconds);
  let picker = null;
  let selectedWeekStart = null;

  return {
    name: cfg.name || '',
    mode,
    seconds: withSeconds,
    timeFormat,
    minuteStep,
    placeholder: cfg.placeholder || '',
    timeValue: '',
    timeDraft: '',
    timeMaskDigits: '',
    timeMaskMeridiem: '',
    timeOpen: false,
    hour: 0,
    minute: 0,
    second: 0,
    _syncing: false,
    _outsideClose: null,

    getValue: typeof cfg.getValue === 'function' ? cfg.getValue : () => '',
    setValue: typeof cfg.setValue === 'function' ? cfg.setValue : () => {},
    isDisabled: typeof cfg.isDisabled === 'function' ? cfg.isDisabled : () => false,

    async init() {
      try {
        await loadFlowbiteDatepicker();
      } catch {
        return;
      }
      this.syncTimeFromState();
      if (this.mode !== 'time') {
        this.initPicker();
      }
      this.bindOutsideClose();
      this.$watch(
        () => this.getValue(),
        () => {
          if (this._syncing) return;
          this.syncPickerFromState();
          this.syncTimeFromState();
        },
      );
    },

    destroy() {
      this.unbindOutsideClose();
      picker?.destroy?.();
      picker = null;
    },

    get disabled() {
      return !!this.isDisabled();
    },

    get defaultPlaceholder() {
      if (this.mode === 'time') return 'Select time';
      if (this.mode === 'datetime') return 'Select date and time';
      if (this.mode === 'week') return 'Select week';
      if (this.mode === 'month') return 'Select month';
      if (this.mode === 'year') return 'Select year';
      return 'Select date';
    },

    get timePlaceholder() {
      if (this.timeFormat === '12') {
        return this.seconds ? 'hh:mm:ss AM' : 'hh:mm AM';
      }
      return this.seconds ? 'HH:mm:ss' : 'HH:mm';
    },

    get stateValue() {
      const raw = this.getValue();
      return raw == null ? '' : String(raw);
    },

    get displayHour() {
      if (this.timeFormat === '12') {
        const h = this.hour % 24;
        const hour12 = h % 12 === 0 ? 12 : h % 12;
        return String(hour12);
      }
      return pad2(this.hour);
    },

    get meridiem() {
      return this.hour % 24 >= 12 ? 'PM' : 'AM';
    },

    padTime(n) {
      return pad2(n);
    },

    refreshTimeDraft() {
      if (!this.timeValue) {
        this.timeDraft = '';
        this.timeMaskDigits = '';
        this.timeMaskMeridiem = '';
        return;
      }
      const mask = timeMaskFromParts(
        { hour: this.hour, minute: this.minute, second: this.second },
        this.timeFormat,
        this.seconds,
      );
      this.timeMaskDigits = mask.digits;
      this.timeMaskMeridiem = mask.meridiem;
      this.timeDraft = formatTimeMaskDraft(
        mask.digits,
        mask.meridiem,
        this.timeFormat,
        this.seconds,
      );
    },

    buildDisplayFormat() {
      const self = this;
      return {
        toValue(date) {
          if (!(date instanceof Date) || Number.isNaN(date.getTime())) return undefined;
          if (self.mode === 'year') {
            return new Date(date.getFullYear(), 0, 1).getTime();
          }
          if (self.mode === 'month') {
            return new Date(date.getFullYear(), date.getMonth(), 1).getTime();
          }
          if (self.mode === 'week') {
            return isoWeekStart(date, 1).getTime();
          }
          return dateOnlyStamp(date);
        },
        toDisplay(date) {
          if (!(date instanceof Date) || Number.isNaN(date.getTime())) return '';
          if (self.mode === 'week') {
            const start = isoWeekStart(date, 1);
            return `Week ${isoWeekNumber(start)}, ${start.getFullYear()}`;
          }
          if (self.mode === 'month') {
            return new Intl.DateTimeFormat(undefined, {
              year: 'numeric',
              month: 'long',
            }).format(date);
          }
          if (self.mode === 'year') {
            return String(date.getFullYear());
          }
          return new Intl.DateTimeFormat(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          }).format(date);
        },
      };
    },

    buildPickerOptions() {
      // Keep in sync with packages/adonis/src/shamar/flowbite-picker.ts
      // Flowbite 1.3 resolves `container` via document.querySelector — Element refs break it.
      const opts = {
        autohide: this.mode === 'date' || this.mode === 'week' || this.mode === 'month' || this.mode === 'year',
        todayBtn: true,
        todayBtnMode: 1,
        todayHighlight: true,
        clearBtn: true,
        format: this.buildDisplayFormat(),
        orientation: 'bottom',
        weekStart: 1,
        container: 'body',
      };
      const min = cfg.min || this.$el?.dataset?.min || '';
      const max = cfg.max || this.$el?.dataset?.max || '';
      if (min) opts.minDate = min;
      if (max) opts.maxDate = max;

      if (this.mode === 'month') {
        opts.pickLevel = 1;
        opts.startView = 1;
      }

      if (this.mode === 'year') {
        opts.pickLevel = 2;
        opts.startView = 2;
      }

      if (this.mode === 'week') {
        opts.calendarWeeks = true;
        opts.beforeShowDay = (date) => {
          if (!selectedWeekStart) return undefined;
          const start = dateOnlyStamp(selectedWeekStart);
          const end = start + 6 * 86400000;
          const stamp = dateOnlyStamp(date);
          if (stamp >= start && stamp <= end) {
            return { classes: 'range bg-gray-200 dark:bg-gray-600' };
          }
          return undefined;
        };
      }

      return opts;
    },

    bindOutsideClose() {
      this.unbindOutsideClose();
      this._outsideClose = (ev) => {
        const target = ev.target;
        if (!(target instanceof Node)) return;

        if (this.timeOpen) {
          const timeWrap = this.$refs.timeWrap;
          if (!timeWrap || !timeWrap.contains(target)) {
            this.closeTime();
          }
        }

        if (!picker?.active) return;
        const input = this.$refs.dateInput;
        const pickerEl = picker.pickerElement;
        if (input && (target === input || input.contains(target))) return;
        if (pickerEl && pickerEl.contains(target)) return;
        picker.hide();
      };
      document.addEventListener('pointerdown', this._outsideClose, true);
    },

    unbindOutsideClose() {
      if (!this._outsideClose) return;
      document.removeEventListener('pointerdown', this._outsideClose, true);
      this._outsideClose = null;
    },

    onEscape() {
      if (this.timeOpen) {
        this.closeTime();
        return;
      }
      if (picker?.active) picker.hide();
    },

    initPicker() {
      const input = this.$refs.dateInput;
      if (!input || typeof window.Datepicker !== 'function') return;

      const options = this.buildPickerOptions();
      if (options.container != null && typeof options.container !== 'string') {
        throw new TypeError('Flowbite datepicker container must be a CSS selector string');
      }
      picker = new window.Datepicker(input, options);

      input.addEventListener('changeDate', (ev) => {
        if (this._syncing || this.disabled) return;
        const detailDate = ev.detail?.date;
        const picked = detailDate ?? picker.getDate?.();
        if (!picked) {
          this.commitState('');
          selectedWeekStart = null;
          return;
        }
        const date = picked instanceof Date ? picked : new Date(picked);
        if (Number.isNaN(date.getTime())) return;

        if (this.mode === 'week') {
          selectedWeekStart = isoWeekStart(date, 1);
          const next = formatPickerState(
            {
              year: selectedWeekStart.getFullYear(),
              month: selectedWeekStart.getMonth() + 1,
              day: selectedWeekStart.getDate(),
              hour: 0,
              minute: 0,
              second: 0,
            },
            'week',
            false,
          );
          this.commitState(next);
          this._syncing = true;
          picker.setDate(selectedWeekStart, { render: true });
          queueMicrotask(() => {
            this._syncing = false;
          });
          return;
        }

        if (this.mode === 'year') {
          this.commitState(String(date.getFullYear()));
          return;
        }

        if (this.mode === 'month') {
          const first = new Date(date.getFullYear(), date.getMonth(), 1);
          this.commitState(
            formatPickerState(
              {
                year: first.getFullYear(),
                month: first.getMonth() + 1,
                day: first.getDate(),
                hour: 0,
                minute: 0,
                second: 0,
              },
              'month',
              false,
            ),
          );
          return;
        }

        if (this.mode === 'datetime') {
          this.commitDateTime(date);
          return;
        }

        this.commitState(
          formatPickerState(
            {
              year: date.getFullYear(),
              month: date.getMonth() + 1,
              day: date.getDate(),
              hour: 0,
              minute: 0,
              second: 0,
            },
            'date',
            false,
          ),
        );
      });

      this.syncPickerFromState();
    },

    syncPickerFromState() {
      if (!picker) return;
      const raw = String(this.getValue() || '').trim();
      if (!raw) {
        picker.setDate({ clear: true });
        selectedWeekStart = null;
        return;
      }
      const bounds = parsePickerBounds(raw);
      if (!bounds) return;
      this._syncing = true;
      if (this.mode === 'week') {
        selectedWeekStart = isoWeekStart(bounds, 1);
        picker.setDate(selectedWeekStart);
      } else if (this.mode === 'month') {
        picker.setDate(new Date(bounds.getFullYear(), bounds.getMonth(), 1));
      } else if (this.mode === 'year') {
        picker.setDate(new Date(bounds.getFullYear(), 0, 1));
      } else {
        picker.setDate(bounds);
      }
      queueMicrotask(() => {
        this._syncing = false;
      });
    },

    syncTimeFromState() {
      if (this.mode !== 'datetime' && this.mode !== 'time') return;
      const parts = parsePickerValue(String(this.getValue() || ''), this.mode);
      if (!parts) {
        this.timeValue = '';
        this.timeDraft = '';
        this.hour = 0;
        this.minute = 0;
        this.second = 0;
        return;
      }
      this.hour = parts.hour;
      this.minute = parts.minute;
      this.second = parts.second;
      this.timeValue = this.seconds
        ? `${pad2(parts.hour)}:${pad2(parts.minute)}:${pad2(parts.second)}`
        : `${pad2(parts.hour)}:${pad2(parts.minute)}`;
      this.refreshTimeDraft();
    },

    commitState(value) {
      this._syncing = true;
      this.setValue(value);
      queueMicrotask(() => {
        this._syncing = false;
      });
    },

    commitDateTime(datePart) {
      this.commitState(
        formatPickerState(
          {
            year: datePart.getFullYear(),
            month: datePart.getMonth() + 1,
            day: datePart.getDate(),
            hour: this.hour || 0,
            minute: this.minute || 0,
            second: this.second || 0,
          },
          'datetime',
          this.seconds,
        ),
      );
    },

    composeTimeValue() {
      return this.seconds
        ? `${pad2(this.hour)}:${pad2(this.minute)}:${pad2(this.second)}`
        : `${pad2(this.hour)}:${pad2(this.minute)}`;
    },

    applyTimeParts() {
      this.timeValue = this.composeTimeValue();
      this.refreshTimeDraft();
      this.onTimeChange();
    },

    openTimeAssist() {
      if (this.disabled) return;
      if (picker?.active) picker.hide();
      this.timeOpen = true;
    },

    toggleTime() {
      if (this.disabled) return;
      if (this.timeOpen) {
        this.closeTime();
        return;
      }
      if (!this.timeValue) {
        const now = new Date();
        this.hour = now.getHours();
        this.minute = now.getMinutes();
        this.second = this.seconds ? now.getSeconds() : 0;
        this.applyTimeParts();
      } else {
        this.refreshTimeDraft();
      }
      this.openTimeAssist();
    },

    closeTime() {
      this.timeOpen = false;
    },

    onTimeFocus() {
      this.openTimeAssist();
    },

    onTimeKeydown(event) {
      if (event.ctrlKey || event.metaKey || event.altKey) return;

      if (event.key === 'ArrowUp') {
        event.preventDefault();
        this.nudge('minute', 1);
        return;
      }
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        this.nudge('minute', -1);
        return;
      }
      if (event.key === 'Enter') {
        event.preventDefault();
        this.commitTimeDraft();
        this.closeTime();
        return;
      }
      if (event.key === 'Escape') {
        event.preventDefault();
        this.refreshTimeDraft();
        this.closeTime();
        return;
      }
      if (
        event.key === 'Tab' ||
        event.key === 'ArrowLeft' ||
        event.key === 'ArrowRight' ||
        event.key === 'Home' ||
        event.key === 'End'
      ) {
        return;
      }

      const result = applyTimeMaskKey(
        { digits: this.timeMaskDigits, meridiem: this.timeMaskMeridiem },
        event.key,
        this.timeFormat,
        this.seconds,
      );
      if (!result.handled) return;
      event.preventDefault();
      this.timeMaskDigits = result.digits;
      this.timeMaskMeridiem = result.meridiem;
      this.timeDraft = result.draft;

      const parsed = parseTimeMaskState(
        { digits: result.digits, meridiem: result.meridiem },
        this.timeFormat,
        this.seconds,
      );
      if (parsed) {
        this.hour = parsed.hour;
        this.minute = parsed.minute;
        this.second = this.seconds ? parsed.second : 0;
        this.applyTimeParts();
      }
    },

    onTimePaste(event) {
      event.preventDefault();
      const text = event.clipboardData?.getData('text') || '';
      const parsed = parseFlexibleTimeInput(text, this.timeFormat);
      if (!parsed) return;
      this.hour = parsed.hour;
      this.minute = parsed.minute;
      this.second = this.seconds ? parsed.second : 0;
      this.applyTimeParts();
    },

    commitTimeDraft() {
      if (this.disabled) return;
      const raw = String(this.timeDraft || '').trim();
      if (!raw) {
        this.clearTime({ keepOpen: true });
        return;
      }
      const fromMask = parseTimeMaskState(
        { digits: this.timeMaskDigits, meridiem: this.timeMaskMeridiem },
        this.timeFormat,
        this.seconds,
      );
      if (fromMask) {
        this.hour = fromMask.hour;
        this.minute = fromMask.minute;
        this.second = this.seconds ? fromMask.second : 0;
        this.applyTimeParts();
        return;
      }
      const need = timeMaskDigitCapacity(this.seconds);
      const typing =
        this.timeMaskDigits.length > 0 &&
        (this.timeMaskDigits.length < need ||
          (this.timeFormat === '12' && !this.timeMaskMeridiem));
      if (typing) {
        this.refreshTimeDraft();
        return;
      }
      const parsed = parseFlexibleTimeInput(raw, this.timeFormat);
      if (!parsed) {
        this.refreshTimeDraft();
        return;
      }
      this.hour = parsed.hour;
      this.minute = parsed.minute;
      this.second = this.seconds ? parsed.second : 0;
      this.applyTimeParts();
    },

    nudge(unit, delta) {
      if (this.disabled) return;
      if (!this.timeValue) {
        const now = new Date();
        this.hour = now.getHours();
        this.minute = now.getMinutes();
        this.second = this.seconds ? now.getSeconds() : 0;
      }
      const next = nudgeTimePart(
        { hour: this.hour, minute: this.minute, second: this.second },
        unit,
        delta,
        this.minuteStep,
      );
      this.hour = next.hour;
      this.minute = next.minute;
      this.second = next.second;
      this.applyTimeParts();
    },

    setTimeNow() {
      const now = new Date();
      this.hour = now.getHours();
      this.minute = now.getMinutes();
      this.second = this.seconds ? now.getSeconds() : 0;
      this.applyTimeParts();
    },

    clearTime(opts = {}) {
      this.hour = 0;
      this.minute = 0;
      this.second = 0;
      this.timeValue = '';
      this.timeDraft = '';
      this.timeMaskDigits = '';
      this.timeMaskMeridiem = '';
      if (this.mode === 'time') {
        this.commitState('');
        if (!opts.keepOpen) this.closeTime();
        return;
      }
      if (this.mode === 'datetime') {
        const parts = parsePickerValue(String(this.getValue() || ''), 'datetime');
        if (!parts) {
          this.commitState('');
          if (!opts.keepOpen) this.closeTime();
          return;
        }
        // Clear means drop time to midnight while keeping the date.
        parts.hour = 0;
        parts.minute = 0;
        parts.second = 0;
        this.timeValue = this.composeTimeValue();
        this.refreshTimeDraft();
        this.commitState(formatPickerState(parts, 'datetime', this.seconds));
      }
      if (!opts.keepOpen) this.closeTime();
    },

    onTimeChange() {
      if (this.disabled) return;
      if (this.mode === 'time') {
        this.commitState(this.timeValue || '');
        return;
      }
      if (this.mode === 'datetime') {
        const parts = parsePickerValue(String(this.getValue() || ''), 'datetime');
        const now = new Date();
        const base = parts || {
          year: now.getFullYear(),
          month: now.getMonth() + 1,
          day: now.getDate(),
          hour: 0,
          minute: 0,
          second: 0,
        };
        base.hour = this.hour || 0;
        base.minute = this.minute || 0;
        base.second = this.second || 0;
        this.commitState(formatPickerState(base, 'datetime', this.seconds));
      }
    },
  };
}


  function syncOrbitDatePath(el, path, value) {
    if (!path || !el) return;
    const wire =
      (typeof el.closest === "function" && el.closest("[wire\\:id], [conduit\\:id]")) ||
      el;
    const component =
      wire?.__conduit ||
      wire?.__livewire ||
      window.Livewire?.find?.(wire?.getAttribute?.("wire:id")) ||
      null;
    if (component && typeof component.sync_data_path === "function") {
      component.sync_data_path(path, value);
      return;
    }
    if (component && typeof component.$set === "function") {
      component.$set(path, value);
      return;
    }
    if (component && typeof component.set === "function") {
      component.set(path, value);
    }
  }

  function register(Alpine) {
    if (!Alpine || typeof Alpine.data !== "function") return;
    Alpine.data("orbitDatePicker", (cfg) => {
      const options = cfg && typeof cfg === "object" ? { ...cfg } : {};
      const api = createOrbitDatePicker(options);
      const userInit = api.init;
      api.init = async function () {
        const root = this.$el;
        const state = this.$refs.state;
        if (!options.mode && root?.dataset?.mode) {
          this.mode = root.dataset.mode;
        }
        if (root?.dataset?.seconds != null) {
          this.seconds = root.dataset.seconds === "true" || root.dataset.seconds === "1";
        }
        if (root?.dataset?.timeFormat) {
          this.timeFormat = resolveTimeDisplayFormat(root.dataset.timeFormat);
        }
        if (root?.dataset?.minuteStep) {
          this.minuteStep = resolveMinuteStep(
            { minuteStep: Number(root.dataset.minuteStep) },
            this.seconds,
          );
        }
        if (root?.dataset?.placeholder) {
          this.placeholder = root.dataset.placeholder;
        }
        if (root?.dataset?.min) options.min = root.dataset.min;
        if (root?.dataset?.max) options.max = root.dataset.max;
        const path = root?.dataset?.path || "";
        this.getValue = () => (state ? String(state.value || "") : "");
        this.setValue = (value) => {
          const next = value == null ? "" : String(value);
          if (state) {
            state.value = next;
            state.dispatchEvent(new Event("input", { bubbles: true }));
            state.dispatchEvent(new Event("change", { bubbles: true }));
          }
          if (path) syncOrbitDatePath(root, path, next);
        };
        this.isDisabled = () =>
          Boolean(state?.disabled) || root?.classList?.contains("is-disabled");
        await userInit.call(this);
      };
      return api;
    });
  }

  window.createOrbitDatePicker = createOrbitDatePicker;
  window.orbitDatePicker = createOrbitDatePicker;

  document.addEventListener("alpine:init", () => register(window.Alpine));
  if (window.Alpine) register(window.Alpine);
})();
