# Änderungen

## Version 6 – 2026-11-03

Fabrik-Version 6 des Auftrags F-0004, entspricht Plugin-Version 0.4.1 (Einzelheiten im Abschnitt 0.4.1).

### Geändert
- Sitzungen in den Arbeitsordnern der Claude-App zeigen in der Halle den Namen ihres Projekts, ohne Projekt und Titel steht in Temp- und Arbeitsordnern „Temp-Ordner“.
- Update-Hinweis und Verbindungsmeldung stehen als Leisten über der Halle und verdecken nichts mehr.
- Jede Effort-Stufe ist mit jedem Modell wählbar, Rollen und abschaltbare Prüfer stehen nur noch in `halle/arbeiter.py`.

### Behoben
- Bedienbarkeit und Kontrast der Halle sind verbessert (Ansagen für Screenreader, Fokusrahmen, Schriftgrößen, Fehlerkarte mit „Erneut versuchen“, kein farbiger Randakzent).
- Ein Netzfehler löscht ein bekanntes Update nicht mehr, und der Zwischenspeicher nimmt nur gültige Versionsnummern an.
- Ungültiges UTF-8 in `einstellungen.json` bricht keine Befehle mehr ab, und Lesen schreibt keine Standardwerte mehr in die Datei.
- Schreibende Anfragen an die Halle mit negativer oder zu großer Länge werden sofort abgelehnt, Pfade aus Transkripten werden normalisiert.
- Werkzeug und Halle legen keine `__pycache__`-Ordner im Plugin mehr an.

## 0.4.1 – 2026-11-03

Korrekturen aus den Prüfungen der Versionen 0.3.0 bis 0.4.0.

### Geändert
- Halle: Sitzungen in den Arbeitsordnern der Claude-App (`~/Library/Application Support/Claude/scratch-workspaces/…`) zeigen wie Sitzungen im Benutzer- oder Temp-Ordner den Namen ihres Projekts. Ohne Projekt und Titel steht in Temp- und Arbeitsordnern „Temp-Ordner“, im Benutzerordner weiter „~ (Benutzerordner)“.
- Halle: Update-Hinweis und Verbindungsmeldung stehen als schmale Leisten über der Halle, schieben sie nach unten und verdecken weder die Halle noch einander. Der Hinweissatz ist fest formuliert, der Schließen-Knopf 44 × 44 px groß.
- Halle: Jede Effort-Stufe ist mit jedem Modell wählbar; die bisherige Liste je Modell war wirkungslos und entfällt.
- Rollen und abschaltbare Prüfer stehen nur noch an einer Stelle (`halle/arbeiter.py`), Werkzeug und Halle übernehmen sie von dort.

### Behoben
- Halle, Bedienung: Verbindungsmeldung und Kopier-Rückmeldung werden für Screenreader angesagt; Kopieren zeigt Zeichen und Wort („✓ kopiert“) statt nur Farbe, auch wenn es scheitert.
- Halle, Bedienung: Ladefehler einer Infokarte werden mit Grund und „Erneut versuchen“ gezeigt, solange die Karte offen ist, wird es weiter versucht. Escape blendet erst den Tooltip aus und schließt die Karte nur, wenn sie offen ist.
- Halle, Darstellung: Tastaturfokus in der Szene mit durchgezogenem gelbem Rahmen (3 px); kleine Schrift (Schritte, Eckdaten, Verlauf, Werkbänke) auf mindestens 12 px; Kontrast von offenen Haken, Platzhaltern und Kopier-Bestätigung erhöht; Abnahmekriterien nennen ihren Zustand auch für Screenreader; eskalierte Aufträge tragen ein nicht blinkendes Ausrufezeichen; die Alarm-Box hat keinen farbigen Randakzent mehr.
- Update-Hinweis: Ein Netzfehler löscht ein schon bekanntes Update nicht mehr; der Zwischenspeicher liefert nur gültige Versionsnummern; die Halle nimmt keinen Zwischenspeicher, der älter als 24 Stunden ist; `fabrik update` hat auch im Fehlerfall dieselben Felder.
- Einstellungen: Ungültiges UTF-8 in `einstellungen.json` bricht keine Befehle mehr ab; Lesen schreibt keine Standardwerte mehr in die Datei; `fabrik modelle` liest die Datei für alle Rollen nur einmal.
- Halle, Sicherheit: Schreibende Anfragen mit negativer oder zu großer Länge werden sofort abgelehnt (400 bzw. 413), statt den Handler zu blockieren. Pfade aus Transkripten werden vor der Prüfung normalisiert, auf eingehängten Laufwerken (`/Volumes` und ähnliche) wird nicht nach Projekten gesucht.
- Werkzeug und Halle legen keine `__pycache__`-Ordner im Plugin an.

## Version 5 – 2026-11-03

Fabrik-Version 5 des Auftrags F-0004, Plugin-Version unverändert 0.4.0.

### Geändert
- `fabrik rolle` und `fabrik einstellung` schreiben die Einstellungsdatei unter derselben Sperre wie die Halle und die Modellwahl, mit eindeutiger Tempdatei je Prozess.

### Behoben
- Eine beschädigte `einstellungen.json` (JSON-Array, Text, Zahl, `null`, kaputtes JSON oder falsches `deaktiviert`) gilt in Kommandozeile und Halle als leer, statt einen Absturz auszulösen.
- Gleichzeitige Änderungen von Kommandozeile und Halle überschreiben sich nicht mehr gegenseitig.

## Version 4 – 2026-11-03

Fabrik-Version 4 des Auftrags F-0004, entspricht Plugin-Version 0.4.0.

### Hinzugefügt
- In der Halle lassen sich Modell und Effort jedes Arbeiters per Klick oder Tastatur wählen, und die Auswahl steht am Band unter jedem Arbeiter.
- Auf der Kommandozeile setzen `fabrik arbeiter <rolle> modell|effort <wert>` und `fabrik modelle` dieselben Einstellungen.
- `/fabrik` gibt das gewählte Modell und den Effort bei jedem Start eines Arbeiters mit.

### Geändert
- Der Schalter zum An- und Abschalten der Prüfer sitzt jetzt in der Einstellungskarte des Arbeiters, und die Sperrzone der Halle ist etwas nach rechts gerückt.
- Prüfer-Schalter und Modellwahl schreiben die Einstellungsdatei unter einer gemeinsamen Sperre.

## 0.4.0 – 2026-11-03

- Modell und Effort je Arbeiter wählbar. In der Halle öffnet ein Klick (oder Enter/Leertaste) auf einen Arbeiter seine Einstellungen: Modell (Fable, Opus, Sonnet, Haiku oder Standard) und Effort (niedrig, mittel, hoch, sehr hoch, max oder Standard). Bei Prüfern sitzt dort auch der Schalter zum An- und Abschalten, der bisher direkt am Klick hing.
- Am Band steht unter jedem Arbeiter, mit welchem Modell und Effort er startet; Helm- und Anzugfarbe folgen dem Modell. Speichern wird bestätigt, Fehler werden mit Grund angezeigt.
- Kommandozeile: `fabrik arbeiter <rolle> modell <wert>`, `fabrik arbeiter <rolle> effort <wert>` (`standard` setzt zurück), `fabrik arbeiter <rolle>` zeigt den Stand, `fabrik modelle` liefert alles als JSON.
- Die Auswahl liegt in `~/.claude/fabrik/einstellungen.json` und übersteht Updates. Ohne eigene Wahl gilt der Standard aus der Agent-Definition.
- `/fabrik` liest vor jedem Start eines Arbeiters `fabrik modelle` und gibt `model` und `effort` beim Agent-Aufruf mit.
- Die Sperrzone in der Halle sitzt etwas weiter rechts, damit die Beschriftung des Approvers frei bleibt.

## 0.3.1 – 2026-10-30

- Neue Datei `changelog.md` in jedem Projekt im Projektwurzelordner: eine Historie, was in welcher Version hinzugefügt, geändert, behoben oder entfernt wurde. Neueste Version oben.
- Der Approver schreibt den Eintrag der Version vor dem Commit. `fabrik commit` ergänzt ihn aus der Commit-Nachricht, falls er fehlt, so bleibt die Datei wie die Commits und Releases aktuell.

## 0.3.0 – 2026-10-28

- Jedes Projekt hat zwei Dateien im Projektwurzelordner, die alle Arbeiter sehen: `todos.md` für alle Aufgaben aus Prüfungen und Gesprächen, `roadmap.md` für alle Phasen des Projekts mit den Features je Phase. `todos.md` wandert damit aus `.fabrik/` in den Projektordner. Der Spec-Arbeiter legt die Roadmap an, der Orchestrator hakt nach der Freigabe die fertigen Features ab.
- `fabrik neue-version` archiviert die `todos.md` und setzt sie zurück, die `roadmap.md` bleibt erhalten.
- Update-Hinweis: Neuer Befehl `fabrik update` vergleicht die installierte Version mit dem neuesten Release auf GitHub (`jahnouni/claude-fabrik`) und liefert `installiert`, `neueste`, `update_verfuegbar` und `befehl` als JSON. Abgefragt wird höchstens alle 6 Stunden, das Ergebnis liegt in `~/.claude/fabrik/update.json`. Ohne Netz oder bei Fehlern gibt es still keinen Hinweis.
- `/fabrik` meldet beim Start in einer Zeile „Update <Version> verfügbar“ mit dem Befehl zum Aktualisieren.
- Halle: dezentes, schließbares Banner oben rechts mit neuer Version und kopierbarem Befehl. Die Abfrage läuft im Hintergrund, die Halle wartet nie darauf.
- Neue Einstellung `update_hinweis` (Standard `an`), abschalten mit `fabrik einstellung update_hinweis aus`.

## 0.2.0 – 2026-10-28

- Halle: Sitzungen im Benutzerordner oder in Temp-Ordnern (`/tmp`, `/private/tmp`, `/var/folders`) zeigen den Namen des Projekts, an dem sie arbeiten. Maßgeblich ist die zuletzt geschriebene Datei: Titel des Fabrik-Auftrags, sonst Name des Git-Repos oder Projektordner unter `~/Documents/Projekte` bzw. `~/Documents`. Ohne solche Datei steht der Sitzungstitel da, nur ohne beides „~ (Benutzerordner)“, dezent dargestellt. Gilt für laufende und ruhende Plätze; das Ergebnis wird pro Transkript zwischengespeichert.
- Halle auf schmalen Bildschirmen (unter 900 px): die Halle wird in Mindestgröße gezeigt und lässt sich scrollen, statt auf ein Viertel zu schrumpfen; Pakete und die Werkstatt-Überschrift haben größere Trefferflächen.
- Infokarte: als Dialog ausgezeichnet, geschlossen nicht mehr per Tab erreichbar, Fokus springt beim Öffnen in die Karte und beim Schließen zurück auf das auslösende Element; die Halle dahinter ist solange gesperrt.

## 0.1.0 – 2026-10-28

Erste Version als Claude-Code-Plugin.

- `/fabrik` mit Spec, Bau, bis zu drei Prüfrunden und Freigabe
- Arbeiter: Spec, Builder, Sicherheit, Inspector, Bediener, Designer, Approver
- Fabrikhalle im Browser (nur lokal, 127.0.0.1:7333)
- Einrichtung beim ersten Start: Lagerordner, Git-Identität, Autorname, Autostart
- Einstellungen und Laufzeitdateien liegen außerhalb des Plugins und überstehen Updates
