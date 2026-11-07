# Todos

## Version 6: offene Punkte aus dem Backlog (Patch 0.3.2)

Alle offenen Backlog-Punkte aus Version 0.3.0 bis 5 sind übernommen (Nutzerwunsch: neue Version bauen und pushen). Issue-Nummern verweisen auf GitHub `jahnouni/claude-fabrik`. Jeden Punkt schließt nur ein Issue, wenn seine Akzeptanzkriterien nachweislich erfüllt sind.

Hinweis des Builders zur Versionsnummer: `plugin.json` und `CHANGELOG.md` standen schon auf 0.4.0 (unveröffentlicht, neuestes Release ist v0.3.1). Ein Patch 0.3.2 wäre kleiner als 0.4.0 und würde die Funktionen aus 0.4.0 unter einer Patch-Nummer ausliefern. Deshalb steht die Version auf **0.4.1**; soll es doch 0.3.2 sein, müssen `plugin.json`, der Abschnitt im CHANGELOG und AK-7 angepasst werden.

### Halle, ohne Issue

- [x] Halle: auch `~/Library/Application Support/Claude/scratch-workspaces/…` als Sammelordner behandeln, damit solche Sitzungen einen Projektnamen statt des kodierten Ordnernamens zeigen. (Backlog) Gelöst: `server.py` zählt `~/Library/Application Support/Claude/scratch-workspaces` zu den Sammelordnern (`TEMP_ORDNER`), solche Sitzungen und ihre Projektordner unter `~/.claude/projects` zeigen das Projekt der zuletzt geschriebenen Datei oder den Titel; Tests in `tests/test_korrekturen.py`.
- [x] Halle: für Temp-Ordner ohne Projekt und Titel einen eigenen Platzhalter („Temp-Ordner“) erwägen. Achtung: AK-6 verlangt derzeit „~ (Benutzerordner)“, deshalb Spec anpassen oder Punkt verwerfen und begründen. (Backlog) Gelöst: Neue Funktion `platzhalter()` liefert in Temp- und Arbeitsordnern „Temp-Ordner“, im Benutzerordner weiter „~ (Benutzerordner)“; AK-6 in `.fabrik/spec.md` ist entsprechend angepasst, Test in `test_halle_namen.py` und `test_korrekturen.py`.

### Designer

- [x] [D-K1] Verbindungsmeldung `#verbindung` ohne `role="status"`/`aria-live` #3 (Designer) Gelöst: `#verbindung` sitzt in der neuen Kopfleiste mit `role="status"` und `aria-live="polite"`, bleibt im Dokument und wird über den Text (leer = verbunden, per `:empty` ausgeblendet) gesteuert, damit Screenreader die Meldung ansagen.
- [x] [D-K2] `.haken.offen` zu kontrastarm (ca. 2:1), zusätzlich Symbol statt nur Farbe #4 (Designer) Gelöst: `.haken.offen` ist jetzt `#6e6858` (5,0:1), `.ja`/`.nein` dunkler (5,9:1 bzw. 7,0:1); die Zeichen ✓ ✗ ○ bleiben, dazu ein vorgelesener Text „erfüllt/nicht erfüllt/offen“.
- [x] [D-K3] Schrift 11 px in Chips, `.schritt`, Eckdaten und Verlauf auf mind. 12 px #5 (Designer) Gelöst: `.schritt`, `.eckdaten span`, `.verlauf time` und Tabellenköpfe auf 12 px (Chips waren schon 12 px), ebenso die Texte der Werkbänke und die Schilder „Pause“ und „abgeschaltet“ in der Szene.
- [x] [D-K4] Fokus der SVG-Elemente schwach sichtbar, gelber Rahmen 3 px #6 (Designer) Gelöst: Gemeinsame Regel für `:focus-visible` an Tafelzahlen, Laufzeit-Einträgen, Werkstatt-Kopf, Werkbänken und Arbeitern: durchgezogener gelber Rahmen, 3 px (Pakete hatten ihn schon).
- [x] [D-K5] Tooltip nur per Hover, auch per Tastatur erreichbar machen #7 (Designer) Gelöst: Arbeiter, Pakete und Werkbänke zeigen den Tooltip schon beim Tastaturfokus; neu blendet Escape einen offenen Tooltip aus, bevor es die Karte schließt.
- [x] [D-K6] Klick auf `#schleier` soll die Karte schließen #8 (Designer) Gelöst: Der Klick auf `#schleier` ruft `schliesseKarte` auf (war bereits verdrahtet, im Browser mit offener Karte geprüft); der Fokus geht danach an den Auslöser zurück.
- [x] [D-K7] Ladefehler der Karte ohne Rückmeldung #9 (Designer) Gelöst: `zeigeKartenFehler` öffnet die Karte mit Grund (`role="alert"`) und Knopf „Erneut versuchen“; solange die Karte offen ist, versucht die regelmäßige Abfrage es weiter. Im Browser mit `#F-9999` geprüft.
- [x] [D-K8] Eskalationsblinken bei `prefers-reduced-motion` entfernen, statisches Symbol ergänzen #10 (Designer) Gelöst: Bei `prefers-reduced-motion` entfällt das Blinken (globale Regel), und jedes eskalierte Paket trägt ein eigenes, nie blinkendes Ausrufezeichen (`.esk-zeichen`) auf der Leuchte.
- [x] [D-K1] Dezenter Platzhalter `#8b93a7` knapp im Kontrast, z. B. `#a0a8bb` #11 (Designer) Gelöst: Platzhalter und Zustandszeile der Werkbänke in `#a0a8bb` mit 12 px (5,5:1 auf dem Boden).
- [x] [D-K2] Escape ruft `schliesseKarte` auch bei geschlossener Karte auf #12 (Designer) Gelöst: Der Escape-Handler prüft `zustand.offeneKarte` und ruft `schliesseKarte` nur bei offener Karte auf (die Funktion selbst bricht zusätzlich ab).
- [x] [D-K1] `.update-zu` auf mind. 44 px #19 (Designer) Gelöst: Der Schließen-Knopf ist 44 × 44 px und steht in der Leiste rechts im Fluss statt absolut positioniert.
- [x] [D-K2] `.kopieren.ok`: Kontrast zu gering, dunkleres Grün #20 (Designer) Gelöst: `.kopieren.ok` nutzt `--gruen-dunkel` `#1d6b2e` (weiße Schrift 6,6:1), ein Fehlschlag `--rot-dunkel`.
- [x] [D-K3] `.verbindung` und Update-Banner überlappen sich #21 (Designer) Gelöst: Beide stehen in der neuen `.kopfleiste` untereinander im normalen Fluss über der Halle und können sich nicht mehr überlagern.
- [x] [D-K4] Hinweissatz im Banner fest formulieren #22 (Designer) Gelöst: Der Satz „Im Terminal ausführen, danach Claude Code neu starten.“ steht fest in `index.html`, er wird nicht mehr aus Serverdaten zusammengesetzt.
- [x] [D-K5] Kopier-Rückmeldung per `aria-live` ansagen #23 (Designer) Gelöst: Neue Ansage-Region `#ansage` (`role="status"`, `aria-live="polite"`); `kopiere` sagt „Befehl in die Zwischenablage kopiert.“ oder bei Fehlschlag den Grund an.
- [x] [D-K3] Update-Banner verdeckt einen Teil der Halle #37 (Designer) Gelöst: Das Banner liegt nicht mehr über der Szene, sondern als schmale Leiste darüber; die Halle (Flex-Layout) bekommt den restlichen Platz und skaliert sich hinein. Screenshots bei 1280 × 800 und 1024 × 700 geprüft.
- [x] [D-K1] Alarm-Box mit farbigem linkem Rahmen entfernen, Projektregel „keine farbigen Randakzente“ #30 (Designer) Gelöst: `.alarm` hat statt `border-left: 5px` nur noch einen dünnen, ringsum gleichen Rahmen.
- [x] [D-K4] Kopieren nur mit Farbsignal, Symbol ergänzen #31 (Designer) Gelöst: Der Knopf zeigt nach dem Klick „✓ kopiert: …“ bzw. „✗ nicht kopiert, bitte von Hand markieren: …“, dazu die Ansage; das regelmäßige Neuzeichnen der Karte überschreibt die Rückmeldung nicht mehr.

### Code, Inspector

- [x] [C-K1] Fehlgeschlagene Update-Abfrage überschreibt bekanntes `neueste` im Cache, alten Wert behalten #15 (Inspector) Gelöst: `update.stand` behält bei einer gescheiterten Abfrage `neueste` aus dem Zwischenspeicher und erneuert nur `geprueft`; Test `test_fehlschlag_behaelt_bekannte_version`.
- [x] [C-K3] Netzfehler löscht bekannten Update-Hinweis #15 (Inspector) Gelöst: Gleiche Änderung wie C-K1 (#15); `fabrik update` und die Halle zeigen ein gefundenes Update weiter.
- [x] [C-K2] `nur_cache` in der Halle ohne Altersgrenze #17 (Inspector) Gelöst: Mit `nur_cache` gilt der Zwischenspeicher nur, wenn er jünger als 24 Stunden ist (`NUR_CACHE_MAX_ALTER_S`), Zeitstempel aus der Zukunft zählen nicht; Test `test_nur_cache_mit_altersgrenze`.
- [x] [C-K3] Rückfall-Dict in `cmd_update` mit gleichem Schema wie `update.stand` #18 (Inspector) Gelöst: Neue Funktion `update.leerer_stand()` liefert das gemeinsame Schema; `cmd_update` nutzt sie im Fehlerfall oder `UPDATE_RUECKFALL` mit denselben Schlüsseln, wenn das Modul fehlt; zwei Tests.
- [x] [C-K3] Effort-Liste je Modell wirkungslos #27 (Inspector) Gelöst: Filter gestrichen, `MODELLE` ist eine einfache Liste, jede Effort-Stufe ist mit jedem Modell wählbar; Halle, `auswahl()` und README angepasst, Test `test_effort_frei_waehlbar`.
- [x] [C-K4] Einstellungen bei Aufruf siebenmal gelesen #28 (Inspector) Gelöst: `aufruf` liest `eigene(daten)` einmal vor der Schleife; Test zählt genau einen Lesevorgang.
- [x] [C-K1] Ungültiges UTF-8 in der Einstellungsdatei bricht Befehle ab #32 (Inspector) Gelöst: `_lies_alles` liest ausdrücklich UTF-8 und fängt `ValueError` (umfasst `UnicodeDecodeError`); `fabrik einstellung`, `modelle`, `rollen` und `update` laufen mit kaputten Bytes durch, Test `test_ungueltiges_utf8_gilt_als_leer`.
- [x] [C-K2] Negative Content-Length hängt den POST-Handler #33 (Inspector) Gelöst: `do_POST` antwortet bei negativer oder nicht lesbarer Länge sofort mit 400 und bei mehr als 1024 Bytes mit 413; Tests mit `http.client` gegen eine Testhalle.
- [x] [C-K4] Lesen der Einstellungen schreibt Standardwert mit #34 (Inspector) Gelöst: `lies_einstellungen` liefert die Datei unverändert, abgeschaltete Prüfer kommen aus `arbeiter.deaktivierte(d)`; `deaktiviert` wird nur noch beim Schalten eines Prüfers geschrieben, Test `test_lesen_schreibt_keinen_standardwert`.
- [x] [C-K5] Rollen- und Prüferlisten an drei Stellen gepflegt #35 (Inspector) Gelöst: `ROLLEN`, `SCHALTBAR` und `deaktivierte()` stehen nur in `halle/arbeiter.py`; `bin/fabrik` und `server.py` übernehmen sie, die Halle bekommt `schaltbar` mit `/api/stand`.
- [x] [C-K6] Pycache-Ordner im Plugin- und Testordner #36 (Inspector) Gelöst: Vorhandene `__pycache__`-Ordner gelöscht; `bin/fabrik`, `server.py` und alle Tests setzen `sys.dont_write_bytecode`, README nennt `python3 -B`. Test prüft, dass `fabrik update` keinen Ordner im Plugin anlegt.

### Sicherheit

- [x] [S-K1] `projekt_von_datei`: Pfade mit `os.path.normpath` normalisieren, `/Volumes` überspringen #13 (Sicherheit) Gelöst: `projekt_von_datei` normalisiert absolute Pfade mit `os.path.normpath` vor allen Prüfungen und sucht nicht unter `/Volumes`, `/net`, `/Network`, `/mnt` und `/media`; Test `test_pfad_wird_normalisiert`.
- [x] [S-K1] `cache_lesen`: `neueste` per `version_lesen` auf SemVer prüfen #16 (Sicherheit) Gelöst: `cache_lesen` übernimmt `neueste` nur, wenn `version_lesen` es annimmt (ohne führendes v), sonst `None`; Test `test_cache_nur_mit_semver`.
- [x] [S-K1] Negative Content-Length hängt den POST-Handler #33 (Sicherheit, Dublette zu C-K2) Gelöst: Siehe C-K2 (#33), 400 bei negativer Länge, 413 bei mehr als 1024 Bytes.

### Bediener

- [x] [B-K1] Update-Banner im Browser visuell prüfen #24 (Bediener) Gelöst: Halle lokal auf 127.0.0.1:7543 mit eigenem Datenordner und Zwischenspeicher 9.9.9 gestartet und mit Chrome headless bei 1280 × 800 und 1024 × 700 aufgenommen: Leiste mit Version, Kopier-Knopf, festem Satz und 44-px-Schließen-Knopf über der Halle, nichts verdeckt; Fehlerkarte und Alarm-Box ebenfalls angesehen.
- [x] [B-K1] Spec: AK-7 nennt noch 0.3.0, auf aktuelle Version und Abnahmekriterien für Modell und Effort anpassen #29 (Bediener) Gelöst: AK-7 nennt 0.4.1, neue AK-9 (Modell und Effort in Halle und Kommandozeile), AK-10 (`fabrik modelle`/`/fabrik`) und AK-11 (beschädigte Einstellungsdatei, gemeinsame Sperre); AK-8 sagt jetzt, dass ein bekanntes Update bei Netzfehlern stehen bleibt.
