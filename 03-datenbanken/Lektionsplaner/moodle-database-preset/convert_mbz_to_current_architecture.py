#!/usr/bin/env python3
"""Fuehrt ein altes Moodle-Datenbank-Backup in die neue Lektionsplaner-Struktur ueber."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET


NULL_VALUE = "$@NULL@$"
MoodleDate = str

MONTHS = {
    "januar": 1,
    "februar": 2,
    "maerz": 3,
    "märz": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "dezember": 12,
}

TEMPLATE_FILES = {
    "singletemplate": "singletemplate.html",
    "listtemplate": "listtemplate.html",
    "listtemplateheader": "listtemplateheader.html",
    "listtemplatefooter": "listtemplatefooter.html",
    "addtemplate": "addtemplate.html",
    "rsstemplate": "rsstemplate.html",
    "rsstitletemplate": "rsstitletemplate.html",
    "csstemplate": "csstemplate.css",
    "jstemplate": "jstemplate.js",
    "asearchtemplate": "asearchtemplate.html",
}

TEXTAREA_FIELDS = {
    "zusatzmaterial_text",
    "lektion_1_aktivitaeten",
    "lektion_2_aktivitaeten",
    "lektion_3_aktivitaeten",
    "lektion_4_aktivitaeten",
    "lektion_5_aktivitaeten",
    "lektion_6_aktivitaeten",
    "hausaufgaben",
    "leistungsnachweis_themen",
    "stuetzkurs_ort",
    "stuetzkurs_hinweis",
    "lernziele",
}

URL_FIELDS = {"zusatzmaterial_link", "stuetzkurs_teams_url", "stuetzkurs_anmeldung_url"}

URL_FIELD_DEFAULT_LABELS = {
    "zusatzmaterial_link": "Zusatzmaterial",
    "stuetzkurs_teams_url": "Teams",
    "stuetzkurs_anmeldung_url": "Anmeldung",
}

CLASS_ALIASES = {
    "BM2-vz-2627": "BM2vz-2627",
    "BM2-tz-2628": "BM2tz-2628",
}

TOPIC_OPTIONS = [
    "Facheinführung",
    "Grundlagen Biologie: Allgemeine Grundlagen",
    "Grundlagen Biologie: Chemische Grundlagen",
    "Cytologie: Aufbau und Funktion von Zellen",
    "Cytologie: Aufbau und Funktion von Biomembranen",
    "Cytologie: Stoffaustausch (Zelltransport)",
    "Cytologie: asexuelle Reproduktion",
    "Cytologie: sexuelle Reproduktion",
    "Exkurs: Reproduktionsmedizin",
]


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"br", "p", "li", "dt", "dd", "h4", "h5"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"p", "li", "dt", "dd", "h4", "h5"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.current_href: str | None = None
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attributes = {name.lower(): value or "" for name, value in attrs}
        self.current_href = attributes.get("href")
        self.current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self.current_href:
            text = normalize_plain_text("".join(self.current_text))
            self.links.append((self.current_href, text))
            self.current_href = None
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_href:
            self.current_text.append(data)


def normalize_plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def normalize_class(value: str) -> str:
    text = normalize_plain_text(value)
    return CLASS_ALIASES.get(text, text)


def split_additional_material(value: str, fallback_label: str = "") -> tuple[str, str]:
    text = normalize_plain_text(value)
    fallback_label = normalize_plain_text(fallback_label)
    if not text or text == NULL_VALUE:
        return "", ""
    match = re.search(r"(?:https?://|/|\$@)\S+", text)
    if not match:
        return "", text
    url = match.group(0).rstrip(".,;")
    label = fallback_label if fallback_label and fallback_label != NULL_VALUE else ""
    if not label:
        label = normalize_plain_text((text[: match.start()] + " " + text[match.end() :]).strip(" -:|"))
    return url, label or "Zusatzmaterial"


def url_import_value(url: str, label: str) -> str:
    url = normalize_plain_text(url)
    label = normalize_plain_text(label)
    return f"{url} {label}".strip() if url else ""


def source_text_for_topics(values: dict[str, str]) -> str:
    return " ".join(
        html_to_text(values.get(field, ""))
        for field in ("Unterrichtsverlauf", "Hausaufgaben", "Lernziele", "thema", "Thema")
    ).casefold()


def infer_topics(values: dict[str, str]) -> str:
    text = source_text_for_topics(values)
    selected: list[str] = []

    def add(option: str) -> None:
        if option not in selected:
            selected.append(option)

    if any(
        marker in text
        for marker in (
            "facheinführung",
            "moodle-einführung",
            "moodlekurse",
            "fachvorgaben",
            "unterrichtsplanung",
            "vorstellungsrunde",
            "naturwissenschaften i",
            "sommer, sonne, sonnencreme",
        )
    ):
        add("Facheinführung")

    if any(
        marker in text
        for marker in (
            "eigenschaften des lebendigen",
            "definition von biologie",
            "biologischen organisation",
            "organisation der biosysteme",
            "systematik",
            "domänen",
            "domäne",
            "reich, stamm",
            "genetischen information",
            "nanotechnologie",
            "totholz",
        )
    ):
        add("Grundlagen Biologie: Allgemeine Grundlagen")

    if any(
        marker in text
        for marker in (
            "chemische grundlagen",
            "eigenschaften von wasser",
            "ph-wert",
            "biomolekül",
            "biomoleküle",
            "aufbau der dna",
            "lipiden",
            "lipide",
        )
    ):
        add("Grundlagen Biologie: Chemische Grundlagen")

    if any(
        marker in text
        for marker in (
            "cytologie",
            "mikroskop",
            "zellbestandteil",
            "organell",
            "organellen",
            "pro- und eukaryot",
            "prokaryontische",
            "eukaryontische",
            "tier- und pflanzenzellen",
            "mundschleimhaut",
            "zwiebelhaut",
            "euglena",
            "hefe",
            "endomembransystem",
        )
    ):
        add("Cytologie: Aufbau und Funktion von Zellen")

    if any(marker in text for marker in ("biomembran", "phospholipid", "membranmodell", "doppelschicht")):
        add("Cytologie: Aufbau und Funktion von Biomembranen")

    if any(marker in text for marker in ("stoffaustausch", "zelltransport", "osmose", "diffusion")):
        add("Cytologie: Stoffaustausch (Zelltransport)")

    if any(marker in text for marker in ("asexuelle", "mitose", "klonen", "vegetative vermehrung")):
        add("Cytologie: asexuelle Reproduktion")

    if any(marker in text for marker in ("sexuelle reproduktion", "meiose", "befruchtung", "gameten")):
        add("Cytologie: sexuelle Reproduktion")

    if any(marker in text for marker in ("reproduktionsmedizin", "ivf", "in-vitro", "pränatal")):
        add("Exkurs: Reproduktionsmedizin")

    return "##".join(option for option in TOPIC_OPTIONS if option in selected)


def html_to_text(value: str) -> str:
    parser = TextExtractor()
    parser.feed(value or "")
    parser.close()
    return normalize_plain_text("".join(parser.parts))


def html_to_lines(value: str) -> list[str]:
    normalized = re.sub(r"(?i)<br\s*/?>", "\n", value or "")
    normalized = re.sub(r"(?i)</p\s*>", "\n", normalized)
    parser = TextExtractor()
    parser.feed(normalized)
    parser.close()
    return [line for line in (normalize_plain_text(part) for part in "".join(parser.parts).splitlines()) if line]


def extract_links(value: str) -> list[tuple[str, str]]:
    parser = LinkExtractor()
    parser.feed(value or "")
    parser.close()
    return parser.links


def first_heading_text(value: str, tags: tuple[str, ...] = ("h4", "h5")) -> str:
    tag_pattern = "|".join(re.escape(tag) for tag in tags)
    match = re.search(rf"(?is)<({tag_pattern})[^>]*>(.*?)</\1>", value or "")
    if not match:
        return ""
    return clean_marker_text(html_to_text(match.group(2)))


def clean_marker_text(value: str) -> str:
    value = normalize_plain_text(value)
    value = re.sub(r"^[\s📍🗓🕣🕠🔗🗫🏫:|-]+", "", value)
    value = re.sub(r"\s*[:|-]\s*$", "", value)
    return value.strip()


def epoch_to_iso_date(value: str) -> MoodleDate:
    try:
        return datetime.fromtimestamp(int(value), timezone.utc).date().isoformat()
    except (TypeError, ValueError, OSError):
        return ""


def iso_week(value: str) -> str:
    if not value:
        return ""
    try:
        return f"KW {datetime.fromisoformat(value).date().isocalendar().week}"
    except ValueError:
        return ""


def parse_german_date(value: str) -> MoodleDate:
    text = html_to_text(value)
    match = re.search(
        r"(?i)\b(\d{1,2})\.\s*"
        r"(Januar|Februar|M[aä]rz|Maerz|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)"
        r"\s+(\d{4})\b",
        text,
    )
    if not match:
        return ""
    day = int(match.group(1))
    month = MONTHS[match.group(2).casefold()]
    year = int(match.group(3))
    try:
        return datetime(year, month, day).date().isoformat()
    except ValueError:
        return ""


def parse_time_range(value: str) -> tuple[str, str]:
    text = html.unescape(html_to_text(value))
    match = re.search(r"\b(\d{1,2}:\d{2})\s*(?:bis|-|–)\s*(\d{1,2}:\d{2})\b", text)
    if match:
        return normalize_time(match.group(1)), normalize_time(match.group(2))
    match = re.search(r"\b(\d{1,2}:\d{2})\b", text)
    if match:
        return normalize_time(match.group(1)), ""
    return "", ""


def normalize_time(value: str) -> str:
    hour, minute = value.split(":", 1)
    return f"{int(hour):02d}:{minute}"


def split_lessons(value: str) -> list[dict[str, str]]:
    fragment = re.sub(r"(?is)<!--.*?-->", "", value or "").strip()
    heading_pattern = re.compile(r"(?is)<h4[^>]*>(.*?)</h4>")
    matches = list(heading_pattern.finditer(fragment))
    lessons: list[dict[str, str]] = []
    if not matches and fragment:
        return [{"start_time": "", "end_time": "", "activities": fragment}]
    for index, match in enumerate(matches):
        heading_text = html_to_text(match.group(1))
        if not re.search(r"(?i)\d+\.\s*Lektion", heading_text):
            continue
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(fragment)
        start_time, end_time = parse_time_range(heading_text)
        activities = fragment[match.end() : next_start].strip()
        lessons.append(
            {
                "start_time": start_time,
                "end_time": end_time,
                "activities": activities,
            }
        )
    return lessons


def remove_heading(value: str, words: tuple[str, ...]) -> str:
    pattern = "|".join(re.escape(word) for word in words)
    return re.sub(rf"(?is)<h[45][^>]*>[^<]*(?:{pattern})[^<]*</h[45]>", "", value or "", count=1).strip()


def split_assessment_and_support(value: str) -> tuple[str, str]:
    match = re.search(r"(?is)<h4[^>]*>\s*St[üu]tzkurs\s*</h4>", value or "")
    if not match:
        return value or "", ""
    return (value or "")[: match.start()].strip(), (value or "")[match.end() :].strip()


def extract_assessment(value: str) -> dict[str, str]:
    title = first_heading_text(value, ("h4",)) or "Leistungsnachweis"
    date_value = parse_german_date(value)
    start_time, end_time = parse_time_range(value)
    topics_match = re.search(r"(?is)<dl[^>]*>.*?</dl>", value or "")
    topics = topics_match.group(0).strip() if topics_match else remove_heading(value, (title,))
    topics = re.sub(r"(?is)<p[^>]*>[^<]*(?:🗓|Uhr).*?</p>", "", topics, count=1).strip()
    return {
        "leistungsnachweis_titel": title,
        "leistungsnachweis_datum": date_value,
        "leistungsnachweis_beginn": start_time,
        "leistungsnachweis_ende": end_time,
        "leistungsnachweis_themen": topics,
    }


def extract_support(value: str) -> dict[str, str]:
    title = first_heading_text(value, ("h5",))
    if not title:
        for line in html_to_lines(value):
            if "📍" in line:
                title = clean_marker_text(line)
                break
    date_value = parse_german_date(value)
    start_time, end_time = parse_time_range(value)
    links = extract_links(value)
    teams_url = next((href for href, _ in links if "teams.microsoft.com" in href.casefold()), "")
    registration_url = next(
        (
            href
            for href, text in links
            if "teams.microsoft.com" not in href.casefold()
            and ("SCHEDULER" in href or "anmeldung" in text.casefold() or "scheduler" in href.casefold())
        ),
        "",
    )
    location = ""
    for line in html_to_lines(value):
        if "🏫" not in line:
            continue
        location = clean_marker_text(line)
        location = re.split(r"\s+oder\s+online\s+via\s+", location, flags=re.IGNORECASE)[0]
        location = clean_marker_text(location.replace("🏫", " "))
        break
    note_parts = re.findall(r"(?is)<p[^>]*>.*?🗫.*?</p>", value or "")
    note = "\n".join(part.strip() for part in note_parts)
    return {
        "stuetzkurs_titel": title,
        "stuetzkurs_datum": date_value,
        "stuetzkurs_beginn": start_time,
        "stuetzkurs_ende": end_time,
        "stuetzkurs_ort": f"<p>{html.escape(location)}</p>" if location else "",
        "stuetzkurs_teams_url": teams_url,
        "stuetzkurs_anmeldung_url": registration_url,
        "stuetzkurs_hinweis": note,
    }


def append_additional_material(lesson_html: str, url: str, label: str) -> str:
    if not url:
        return lesson_html
    link_text = label if label and label != NULL_VALUE else "Zusatzmaterial"
    addition = (
        f'<p><strong>Zusatzmaterial:</strong> '
        f'<a href="{html.escape(url, quote=True)}">{html.escape(link_text)}</a></p>'
    )
    return f"{lesson_html}\n{addition}".strip() if lesson_html else addition


def old_record_values(record: ET.Element, field_names_by_id: dict[str, str]) -> dict[str, str]:
    values: dict[str, str] = {}
    labels: dict[str, str] = {}
    contents = record.find("contents")
    if contents is None:
        return values
    for content in contents.findall("content"):
        field_id = content.findtext("fieldid") or ""
        name = field_names_by_id.get(field_id, field_id)
        values[name] = content.findtext("content") or ""
        labels[f"{name}#content1"] = content.findtext("content1") or ""
    values.update(labels)
    return values


def map_record(values: dict[str, str]) -> dict[str, str]:
    lesson_date = epoch_to_iso_date(values.get("Datum", ""))
    lessons = split_lessons(values.get("Unterrichtsverlauf", ""))
    additional_url, additional_label = split_additional_material(
        values.get("Zusatzmaterial", "").strip(),
        values.get("Zusatzmaterial#content1", "").strip(),
    )

    assessment_part, support_part = split_assessment_and_support(values.get("Bemerkung", ""))
    mapped = {
        "klasse": normalize_class(values.get("Klasse", "")),
        "unterrichtsdatum": lesson_date,
        "kalenderwoche": iso_week(lesson_date),
        "thema": infer_topics(values),
        "zusatzmaterial_text": "" if additional_url else additional_label,
        "zusatzmaterial_link": url_import_value(additional_url, additional_label),
        "zusatzmaterial_datei": "",
        "hausaufgaben": remove_heading(values.get("Hausaufgaben", ""), ("Arbeitsaufträge", "Arbeitsauftraege")),
        "lernziele": values.get("Lernziele", "").strip(),
    }

    for number in range(1, 7):
        if number <= len(lessons):
            lesson = lessons[number - 1]
            mapped[f"lektion_{number}_beginn"] = lesson["start_time"]
            mapped[f"lektion_{number}_ende"] = lesson["end_time"]
            mapped[f"lektion_{number}_aktivitaeten"] = lesson["activities"]
        else:
            mapped[f"lektion_{number}_beginn"] = ""
            mapped[f"lektion_{number}_ende"] = ""
            mapped[f"lektion_{number}_aktivitaeten"] = ""

    if len(lessons) > 6:
        overflow = "\n".join(lesson["activities"] for lesson in lessons[6:] if lesson["activities"])
        if overflow:
            mapped["lektion_6_aktivitaeten"] = (
                f"{mapped['lektion_6_aktivitaeten']}\n<h5>Weitere Inhalte</h5>\n{overflow}"
            ).strip()

    mapped.update(extract_assessment(assessment_part) if assessment_part else {})
    mapped.update(extract_support(support_part) if support_part else {})

    for field in [
        "leistungsnachweis_titel",
        "leistungsnachweis_datum",
        "leistungsnachweis_beginn",
        "leistungsnachweis_ende",
        "leistungsnachweis_themen",
        "stuetzkurs_titel",
        "stuetzkurs_datum",
        "stuetzkurs_beginn",
        "stuetzkurs_ende",
        "stuetzkurs_ort",
        "stuetzkurs_teams_url",
        "stuetzkurs_anmeldung_url",
        "stuetzkurs_hinweis",
    ]:
        mapped.setdefault(field, "")

    return mapped


def read_preset_fields(preset_dir: Path) -> list[dict[str, str]]:
    root = ET.parse(preset_dir / "preset.xml").getroot()
    fields: list[dict[str, str]] = []
    for field in root.findall("field"):
        fields.append(
            {
                "type": field.findtext("type") or "text",
                "name": field.findtext("name") or "",
                "description": field.findtext("description") or "",
                "required": field.findtext("required") or "0",
                **{f"param{index}": field.findtext(f"param{index}") or "" for index in range(1, 11)},
            }
        )
    return fields


def create_field_element(field_id: int, field: dict[str, str]) -> ET.Element:
    element = ET.Element("field", {"id": str(field_id)})
    for key in ["type", "name", "description", "required", *[f"param{index}" for index in range(1, 11)]]:
        child = ET.SubElement(element, key)
        child.text = field.get(key, "")
    return element


def create_content_element(content_id: int, field_id: int, field_name: str, value: str) -> ET.Element:
    element = ET.Element("content", {"id": str(content_id)})
    ET.SubElement(element, "fieldid").text = str(field_id)
    if field_name in URL_FIELDS:
        url, label = split_additional_material(value, URL_FIELD_DEFAULT_LABELS.get(field_name, ""))
        ET.SubElement(element, "content").text = url or ""
        ET.SubElement(element, "content1").text = label if url else ""
    else:
        ET.SubElement(element, "content").text = value or ""
    if field_name in TEXTAREA_FIELDS:
        ET.SubElement(element, "content1").text = "1" if value else NULL_VALUE
    elif field_name not in URL_FIELDS:
        ET.SubElement(element, "content1").text = NULL_VALUE
    ET.SubElement(element, "content2").text = NULL_VALUE
    ET.SubElement(element, "content3").text = NULL_VALUE
    ET.SubElement(element, "content4").text = NULL_VALUE
    return element


def replace_templates(data: ET.Element, preset_dir: Path) -> None:
    for tag_name, file_name in TEMPLATE_FILES.items():
        element = data.find(tag_name)
        if element is None:
            element = ET.SubElement(data, tag_name)
        element.text = (preset_dir / file_name).read_text(encoding="utf-8").strip()
    config = data.find("config")
    if config is not None:
        config.text = json.dumps(
            {
                "editor_addtemplate": True,
                "editor_singletemplate": True,
                "editor_listtemplate": True,
                "editor_asearchtemplate": True,
                "editor_rsstemplate": True,
                "editor_csstemplate": True,
                "editor_jstemplate": True,
            },
            separators=(",", ":"),
        )


def transform_backup(work_dir: Path, preset_dir: Path) -> dict[str, int]:
    data_xml = work_dir / "activities" / "data_69203" / "data.xml"
    tree = ET.parse(data_xml)
    activity = tree.getroot()
    data = activity.find("data")
    if data is None:
        raise RuntimeError("activities/data_69203/data.xml enthaelt kein <data>-Element.")

    old_fields_element = data.find("fields")
    records_element = data.find("records")
    if old_fields_element is None or records_element is None:
        raise RuntimeError("Das Moodle-Backup enthaelt keine lesbaren Datenbankfelder oder Records.")

    old_field_names = {
        field.get("id") or "": field.findtext("name") or ""
        for field in old_fields_element.findall("field")
    }
    old_records = list(records_element.findall("record"))
    mapped_records = [map_record(old_record_values(record, old_field_names)) for record in old_records]

    preset_fields = read_preset_fields(preset_dir)
    first_field_id = 4595
    first_content_id = 27268
    field_ids = {
        field["name"]: first_field_id + index
        for index, field in enumerate(preset_fields)
    }

    fields_element = ET.Element("fields")
    for index, field in enumerate(preset_fields):
        fields_element.append(create_field_element(first_field_id + index, field))
    data.remove(old_fields_element)
    insert_at = list(data).index(records_element)
    data.insert(insert_at, fields_element)

    content_id = first_content_id
    for record, mapped_values in zip(old_records, mapped_records):
        old_contents = record.find("contents")
        if old_contents is not None:
            record.remove(old_contents)
        contents = ET.Element("contents")
        for field in preset_fields:
            field_name = field["name"]
            contents.append(
                create_content_element(
                    content_id,
                    field_ids[field_name],
                    field_name,
                    mapped_values.get(field_name, ""),
                )
            )
            content_id += 1
        insert_record_contents(record, contents)

    name = data.find("name")
    if name is not None:
        name.text = "Lektionsplaner"
    intro = data.find("intro")
    if intro is not None:
        intro.text = "<p>Diese Datenbank enthaelt ueberfuehrte Lektionsplanungen im neuen Lektionsplaner-Layout.</p>"
    defaultsort = data.find("defaultsort")
    if defaultsort is not None:
        defaultsort.text = str(field_ids["unterrichtsdatum"])
    defaultsortdir = data.find("defaultsortdir")
    if defaultsortdir is not None:
        defaultsortdir.text = "1"
    timemodified = data.find("timemodified")
    if timemodified is not None:
        timemodified.text = str(int(time.time()))

    replace_templates(data, preset_dir)
    ET.indent(tree, space="  ")
    tree.write(data_xml, encoding="UTF-8", xml_declaration=True)

    update_backup_name(work_dir, "lektionsplaner-datenbank-mit-daten.mbz")
    update_archive_index(work_dir)

    return {
        "fields": len(preset_fields),
        "records": len(mapped_records),
        "contents": len(mapped_records) * len(preset_fields),
    }


def insert_record_contents(record: ET.Element, contents: ET.Element) -> None:
    children = list(record)
    for index, child in enumerate(children):
        if child.tag in {"ratings", "tags"}:
            record.insert(index, contents)
            return
    record.append(contents)


def update_backup_name(work_dir: Path, file_name: str) -> None:
    backup_xml = work_dir / "moodle_backup.xml"
    tree = ET.parse(backup_xml)
    root = tree.getroot()
    name = root.find("./information/name")
    if name is not None:
        name.text = file_name
    backup_date = root.find("./information/backup_date")
    if backup_date is not None:
        backup_date.text = str(int(time.time()))
    title = root.find("./information/contents/activities/activity/title")
    if title is not None:
        title.text = "Lektionsplaner"
    for setting in root.findall("./information/settings/setting"):
        setting_name = setting.findtext("name")
        if setting_name == "filename":
            value = setting.find("value")
            if value is not None:
                value.text = file_name
    ET.indent(tree, space="  ")
    tree.write(backup_xml, encoding="UTF-8", xml_declaration=True)


def archive_entries(root: Path) -> list[Path]:
    entries: list[Path] = []
    for path in root.rglob("*"):
        if path.name == ".ARCHIVE_INDEX":
            continue
        entries.append(path)
    return sorted(entries, key=lambda path: path.relative_to(root).as_posix())


def update_archive_index(root: Path) -> None:
    entries = archive_entries(root)
    lines = [f"Moodle archive file index. Count: {len(entries)}"]
    for path in entries:
        relative_path = path.relative_to(root).as_posix()
        if path.is_dir():
            lines.append(f"{relative_path}/\td\t0\t?")
        else:
            stat = path.stat()
            lines.append(f"{relative_path}\tf\t{stat.st_size}\t{int(stat.st_mtime)}")
    (root / ".ARCHIVE_INDEX").write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_mbz(root: Path, destination: Path) -> None:
    entries = [root / ".ARCHIVE_INDEX", *archive_entries(root)]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(destination, "w:gz", format=tarfile.GNU_FORMAT) as archive:
        for path in entries:
            archive.add(path, arcname=path.relative_to(root).as_posix(), recursive=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_mbz", type=Path)
    parser.add_argument("preset_dir", type=Path)
    parser.add_argument("destination_mbz", type=Path)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="lektionsplaner-mbz-") as temporary_directory:
        work_dir = Path(temporary_directory) / "backup"
        work_dir.mkdir()
        with tarfile.open(args.source_mbz, "r:gz") as archive:
            archive.extractall(work_dir, filter="data")
        summary = transform_backup(work_dir, args.preset_dir)
        create_mbz(work_dir, args.destination_mbz)

    print(
        f"{args.destination_mbz}: {summary['records']} Records, "
        f"{summary['fields']} Felder, {summary['contents']} Feldinhalte"
    )


if __name__ == "__main__":
    main()
