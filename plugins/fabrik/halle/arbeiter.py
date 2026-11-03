"""Modell und Effort je Arbeiter: lesen, prüfen und speichern.

Wird vom Werkzeug fabrik (`fabrik arbeiter <rolle> modell|effort <wert>`,
`fabrik modelle`) und von der Halle genutzt. Nur Standardbibliothek.

Gespeichert wird in einstellungen.json im Datenordner (~/.claude/fabrik/)
unter dem Schlüssel "arbeiter", also außerhalb des Plugins: Updates lassen
die Auswahl unberührt. Fehlt eine Einstellung, gilt der Standard aus der
Agent-Definition (agents/fabrik-<rolle>.md).
"""
import fcntl
import json
import os
import re
from contextlib import contextmanager
from pathlib import Path

WERK = Path(__file__).resolve().parent.parent
AGENTEN = WERK / "agents"

ROLLEN = ["spec", "builder", "sicherheit", "designer", "inspector", "bediener", "approver"]
# Werte, die das Agent-Werkzeug von Claude Code für `model` und `effort` annimmt.
EFFORTS = ["low", "medium", "high", "xhigh", "max"]
# Je Modell die Effort-Stufen, die es unterstützt.
MODELLE = {
    "fable": EFFORTS,
    "opus": EFFORTS,
    "sonnet": EFFORTS,
    "haiku": EFFORTS,
}
MODELL_NAMEN = {"fable": "Fable", "opus": "Opus", "sonnet": "Sonnet", "haiku": "Haiku"}
EFFORT_NAMEN = {"low": "niedrig", "medium": "mittel", "high": "hoch", "xhigh": "sehr hoch", "max": "max"}
# Deutsche Eingaben auf der Kommandozeile sind ebenfalls erlaubt.
EFFORT_ALIAS = {"niedrig": "low", "mittel": "medium", "hoch": "high", "sehr-hoch": "xhigh",
                "sehrhoch": "xhigh", "sehr_hoch": "xhigh", "sehr hoch": "xhigh", "maximal": "max"}
# Mit diesem Wert wird die eigene Einstellung entfernt und der Standard gilt wieder.
STANDARD = "standard"
FELDER = ("modell", "effort")


class Ungueltig(ValueError):
    """Unbekannte Rolle, unbekanntes Feld oder Wert, den das Modell nicht kennt."""


def einstellungen_datei(daten):
    return Path(daten) / "einstellungen.json"


@contextmanager
def _sperre(daten):
    Path(daten).mkdir(parents=True, exist_ok=True)
    with open(Path(daten) / "einstellungen.lock", "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _lies_alles(daten):
    try:
        d = json.loads(einstellungen_datei(daten).read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return d if isinstance(d, dict) else {}


def _schreibe_alles(daten, d):
    datei = einstellungen_datei(daten)
    tmp = datei.with_name(f".einstellungen.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, datei)


def normalisiere(feld, wert):
    """Bringt eine Eingabe in die Form, die das Agent-Werkzeug erwartet. STANDARD bleibt STANDARD."""
    if not isinstance(wert, str):
        raise Ungueltig(f"{feld} muss ein Text sein")
    w = wert.strip().lower()
    if w in ("", STANDARD):
        return STANDARD
    if feld == "modell":
        if w not in MODELLE:
            raise Ungueltig(f"Modell muss eines von {', '.join(MODELLE)} oder {STANDARD} sein")
        return w
    if feld == "effort":
        w = EFFORT_ALIAS.get(w, w)
        if w not in EFFORTS:
            raise Ungueltig(f"Effort muss einer von {', '.join(EFFORTS)} oder {STANDARD} sein")
        return w
    raise Ungueltig(f"Feld muss {' oder '.join(FELDER)} sein")


def eigene(daten):
    """Gespeicherte Auswahl je Rolle, nur gültige Einträge: {rolle: {"modell": …, "effort": …}}."""
    roh = _lies_alles(daten).get("arbeiter")
    ergebnis = {}
    if not isinstance(roh, dict):
        return ergebnis
    for rolle, werte in roh.items():
        if rolle not in ROLLEN or not isinstance(werte, dict):
            continue
        sauber = {}
        for feld in FELDER:
            try:
                w = normalisiere(feld, werte.get(feld))
            except Ungueltig:
                continue
            if w != STANDARD:
                sauber[feld] = w
        if sauber:
            ergebnis[rolle] = sauber
    return ergebnis


def definition(rolle, agenten=None):
    """Modell und Effort aus der Agent-Definition (Frontmatter), soweit angegeben."""
    datei = Path(agenten or AGENTEN) / f"fabrik-{rolle}.md"
    try:
        text = datei.read_text()
    except (OSError, UnicodeDecodeError):
        return {"modell": None, "effort": None}
    kopf = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    werte = {}
    for zeile in (kopf.group(1).splitlines() if kopf else []):
        m = re.match(r"^(model|effort)\s*:\s*['\"]?([A-Za-z0-9_.-]+)['\"]?\s*$", zeile.strip())
        if m:
            werte[m.group(1)] = m.group(2).lower()
    modell = werte.get("model")
    effort = werte.get("effort")
    return {"modell": modell if modell in MODELLE else None, "effort": effort if effort in EFFORTS else None}


def stand(daten, agenten=None):
    """Für jede Rolle: eigene Auswahl, Standard aus der Definition und was beim Start gilt."""
    gespeichert = eigene(daten)
    ergebnis = {}
    for rolle in ROLLEN:
        std = definition(rolle, agenten)
        eigen = gespeichert.get(rolle, {})
        modell = eigen.get("modell") or std["modell"]
        effort = eigen.get("effort")
        # Passt der Standard-Effort nicht zum gewählten Modell, entfällt er.
        if not effort and std["effort"] and modell and std["effort"] in MODELLE.get(modell, ()):
            effort = std["effort"]
        ergebnis[rolle] = {
            "modell": eigen.get("modell"),
            "effort": eigen.get("effort"),
            "standard_modell": std["modell"],
            "standard_effort": std["effort"],
            "gilt_modell": modell,
            "gilt_effort": effort,
        }
    return ergebnis


def aufruf(daten):
    """Parameter für den Agent-Aufruf je Rolle: nur gesetzte Werte, sonst leer (dann gilt die Definition)."""
    ergebnis = {}
    for rolle in ROLLEN:
        eigen = eigene(daten).get(rolle, {})
        parameter = {}
        if eigen.get("modell"):
            parameter["model"] = eigen["modell"]
        if eigen.get("effort"):
            parameter["effort"] = eigen["effort"]
        ergebnis[rolle] = parameter
    return ergebnis


def setze(daten, rolle, feld, wert, agenten=None):
    """Speichert Modell oder Effort einer Rolle. STANDARD entfernt die eigene Einstellung.

    Liefert den neuen Stand der Rolle (wie in `stand`). Wirft Ungueltig bei
    falschen Eingaben und OSError, wenn nicht gespeichert werden kann."""
    if rolle not in ROLLEN:
        raise Ungueltig(f"Rolle muss eine von {', '.join(ROLLEN)} sein")
    if feld not in FELDER:
        raise Ungueltig(f"Feld muss {' oder '.join(FELDER)} sein")
    w = normalisiere(feld, wert)
    with _sperre(daten):
        d = _lies_alles(daten)
        alle = d.get("arbeiter") if isinstance(d.get("arbeiter"), dict) else {}
        eigen = dict(alle.get(rolle) or {}) if isinstance(alle.get(rolle), dict) else {}
        if w == STANDARD:
            eigen.pop(feld, None)
        else:
            eigen[feld] = w
        # Effort muss zum Modell passen, das dann gilt.
        modell = eigen.get("modell") or definition(rolle, agenten)["modell"]
        if eigen.get("effort") and modell and eigen["effort"] not in MODELLE.get(modell, ()):
            if feld == "effort":
                raise Ungueltig(f"{MODELL_NAMEN[modell]} unterstützt Effort {eigen['effort']} nicht")
            eigen.pop("effort")
        if eigen:
            alle[rolle] = eigen
        else:
            alle.pop(rolle, None)
        if alle:
            d["arbeiter"] = alle
        else:
            d.pop("arbeiter", None)
        _schreibe_alles(daten, d)
    return stand(daten, agenten)[rolle]


def auswahl():
    """Mögliche Werte für Oberfläche und Hilfe."""
    return {
        "modelle": [{"wert": m, "name": MODELL_NAMEN[m], "efforts": list(e)} for m, e in MODELLE.items()],
        "efforts": [{"wert": e, "name": EFFORT_NAMEN[e]} for e in EFFORTS],
    }
