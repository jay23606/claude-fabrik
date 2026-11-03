# Roadmap

Phasen des Projekts Claude Fabrik. Fertige Features sind abgehakt, offene stehen darunter. Der Spec-Arbeiter legt die Roadmap an, der Orchestrator hakt nach der Freigabe die fertigen Features ab.

## Phase 1: Grundlage (Version 0.1.0)

- [x] `/fabrik` mit Spec, Bau, bis zu drei Prüfrunden und Freigabe
- [x] Arbeiter Spec, Builder, Sicherheit, Inspector, Bediener, Designer, Approver
- [x] Fabrikhalle im Browser, lokal auf 127.0.0.1:7333

## Phase 2: Übersicht und Bedienung (Version 0.2.0)

- [x] Halle zeigt bei Sitzungen im Benutzerordner den Namen des Projekts
- [x] Halle auf schmalen Bildschirmen scrollbar, größere Trefferflächen
- [x] Infokarte als Dialog mit Fokusführung

## Phase 3: Projektdateien und Updates (Versionen 0.3.0 und 0.3.1)

- [x] `todos.md` und `roadmap.md` im Projektordner
- [x] `fabrik neue-version` archiviert die Todos und behält die Roadmap
- [x] Update-Hinweis mit `fabrik update`, Banner in der Halle, abschaltbar
- [x] `changelog.md` im Projektordner, vom Approver vor dem Commit geführt

## Phase 4: Steuerung der Arbeiter (Version 0.4.0)

- [x] Modell und Effort je Arbeiter in der Halle wählbar
- [x] Auswahl auf der Kommandozeile (`fabrik arbeiter`, `fabrik modelle`)
- [x] `/fabrik` gibt Modell und Effort beim Start eines Arbeiters mit

## Phase 5: Korrekturen aus den Prüfungen

- [ ] Einstellungen im CLI unter derselben Sperre schreiben (#25)
- [ ] Beschädigte Einstellungsdatei führt nicht mehr zum Absturz (#26)
- [ ] Effort-Liste je Modell pflegen oder Filter streichen (#27)
- [ ] Einstellungen in `aufruf` nur einmal lesen (#28)
- [ ] Spec: AK-7 auf aktuelle Version und Abnahmekriterien für Modell und Effort (#29)
- [ ] Farbiger linker Rahmen an `.alarm` entfernt (#30)
- [ ] Update-Banner: Schließen-Knopf, Überlappung, Kopier-Rückmeldung, Browserprüfung (#19, #21, #24, #31)
