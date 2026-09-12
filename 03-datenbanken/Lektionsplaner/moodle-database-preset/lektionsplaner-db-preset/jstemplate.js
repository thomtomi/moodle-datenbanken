(function () {
  "use strict";

  function toArray(list) {
    return Array.prototype.slice.call(list || []);
  }

  function normaliseText(value) {
    return String(value || "")
      .replace(/\u00a0/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function hasValueContent(element) {
    if (!element) {
      return false;
    }
    if (normaliseText(element.textContent)) {
      return true;
    }
    return Boolean(element.querySelector("a[href], img, table, video, audio"));
  }

  function groupHasContent(group) {
    var values = toArray(group.querySelectorAll(".lp-value"));
    if (!values.length) {
      return hasValueContent(group);
    }
    return values.some(hasValueContent);
  }

  function canonicalDate(value) {
    var text = normaliseText(value);
    var match = text.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!match) {
      var local = text.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
      if (local) {
        match = [text, local[3], local[2], local[1]];
      }
    }
    if (!match) {
      return "";
    }
    var year = Number(match[1]);
    var month = Number(match[2]);
    var day = Number(match[3]);
    var date = new Date(0);
    date.setUTCFullYear(year, month - 1, day);
    if (year < 1 || date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) {
      return "";
    }
    return match[1] + "-" + ("0" + month).slice(-2) + "-" + ("0" + day).slice(-2);
  }

  function isoWeek(dateText) {
    var value = canonicalDate(dateText);
    if (!value) {
      return "";
    }
    var date = new Date(value + "T00:00:00Z");
    var weekday = date.getUTCDay() || 7;
    date.setUTCDate(date.getUTCDate() + 4 - weekday);
    var yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
    return String(Math.ceil(((date - yearStart) / 86400000 + 1) / 7));
  }

  function fieldControl(field) {
    if (!field) {
      return null;
    }
    return field.querySelector("select, textarea, input:not([type='hidden'])");
  }

  function findAddControl(root, fieldName) {
    if (!root || !root.querySelector) {
      return null;
    }
    return fieldControl(root.querySelector("[data-lp-field='" + fieldName + "']"));
  }

  function dispatchControlChange(control) {
    if (!control) {
      return;
    }
    try {
      control.dispatchEvent(new Event("input", { bubbles: true }));
      control.dispatchEvent(new Event("change", { bubbles: true }));
    } catch (error) {
      var changeEvent = document.createEvent("HTMLEvents");
      changeEvent.initEvent("change", true, false);
      control.dispatchEvent(changeEvent);
    }
  }

  function setControlValue(control, value) {
    if (!control) {
      return;
    }
    if (control.tagName && control.tagName.toLowerCase() === "select") {
      var hasOption = toArray(control.options).some(function (option) {
        return option.value === value;
      });
      control.value = hasOption ? value : "";
    } else {
      control.value = value;
    }
    dispatchControlChange(control);
  }

  function updateComputedWeeks(root) {
    toArray(root.querySelectorAll(".lp-plan")).forEach(function (plan) {
      var manualWeek = plan.querySelector(".lp-stored-week");
      var computedWeek = plan.querySelector(".lp-js-week");
      var dateValue = plan.querySelector(".lp-date-value");
      if (!computedWeek || !dateValue) {
        return;
      }
      computedWeek.textContent = "";
      if (hasValueContent(manualWeek)) {
        return;
      }
      var week = isoWeek(dateValue.textContent);
      if (week) {
        computedWeek.textContent = "KW " + week;
      }
    });
  }

  function hideEmptyDisplayGroups(root) {
    var groups = toArray(root.querySelectorAll(".lp-display [data-empty-group]")).reverse();
    groups.forEach(function (group) {
      if (groupHasContent(group)) {
        group.classList.remove("lp-hidden");
      } else {
        group.classList.add("lp-hidden");
      }
    });
  }

  function tidySeparators(root) {
    toArray(root.querySelectorAll(".lp-plan-subtitle, .lp-muted")).forEach(function (line) {
      var visibleValues = toArray(line.querySelectorAll(".lp-value")).filter(function (value) {
        return !value.closest(".lp-hidden") && hasValueContent(value);
      });
      toArray(line.querySelectorAll(".lp-dot")).forEach(function (dot) {
        dot.classList.toggle("lp-hidden", visibleValues.length < 2);
      });
    });
  }

  function setPlaceholders(root) {
    toArray(root.querySelectorAll(".lp-db-add .lp-field[data-placeholder]")).forEach(function (field) {
      var control = field.querySelector("input[type='text'], input[type='url'], textarea");
      if (control && !control.getAttribute("placeholder")) {
        control.setAttribute("placeholder", field.getAttribute("data-placeholder"));
      }
    });
  }

  function hasRichContent(value) {
    var content = document.createElement("template");
    content.innerHTML = value;
    return Boolean(normaliseText(content.content.textContent) ||
      content.content.querySelector("img, video, audio, iframe, object, table, a[href]"));
  }

  function controlHasContent(control) {
    if (!control || control.type === "hidden" || /_content1$/.test(control.name || "")) {
      return false;
    }
    if (control.tagName.toLowerCase() === "textarea") {
      return hasRichContent(control.value);
    }
    if (control.tagName && control.tagName.toLowerCase() === "select" && control.multiple) {
      return toArray(control.selectedOptions).some(function (option) {
        return normaliseText(option.value) && option.value !== "xxx";
      });
    }
    if (typeof control.value === "string" && normaliseText(control.value)) {
      return true;
    }
    return false;
  }

  function enhanceDateInputs(root) {
    toArray(root.querySelectorAll(".lp-db-add [data-lp-date]")).forEach(function (field) {
      var control = field.querySelector("input:not([type='hidden'])");
      if (!control || control.getAttribute("data-lp-date-bound") === "1") {
        return;
      }
      control.setAttribute("data-lp-date-bound", "1");
      var hint = document.createElement("p");
      hint.className = "lp-date-help";
      hint.id = control.id + "-lp-date-help";
      hint.textContent = "Dieses Datum konnte nicht erkannt werden. Verwenden Sie JJJJ-MM-TT oder TT.MM.JJJJ. Der vorhandene Wert bleibt erhalten.";
      hint.hidden = true;
      field.appendChild(hint);
      var describedBy = (control.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean);
      describedBy.push(hint.id);
      control.setAttribute("aria-describedby", describedBy.join(" "));
      var enhance = function () {
        var value = canonicalDate(control.value);
        if (normaliseText(control.value) && !value) {
          hint.hidden = false;
          return;
        }
        // Assign a validated value before changing type: browsers erase non-ISO values.
        control.value = value;
        control.setAttribute("type", "date");
        hint.hidden = true;
      };
      control.addEventListener("change", enhance);
      enhance();
    });
  }

  function bindAutoWeeks(root) {
    toArray(root.querySelectorAll(".lp-db-add")).forEach(function (form) {
      if (form.getAttribute("data-lp-week-bound") === "1") {
        return;
      }
      var dateControl = findAddControl(form, "unterrichtsdatum");
      var weekControl = findAddControl(form, "kalenderwoche");
      var output = form.querySelector("[data-lp-week-output]");
      if (!dateControl || !output) {
        return;
      }
      form.setAttribute("data-lp-week-bound", "1");
      var sync = function () {
        var week = isoWeek(dateControl.value);
        var storage = form.querySelector(".lp-auto-week-storage");
        var unknownDate = normaliseText(dateControl.value) && !week;
        if (storage) {
          storage.classList.toggle("lp-enhanced", !unknownDate);
        }
        if (unknownDate) {
          output.textContent = "Kalenderwoche nicht berechenbar";
          return;
        }
        var text = week ? "KW " + week : "";
        output.textContent = text;
        if (weekControl) {
          setControlValue(weekControl, text);
        }
      };
      dateControl.addEventListener("input", sync);
      dateControl.addEventListener("change", sync);
      sync();
    });
  }

  function selectHasValue(select, value) {
    return toArray(select.options).some(function (option) {
      return option.value === value;
    });
  }

  function bindLessonSlots(root) {
    toArray(root.querySelectorAll(".lp-db-add [data-lp-slot-select]")).forEach(function (slotSelect) {
      if (slotSelect.getAttribute("data-lp-bound") === "1") {
        return;
      }
      var container = slotSelect.closest(".lp-db-add");
      var startControl = findAddControl(container, slotSelect.getAttribute("data-lp-target-start"));
      var endControl = findAddControl(container, slotSelect.getAttribute("data-lp-target-end"));
      if (!startControl || !endControl) {
        return;
      }
      slotSelect.setAttribute("data-lp-bound", "1");
      slotSelect.disabled = false;
      var syncSlotFromControls = function () {
        var value = normaliseText(startControl.value) && normaliseText(endControl.value)
          ? startControl.value + "|" + endControl.value
          : "";
        slotSelect.value = selectHasValue(slotSelect, value) ? value : "";
      };
      slotSelect.addEventListener("change", function () {
        var parts = slotSelect.value.split("|");
        setControlValue(startControl, parts[0] || "");
        setControlValue(endControl, parts[1] || "");
      });
      startControl.addEventListener("change", syncSlotFromControls);
      endControl.addEventListener("change", syncSlotFromControls);
      syncSlotFromControls();
    });
  }

  function enhanceTopicPicker(root) {
    toArray(root.querySelectorAll(".lp-db-add [data-lp-topic-picker]")).forEach(function (field) {
      if (field.getAttribute("data-lp-enhanced") === "1") {
        return;
      }
      var select = field.querySelector("select[multiple]");
      if (!select) {
        return;
      }
      field.setAttribute("data-lp-enhanced", "1");
      var picker = document.createElement("div");
      picker.className = "lp-chip-picker";
      picker.setAttribute("role", "group");
      picker.setAttribute("aria-label", "Themen auswählen");
      var buttons = [];
      var syncButtons = function () {
        buttons.forEach(function (button) {
          var option = button.lpOption;
          button.classList.toggle("is-selected", option.selected);
          button.setAttribute("aria-pressed", option.selected ? "true" : "false");
        });
      };
      toArray(select.options).forEach(function (option) {
        if (!normaliseText(option.value)) {
          return;
        }
        var button = document.createElement("button");
        button.type = "button";
        button.className = "lp-topic-chip";
        button.textContent = option.textContent;
        button.lpOption = option;
        button.addEventListener("click", function () {
          option.selected = !option.selected;
          syncButtons();
          dispatchControlChange(select);
        });
        buttons.push(button);
        picker.appendChild(button);
      });
      select.classList.add("lp-native-select-hidden");
      select.tabIndex = -1;
      select.setAttribute("aria-hidden", "true");
      select.parentNode.insertBefore(picker, select.nextSibling);
      select.addEventListener("change", syncButtons);
      syncButtons();
    });
  }

  function bindLearningGoalStarter(root) {
    toArray(root.querySelectorAll(".lp-db-add [data-lp-prefill]")).forEach(function (field) {
      var textarea = field.querySelector("textarea");
      if (!textarea || field.getAttribute("data-lp-starter-bound") === "1") {
        return;
      }
      field.setAttribute("data-lp-starter-bound", "1");
      var button = document.createElement("button");
      button.type = "button";
      button.className = "lp-starter-button";
      button.textContent = "Satzanfang einfügen";
      var status = document.createElement("p");
      status.className = "lp-add-note";
      status.setAttribute("role", "status");
      button.addEventListener("click", function () {
        var value = field.getAttribute("data-lp-prefill") || "";
        var tiny = window.tinyMCE || window.tinymce;
        var editor = tiny && tiny.get(textarea.id);
        var editable = field.querySelector("[contenteditable='true']");
        status.textContent = "";
        if (editor && editor.initialized) {
          if (hasRichContent(editor.getContent())) {
            status.textContent = "Es sind bereits Lernziele vorhanden.";
            return;
          }
          var paragraph = document.createElement("p");
          paragraph.textContent = value;
          editor.undoManager.transact(function () { editor.setContent(paragraph.outerHTML); });
          editor.save();
          editor.focus();
        } else if (editable) {
          if (hasRichContent(editable.innerHTML)) {
            status.textContent = "Es sind bereits Lernziele vorhanden.";
            return;
          }
          editable.textContent = value;
          dispatchControlChange(editable);
        } else if (editor || document.querySelector('script[data-tinymce="tinymce"]') ||
            window.getComputedStyle(textarea).display === "none") {
          status.textContent = "Der Texteditor ist noch nicht bereit. Versuchen Sie es gleich nochmals oder geben Sie den Satzanfang direkt ein.";
          return;
        } else {
          if (controlHasContent(textarea)) {
            status.textContent = "Es sind bereits Lernziele vorhanden.";
            return;
          }
          textarea.value = value;
          textarea.focus();
        }
        dispatchControlChange(textarea);
        status.textContent = "Satzanfang eingefügt.";
      });
      field.appendChild(button);
      field.appendChild(status);
    });
  }

  function openFilledDetails(root) {
    toArray(root.querySelectorAll(".lp-db-add details[data-open-if-filled]")).forEach(function (details) {
      if (details.getAttribute("data-lp-open-checked") === "1") {
        return;
      }
      details.setAttribute("data-lp-open-checked", "1");
      var controls = toArray(details.querySelectorAll("input, textarea, select"));
      if (controls.some(controlHasContent)) {
        details.setAttribute("open", "open");
      }
    });
  }

  function init() {
    var root = document;
    updateComputedWeeks(root);
    hideEmptyDisplayGroups(root);
    tidySeparators(root);
    setPlaceholders(root);
    enhanceDateInputs(root);
    bindLearningGoalStarter(root);
    bindAutoWeeks(root);
    bindLessonSlots(root);
    enhanceTopicPicker(root);
    openFilledDetails(root);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
