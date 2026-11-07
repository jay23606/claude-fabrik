"""Tests für die Korrekturen aus den Prüfungen (Version 0.4.1).

Einstellungsdatei (#32, #34, #28, #35), POST-Handler (#33), Update-Zwischenspeicher
(#15, #16, #17, #18), Projektnamen in der Halle (#13, scratch-workspaces, Temp-Platzhalter)
und keine __pycache__-Ordner im Plugin (#36). Kein Test nutzt das Netz.

Start: python3 -B -m unittest discover -s tests
"""
import http.client
import importlib.machinery
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

# Beim Laden der Plugin-Module keine __pycache__-Ordner im Plugin anlegen.
sys.dont_write_bytecode = True

PLUGIN = Path(__file__).resolve().parent.parent / "plugins/fabrik"
WERKZEUG = PLUGIN / "bin/fabrik"


def lade(name, datei, env=None):
    with mock.patch.dict(os.environ, env or {}):
        # Das Werkzeug bin/fabrik hat keine Endung .py, deshalb den Lader angeben.
        lader = importlib.machinery.SourceFileLoader(name, str(datei))
        spec = importlib.util.spec_from_file_location(name, datei, loader=lader)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
    return modul


a = lade("fabrik_arbeiter_korrektur_test", PLUGIN / "halle/arbeiter.py")
u = lade("fabrik_update_korrektur_test", PLUGIN / "halle/update.py")


class Werkzeug(unittest.TestCase):
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


class EinstellungsdateiTest(Werkzeug):
    def test_ungueltiges_utf8_gilt_als_leer(self):
        # Bytes, die kein gültiges UTF-8 sind (#32).
        self.datei.write_bytes(b'{"autor": "\xff\xfe"}')
        for args in (["einstellung"], ["modelle"], ["rollen"], ["einstellung", "autor"], ["update"]):
            with self.subTest(args=args):
                r = self.fabrik(*args)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(a._lies_alles(self.daten), {})

    def test_lesen_schreibt_keinen_standardwert(self):
        # `deaktiviert` wird nur geschrieben, wenn ein Prüfer geschaltet wird (#34).
        self.assertEqual(self.fabrik("einstellung", "eingerichtet").returncode, 0)
        self.assertEqual(self.fabrik("einstellung", "autor", "Erika Muster").returncode, 0)
        d = json.loads(self.datei.read_text())
        self.assertEqual(d, {"eingerichtet": True, "autor": "Erika Muster"})
        self.assertEqual(json.loads(self.fabrik("einstellung").stdout)["deaktiviert"], [])
        self.assertEqual(self.fabrik("rolle", "designer", "aus").returncode, 0)
        self.assertEqual(json.loads(self.datei.read_text())["deaktiviert"], ["designer"])

    def test_lager_eintrag_ohne_text(self):
        self.datei.write_text(json.dumps({"lager": 42}))
        r = self.fabrik("liste")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_aufruf_liest_einmal(self):
        # Vorher wurde die Datei je Rolle gelesen, also siebenmal (#28).
        with mock.patch.object(a, "_lies_alles", wraps=a._lies_alles) as lesen:
            a.aufruf(self.daten)
        self.assertEqual(lesen.call_count, 1)

    def test_effort_frei_waehlbar(self):
        # Kein wirkungsloser Filter je Modell mehr (#27): jede Stufe geht mit jedem Modell.
        for modell in a.MODELLE:
            for effort in a.EFFORTS:
                with self.subTest(modell=modell, effort=effort):
                    a.setze(self.daten, "builder", "modell", modell)
                    st = a.setze(self.daten, "builder", "effort", effort)
                    self.assertEqual((st["gilt_modell"], st["gilt_effort"]), (modell, effort))
        self.assertNotIn("efforts", a.auswahl()["modelle"][0])

    def test_listen_nur_an_einer_stelle(self):
        # Werkzeug und Halle übernehmen Rollen und Prüfer aus arbeiter.py (#35).
        for datei in (WERKZEUG, PLUGIN / "halle/server.py"):
            text = datei.read_text()
            with self.subTest(datei=datei.name):
                self.assertNotIn('"sicherheit", "designer", "inspector", "bediener"', text)
        self.assertEqual(a.deaktivierte({"deaktiviert": ["bediener", 3, "chef", "designer"]}), ["designer", "bediener"])
        self.assertEqual(a.deaktivierte({"deaktiviert": "designer"}), [])
        self.assertEqual(a.deaktivierte([]), [])


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.daten = Path(self.tmp.name) / "daten"
        self.daten.mkdir()
        self.cache = self.daten / "update.json"
        self.plugin_json = Path(self.tmp.name) / "plugin.json"
        self.plugin_json.write_text(json.dumps({"version": "0.4.1"}))

    def tearDown(self):
        self.tmp.cleanup()

    def stand(self, neueste, jetzt, **kw):
        return u.stand(self.daten, holen=lambda: neueste, jetzt=jetzt, plugin_json=self.plugin_json, **kw)

    def test_fehlschlag_behaelt_bekannte_version(self):
        # #15: ein Netzfehler darf ein schon gefundenes Update nicht löschen.
        self.assertTrue(self.stand("0.5.0", 1_000_000.0)["update_verfuegbar"])
        s = self.stand(None, 1_000_000.0 + 7 * 3600)
        self.assertEqual(s["neueste"], "0.5.0")
        self.assertTrue(s["update_verfuegbar"])
        gespeichert = json.loads(self.cache.read_text())
        self.assertEqual(gespeichert, {"geprueft": 1_000_000.0 + 7 * 3600, "neueste": "0.5.0"})

    def test_cache_nur_mit_semver(self):
        # #16: auch der Zwischenspeicher liefert nur geprüfte Versionen.
        for roh, erwartet in (("9.9.9", "9.9.9"), ("v1.2.3", "1.2.3"), ("1.0", None),
                              ("neu", None), (42, None), (None, None)):
            with self.subTest(roh=roh):
                self.cache.write_text(json.dumps({"geprueft": 5.0, "neueste": roh}))
                self.assertEqual(u.cache_lesen(self.cache)["neueste"], erwartet)

    def test_nur_cache_mit_altersgrenze(self):
        # #17: die Halle nimmt keinen uralten Zwischenspeicher.
        self.cache.write_text(json.dumps({"geprueft": 1_000_000.0, "neueste": "0.5.0"}))
        self.assertTrue(self.stand("x", 1_000_000.0 + 23 * 3600, nur_cache=True)["update_verfuegbar"])
        s = self.stand("x", 1_000_000.0 + 25 * 3600, nur_cache=True)
        self.assertIsNone(s["neueste"])
        self.assertFalse(s["update_verfuegbar"])
        self.assertFalse(self.stand("x", 1_000_000.0 - 60, nur_cache=True)["update_verfuegbar"])

    def test_rueckfall_mit_gleichem_schema(self):
        # #18: der Rückfall in `fabrik update` hat dieselben Schlüssel wie update.stand.
        schluessel = set(self.stand(None, 1_000_000.0))
        self.assertEqual(set(u.leerer_stand()), schluessel)
        werkzeug = lade("fabrik_werkzeug_korrektur_test", WERKZEUG,
                        {"FABRIK_DATEN": str(self.daten), "FABRIK_LAGER": str(self.daten / "lager")})
        self.assertEqual(set(werkzeug.UPDATE_RUECKFALL), schluessel)

    def test_werkzeug_bei_fehler_im_modul(self):
        werkzeug = lade("fabrik_werkzeug_korrektur_test2", WERKZEUG,
                        {"FABRIK_DATEN": str(self.daten), "FABRIK_LAGER": str(self.daten / "lager")})
        import update as echtes_update
        with mock.patch.object(echtes_update, "stand", side_effect=RuntimeError("kaputt")), \
                mock.patch("builtins.print") as ausgabe:
            werkzeug.cmd_update(None)
        d = json.loads(ausgabe.call_args.args[0])
        self.assertEqual(set(d), set(u.leerer_stand()))
        self.assertFalse(d["update_verfuegbar"])


class PostTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        home = Path(self.tmp.name) / "home"
        self.daten = home / ".claude/fabrik"
        (home / ".claude/projects").mkdir(parents=True)
        self.s = lade("halle_server_korrektur_test", PLUGIN / "halle/server.py",
                      {"HOME": str(home), "FABRIK_LAGER": str(home / "lager"), "FABRIK_DATEN": str(self.daten)})
        self.server = self.s.LokalerServer(("127.0.0.1", 0), self.s.Halle)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.port = self.server.server_port

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def post_mit_laenge(self, laenge, koerper=b""):
        verbindung = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            verbindung.putrequest("POST", "/api/rolle", skip_accept_encoding=True)
            verbindung.putheader("Content-Type", "application/json")
            verbindung.putheader("X-Fabrik-Halle", "1")
            verbindung.putheader("Origin", f"http://127.0.0.1:{self.port}")
            verbindung.putheader("Content-Length", str(laenge))
            verbindung.endheaders(koerper)
            antwort = verbindung.getresponse()
            return antwort.status
        finally:
            verbindung.close()

    def test_negative_laenge_antwortet_sofort(self):
        # #33: vorher las der Handler bis zum Verbindungsende und hing.
        self.assertEqual(self.post_mit_laenge(-5), 400)
        self.assertEqual(self.post_mit_laenge("keine-zahl"), 400)

    def test_zu_grosser_koerper(self):
        self.assertEqual(self.post_mit_laenge(5000, b"{" + b" " * 4998 + b"}"), 413)

    def test_gueltige_anfrage_geht_weiter(self):
        koerper = json.dumps({"rolle": "designer", "aktiv": False}).encode()
        self.assertEqual(self.post_mit_laenge(len(koerper), koerper), 200)
        self.assertEqual(self.s.rollen_aus(), ["designer"])


class HalleNamenTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name).resolve() / "home"
        self.lager = self.home / "Documents/Projekte/Fabrik"
        (self.home / ".claude/projects").mkdir(parents=True)
        self.lager.mkdir(parents=True)
        self.env = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        self.env.start()
        self.s = lade("halle_server_namen_korrektur_test", PLUGIN / "halle/server.py",
                      {"HOME": str(self.home), "FABRIK_LAGER": str(self.lager),
                       "FABRIK_DATEN": str(self.home / ".claude/fabrik")})
        self.scratch = self.home / "Library/Application Support/Claude/scratch-workspaces"
        # Der Test läuft selbst in einem echten Temp-Ordner; die Liste muss also ohne ihn auskommen.
        self.assertIn(self.scratch, self.s.TEMP_ORDNER)
        self.s.TEMP_ORDNER = [self.scratch]
        self.s.NAMEN_CACHE.clear()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_scratch_workspaces_sind_sammelordner(self):
        cwd = self.scratch / "abc123"
        self.assertTrue(self.s.ohne_projekt(str(cwd)))
        self.assertTrue(self.s.ohne_projekt_kodiert(self.s.kodiert(cwd)))
        self.assertIsNone(self.s.projekt_von_datei(cwd / "notiz.md"))
        self.assertEqual(self.s.anzeigename(str(cwd)), (self.s.TEMP_PLATZHALTER, True))
        self.assertEqual(self.s.anzeigename(str(self.home)), (self.s.BENUTZERORDNER, True))

    def test_scratch_sitzung_zeigt_projekt(self):
        cwd = self.scratch / "abc123"
        ordner = self.home / ".claude/projects" / self.s.kodiert(cwd)
        ordner.mkdir(parents=True)
        datei = ordner / "11111111-2222-3333-4444-555555555555.jsonl"
        eintrag = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Edit",
                   "input": {"file_path": str(self.home / "Documents/Projekte/Tracko/a.py")}}]}}
        datei.write_text(json.dumps(eintrag) + "\n")
        self.assertEqual(self.s.anzeigename(str(cwd), datei), ("Tracko", False))
        ruhend = [x for x in self.s.sitzungen() if x["zustand"] == "ruht"]
        self.assertEqual([x["projekt"] for x in ruhend], ["Tracko"])

    def test_pfad_wird_normalisiert(self):
        # #13: „..“ darf die Ausnahme für ~/.claude nicht umgehen, fremde Laufwerke werden übersprungen.
        umweg = str(self.home / "Documents/Projekte/X/../../../.claude/plan.md")
        self.assertIsNone(self.s.projekt_von_datei(umweg))
        self.assertEqual(self.s.projekt_von_datei(str(self.home / "Documents/Projekte/A/../B/c.py")), "B")
        with mock.patch.object(Path, "exists", side_effect=AssertionError("auf fremdem Laufwerk gesucht")):
            self.assertIsNone(self.s.projekt_von_datei("/Volumes/Netz/projekt/datei.py"))


class OhnePycacheTest(Werkzeug):
    def test_werkzeug_legt_keinen_pycache_an(self):
        # #36: das Werkzeug lädt halle/arbeiter.py und halle/update.py ohne Bytecode-Dateien.
        vorher = {p for p in PLUGIN.rglob("__pycache__")}
        env = {k: v for k, v in self.env.items() if k != "PYTHONDONTWRITEBYTECODE"}
        r = subprocess.run([sys.executable, str(WERKZEUG), "update"], env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual({p for p in PLUGIN.rglob("__pycache__")} - vorher, set())


if __name__ == "__main__":
    unittest.main()
