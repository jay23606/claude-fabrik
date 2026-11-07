"""Tests für Modell und Effort je Arbeiter: Speichern, Standard, Kommandozeile und Halle.

Start: python3 -B -m unittest discover -s tests
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

# Beim Laden der Plugin-Module keine __pycache__-Ordner im Plugin anlegen.
sys.dont_write_bytecode = True

PLUGIN = Path(__file__).resolve().parent.parent / "plugins/fabrik"
WERKZEUG = PLUGIN / "bin/fabrik"


def lade(name, datei, env=None):
    with mock.patch.dict(os.environ, env or {}):
        spec = importlib.util.spec_from_file_location(name, datei)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
    return modul


a = lade("fabrik_arbeiter_test", PLUGIN / "halle/arbeiter.py")


class ArbeiterModulTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.daten = Path(self.tmp.name) / "daten"
        self.agenten = Path(self.tmp.name) / "agents"
        self.agenten.mkdir()
        (self.agenten / "fabrik-builder.md").write_text("---\nname: fabrik-builder\nmodel: opus\n---\nText\n")
        (self.agenten / "fabrik-designer.md").write_text("---\nname: fabrik-designer\nmodel: sonnet\neffort: medium\n---\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_ohne_einstellung_gilt_definition(self):
        st = a.stand(self.daten, self.agenten)
        self.assertEqual(st["builder"]["gilt_modell"], "opus")
        self.assertIsNone(st["builder"]["modell"])
        self.assertIsNone(st["builder"]["gilt_effort"])
        self.assertEqual(st["designer"]["gilt_effort"], "medium")
        self.assertEqual(a.aufruf(self.daten)["builder"], {})

    def test_setzen_und_zuruecksetzen(self):
        a.setze(self.daten, "builder", "modell", "Sonnet", self.agenten)
        st = a.setze(self.daten, "builder", "effort", "hoch", self.agenten)
        self.assertEqual((st["gilt_modell"], st["gilt_effort"]), ("sonnet", "high"))
        self.assertEqual(a.aufruf(self.daten)["builder"], {"model": "sonnet", "effort": "high"})
        st = a.setze(self.daten, "builder", "modell", "standard", self.agenten)
        self.assertEqual((st["gilt_modell"], st["modell"]), ("opus", None))
        a.setze(self.daten, "builder", "effort", "standard", self.agenten)
        d = json.loads((self.daten / "einstellungen.json").read_text())
        self.assertNotIn("arbeiter", d)

    def test_andere_einstellungen_bleiben(self):
        self.daten.mkdir(parents=True)
        (self.daten / "einstellungen.json").write_text(json.dumps({"lager": "/x", "deaktiviert": ["designer"]}))
        a.setze(self.daten, "approver", "effort", "max", self.agenten)
        d = json.loads((self.daten / "einstellungen.json").read_text())
        self.assertEqual(d["lager"], "/x")
        self.assertEqual(d["deaktiviert"], ["designer"])
        self.assertEqual(d["arbeiter"]["approver"], {"effort": "max"})

    def test_ungueltige_eingaben(self):
        for rolle, feld, wert in [("chef", "modell", "opus"), ("builder", "farbe", "rot"),
                                  ("builder", "modell", "gpt"), ("builder", "effort", "ultra"),
                                  ("builder", "modell", None), ("builder", "effort", 3)]:
            with self.subTest(rolle=rolle, feld=feld, wert=wert):
                with self.assertRaises(a.Ungueltig):
                    a.setze(self.daten, rolle, feld, wert, self.agenten)
        self.assertFalse((self.daten / "einstellungen.json").exists())

    def test_kaputte_datei_und_fremde_werte(self):
        self.daten.mkdir(parents=True)
        (self.daten / "einstellungen.json").write_text("{kaputt")
        self.assertEqual(a.eigene(self.daten), {})
        (self.daten / "einstellungen.json").write_text(json.dumps(
            {"arbeiter": {"builder": {"modell": "gpt", "effort": "high"}, "chef": {"modell": "opus"}, "spec": "x"}}))
        self.assertEqual(a.eigene(self.daten), {"builder": {"effort": "high"}})

    def test_alle_rollen_und_auswahl(self):
        self.assertEqual(set(a.stand(self.daten, self.agenten)), set(a.ROLLEN))
        aus = a.auswahl()
        self.assertEqual([m["wert"] for m in aus["modelle"]], ["fable", "opus", "sonnet", "haiku"])
        self.assertEqual([e["wert"] for e in aus["efforts"]], ["low", "medium", "high", "xhigh", "max"])

    def test_echte_definitionen_haben_modell(self):
        for rolle, st in a.stand(self.daten).items():
            with self.subTest(rolle=rolle):
                self.assertIn(st["standard_modell"], a.MODELLE)


class KommandozeileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.daten = Path(self.tmp.name) / "daten"
        self.lager = Path(self.tmp.name) / "lager"
        self.env = {**os.environ, "FABRIK_DATEN": str(self.daten), "FABRIK_LAGER": str(self.lager)}

    def tearDown(self):
        self.tmp.cleanup()

    def fabrik(self, *args):
        return subprocess.run([sys.executable, str(WERKZEUG), *args], env=self.env,
                              capture_output=True, text=True, timeout=30)

    def test_setzen_anzeigen_modelle(self):
        r = self.fabrik("arbeiter", "inspector", "modell", "haiku")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Haiku", r.stdout)
        self.assertEqual(self.fabrik("arbeiter", "inspector", "effort", "low").returncode, 0)
        self.assertIn("niedrig", self.fabrik("arbeiter", "inspector").stdout)
        d = json.loads(self.fabrik("modelle").stdout)
        self.assertEqual(d["aufruf"]["inspector"], {"model": "haiku", "effort": "low"})
        self.assertEqual(d["aufruf"]["builder"], {})
        self.assertEqual(d["stand"]["builder"]["gilt_modell"], "opus")

    def test_fehler_mit_meldung(self):
        for args in (["arbeiter", "inspector", "modell", "gpt"], ["arbeiter", "chef", "modell", "opus"],
                     ["arbeiter", "inspector", "farbe", "rot"], ["arbeiter", "inspector", "modell"]):
            with self.subTest(args=args):
                r = self.fabrik(*args)
                self.assertEqual(r.returncode, 1)
                self.assertTrue(r.stderr.startswith("fabrik:"))

    def test_meldung_von_arbeitern_geht_weiter(self):
        aid = json.loads(self.fabrik("neu", "--titel", "T", "--slug", "t", "--auftrag", "x").stdout)["id"]
        r = self.fabrik("arbeiter", aid, "builder", "ende")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.fabrik("arbeiter", aid, "builder", "los").returncode, 1)
        status = json.loads(self.fabrik("zeige", aid).stdout)
        self.assertEqual(status["aktive_arbeiter"], [])


class HalleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        home = Path(self.tmp.name) / "home"
        self.daten = home / ".claude/fabrik"
        (home / ".claude/projects").mkdir(parents=True)
        self.s = lade("halle_server_arbeiter_test", PLUGIN / "halle/server.py",
                      {"HOME": str(home), "FABRIK_LAGER": str(home / "lager"), "FABRIK_DATEN": str(self.daten)})
        self.server = self.s.LokalerServer(("127.0.0.1", 0), self.s.Halle)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.basis = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def post(self, pfad, daten, origin=True):
        kopf = {"Content-Type": "application/json", "X-Fabrik-Halle": "1"}
        if origin:
            kopf["Origin"] = self.basis
        req = urllib.request.Request(self.basis + pfad, data=json.dumps(daten).encode(), headers=kopf, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            with e:
                inhalt = e.read()
            try:
                return e.code, json.loads(inhalt)
            except json.JSONDecodeError:
                return e.code, inhalt.decode()

    def test_stand_enthaelt_arbeiter(self):
        with urllib.request.urlopen(self.basis + "/api/stand", timeout=5) as r:
            d = json.loads(r.read())
        self.assertEqual(set(d["arbeiter"]["stand"]), set(a.ROLLEN))
        self.assertTrue(d["arbeiter"]["modelle"])

    def test_speichern_ueber_halle(self):
        code, d = self.post("/api/arbeiter", {"rolle": "spec", "feld": "modell", "wert": "fable"})
        self.assertEqual(code, 200)
        self.assertEqual(d["stand"]["gilt_modell"], "fable")
        gespeichert = json.loads((self.daten / "einstellungen.json").read_text())
        self.assertEqual(gespeichert["arbeiter"]["spec"], {"modell": "fable"})
        # Prüfer abschalten lässt die Modellwahl stehen.
        code, _ = self.post("/api/rolle", {"rolle": "designer", "aktiv": False})
        self.assertEqual(code, 200)
        gespeichert = json.loads((self.daten / "einstellungen.json").read_text())
        self.assertEqual(gespeichert["arbeiter"]["spec"], {"modell": "fable"})
        self.assertEqual(gespeichert["deaktiviert"], ["designer"])

    def test_ungueltig_und_fremder_ursprung(self):
        code, d = self.post("/api/arbeiter", {"rolle": "spec", "feld": "modell", "wert": "gpt"})
        self.assertEqual(code, 400)
        self.assertIn("Modell", d["fehler"])
        code, _ = self.post("/api/arbeiter", ["spec"])
        self.assertEqual(code, 400)
        code, _ = self.post("/api/arbeiter", {"rolle": "spec", "feld": "modell", "wert": "opus"}, origin=False)
        self.assertEqual(code, 403)

    def test_speicherfehler_wird_gemeldet(self):
        with mock.patch.object(self.s.arbeiter, "_schreibe_alles", side_effect=OSError("voll")):
            code, d = self.post("/api/arbeiter", {"rolle": "spec", "feld": "effort", "wert": "max"})
        self.assertEqual(code, 500)
        self.assertIn("nicht gespeichert", d["fehler"])


if __name__ == "__main__":
    unittest.main()
