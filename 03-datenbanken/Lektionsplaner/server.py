#!/usr/bin/env python3
"""Lokaler Server fuer die Planung und Archivierung von Biologielektionen."""

from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
import threading
import uuid
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse, urlsplit


APPLICATION_DIR = Path(__file__).resolve().parent
REPOSITORY_DIR = APPLICATION_DIR.parents[1]
DATA_FILE = APPLICATION_DIR / "data" / "lektionen.json"
STATIC_DIR = APPLICATION_DIR / "static"
ACTIVE_HTML_DIR = APPLICATION_DIR / "data" / "wochenplaene"
LEGACY_ARCHIVE_DIR = APPLICATION_DIR / "data" / "archiv"
DATABASE_LOCK = threading.RLock()
MAX_JSON_BYTES = 1_000_000
LOCAL_ORIGIN_HOSTS = {"127.0.0.1", "localhost", "::1"}
ALLOWED_TAGS = {
    "a",
    "br",
    "em",
    "li",
    "ol",
    "p",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}
VOID_TAGS = {"br"}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
}
ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}
GERMAN_WEEKDAYS = (
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag",
)
GERMAN_MONTHS = (
    "Januar",
    "Februar",
    "Maerz",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
)


class ValidationError(ValueError):
    """Beschreibt einen Fehler in den vom Browser erhaltenen Planungsdaten."""


class RichTextSanitizer(HTMLParser):
    """Erlaubt nur kleine, Moodle-kompatible HTML-Fragmente."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag not in ALLOWED_TAGS:
            self.errors.append(f"Das HTML-Element <{tag}> ist nicht erlaubt.")
            return

        allowed_attributes = ALLOWED_ATTRIBUTES.get(tag, set())
        rendered_attributes: list[str] = []
        for name, value in attributes:
            name = name.lower()
            if name not in allowed_attributes:
                self.errors.append(
                    f"Das Attribut {name} bei <{tag}> ist nicht erlaubt."
                )
                continue
            value = value or ""
            if name == "href" and not is_safe_url(value):
                self.errors.append("Links duerfen nur http, https oder mailto verwenden.")
                continue
            rendered_attributes.append(f' {name}="{html.escape(value, quote=True)}"')

        suffix = " />" if tag in VOID_TAGS else ">"
        self.parts.append(f"<{tag}{''.join(rendered_attributes)}{suffix}")

    def handle_startendtag(
        self, tag: str, attributes: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attributes)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in ALLOWED_TAGS and tag not in VOID_TAGS:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(html.escape(data))

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")


class PlainTextExtractor(HTMLParser):
    """Erzeugt ein durchsuchbares Textfeld aus einem HTML-Fragment."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def is_safe_url(value: str) -> bool:
    parsed = urlsplit(value.strip())
    return parsed.scheme.lower() in ALLOWED_URL_SCHEMES


def sanitize_rich_html(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} muss Text sein.")
    sanitizer = RichTextSanitizer()
    sanitizer.feed(value)
    sanitizer.close()
    if sanitizer.errors:
        raise ValidationError(" ".join(sanitizer.errors))
    return "".join(sanitizer.parts).strip()


def rich_text_to_plain_text(value: str) -> str:
    parser = PlainTextExtractor()
    parser.feed(value)
    parser.close()
    return re.sub(r"\s+", " ", "".join(parser.parts)).strip()


def optional_text(value: object, field_name: str) -> str:
    if value in (None, ""):
        return ""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} muss Text sein.")
    return value.strip()


def validate_iso_date(value: object, field_name: str) -> str:
    text = optional_text(value, field_name)
    if not text:
        return ""
    try:
        date.fromisoformat(text)
    except ValueError as error:
        raise ValidationError(f"{field_name} muss ein Datum im Format JJJJ-MM-TT sein.") from error
    return text


def validate_time(value: object, field_name: str) -> str:
    text = optional_text(value, field_name)
    if not text:
        return ""
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", text):
        raise ValidationError(f"{field_name} muss eine Uhrzeit im Format HH:MM sein.")
    return text


def validate_optional_url(value: object, field_name: str) -> str:
    text = optional_text(value, field_name)
    if text and not is_safe_url(text):
        raise ValidationError(f"{field_name} muss mit http, https oder mailto beginnen.")
    return text


def validate_rich_text_items(value: object, field_name: str) -> list[dict[str, str]]:
    if value in (None, []):
        return []
    if not isinstance(value, list):
        raise ValidationError(f"{field_name} muss eine Liste sein.")

    items: list[dict[str, str]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise ValidationError(f"{field_name}, Eintrag {index}, ist ungueltig.")
        content_html = sanitize_rich_html(
            item.get("content_html", ""), f"{field_name}, Eintrag {index}"
        )
        if not rich_text_to_plain_text(content_html):
            raise ValidationError(f"{field_name}, Eintrag {index}, darf nicht leer sein.")
        items.append({"id": optional_text(item.get("id"), "Eintrags-ID") or str(uuid.uuid4()), "content_html": content_html})
    return items


def validate_lessons(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or not value:
        raise ValidationError("Mindestens ein Lektionsblock ist erforderlich.")

    lessons: list[dict[str, object]] = []
    for index, lesson in enumerate(value, start=1):
        if not isinstance(lesson, dict):
            raise ValidationError(f"Lektionsblock {index} ist ungueltig.")
        label = optional_text(lesson.get("label"), f"Lektionsblock {index}: Bezeichnung")
        if not label:
            label = f"{index}. Lektion"
        activities = validate_rich_text_items(
            lesson.get("activities", []), f"Lektionsblock {index}: Aktivitaeten"
        )
        lessons.append(
            {
                "id": optional_text(lesson.get("id"), "Lektions-ID") or str(uuid.uuid4()),
                "label": label,
                "start_time": validate_time(
                    lesson.get("start_time"), f"Lektionsblock {index}: Beginn"
                ),
                "end_time": validate_time(
                    lesson.get("end_time"), f"Lektionsblock {index}: Ende"
                ),
                "activities": activities,
            }
        )
    return lessons


def validate_assessment(value: object) -> dict[str, object] | None:
    if value in (None, {}):
        return None
    if not isinstance(value, dict):
        raise ValidationError("Leistungsnachweis ist ungueltig.")

    title = optional_text(value.get("title"), "Titel des Leistungsnachweises")
    if not title:
        return None
    topics_value = value.get("topics", [])
    if not isinstance(topics_value, list):
        raise ValidationError("Themen des Leistungsnachweises muessen eine Liste sein.")

    topics: list[dict[str, str]] = []
    for index, topic in enumerate(topics_value, start=1):
        if not isinstance(topic, dict):
            raise ValidationError(f"Thema {index} des Leistungsnachweises ist ungueltig.")
        topic_title = optional_text(topic.get("title"), f"Thema {index}: Titel")
        description_html = sanitize_rich_html(
            topic.get("description_html", ""), f"Thema {index}: Beschreibung"
        )
        if not topic_title or not rich_text_to_plain_text(description_html):
            raise ValidationError(
                f"Thema {index} des Leistungsnachweises braucht Titel und Beschreibung."
            )
        topics.append({"title": topic_title, "description_html": description_html})

    return {
        "title": title,
        "date": validate_iso_date(value.get("date"), "Datum des Leistungsnachweises"),
        "start_time": validate_time(value.get("start_time"), "Beginn des Leistungsnachweises"),
        "end_time": validate_time(value.get("end_time"), "Ende des Leistungsnachweises"),
        "topics": topics,
    }


def validate_support_course(value: object) -> dict[str, str] | None:
    if value in (None, {}):
        return None
    if not isinstance(value, dict):
        raise ValidationError("Stuetzkurs ist ungueltig.")

    fields = {
        "title": optional_text(value.get("title"), "Titel des Stuetzkurses"),
        "date": validate_iso_date(value.get("date"), "Datum des Stuetzkurses"),
        "start_time": validate_time(value.get("start_time"), "Beginn des Stuetzkurses"),
        "end_time": validate_time(value.get("end_time"), "Ende des Stuetzkurses"),
        "location_html": sanitize_rich_html(
            value.get("location_html", ""), "Ort des Stuetzkurses"
        ),
        "teams_url": validate_optional_url(value.get("teams_url"), "Teams-Link"),
        "registration_url": validate_optional_url(
            value.get("registration_url"), "Anmeldelink"
        ),
        "note_html": sanitize_rich_html(value.get("note_html", ""), "Hinweis zum Stuetzkurs"),
    }
    return fields if any(fields.values()) else None


def validate_plan(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValidationError("Die Planung muss ein Objekt sein.")

    class_name = optional_text(value.get("class_name"), "Klasse")
    if not class_name:
        raise ValidationError("Eine Klasse ist erforderlich.")
    lesson_date = validate_iso_date(value.get("date"), "Unterrichtsdatum")
    if not lesson_date:
        raise ValidationError("Ein Unterrichtsdatum ist erforderlich.")
    parsed_date = date.fromisoformat(lesson_date)

    return {
        "id": optional_text(value.get("id"), "Planungs-ID") or str(uuid.uuid4()),
        "class_name": class_name,
        "date": lesson_date,
        "calendar_week": parsed_date.isocalendar().week,
        "lessons": validate_lessons(value.get("lessons")),
        "homework": validate_rich_text_items(value.get("homework", []), "Hausaufgaben"),
        "assessment": validate_assessment(value.get("assessment")),
        "support_course": validate_support_course(value.get("support_course")),
        "learning_objectives": validate_rich_text_items(
            value.get("learning_objectives", []), "Lernziele"
        ),
    }


def empty_database() -> dict[str, object]:
    return {"version": 1, "plans": []}


def load_database() -> dict[str, object]:
    if not DATA_FILE.exists():
        return empty_database()
    try:
        with DATA_FILE.open(encoding="utf-8") as file_handle:
            database = json.load(file_handle)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Die Planungsdaten konnten nicht gelesen werden: {error}") from error

    if not isinstance(database, dict) or database.get("version") != 1:
        raise RuntimeError("Die Planungsdaten haben ein unbekanntes Format.")
    if not isinstance(database.get("plans"), list):
        raise RuntimeError("Die Planungsdaten enthalten keine gueltige Planungsliste.")
    return database


def write_database(database: dict[str, object]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=DATA_FILE.parent, delete=False
    ) as temporary_file:
        json.dump(database, temporary_file, ensure_ascii=False, indent=2)
        temporary_file.write("\n")
        temporary_path = Path(temporary_file.name)
    temporary_path.replace(DATA_FILE)


def save_plan(raw_plan: object) -> dict[str, object]:
    plan = validate_plan(raw_plan)
    with DATABASE_LOCK:
        database = load_database()
        plans = database["plans"]
        assert isinstance(plans, list)

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        existing_index = next(
            (index for index, existing in enumerate(plans) if existing.get("id") == plan["id"]),
            None,
        )
        for existing in plans:
            if existing.get("id") != plan["id"] and (
                existing.get("class_name") == plan["class_name"]
                and existing.get("date") == plan["date"]
            ):
                raise ValidationError("Fuer diese Klasse und dieses Datum existiert bereits eine Planung.")

        if existing_index is None:
            plan["created_at"] = now
            plans.append(plan)
        else:
            existing = plans[existing_index]
            plan["created_at"] = existing.get("created_at", now)
            plans[existing_index] = plan
        plan["updated_at"] = now
        write_database(database)
    return plan


def plan_summary(plan: dict[str, object]) -> dict[str, object]:
    return {
        "id": plan["id"],
        "class_name": plan["class_name"],
        "date": plan["date"],
        "calendar_week": plan["calendar_week"],
        "updated_at": plan.get("updated_at", ""),
    }


def format_german_date(iso_date: str) -> str:
    parsed_date = date.fromisoformat(iso_date)
    return (
        f"{GERMAN_WEEKDAYS[parsed_date.weekday()]}, {parsed_date.day:02d}. "
        f"{GERMAN_MONTHS[parsed_date.month - 1]} {parsed_date.year}"
    )


def html_text(value: object) -> str:
    return html.escape(str(value), quote=False)


def render_list(items: list[dict[str, str]], tag: str) -> str:
    if not items:
        return ""
    entries = "\n".join(f"  <li>{item['content_html']}</li>" for item in items)
    return f"<{tag}>\n{entries}\n</{tag}>"


def render_moodle_fragment(plan: dict[str, object]) -> str:
    """Rendert einen gespeicherten Plan als direkt einsetzbares Moodle-Fragment."""
    parts = [
        f"<!--<h1>{html_text(plan['class_name'])} {html_text(plan['date'])}</h1>-->"
    ]
    lessons = plan["lessons"]
    assert isinstance(lessons, list)
    for lesson in lessons:
        assert isinstance(lesson, dict)
        time_text = ""
        if lesson["start_time"] and lesson["end_time"]:
            time_text = f", 🕣 {lesson['start_time']} bis {lesson['end_time']}"
        elif lesson["start_time"]:
            time_text = f", 🕣 {lesson['start_time']}"
        parts.append(f"<h4>{html_text(lesson['label'])}{time_text}</h4>")
        activities = lesson["activities"]
        assert isinstance(activities, list)
        rendered_activities = render_list(activities, "ul")
        if rendered_activities:
            parts.append(rendered_activities)

    homework = plan["homework"]
    assert isinstance(homework, list)
    rendered_homework = render_list(homework, "ul")
    if rendered_homework:
        parts.extend(["<h4>Hausaufgaben</h4>", "<h5>📝 Arbeitsaufträge</h5>", rendered_homework])

    assessment = plan["assessment"]
    if assessment:
        assert isinstance(assessment, dict)
        parts.append(f"<h4>{html_text(assessment['title'])}</h4>")
        assessment_details: list[str] = []
        if assessment["date"]:
            assessment_details.append(f"🗓 {format_german_date(str(assessment['date']))}")
        if assessment["start_time"] and assessment["end_time"]:
            assessment_details.append(
                f"🕣 {assessment['start_time']} bis {assessment['end_time']} Uhr"
            )
        elif assessment["start_time"]:
            assessment_details.append(f"🕣 {assessment['start_time']} Uhr")
        if assessment_details:
            parts.append(f"<p>{'<br />'.join(assessment_details)}</p>")
        topics = assessment["topics"]
        assert isinstance(topics, list)
        if topics:
            rendered_topics = "\n".join(
                f"  <dt>{html_text(topic['title'])}</dt>\n  <dd>{topic['description_html']}</dd>"
                for topic in topics
            )
            parts.append(f"<dl>\n{rendered_topics}\n</dl>")

    support_course = plan["support_course"]
    if support_course:
        assert isinstance(support_course, dict)
        parts.append("<h4>Stützkurs</h4>")
        if support_course["title"]:
            parts.append(f"<h5>📍 {html_text(support_course['title'])}</h5>")
        support_details: list[str] = []
        if support_course["date"]:
            support_details.append(f"🗓 {format_german_date(str(support_course['date']))}")
        if support_course["start_time"] and support_course["end_time"]:
            support_details.append(
                f"🕠 von {support_course['start_time']} bis {support_course['end_time']} Uhr"
            )
        elif support_course["start_time"]:
            support_details.append(f"🕠 ab {support_course['start_time']} Uhr")
        if support_course["location_html"]:
            location = f"🏫 {support_course['location_html']}"
            if support_course["teams_url"]:
                location += (
                    " oder online via "
                    f'<a href="{html.escape(str(support_course["teams_url"]), quote=True)}">Teams</a>'
                )
            support_details.append(location)
        elif support_course["teams_url"]:
            support_details.append(
                "🔗 Online via "
                f'<a href="{html.escape(str(support_course["teams_url"]), quote=True)}">Teams</a>'
            )
        if support_details:
            parts.append(f"<p>{'<br />'.join(support_details)}</p>")
        if support_course["note_html"]:
            parts.append(f"<p>🗫 {support_course['note_html']}</p>")
        if support_course["registration_url"]:
            parts.append(
                "<p>🔗 "
                f'<a href="{html.escape(str(support_course["registration_url"]), quote=True)}">'
                "Anmeldung zum Stützkurs</a></p>"
            )

    learning_objectives = plan["learning_objectives"]
    assert isinstance(learning_objectives, list)
    rendered_objectives = render_list(learning_objectives, "ol")
    if rendered_objectives:
        parts.extend(["<h5>Lernziele</h5>", "<p>Sie sind in der Lage ...</p>", rendered_objectives])

    return "\n\n".join(parts)


def class_slug(value: str) -> str:
    normalized = value.casefold().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return normalized or "klasse"


def render_archive_document(plan: dict[str, object]) -> str:
    title = f"Lektionsplanung {plan['class_name']} {plan['date']}"
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="de">',
            "  <head>",
            '    <meta charset="UTF-8" />',
            f"    <title>{html_text(title)}</title>",
            "  </head>",
            "  <body>",
            render_moodle_fragment(plan),
            "  </body>",
            "</html>",
            "",
        ]
    )


def write_archive_file(plan: dict[str, object]) -> Path:
    archive_directory = LEGACY_ARCHIVE_DIR / "Einzelplanungen" / str(plan["date"])[0:4]
    archive_directory.mkdir(parents=True, exist_ok=True)
    archive_file = archive_directory / (
        f"{plan['date']}--{class_slug(str(plan['class_name']))}.html"
    )
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=archive_directory, delete=False
    ) as temporary_file:
        temporary_file.write(render_archive_document(plan))
        temporary_path = Path(temporary_file.name)
    temporary_path.replace(archive_file)
    return archive_file


class LegacyActivityParser(HTMLParser):
    """Liest direkte Aktivitaetslisten aus den bisherigen Wochen-HTML-Dateien."""

    def __init__(self, source_name: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source_name = source_name
        self.current_class = "Nicht zugeordnet"
        self.current_class_parts: list[str] | None = None
        self.current_heading_parts: list[str] | None = None
        self.current_lesson = ""
        self.awaiting_activity_list = False
        self.list_depth = 0
        self.current_item_parts: list[str] | None = None
        self.item_depth = 0
        self.activities: list[dict[str, str]] = []

    def handle_comment(self, data: str) -> None:
        match = re.search(r"<h1>\s*(.*?)\s*</h1>", data, flags=re.IGNORECASE | re.DOTALL)
        if match:
            class_name = rich_text_to_plain_text(match.group(1))
            self.current_class = class_name or "Nicht zugeordnet"

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "h1":
            self.current_class_parts = []
            return
        if tag == "h4":
            self.current_heading_parts = []
            return
        if tag == "ul":
            if self.awaiting_activity_list and self.list_depth == 0:
                self.list_depth = 1
                self.awaiting_activity_list = False
                return
            if self.list_depth:
                self.list_depth += 1
                self._append_tag(tag, attributes)
            return
        if tag == "li" and self.list_depth == 1:
            self.current_item_parts = []
            self.item_depth = 1
            return
        if tag == "li" and self.current_item_parts is not None:
            self.item_depth += 1
        self._append_tag(tag, attributes)

    def handle_startendtag(
        self, tag: str, attributes: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attributes)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "h1" and self.current_class_parts is not None:
            class_name = re.sub(r"\s+", " ", "".join(self.current_class_parts)).strip()
            self.current_class = class_name or "Nicht zugeordnet"
            self.current_class_parts = None
            return
        if tag == "h4" and self.current_heading_parts is not None:
            heading = re.sub(r"\s+", " ", "".join(self.current_heading_parts)).strip()
            self.current_heading_parts = None
            if re.match(r"^\d+\.\s*Lektion\b", heading, flags=re.IGNORECASE):
                self.current_lesson = heading
                self.awaiting_activity_list = True
            else:
                self.awaiting_activity_list = False
            return
        if tag == "li" and self.current_item_parts is not None:
            self.item_depth -= 1
            if self.item_depth == 0:
                self._finish_item()
                return
        if tag == "ul" and self.list_depth:
            self.list_depth -= 1
            if self.list_depth == 0:
                self.current_item_parts = None
            else:
                self._append_end_tag(tag)
            return
        self._append_end_tag(tag)

    def handle_data(self, data: str) -> None:
        if self.current_class_parts is not None:
            self.current_class_parts.append(data)
        if self.current_heading_parts is not None:
            self.current_heading_parts.append(data)
        if self.current_item_parts is not None:
            self.current_item_parts.append(html.escape(data))

    def _append_tag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        if self.current_item_parts is None:
            return
        allowed_attributes = ALLOWED_ATTRIBUTES.get(tag, set())
        safe_attributes = []
        for name, value in attributes:
            if name.lower() in allowed_attributes and (
                name.lower() != "href" or is_safe_url(value or "")
            ):
                safe_attributes.append(
                    f' {name.lower()}="{html.escape(value or "", quote=True)}"'
                )
        suffix = " />" if tag in VOID_TAGS else ">"
        if tag in ALLOWED_TAGS:
            self.current_item_parts.append(f"<{tag}{''.join(safe_attributes)}{suffix}")

    def _append_end_tag(self, tag: str) -> None:
        if self.current_item_parts is not None and tag in ALLOWED_TAGS and tag not in VOID_TAGS:
            self.current_item_parts.append(f"</{tag}>")

    def _finish_item(self) -> None:
        assert self.current_item_parts is not None
        content_html = "".join(self.current_item_parts).strip()
        plain_text = rich_text_to_plain_text(content_html)
        if plain_text:
            self.activities.append(
                {
                    "content_html": content_html,
                    "plain_text": plain_text,
                    "class_name": self.current_class,
                    "lesson_label": self.current_lesson,
                    "source": self.source_name,
                    "source_type": "Archiv",
                }
            )
        self.current_item_parts = None


def extract_legacy_activities() -> tuple[list[dict[str, str]], list[str]]:
    activities: list[dict[str, str]] = []
    warnings: list[str] = []
    source_files: list[Path] = []
    if ACTIVE_HTML_DIR.exists():
        source_files.extend(ACTIVE_HTML_DIR.glob("*.html"))
    if LEGACY_ARCHIVE_DIR.exists():
        generated_plans_dir = LEGACY_ARCHIVE_DIR / "Einzelplanungen"
        source_files.extend(
            source_file
            for source_file in LEGACY_ARCHIVE_DIR.rglob("*.html")
            if not source_file.is_relative_to(generated_plans_dir)
        )
    for source_file in sorted(source_files):
        try:
            try:
                source_name = str(source_file.relative_to(REPOSITORY_DIR))
            except ValueError:
                source_name = str(source_file)
            parser = LegacyActivityParser(source_name)
            parser.feed(source_file.read_text(encoding="utf-8"))
            parser.close()
            activities.extend(parser.activities)
        except OSError as error:
            warnings.append(f"{source_file} konnte nicht gelesen werden: {error}")
    return activities, warnings


def extract_saved_activities() -> list[dict[str, str]]:
    database = load_database()
    plans = database["plans"]
    assert isinstance(plans, list)
    activities: list[dict[str, str]] = []
    for plan in plans:
        lessons = plan.get("lessons", [])
        if not isinstance(lessons, list):
            continue
        for lesson in lessons:
            if not isinstance(lesson, dict):
                continue
            for activity in lesson.get("activities", []):
                if not isinstance(activity, dict):
                    continue
                content_html = str(activity.get("content_html", ""))
                plain_text = rich_text_to_plain_text(content_html)
                if plain_text:
                    activities.append(
                        {
                            "content_html": content_html,
                            "plain_text": plain_text,
                            "class_name": str(plan.get("class_name", "Nicht zugeordnet")),
                            "lesson_label": str(lesson.get("label", "Lektion")),
                            "source": str(plan.get("date", "Eigene Planung")),
                            "source_type": "Eigene Planung",
                        }
                    )
    return activities


def search_activities(query: str, class_filter: str = "") -> dict[str, object]:
    normalized_query = query.casefold().strip()
    normalized_class_filter = class_filter.casefold().strip()
    legacy_activities, warnings = extract_legacy_activities()
    all_activities = [*extract_saved_activities(), *legacy_activities]
    matches = [
        activity
        for activity in all_activities
        if (not normalized_query or normalized_query in activity["plain_text"].casefold())
        and (
            not normalized_class_filter
            or normalized_class_filter in activity["class_name"].casefold()
        )
    ]
    return {"activities": matches[:100], "warnings": warnings}


def latest_plan_for_class(class_name: str) -> dict[str, object] | None:
    normalized_class_name = class_name.casefold().strip()
    if not normalized_class_name:
        return None
    database = load_database()
    plans = database["plans"]
    assert isinstance(plans, list)
    matching_plans = [
        plan for plan in plans if str(plan.get("class_name", "")).casefold() == normalized_class_name
    ]
    return max(matching_plans, key=lambda plan: str(plan.get("date", "")), default=None)


def is_allowed_local_origin(origin: str | None, host: str | None) -> bool:
    if not origin:
        return True
    try:
        parsed_origin = urlparse(origin)
    except ValueError:
        return False
    if parsed_origin.scheme != "http" or not parsed_origin.netloc:
        return False
    request_host = (host or "").casefold()
    origin_host = (parsed_origin.hostname or "").casefold()
    return (
        origin_host in LOCAL_ORIGIN_HOSTS
        and parsed_origin.netloc.casefold() == request_host
    )


class LektionsplanerRequestHandler(SimpleHTTPRequestHandler):
    """Stellt die lokale Oberfläche und die kleine JSON-API bereit."""

    server_version = "Lektionsplaner/1.0"

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store" if self.path.startswith("/api/") else "no-cache")
        super().end_headers()

    def send_api_error(self, status: HTTPStatus, message: str) -> None:
        self.send_json({"error": message}, status)

    def reject_untrusted_origin(self) -> bool:
        if is_allowed_local_origin(self.headers.get("Origin"), self.headers.get("Host")):
            return False
        self.send_api_error(
            HTTPStatus.FORBIDDEN,
            "Schreibende API-Anfragen sind nur aus dem lokalen Lektionsplaner erlaubt.",
        )
        return True

    def do_GET(self) -> None:  # noqa: N802
        try:
            self.handle_get()
        except RuntimeError as error:
            self.send_api_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))

    def handle_get(self) -> None:
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/api/health":
            self.send_json({"status": "ok"})
            return
        if parsed_url.path == "/api/classes":
            database = load_database()
            plans = database["plans"]
            assert isinstance(plans, list)
            classes = sorted(
                {str(plan.get("class_name", "")) for plan in plans if plan.get("class_name")},
                key=str.casefold,
            )
            self.send_json({"classes": classes})
            return
        if parsed_url.path == "/api/plans/latest":
            class_name = parse_qs(parsed_url.query).get("class", [""])[0]
            self.send_json({"plan": latest_plan_for_class(class_name)})
            return
        if parsed_url.path == "/api/search":
            parameters = parse_qs(parsed_url.query)
            self.send_json(
                search_activities(
                    parameters.get("query", [""])[0], parameters.get("class", [""])[0]
                )
            )
            return
        if parsed_url.path == "/api/plans":
            database = load_database()
            plans = database["plans"]
            assert isinstance(plans, list)
            summaries = sorted(
                (plan_summary(plan) for plan in plans),
                key=lambda plan: (str(plan["date"]), str(plan["class_name"])),
                reverse=True,
            )
            self.send_json({"plans": summaries})
            return
        if parsed_url.path.startswith("/api/plans/"):
            path_parts = parsed_url.path.split("/")
            if len(path_parts) == 5 and path_parts[4] == "export":
                plan_id = unquote(path_parts[3])
                database = load_database()
                plans = database["plans"]
                assert isinstance(plans, list)
                plan = next((item for item in plans if item.get("id") == plan_id), None)
                if plan is None:
                    self.send_api_error(HTTPStatus.NOT_FOUND, "Planung nicht gefunden.")
                    return
                self.send_json({"html": render_moodle_fragment(plan)})
                return
            plan_id = unquote(parsed_url.path.removeprefix("/api/plans/"))
            database = load_database()
            plans = database["plans"]
            assert isinstance(plans, list)
            plan = next((item for item in plans if item.get("id") == plan_id), None)
            if plan is None:
                self.send_api_error(HTTPStatus.NOT_FOUND, "Planung nicht gefunden.")
                return
            self.send_json({"plan": plan})
            return
        if parsed_url.path.startswith("/api/"):
            self.send_api_error(HTTPStatus.NOT_FOUND, "Unbekannter API-Endpunkt.")
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.reject_untrusted_origin():
            return
        try:
            self.handle_post()
        except RuntimeError as error:
            self.send_api_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))

    def handle_post(self) -> None:
        parsed_url = urlparse(self.path)
        if parsed_url.path.startswith("/api/plans/") and parsed_url.path.endswith("/archive"):
            path_parts = parsed_url.path.split("/")
            if len(path_parts) != 5:
                self.send_api_error(HTTPStatus.NOT_FOUND, "Unbekannter API-Endpunkt.")
                return
            plan_id = unquote(path_parts[3])
            database = load_database()
            plans = database["plans"]
            assert isinstance(plans, list)
            plan = next((item for item in plans if item.get("id") == plan_id), None)
            if plan is None:
                self.send_api_error(HTTPStatus.NOT_FOUND, "Planung nicht gefunden.")
                return
            archive_file = write_archive_file(plan)
            try:
                archive_path = archive_file.relative_to(REPOSITORY_DIR)
            except ValueError:
                archive_path = archive_file
            self.send_json(
                {"archive_path": str(archive_path)}, HTTPStatus.CREATED
            )
            return
        if parsed_url.path != "/api/plans":
            self.send_api_error(HTTPStatus.NOT_FOUND, "Unbekannter API-Endpunkt.")
            return
        try:
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError as error:
                raise ValidationError("Content-Length ist ungueltig.") from error
            if content_length < 0:
                raise ValidationError("Content-Length ist ungueltig.")
            if content_length > MAX_JSON_BYTES:
                self.send_json(
                    {"error": "Die Anfrage ist zu gross."},
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                )
                return
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
            plan = save_plan(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            self.send_json({"error": f"Die Anfrage enthaelt kein gueltiges JSON: {error}"}, HTTPStatus.BAD_REQUEST)
            return
        except ValidationError as error:
            self.send_json({"error": str(error)}, HTTPStatus.UNPROCESSABLE_ENTITY)
            return
        except RuntimeError as error:
            self.send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self.send_json({"plan": plan}, HTTPStatus.CREATED)

    def do_DELETE(self) -> None:  # noqa: N802
        if self.reject_untrusted_origin():
            return
        try:
            self.handle_delete()
        except RuntimeError as error:
            self.send_api_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))

    def handle_delete(self) -> None:
        parsed_url = urlparse(self.path)
        if not parsed_url.path.startswith("/api/plans/"):
            self.send_api_error(HTTPStatus.NOT_FOUND, "Unbekannter API-Endpunkt.")
            return
        plan_id = unquote(parsed_url.path.removeprefix("/api/plans/"))
        with DATABASE_LOCK:
            database = load_database()
            plans = database["plans"]
            assert isinstance(plans, list)
            remaining_plans = [plan for plan in plans if plan.get("id") != plan_id]
            if len(remaining_plans) == len(plans):
                self.send_api_error(HTTPStatus.NOT_FOUND, "Planung nicht gefunden.")
                return
            database["plans"] = remaining_plans
            write_database(database)
        self.send_json({"deleted_id": plan_id})

    def send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded_payload)))
        self.end_headers()
        self.wfile.write(encoded_payload)

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"{self.address_string()} - {format_string % args}")


def run_server(port: int) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), LektionsplanerRequestHandler)
    print(f"Lektionsplaner: http://127.0.0.1:{port}")
    print("Zum Beenden Ctrl+C druecken.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLektionsplaner beendet.")
    finally:
        server.server_close()


def main() -> None:
    global ACTIVE_HTML_DIR, LEGACY_ARCHIVE_DIR
    parser = argparse.ArgumentParser(description="Startet den lokalen Lektionsplaner.")
    parser.add_argument("--port", type=int, default=8765, help="Lokaler Port (Standard: 8765)")
    parser.add_argument("--active-html-dir", type=Path, default=ACTIVE_HTML_DIR,
                        help="Verzeichnis bestehender Wochenpläne (wird nur gelesen)")
    parser.add_argument("--archive-dir", type=Path, default=LEGACY_ARCHIVE_DIR,
                        help="Archiv: liest vorhandene HTML-Dateien, schreibt neue unter Einzelplanungen/")
    arguments = parser.parse_args()
    ACTIVE_HTML_DIR = arguments.active_html_dir.expanduser().resolve()
    LEGACY_ARCHIVE_DIR = arguments.archive_dir.expanduser().resolve()
    run_server(arguments.port)


if __name__ == "__main__":
    main()
