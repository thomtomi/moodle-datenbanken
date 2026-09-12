const state = {
  currentPlan: null,
  plans: [],
  classes: [],
  latestPlan: null,
  searchResults: [],
  searchTimer: null,
  suggestionTimer: null,
};

const draftStorageKey = "lektionsplaner-draft-v1";
const $ = (selector) => document.querySelector(selector);
const $$ = (selector, root = document) =>
  Array.from(root.querySelectorAll(selector));

function emptyRichItem() {
  return { id: newId(), content_html: "" };
}

function emptyLesson(number) {
  return {
    id: newId(),
    label: `${number}. Lektion`,
    start_time: "",
    end_time: "",
    activities: [emptyRichItem()],
  };
}

function createEmptyPlan() {
  return {
    id: "",
    class_name: "",
    date: new Date().toISOString().slice(0, 10),
    lessons: [emptyLesson(1)],
    homework: [],
    assessment: {
      title: "",
      date: "",
      start_time: "",
      end_time: "",
      topics: [],
    },
    support_course: {
      title: "",
      date: "",
      start_time: "",
      end_time: "",
      location_html: "",
      teams_url: "",
      registration_url: "",
      note_html: "",
    },
    learning_objectives: [],
  };
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function asObject(value) {
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function escapeHtml(value) {
  const replacements = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return String(value ?? "").replace(/[&<>"']/g, (match) => replacements[match]);
}

function newId() {
  const cryptoApi = globalThis.crypto;
  if (cryptoApi && typeof cryptoApi.randomUUID === "function") {
    return cryptoApi.randomUUID();
  }
  if (cryptoApi && typeof cryptoApi.getRandomValues === "function") {
    const values = new Uint32Array(2);
    cryptoApi.getRandomValues(values);
    return `entry-${Date.now()}-${values[0].toString(36)}-${values[1].toString(36)}`;
  }
  return `entry-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function normaliseRichItems(items) {
  return asArray(items).map((item) => {
    const source = asObject(item);
    return {
      id: typeof source.id === "string" && source.id ? source.id : newId(),
      content_html:
        typeof source.content_html === "string" ? source.content_html : "",
    };
  });
}

function normaliseAssessment(value) {
  const source = asObject(value);
  return {
    title: typeof source.title === "string" ? source.title : "",
    date: typeof source.date === "string" ? source.date : "",
    start_time: typeof source.start_time === "string" ? source.start_time : "",
    end_time: typeof source.end_time === "string" ? source.end_time : "",
    topics: asArray(source.topics).map((topic) => {
      const topicSource = asObject(topic);
      return {
        title: typeof topicSource.title === "string" ? topicSource.title : "",
        description_html:
          typeof topicSource.description_html === "string"
            ? topicSource.description_html
            : "",
      };
    }),
  };
}

function normaliseSupportCourse(value) {
  const source = asObject(value);
  return {
    title: typeof source.title === "string" ? source.title : "",
    date: typeof source.date === "string" ? source.date : "",
    start_time: typeof source.start_time === "string" ? source.start_time : "",
    end_time: typeof source.end_time === "string" ? source.end_time : "",
    location_html:
      typeof source.location_html === "string" ? source.location_html : "",
    teams_url: typeof source.teams_url === "string" ? source.teams_url : "",
    registration_url:
      typeof source.registration_url === "string"
        ? source.registration_url
        : "",
    note_html: typeof source.note_html === "string" ? source.note_html : "",
  };
}

function normalisePlan(value) {
  const source = asObject(value);
  const lessons = asArray(source.lessons).map((lesson, index) => {
    const lessonSource = asObject(lesson);
    const activities = normaliseRichItems(lessonSource.activities);
    return {
      id:
        typeof lessonSource.id === "string" && lessonSource.id
          ? lessonSource.id
          : newId(),
      label:
        typeof lessonSource.label === "string" && lessonSource.label.trim()
          ? lessonSource.label
          : `${index + 1}. Lektion`,
      start_time:
        typeof lessonSource.start_time === "string"
          ? lessonSource.start_time
          : "",
      end_time:
        typeof lessonSource.end_time === "string" ? lessonSource.end_time : "",
      activities: activities.length ? activities : [emptyRichItem()],
    };
  });

  return {
    id: typeof source.id === "string" ? source.id : "",
    class_name: typeof source.class_name === "string" ? source.class_name : "",
    date:
      typeof source.date === "string" && source.date
        ? source.date
        : new Date().toISOString().slice(0, 10),
    lessons: lessons.length ? lessons : [emptyLesson(1)],
    homework: normaliseRichItems(source.homework),
    assessment: normaliseAssessment(source.assessment),
    support_course: normaliseSupportCourse(source.support_course),
    learning_objectives: normaliseRichItems(source.learning_objectives),
  };
}

function hasMeaningfulValue(value) {
  if (Array.isArray(value)) return value.length > 0;
  if (!value || typeof value !== "object") return Boolean(value);
  return Object.keys(value).some((key) => hasMeaningfulValue(value[key]));
}

function isoWeek(dateText) {
  if (!dateText) return null;
  const [year, month, day] = dateText.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  const weekday = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() + 4 - weekday);
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  return Math.ceil(((date - yearStart) / 86400000 + 1) / 7);
}

function formatDate(dateText) {
  if (!dateText) return "";
  return new Intl.DateTimeFormat("de-CH", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  }).format(new Date(`${dateText}T12:00:00`));
}

function renderRichItems(items, section) {
  items = asArray(items);
  if (!items.length) {
    return '<p class="muted-message">Noch keine Einträge.</p>';
  }
  return items
    .map(
      (item) => `
        <div class="rich-item-row" data-rich-section="${section}" data-item-id="${item.id}">
          <textarea class="rich-content" rows="3" aria-label="HTML-Inhalt">${escapeHtml(item.content_html)}</textarea>
          <button class="icon-button danger" data-action="remove-rich-item" aria-label="Eintrag entfernen" title="Eintrag entfernen" type="button">×</button>
        </div>`,
    )
    .join("");
}

function renderLessons() {
  const lessons = state.currentPlan.lessons;
  $("#lessons").innerHTML = lessons
    .map(
      (lesson, index) => `
        <article class="lesson-card" data-lesson-id="${lesson.id}">
          <div class="lesson-card-header">
            <label>Bezeichnung
              <input class="lesson-label" value="${escapeHtml(lesson.label)}" />
            </label>
            <label>Beginn
              <input class="lesson-start" type="time" value="${escapeHtml(lesson.start_time)}" />
            </label>
            <label>Ende
              <input class="lesson-end" type="time" value="${escapeHtml(lesson.end_time)}" />
            </label>
            <div class="lesson-controls" aria-label="Lektionsblock verschieben oder entfernen">
              <button class="icon-button" data-action="move-lesson-up" aria-label="Nach oben verschieben" title="Nach oben verschieben" type="button" ${index === 0 ? "disabled" : ""}>↑</button>
              <button class="icon-button" data-action="move-lesson-down" aria-label="Nach unten verschieben" title="Nach unten verschieben" type="button" ${index === lessons.length - 1 ? "disabled" : ""}>↓</button>
              <button class="icon-button danger" data-action="remove-lesson" aria-label="Lektionsblock entfernen" title="Lektionsblock entfernen" type="button">×</button>
            </div>
          </div>
          <div class="lesson-activity-list">
            ${lesson.activities
              .map(
                (activity) => `
                  <div class="activity-row" data-activity-id="${activity.id}">
                    <textarea class="activity-content" rows="3" aria-label="Aktivität, freies HTML möglich">${escapeHtml(activity.content_html)}</textarea>
                    <button class="icon-button danger" data-action="remove-activity" aria-label="Aktivität entfernen" title="Aktivität entfernen" type="button">×</button>
                  </div>`,
              )
              .join("")}
          </div>
          <button class="icon-text-button add-activity-button" data-action="add-activity" type="button">+ Aktivität</button>
        </article>`,
    )
    .join("");
  updateSearchTargetOptions();
}

function renderStaticFields() {
  const plan = state.currentPlan;
  $("#class-name").value = plan.class_name || "";
  $("#lesson-date").value = plan.date || "";
  $("#assessment-title").value = plan.assessment?.title || "";
  $("#assessment-date").value = plan.assessment?.date || "";
  $("#assessment-start").value = plan.assessment?.start_time || "";
  $("#assessment-end").value = plan.assessment?.end_time || "";
  $("#support-title").value = plan.support_course?.title || "";
  $("#support-date").value = plan.support_course?.date || "";
  $("#support-start").value = plan.support_course?.start_time || "";
  $("#support-end").value = plan.support_course?.end_time || "";
  $("#support-location").value = plan.support_course?.location_html || "";
  $("#support-teams-url").value = plan.support_course?.teams_url || "";
  $("#support-registration-url").value =
    plan.support_course?.registration_url || "";
  $("#support-note").value = plan.support_course?.note_html || "";
  $("#homework-items").innerHTML = renderRichItems(plan.homework, "homework");
  $("#learning-objective-items").innerHTML = renderRichItems(
    plan.learning_objectives,
    "learning_objectives",
  );
  $("#assessment-topics").innerHTML = renderAssessmentTopics(
    plan.assessment?.topics || [],
  );
  updateCalendarWeek();
}

function renderAssessmentTopics(topics) {
  if (!topics.length) return '<p class="muted-message">Noch keine Themen.</p>';
  return topics
    .map(
      (topic, index) => `
        <div class="topic-row" data-topic-index="${index}">
          <label>Thema
            <input class="topic-title" value="${escapeHtml(topic.title)}" />
          </label>
          <label>Beschreibung (freies HTML möglich)
            <textarea class="topic-description" rows="2">${escapeHtml(topic.description_html)}</textarea>
          </label>
          <button class="icon-button danger" data-action="remove-assessment-topic" aria-label="Thema entfernen" title="Thema entfernen" type="button">×</button>
        </div>`,
    )
    .join("");
}

function renderPlan() {
  state.currentPlan = normalisePlan(state.currentPlan);
  renderStaticFields();
  renderLessons();
  renderLatestPlanSuggestion();
  updatePreview();
}

function syncPlanFromForm() {
  const plan = state.currentPlan;
  plan.class_name = $("#class-name").value.trim();
  plan.date = $("#lesson-date").value;
  plan.lessons = $$(".lesson-card").map((card, index) => ({
    id: card.dataset.lessonId,
    label:
      card.querySelector(".lesson-label").value.trim() ||
      `${index + 1}. Lektion`,
    start_time: card.querySelector(".lesson-start").value,
    end_time: card.querySelector(".lesson-end").value,
    activities: $$(".activity-row", card)
      .map((row) => ({
        id: row.dataset.activityId,
        content_html: row.querySelector(".activity-content").value,
      }))
      .filter((activity) => activity.content_html.trim()),
  }));
  plan.homework = readRichItems("#homework-items", "homework");
  plan.learning_objectives = readRichItems(
    "#learning-objective-items",
    "learning_objectives",
  );
  plan.assessment = {
    title: $("#assessment-title").value.trim(),
    date: $("#assessment-date").value,
    start_time: $("#assessment-start").value,
    end_time: $("#assessment-end").value,
    topics: $$("#assessment-topics .topic-row")
      .map((row) => ({
        title: row.querySelector(".topic-title").value.trim(),
        description_html: row.querySelector(".topic-description").value,
      }))
      .filter((topic) => topic.title || topic.description_html.trim()),
  };
  plan.support_course = {
    title: $("#support-title").value.trim(),
    date: $("#support-date").value,
    start_time: $("#support-start").value,
    end_time: $("#support-end").value,
    location_html: $("#support-location").value,
    teams_url: $("#support-teams-url").value.trim(),
    registration_url: $("#support-registration-url").value.trim(),
    note_html: $("#support-note").value,
  };
  return plan;
}

function readRichItems(containerSelector, section) {
  return $$(`${containerSelector} [data-rich-section="${section}"]`)
    .map((row) => ({
      id: row.dataset.itemId,
      content_html: row.querySelector(".rich-content").value,
    }))
    .filter((item) => item.content_html.trim());
}

function updateCalendarWeek() {
  const week = isoWeek($("#lesson-date").value);
  $("#calendar-week").textContent = week ? `KW ${week}` : "KW -";
}

function renderClientFragment(plan) {
  const parts = [
    `<!--<h1>${escapeHtml(plan.class_name)} ${escapeHtml(plan.date)}</h1>-->`,
  ];
  plan.lessons.forEach((lesson) => {
    const time =
      lesson.start_time && lesson.end_time
        ? `, 🕣 ${lesson.start_time} bis ${lesson.end_time}`
        : lesson.start_time
          ? `, 🕣 ${lesson.start_time}`
          : "";
    parts.push(`<h4>${escapeHtml(lesson.label)}${time}</h4>`);
    if (lesson.activities.length) {
      parts.push(
        `<ul>${lesson.activities.map((item) => `<li>${item.content_html}</li>`).join("")}</ul>`,
      );
    }
  });
  if (plan.homework.length) {
    parts.push("<h4>Hausaufgaben</h4><h5>📝 Arbeitsaufträge</h5>");
    parts.push(
      `<ul>${plan.homework.map((item) => `<li>${item.content_html}</li>`).join("")}</ul>`,
    );
  }
  if (plan.assessment.title) {
    parts.push(`<h4>${escapeHtml(plan.assessment.title)}</h4>`);
    const assessmentDetails = [];
    if (plan.assessment.date) {
      assessmentDetails.push(`🗓 ${escapeHtml(formatDate(plan.assessment.date))}`);
    }
    if (plan.assessment.start_time && plan.assessment.end_time) {
      assessmentDetails.push(
        `🕣 ${escapeHtml(plan.assessment.start_time)} bis ${escapeHtml(plan.assessment.end_time)} Uhr`,
      );
    } else if (plan.assessment.start_time) {
      assessmentDetails.push(`🕣 ${escapeHtml(plan.assessment.start_time)} Uhr`);
    }
    if (assessmentDetails.length) {
      parts.push(`<p>${assessmentDetails.join("<br />")}</p>`);
    }
    if (plan.assessment.topics.length) {
      parts.push(
        `<dl>${plan.assessment.topics.map((topic) => `<dt>${escapeHtml(topic.title)}</dt><dd>${topic.description_html}</dd>`).join("")}</dl>`,
      );
    }
  }
  if (hasMeaningfulValue(plan.support_course)) {
    parts.push("<h4>Stützkurs</h4>");
    if (plan.support_course.title)
      parts.push(`<h5>📍 ${escapeHtml(plan.support_course.title)}</h5>`);
    const details = [];
    if (plan.support_course.date)
      details.push(`🗓 ${escapeHtml(formatDate(plan.support_course.date))}`);
    if (plan.support_course.start_time && plan.support_course.end_time) {
      details.push(
        `🕠 von ${escapeHtml(plan.support_course.start_time)} bis ${escapeHtml(plan.support_course.end_time)} Uhr`,
      );
    } else if (plan.support_course.start_time) {
      details.push(`🕠 ab ${escapeHtml(plan.support_course.start_time)} Uhr`);
    }
    if (plan.support_course.location_html) {
      let location = `🏫 ${plan.support_course.location_html}`;
      if (plan.support_course.teams_url) {
        location += ` oder online via <a href="${escapeHtml(plan.support_course.teams_url)}">Teams</a>`;
      }
      details.push(location);
    } else if (plan.support_course.teams_url) {
      details.push(
        `🔗 Online via <a href="${escapeHtml(plan.support_course.teams_url)}">Teams</a>`,
      );
    }
    if (details.length) parts.push(`<p>${details.join("<br />")}</p>`);
    if (plan.support_course.note_html)
      parts.push(`<p>🗫 ${plan.support_course.note_html}</p>`);
    if (plan.support_course.registration_url) {
      parts.push(
        `<p>🔗 <a href="${escapeHtml(plan.support_course.registration_url)}">Anmeldung zum Stützkurs</a></p>`,
      );
    }
  }
  if (plan.learning_objectives.length) {
    parts.push("<h5>Lernziele</h5><p>Sie sind in der Lage ...</p>");
    parts.push(
      `<ol>${plan.learning_objectives.map((item) => `<li>${item.content_html}</li>`).join("")}</ol>`,
    );
  }
  return parts.join("\n\n");
}

function updatePreview() {
  const plan = syncPlanFromForm();
  const fragment = renderClientFragment(plan);
  $("#character-count").textContent =
    `${fragment.length.toLocaleString("de-CH")} Zeichen${fragment.length > 9000 ? " - möglicherweise zu lang" : ""}`;
  const previewStyle = `
    <style>
      body { color: #17221f; font: 16px/1.55 "Noto Sans", sans-serif; padding: 12px; }
      h4 { margin: 20px 0 8px; color: #004d49; } h5 { margin: 16px 0 6px; color: #006d68; }
      p { margin: 8px 0; } ul, ol { margin-top: 5px; padding-left: 25px; }
      li { margin: 5px 0; } dt { font-weight: 700; margin-top: 8px; } dd { margin-left: 18px; }
      a { color: #006d68; } table { border-collapse: collapse; } td, th { border: 1px solid #d5ded8; padding: 5px; }
    </style>`;
  $("#preview-frame").srcdoc = `${previewStyle}${fragment}`;
  saveDraft();
}

function saveDraft() {
  try {
    localStorage.setItem(draftStorageKey, JSON.stringify(state.currentPlan));
  } catch {
    // Ein fehlender Browser-Speicher verhindert die reguläre Serverspeicherung nicht.
  }
}

function restoreDraft() {
  try {
    const draft = localStorage.getItem(draftStorageKey);
    return draft ? normalisePlan(JSON.parse(draft)) : null;
  } catch {
    return null;
  }
}

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const contentType = response.headers.get("Content-Type") || "";
  const body = contentType.includes("application/json")
    ? await response.json().catch(() => ({}))
    : {};
  if (!response.ok)
    throw new Error(
      body.error ||
        `Die Anfrage konnte nicht verarbeitet werden (HTTP ${response.status}).`,
    );
  return body;
}

async function loadPlanIndex() {
  const [plansResponse, classesResponse] = await Promise.all([
    request("/api/plans"),
    request("/api/classes"),
  ]);
  state.plans = asArray(plansResponse.plans);
  state.classes = asArray(classesResponse.classes).filter(
    (className) => typeof className === "string",
  );
  renderPlanList();
  renderClassSuggestions();
}

function renderPlanList() {
  const filter = $("#plan-filter").value.trim().toLocaleLowerCase("de-CH");
  const plans = state.plans.filter((plan) =>
    `${plan.class_name} ${plan.date}`
      .toLocaleLowerCase("de-CH")
      .includes(filter),
  );
  $("#plan-list").innerHTML = plans.length
    ? plans
        .map(
          (plan) => `
          <div class="plan-row">
            <button class="plan-load-button" data-action="load-plan" data-plan-id="${plan.id}" type="button">
              <strong>${escapeHtml(plan.class_name)}</strong>
              <span>${escapeHtml(plan.date)} · KW ${plan.calendar_week}</span>
            </button>
            <button class="delete-plan-button" data-action="delete-plan" data-plan-id="${plan.id}" aria-label="Planung löschen" title="Planung löschen" type="button">×</button>
          </div>`,
        )
        .join("")
    : '<p class="muted-message">Noch keine gespeicherten Planungen.</p>';
}

function renderClassSuggestions() {
  $("#class-suggestions").innerHTML = state.classes
    .map((className) => `<option value="${escapeHtml(className)}"></option>`)
    .join("");
  const selected = $("#search-class-filter").value;
  $("#search-class-filter").innerHTML = [
    '<option value="">Alle Klassen</option>',
    ...state.classes.map(
      (className) =>
        `<option value="${escapeHtml(className)}">${escapeHtml(className)}</option>`,
    ),
  ].join("");
  $("#search-class-filter").value = selected;
}

function updateSearchTargetOptions() {
  const target = $("#search-target");
  if (!target) return;
  const selected = target.value;
  target.innerHTML = state.currentPlan.lessons
    .map(
      (lesson) =>
        `<option value="${lesson.id}">${escapeHtml(lesson.label)}</option>`,
    )
    .join("");
  target.value = state.currentPlan.lessons.some(
    (lesson) => lesson.id === selected,
  )
    ? selected
    : state.currentPlan.lessons[0]?.id || "";
}

async function loadPlan(planId) {
  try {
    const response = await request(`/api/plans/${encodeURIComponent(planId)}`);
    state.currentPlan = normalisePlan(response.plan);
    state.latestPlan = null;
    renderPlan();
    showToast("Planung geladen.");
    requestLatestPlan();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function savePlan(showSuccess = true) {
  syncPlanFromForm();
  const response = await request("/api/plans", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(state.currentPlan),
  });
  state.currentPlan = normalisePlan(response.plan);
  localStorage.removeItem(draftStorageKey);
  await loadPlanIndex();
  $("#export-status").textContent =
    `Gespeichert: ${new Date(response.plan.updated_at).toLocaleString("de-CH")}`;
  if (showSuccess) showToast("Planung gespeichert.");
  return response.plan;
}

async function ensureSaved() {
  return savePlan(false);
}

async function copyMoodleHtml() {
  try {
    const plan = await ensureSaved();
    const response = await request(
      `/api/plans/${encodeURIComponent(plan.id)}/export`,
    );
    await copyToClipboard(response.html);
    $("#export-status").textContent =
      "Moodle-HTML in die Zwischenablage kopiert.";
    showToast("Moodle-HTML kopiert.");
  } catch (error) {
    showToast(error.message, true);
  }
}

async function archivePlan() {
  try {
    const plan = await ensureSaved();
    const response = await request(
      `/api/plans/${encodeURIComponent(plan.id)}/archive`,
      { method: "POST" },
    );
    $("#export-status").textContent = `Archiviert: ${response.archive_path}`;
    showToast("HTML-Archiv aktualisiert.");
  } catch (error) {
    showToast(error.message, true);
  }
}

async function copyToClipboard(value) {
  try {
    if (!navigator.clipboard || typeof navigator.clipboard.writeText !== "function") {
      throw new Error("Clipboard API nicht verfügbar.");
    }
    await navigator.clipboard.writeText(value);
  } catch {
    $("#export-fallback").value = value;
    const dialog = $("#export-dialog");
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
    $("#export-fallback").select();
    throw new Error(
      "Die Zwischenablage ist gesperrt. Der HTML-Code steht im geöffneten Dialog bereit.",
    );
  }
}

async function searchActivities() {
  const query = $("#activity-search").value.trim();
  if (!query) {
    state.searchResults = [];
    $("#search-results").innerHTML = "";
    $("#search-message").textContent = "Suchbegriff eingeben.";
    return;
  }
  try {
    const classFilter = $("#search-class-filter").value;
    const response = await request(
      `/api/search?query=${encodeURIComponent(query)}&class=${encodeURIComponent(classFilter)}`,
    );
    state.searchResults = response.activities;
    $("#search-message").textContent = response.activities.length
      ? `${response.activities.length} Treffer`
      : "Keine passenden Aktivitäten gefunden.";
    renderSearchResults();
    if (response.warnings.length) showToast(response.warnings.join(" "), true);
  } catch (error) {
    showToast(error.message, true);
  }
}

function renderSearchResults() {
  $("#search-results").innerHTML = state.searchResults
    .map(
      (activity, index) => `
        <article class="search-result">
          <p>${escapeHtml(activity.plain_text)}</p>
          <div class="search-result-footer">
            <span class="result-meta">${escapeHtml(activity.class_name)} · ${escapeHtml(activity.lesson_label)}<br />${escapeHtml(activity.source)} · ${escapeHtml(activity.source_type)}</span>
            <button class="icon-text-button" data-action="adopt-activity" data-activity-index="${index}" type="button">Übernehmen</button>
          </div>
        </article>`,
    )
    .join("");
}

function adoptActivity(index) {
  syncPlanFromForm();
  const activity = state.searchResults[index];
  const targetId = $("#search-target").value;
  const lesson = state.currentPlan.lessons.find(
    (entry) => entry.id === targetId,
  );
  if (!activity || !lesson) {
    showToast("Bitte zuerst einen Ziel-Lektionsblock wählen.", true);
    return;
  }
  lesson.activities.push({ id: newId(), content_html: activity.content_html });
  renderLessons();
  updatePreview();
  showToast("Aktivität übernommen.");
}

async function requestLatestPlan() {
  const className = $("#class-name").value.trim();
  if (!className) {
    state.latestPlan = null;
    renderLatestPlanSuggestion();
    return;
  }
  try {
    const response = await request(
      `/api/plans/latest?class=${encodeURIComponent(className)}`,
    );
    const latestPlan = response.plan ? normalisePlan(response.plan) : null;
    state.latestPlan =
      latestPlan?.id === state.currentPlan.id ? null : latestPlan;
    renderLatestPlanSuggestion();
  } catch (error) {
    showToast(error.message, true);
  }
}

function renderLatestPlanSuggestion() {
  const container = $("#latest-plan-suggestion");
  const plan = state.latestPlan;
  if (!plan) {
    container.hidden = true;
    container.innerHTML = "";
    return;
  }
  const available = [
    ["homework", "Hausaufgaben"],
    ["assessment", "Leistungsnachweis"],
    ["support_course", "Stützkurs"],
    ["learning_objectives", "Lernziele"],
  ].filter(([property]) => {
    const value = plan[property];
    return hasMeaningfulValue(value);
  });
  if (!available.length) {
    container.hidden = true;
    return;
  }
  container.hidden = false;
  container.innerHTML = `
    <span class="suggestion-label">Aus ${escapeHtml(plan.date)} übernehmen:</span>
    ${available
      .map(
        ([property, label]) =>
          `<button class="suggestion-copy-button" data-action="adopt-latest" data-property="${property}" type="button">${label}</button>`,
      )
      .join("")}`;
}

function adoptLatest(property) {
  if (!state.latestPlan) return;
  syncPlanFromForm();
  state.currentPlan[property] = clone(state.latestPlan[property]);
  if (Array.isArray(state.currentPlan[property])) {
    state.currentPlan[property] = state.currentPlan[property].map((item) => ({
      ...item,
      id: newId(),
    }));
  }
  renderPlan();
  showToast("Block aus der letzten Planung übernommen.");
}

async function deletePlan(planId) {
  if (!window.confirm("Diese Planung wirklich löschen?")) return;
  try {
    await request(`/api/plans/${encodeURIComponent(planId)}`, {
      method: "DELETE",
    });
    if (state.currentPlan.id === planId) state.currentPlan = createEmptyPlan();
    await loadPlanIndex();
    renderPlan();
    showToast("Planung gelöscht.");
  } catch (error) {
    showToast(error.message, true);
  }
}

function addRichItem(section) {
  syncPlanFromForm();
  state.currentPlan[section].push(emptyRichItem());
  renderPlan();
}

function handleAction(event) {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const action = button.dataset.action;
  if (action === "load-plan") loadPlan(button.dataset.planId);
  if (action === "delete-plan") deletePlan(button.dataset.planId);
  if (action === "adopt-activity")
    adoptActivity(Number(button.dataset.activityIndex));
  if (action === "adopt-latest") adoptLatest(button.dataset.property);

  if (
    [
      "add-activity",
      "remove-activity",
      "remove-lesson",
      "move-lesson-up",
      "move-lesson-down",
    ].includes(action)
  ) {
    syncPlanFromForm();
    const card = button.closest(".lesson-card");
    const lessonIndex = state.currentPlan.lessons.findIndex(
      (lesson) => lesson.id === card.dataset.lessonId,
    );
    const lesson = state.currentPlan.lessons[lessonIndex];
    if (action === "add-activity") lesson.activities.push(emptyRichItem());
    if (action === "remove-activity") {
      const row = button.closest(".activity-row");
      lesson.activities = lesson.activities.filter(
        (item) => item.id !== row.dataset.activityId,
      );
    }
    if (action === "remove-lesson" && state.currentPlan.lessons.length > 1) {
      state.currentPlan.lessons.splice(lessonIndex, 1);
    }
    if (action === "move-lesson-up" && lessonIndex > 0) {
      [
        state.currentPlan.lessons[lessonIndex - 1],
        state.currentPlan.lessons[lessonIndex],
      ] = [
        state.currentPlan.lessons[lessonIndex],
        state.currentPlan.lessons[lessonIndex - 1],
      ];
    }
    if (
      action === "move-lesson-down" &&
      lessonIndex < state.currentPlan.lessons.length - 1
    ) {
      [
        state.currentPlan.lessons[lessonIndex + 1],
        state.currentPlan.lessons[lessonIndex],
      ] = [
        state.currentPlan.lessons[lessonIndex],
        state.currentPlan.lessons[lessonIndex + 1],
      ];
    }
    renderPlan();
  }

  if (action === "remove-rich-item") {
    syncPlanFromForm();
    const row = button.closest("[data-rich-section]");
    const section = row.dataset.richSection;
    state.currentPlan[section] = state.currentPlan[section].filter(
      (item) => item.id !== row.dataset.itemId,
    );
    renderPlan();
  }

  if (action === "remove-assessment-topic") {
    syncPlanFromForm();
    const row = button.closest("[data-topic-index]");
    state.currentPlan.assessment.topics.splice(
      Number(row.dataset.topicIndex),
      1,
    );
    renderPlan();
  }
}

function showToast(message, isError = false) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.style.background = isError ? "#8f3528" : "";
  toast.classList.add("visible");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(
    () => toast.classList.remove("visible"),
    4200,
  );
}

function bindEvents() {
  document.addEventListener("click", handleAction);
  $("#new-plan-button").addEventListener("click", () => {
    state.currentPlan = createEmptyPlan();
    state.latestPlan = null;
    renderPlan();
    showToast("Neue Planung angelegt.");
  });
  $("#save-button").addEventListener("click", async () => {
    try {
      await savePlan();
    } catch (error) {
      showToast(error.message, true);
    }
  });
  $("#copy-export-button").addEventListener("click", copyMoodleHtml);
  $("#archive-button").addEventListener("click", archivePlan);
  $("#add-lesson-button").addEventListener("click", () => {
    syncPlanFromForm();
    state.currentPlan.lessons.push(
      emptyLesson(state.currentPlan.lessons.length + 1),
    );
    renderPlan();
  });
  $$("[data-add-rich-item]").forEach((button) => {
    button.addEventListener("click", () =>
      addRichItem(button.dataset.addRichItem),
    );
  });
  $("#add-assessment-topic").addEventListener("click", () => {
    syncPlanFromForm();
    state.currentPlan.assessment.topics.push({
      title: "",
      description_html: "",
    });
    renderPlan();
  });
  $("#plan-filter").addEventListener("input", renderPlanList);
  $("#activity-search").addEventListener("input", () => {
    window.clearTimeout(state.searchTimer);
    state.searchTimer = window.setTimeout(searchActivities, 250);
  });
  $("#search-class-filter").addEventListener("change", searchActivities);
  $("#plan-form").addEventListener("input", () => {
    updateCalendarWeek();
    updatePreview();
  });
  $("#class-name").addEventListener("input", () => {
    window.clearTimeout(state.suggestionTimer);
    state.suggestionTimer = window.setTimeout(requestLatestPlan, 350);
  });
  $("#dialog-copy-button").addEventListener("click", async () => {
    try {
      if (!navigator.clipboard || typeof navigator.clipboard.writeText !== "function") {
        throw new Error("Clipboard API nicht verfügbar.");
      }
      await navigator.clipboard.writeText($("#export-fallback").value);
      $("#export-dialog").close();
      showToast("Moodle-HTML kopiert.");
    } catch {
      $("#export-fallback").select();
      showToast("Den markierten Code mit Ctrl+C kopieren.", true);
    }
  });
}

async function initialise() {
  state.currentPlan = restoreDraft() || createEmptyPlan();
  bindEvents();
  renderPlan();
  try {
    await loadPlanIndex();
    requestLatestPlan();
  } catch (error) {
    showToast(`Server nicht erreichbar: ${error.message}`, true);
  }
}

initialise();
