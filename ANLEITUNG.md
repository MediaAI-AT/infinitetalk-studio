# InfiniteTalk Studio — Anleitung

Automatisierter Workflow: **Textskript → Sprache → Avatar-Video → Fertig**

---

## Was du brauchst

| Tool | Zweck | Kosten |
|------|-------|--------|
| ElevenLabs | Stimme generieren | $22/Monat (Creator) |
| WaveSpeed InfiniteTalk | Avatar-Video rendern | ~$0.30 / 5 Sek. (720p) |
| Python 3 | Pipeline ausführen | kostenlos |
| Node.js | Remotion (Zusammenfügen) | kostenlos |

---

## Einmalige Einrichtung

### 1. Referenzbild ablegen
Lege dein Foto in den `images/` Ordner:
```
images/avatar.jpg
```
Dateiformat: JPG, PNG oder WebP. Am besten ein klares Porträtfoto.

### 2. API-Keys prüfen
In der `.env` Datei stehen bereits deine Keys:
```
WAVESPEED_API_KEY=...
ELEVENLABS_API_KEY=...
```

### 3. Voice ID prüfen
In `config.json` ist deine ElevenLabs Voice ID bereits hinterlegt:
```json
"voice": {
  "id": "TzZHz7pbncdwUyLANO1U"
}
```

---

## Täglicher Workflow

### Schritt 1 — Skript schreiben
Lege eine `.txt` Datei in den `scripts/` Ordner ab:
```
scripts/mein-video.txt
```

Schreib einfach normalen Fließtext. Keine Formatierung nötig.
Das System teilt es automatisch in Chunks auf (~100 Wörter / max. 55 Sek. pro Part).

### Schritt 2 — Skript in config.json eintragen
```json
"scripts": {
  "1": {
    "title": "Mein Video-Titel",
    "file": "scripts/mein-video.txt"
  }
}
```
Für mehrere Videos einfach weitere Einträge hinzufügen (`"2"`, `"3"`, ...).

### Schritt 3 — Trockentest (kostenlos)
```bash
python generate.py --dry-run
```
Zeigt wie viele Chunks entstehen, ohne API-Calls zu machen.

### Schritt 4 — Video generieren
```bash
python generate.py --script 1
```
Die Pipeline läuft automatisch durch:
1. Skript aufteilen
2. Audio via ElevenLabs generieren
3. Bild + Audio an WaveSpeed senden
4. Warten bis fertig (~3-5 Min. pro Part bei 720p)
5. Video herunterladen nach `output/videos/`

### Schritt 5 — Videos zusammenfügen (bei mehreren Parts)
```bash
python stitch.py --script 1
```
Fügt alle Parts mit einem sanften Crossfade zusammen.
Ergebnis: `output/final/1-final.mp4`

---

## Alle Befehle im Überblick

```bash
# Trockentest — zeigt Chunk-Aufteilung, keine Kosten
python generate.py --dry-run

# Ein bestimmtes Skript verarbeiten
python generate.py --script 1

# Nur den ersten Chunk testen (zum Ausprobieren)
python generate.py --script 1 --max-parts 1

# Alle Skripte auf einmal
python generate.py

# Fortschritt anzeigen
python generate.py --status

# Videos zusammenfügen
python stitch.py --script 1

# Alle fertigen Skripte zusammenfügen
python stitch.py
```

---

## Ordnerstruktur

```
infinitetalk-studio/
│
├── images/              ← Dein Referenzfoto ablegen
├── scripts/             ← Textskripte (.txt) ablegen
│
├── output/
│   ├── audio/           ← Generierte Audiodateien (MP3)
│   ├── videos/          ← Einzelne Video-Parts (MP4)
│   └── final/           ← Fertige zusammengefügte Videos
│
├── generate.py          ← Haupt-Pipeline starten
├── stitch.py            ← Videos zusammenfügen
└── config.json          ← Einstellungen anpassen
```

---

## Kosten kalkulieren

**Faustregel:** ~100 Wörter = ~45 Sek. Audio = 1 Part = ca. $2.70 WaveSpeed-Kosten

| Skriptlänge | Parts | Kosten (ca.) |
|-------------|-------|--------------|
| 100 Wörter | 1 | ~$2.70 |
| 300 Wörter | 3 | ~$8.10 |
| 500 Wörter | 5 | ~$13.50 |
| 1000 Wörter | 10 | ~$27.00 |

ElevenLabs-Kosten fallen kaum ins Gewicht (Creator Plan: 100 Min. für $22/Monat).

---

## Häufige Probleme

**Pipeline bricht ab / Fehler bei einem Part**
Einfach erneut starten. Der Fortschritt ist gespeichert, abgeschlossene Schritte werden übersprungen:
```bash
python generate.py --script 1
```

**Audio zu lang (Warnung: "exceeds limit")**
Chunk-Größe in `config.json` reduzieren:
```json
"pipeline": {
  "max_chunk_words": 80
}
```

**Anderes Foto verwenden**
1. Neues Foto in `images/` ablegen
2. Pfad in `config.json` anpassen: `"image": "images/neues-foto.jpg"`
3. Pipeline neu starten (neues `state.json` oder alten Eintrag löschen)

**Fortschritt zurücksetzen**
`state.json` löschen und neu starten:
```bash
del state.json
python generate.py --script 1
```

---

## Voice-Einstellungen anpassen

In `config.json` unter `voice.settings`:

| Einstellung | Wert | Effekt |
|-------------|------|--------|
| `stability` | 0.0 – 1.0 | Niedrig = variabler, Hoch = gleichmäßiger |
| `similarity_boost` | 0.0 – 1.0 | Ähnlichkeit zur Originalstimme |
| `style` | 0.0 – 1.0 | Expressivität / Emotionen |
| `speed` | 0.7 – 1.2 | Sprechgeschwindigkeit |

Empfehlung für natürliche Videos:
```json
"stability": 0.40,
"similarity_boost": 0.75,
"style": 0.20,
"speed": 1.03
```
