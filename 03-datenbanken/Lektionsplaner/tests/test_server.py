from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import server  # noqa: E402


class ServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self.temporary_directory.name)
        self.original_data_file = server.DATA_FILE
        self.original_active_html_dir = server.ACTIVE_HTML_DIR
        self.original_archive_directory = server.LEGACY_ARCHIVE_DIR
        server.DATA_FILE = self.temporary_path / "data" / "lektionen.json"
        server.ACTIVE_HTML_DIR = self.temporary_path / "active"
        server.LEGACY_ARCHIVE_DIR = self.temporary_path / "archive"

    def tearDown(self) -> None:
        server.DATA_FILE = self.original_data_file
        server.ACTIVE_HTML_DIR = self.original_active_html_dir
        server.LEGACY_ARCHIVE_DIR = self.original_archive_directory
        self.temporary_directory.cleanup()

    def sample_plan(self) -> dict[str, object]:
        return {
            "class_name": "VZ",
            "date": "2026-06-02",
            "lessons": [
                {
                    "label": "1. Lektion",
                    "start_time": "11:20",
                    "end_time": "12:05",
                    "activities": [
                        {"content_html": "<strong>Diffusion</strong> mit einem Beispiel erklären."}
                    ],
                }
            ],
            "homework": [{"content_html": "Arbeitsblatt <em>Osmose</em> abschliessen."}],
            "assessment": {
                "title": "Biologieprüfung I",
                "date": "2026-06-09",
                "start_time": "11:20",
                "end_time": "12:05",
                "topics": [
                    {"title": "Stofftransport", "description_html": "Diffusion und Osmose"}
                ],
            },
            "support_course": {
                "title": "Prüfungsvorbereitung",
                "date": "2026-06-04",
                "start_time": "13:30",
                "end_time": "14:30",
                "location_html": "Zimmer 304",
                "teams_url": "https://teams.microsoft.com/meeting",
                "registration_url": "https://moodle.strickhof.ch/mod/scheduler/view.php?id=1",
                "note_html": "Bitte anmelden.",
            },
            "learning_objectives": [
                {"content_html": "<strong>Osmose</strong> erklären."}
            ],
        }

    def test_save_and_render_plan(self) -> None:
        plan = server.save_plan(self.sample_plan())

        self.assertEqual(plan["calendar_week"], 23)
        self.assertTrue(server.DATA_FILE.exists())
        fragment = server.render_moodle_fragment(plan)

        self.assertIn("<!--<h1>VZ 2026-06-02</h1>-->", fragment)
        self.assertIn("<h4>1. Lektion, 🕣 11:20 bis 12:05</h4>", fragment)
        self.assertIn("<h4>Hausaufgaben</h4>", fragment)
        self.assertIn("<dl>", fragment)
        self.assertIn("<h4>Stützkurs</h4>", fragment)
        self.assertIn("<h5>Lernziele</h5>", fragment)
        self.assertIn("Dienstag, 09. Juni 2026", fragment)
        self.assertIn("von 13:30 bis 14:30 Uhr", fragment)
        self.assertIn('href="https://teams.microsoft.com/meeting"', fragment)
        self.assertNotIn("<body>", fragment)

    def test_archive_document_is_complete_html_file(self) -> None:
        plan = server.save_plan(self.sample_plan())
        archive_file = server.write_archive_file(plan)
        document = archive_file.read_text(encoding="utf-8")

        self.assertEqual(archive_file.name, "2026-06-02--vz.html")
        self.assertIn('<html lang="de">', document)
        self.assertIn('<meta charset="UTF-8" />', document)
        self.assertIn("<body>", document)
        self.assertIn("<h4>Biologieprüfung I</h4>", document)

    def test_rich_html_rejects_scripts_and_unsafe_links(self) -> None:
        with self.assertRaises(server.ValidationError):
            server.sanitize_rich_html("<script>alert('x')</script>", "Test")
        with self.assertRaises(server.ValidationError):
            server.sanitize_rich_html('<a href="javascript:alert(1)">Link</a>', "Test")

    def test_extracts_activities_from_active_and_archived_week_files(self) -> None:
        server.ACTIVE_HTML_DIR.mkdir(parents=True)
        active_file = server.ACTIVE_HTML_DIR / "2026-kw-36.html"
        active_file.write_text(
            "<h1>BM2-vz vom 31. August 2026</h1><h4>1. Lektion</h4>"
            "<ul><li>Aktuelle Aktivität</li></ul>",
            encoding="utf-8",
        )
        archived_file = server.LEGACY_ARCHIVE_DIR / "2026" / "2026-KW-22.html"
        archived_file.parent.mkdir(parents=True)
        archived_file.write_text(
            "<!--<h1>VZ</h1>--><h4>2. Lektion</h4>"
            "<ul><li>Übungsprüfung lösen</li></ul>",
            encoding="utf-8",
        )
        generated_file = server.LEGACY_ARCHIVE_DIR / "Einzelplanungen" / "2026" / "ignored.html"
        generated_file.parent.mkdir(parents=True)
        generated_file.write_text(
            "<!--<h1>VZ</h1>--><h4>1. Lektion</h4>"
            "<ul><li>Darf nicht gefunden werden</li></ul>",
            encoding="utf-8",
        )
        activities, warnings = server.extract_legacy_activities()

        self.assertEqual(warnings, [])
        self.assertEqual(
            {activity["plain_text"] for activity in activities},
            {"Aktuelle Aktivität", "Übungsprüfung lösen"},
        )
        active_activity = next(
            activity for activity in activities if activity["plain_text"] == "Aktuelle Aktivität"
        )
        self.assertEqual(active_activity["class_name"], "BM2-vz vom 31. August 2026")
        archived_activity = next(
            activity for activity in activities if activity["plain_text"] == "Übungsprüfung lösen"
        )
        self.assertEqual(archived_activity["class_name"], "VZ")
        self.assertTrue(archived_activity["source"].endswith("2026-KW-22.html"))

    def test_api_supports_save_export_archive_and_delete(self) -> None:
        http_server = server.ThreadingHTTPServer(
            ("127.0.0.1", 0), server.LektionsplanerRequestHandler
        )
        server_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        server_thread.start()
        base_url = f"http://127.0.0.1:{http_server.server_port}"
        try:
            request = Request(
                f"{base_url}/api/plans",
                data=json.dumps(self.sample_plan()).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request) as response:
                saved_plan = json.load(response)["plan"]

            plan_id = saved_plan["id"]
            with urlopen(f"{base_url}/api/plans/{plan_id}/export") as response:
                moodle_html = json.load(response)["html"]
            self.assertIn("<h4>Stützkurs</h4>", moodle_html)

            archive_request = Request(f"{base_url}/api/plans/{plan_id}/archive", method="POST")
            with urlopen(archive_request) as response:
                archive_path = json.load(response)["archive_path"]
            self.assertTrue((self.temporary_path / "archive" / "Einzelplanungen" / "2026").exists())
            self.assertTrue(archive_path.endswith("2026-06-02--vz.html"))

            delete_request = Request(f"{base_url}/api/plans/{plan_id}", method="DELETE")
            with urlopen(delete_request) as response:
                self.assertEqual(json.load(response)["deleted_id"], plan_id)
            with self.assertRaises(HTTPError) as missing_plan:
                urlopen(f"{base_url}/api/plans/{plan_id}")
            self.assertEqual(missing_plan.exception.code, 404)
        finally:
            http_server.shutdown()
            http_server.server_close()
            server_thread.join()

    def test_api_rejects_cross_origin_writes(self) -> None:
        http_server = server.ThreadingHTTPServer(
            ("127.0.0.1", 0), server.LektionsplanerRequestHandler
        )
        server_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        server_thread.start()
        base_url = f"http://127.0.0.1:{http_server.server_port}"
        try:
            request = Request(
                f"{base_url}/api/plans",
                data=json.dumps(self.sample_plan()).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Origin": "http://example.com",
                },
                method="POST",
            )
            with self.assertRaises(HTTPError) as forbidden_request:
                urlopen(request)
            self.assertEqual(forbidden_request.exception.code, 403)
            error_body = json.loads(
                forbidden_request.exception.read().decode("utf-8")
            )
            self.assertIn("error", error_body)
        finally:
            http_server.shutdown()
            http_server.server_close()
            server_thread.join()

    def test_api_returns_json_when_database_is_invalid(self) -> None:
        server.DATA_FILE.parent.mkdir(parents=True)
        server.DATA_FILE.write_text("{keine gueltige json-datei", encoding="utf-8")
        http_server = server.ThreadingHTTPServer(
            ("127.0.0.1", 0), server.LektionsplanerRequestHandler
        )
        server_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        server_thread.start()
        base_url = f"http://127.0.0.1:{http_server.server_port}"
        try:
            with self.assertRaises(HTTPError) as failed_request:
                urlopen(f"{base_url}/api/plans")
            self.assertEqual(failed_request.exception.code, 500)
            self.assertEqual(
                failed_request.exception.headers["Content-Type"],
                "application/json; charset=utf-8",
            )
            error_body = json.loads(failed_request.exception.read().decode("utf-8"))
            self.assertIn("Planungsdaten konnten nicht gelesen werden", error_body["error"])
        finally:
            http_server.shutdown()
            http_server.server_close()
            server_thread.join()


if __name__ == "__main__":
    unittest.main()
