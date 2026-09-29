# CHANGE_LOG — andreaseirich

Vollständiges Änderungsprotokoll im Micro-Change-Format.

## Änderungsprotokoll

### 2026-09-29

#### 08:15 — Schreibweise andicode.de und Preceptly-Beschreibung korrigiert
- **Dateien:** README.md
- **Aktion:** „AndiCode.de“ durchgehend als „andicode.de“ geschrieben (auf Wunsch von Andreas); Badge-Zeile im Kopf auf Stil `plastic` umgestellt, weil `for-the-badge` alles in Großbuchstaben setzt; „public booking“ bei Preceptly entfernt, die öffentliche Buchungsseite ist laut PRD seit 24.09.2026 entfernt, gebucht wird über das Portal
- **Ergebnis:** OK
- **Verifikation:** `grep "AndiCode"` ohne Treffer; Abgleich mit `PRD.md` im Repo preceptly
- **Nächster Schritt:** –
- **Blocker:** –
- **Weiter bei:** –

#### 07:20 — Profil-README überarbeitet
- **Dateien:** README.md
- **Aktion:** Profil neu gegliedert; Projekte (Preceptly, Honey Treasures, ChatCompanion, RADhuus Nortrup, andicode.de) mit Live-Links, Demo-Videos und Case Studies ergänzt; Links zu Portfolio und andicode.de ergänzt; Tech-Stack entdoppelt (C, C++, HTML5, JavaScript standen doppelt), nach Kategorien gruppiert und um belegte Technologien ergänzt (TypeScript, Streamlit, Redis, Railway, Let's Encrypt, Stripe, Linux)
- **Korrekturen:** PayPal-Link (`paypal.me/paypal.me/…` → `paypal.me/andreaseirich04`); ungültige Gunicorn-Badge-Farbe (`%298729` → `499848`); Logos `css3` und `linkedin` fehlen in Simple Icons (CSS-Badge auf `css` umgestellt, LinkedIn-Logo eingebettet); Streak-Karte von Dritt-Instanz auf `streak-stats.demolab.com` umgestellt; Alt-Texte für Statistik-Karten ergänzt; Überschriften-Hierarchie vereinheitlicht
- **Ergebnis:** OK
- **Verifikation:** Projektangaben gegen READMEs und Portfolio-Seiten der Repos abgeglichen; Logo-Slugs gegen simple-icons 16.33.0 geprüft; Live-Erreichbarkeit der externen Links aus der Sandbox nicht prüfbar (Netzwerk gesperrt)
- **Nächster Schritt:** Profilseite auf GitHub sichten (Badges, Statistik-Karten, PayPal-Link)
- **Blocker:** –
- **Weiter bei:** –

### 2026-04-17

#### 13:00 — Docs-Struktur initialisiert
- **Dateien:** docs/CHANGE_LOG.md, docs/README.md, docs/conventions/
- **Aktion:** Initiale Docs-Struktur erstellt
- **Ergebnis:** OK
- **Verifikation:** –
- **Nächster Schritt:** –
- **Blocker:** –
- **Weiter bei:** –
