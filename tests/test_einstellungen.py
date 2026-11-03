"""Tests für einstellungen.json: gleichzeitiges Schreiben (Issue #25) und beschädigte Datei (Issue #26).

Start: python3 -m unittest discover -s tests
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

PLUGIN = Path(__file__).resolve().parent.parent / "plugins/fabrik"
WERKZEUG = PLUGIN / "bin/fabrik"


def lade(name, datei, env=None):
    with mock.patch.dict(os.environ, env or {}):
        spec = importlib.util.spec_from_file_location(name, datei)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
    return modul


a = lade("fabrik_arbeiter_einstellungen_test", PLUGIN / "halle/arbeiter.py")


class Basis(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.daten = Path(self.tmp.name) / "daten"
        self.daten.mkdir()
        self.datei = self.daten / "einstellungen.json"
        self.env = {**os.environ, "FABRIK_DATEN": str(self.daten),
                    "FABRIK_LAGER": str(Path(self.tmp.name) / "lager")}

    def tearDown(self):
        self.tmp.cleanup()

    def fabrik(self, *args):
        return subprocess.run([sys.executable, str(WERKZEUG), *args], env=self.env,
                              capture_output=True, text=True, timeout=60)

    def starte(self, *args):
        return subprocess.Popen([sys.executable, str(WERKZEUG), *args], env=self.env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


class KaputteDateiTest(Basis):
    """Steht in einstellungen.json kein JSON-Objekt, gilt die Datei als leer statt abzustürzen."""

    INHALTE = ('["designer", "inspector"]', '"text"', "42", "null", "{kaputt",
               '{"deaktiviert": "designer"}', '{"deaktiviert": [1, null, "designer"]}')

    def test_lesen_mit_beschaedigter_datei(self):
        for inhalt in self.INHALTE:
            with self.subTest(inhalt=inhalt):
                self.datei.write_text(inhalt)
                r = self.fabrik("einstellung")
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertNotIn("Traceback", r.stderr)
                self.assertIsInstance(json.loads(r.stdout)["deaktiviert"], list)
                r = self.fabrik("rollen")
                self.assertEqual(r.returncode, 0, r.stderr)
                aus = json.loads(r.stdout)["deaktiviert"]
                self.assertTrue(set(aus) <= {"designer"})
                self.assertEqual(self.fabrik("einstellung", "autor").returncode, 0)

    def test_schreiben_repariert_datei(self):
        self.datei.write_text('["designer"]')
        r = self.fabrik("rolle", "designer", "aus")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(self.datei.read_text())["deaktiviert"], ["designer"])
        self.datei.write_text("[1, 2]")
        r = self.fabrik("einstellung", "autor", "Erika Muster")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(self.datei.read_text())["autor"], "Erika Muster")
        self.datei.write_text("[]")
        self.assertEqual(self.fabrik("einstellung", "eingerichtet").returncode, 0)
        self.assertTrue(json.loads(self.datei.read_text())["eingerichtet"])

    def test_halle_mit_json_array(self):
        home = Path(self.tmp.name) / "home"
        (home / ".claude/projects").mkdir(parents=True)
        s = lade("halle_server_einstellungen_test", PLUGIN / "halle/server.py",
                 {"HOME": str(home), "FABRIK_LAGER": str(home / "lager"), "FABRIK_DATEN": str(self.daten)})
        self.datei.write_text('["designer"]')
        self.assertEqual(s.rollen_aus(), [])
        self.assertEqual(s.setze_rolle("inspector", False), ["inspector"])
        self.assertEqual(s.rollen_aus(), ["inspector"])


class GleichzeitigTest(Basis):
    """Viele Aufrufe gleichzeitig: keine Änderung darf verloren gehen."""

    def test_gleichzeitige_aufrufe_verlieren_nichts(self):
        self.fabrik("einstellung", "update_hinweis", "an")
        prozesse = [
            self.starte("rolle", "designer", "aus"),
            self.starte("rolle", "inspector", "aus"),
            self.starte("rolle", "bediener", "aus"),
            self.starte("einstellung", "autor", "Erika Muster"),
            self.starte("einstellung", "git_name", "Erika"),
            self.starte("einstellung", "git_email", "erika@example.org"),
            self.starte("einstellung", "update_hinweis", "aus"),
            self.starte("einstellung", "eingerichtet"),
            self.starte("arbeiter", "builder", "modell", "sonnet"),
            self.starte("arbeiter", "spec", "effort", "high"),
        ]
        # Parallel dazu schreibt die Halle (gleiches Modul, gleiche Sperre) im eigenen Prozess.
        halle = threading.Thread(target=a.setze, args=(self.daten, "approver", "modell", "haiku"))
        halle.start()
        for p in prozesse:
            _, fehler = p.communicate(timeout=60)
            self.assertEqual(p.returncode, 0, fehler)
        halle.join(timeout=60)

        d = json.loads(self.datei.read_text())
        self.assertEqual(d["deaktiviert"], ["designer", "inspector", "bediener"])
        self.assertEqual(d["autor"], "Erika Muster")
        self.assertEqual(d["git_name"], "Erika")
        self.assertEqual(d["git_email"], "erika@example.org")
        self.assertEqual(d["update_hinweis"], "aus")
        self.assertTrue(d["eingerichtet"])
        self.assertEqual(d["arbeiter"]["builder"], {"modell": "sonnet"})
        self.assertEqual(d["arbeiter"]["spec"], {"effort": "high"})
        self.assertEqual(d["arbeiter"]["approver"], {"modell": "haiku"})
        # Keine liegengebliebenen Tempdateien.
        self.assertEqual([p.name for p in self.daten.glob("*.tmp")], [])

    def test_cli_wartet_auf_sperre(self):
        """Hält jemand die Sperre, schreibt das CLI erst danach und übernimmt die Änderung des anderen."""
        fertig = threading.Event()
        with a._sperre(self.daten):
            p = self.starte("einstellung", "autor", "Erika Muster")
            t = threading.Thread(target=lambda: (p.communicate(timeout=60), fertig.set()))
            t.start()
            self.assertFalse(fertig.wait(1.5), "CLI hat geschrieben, obwohl die Sperre gehalten wurde")
            a._schreibe_alles(self.daten, {"git_name": "Erika"})
        t.join(timeout=60)
        self.assertEqual(p.returncode, 0)
        d = json.loads(self.datei.read_text())
        self.assertEqual((d["git_name"], d["autor"]), ("Erika", "Erika Muster"))


if __name__ == "__main__":
    unittest.main()
