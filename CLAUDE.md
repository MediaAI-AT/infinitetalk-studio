# InfiniteTalk Studio

Automated pipeline: Text script → ElevenLabs speech → WaveSpeed InfiniteTalk → Talking avatar video (720p).

## Quick Start

### 1. Referenzbild ablegen
Lege dein Foto in `images/` ab und aktualisiere `config.json`:
```json
"image": "images/dein-foto.jpg"
```

### 2. Skript schreiben
Lege eine `.txt`-Datei in `scripts/` ab und trage sie in `config.json` ein:
```json
"scripts": {
  "1": {
    "title": "Mein Video",
    "file": "scripts/mein-skript.txt"
  }
}
```

### 3. Pipeline starten
```bash
# Nur aufteilen, keine API-Kosten (Test)
python generate.py --dry-run

# Einzelnen Script verarbeiten
python generate.py --script 1

# Nur ersten Chunk testen (~$0.30 für 5s bei 720p)
python generate.py --script 1 --max-parts 1

# Alle Scripts
python generate.py

# Fortschritt anzeigen
python generate.py --status
```

## Konfiguration (`config.json`)

| Feld | Bedeutung |
|------|-----------|
| `image` | Pfad zum Referenzbild (jpg/png/webp) |
| `voice.id` | ElevenLabs Voice ID |
| `voice.settings` | Stability, Similarity, Speed etc. |
| `pipeline.max_chunk_words` | Maximale Wörter pro Chunk (Standard: 100 ≈ 45s) |
| `pipeline.max_audio_duration_sec` | Warnung ab dieser Audio-Länge (Standard: 55s) |
| `pipeline.resolution` | `"480p"` oder `"720p"` (Standard: 720p) |
| `scripts` | Skript-Einträge mit Titel und Dateipfad |

## Kosten

| Komponente | Preis |
|-----------|-------|
| WaveSpeed InfiniteTalk 720p | ~$0.30 / 5 Sekunden Video |
| ElevenLabs (Creator Plan) | $22/Monat für 100 Min. Audio |

Ein 55s Chunk = ~$3.30 WaveSpeed-Kosten.

## Ordnerstruktur

```
infinitetalk-studio/
├── images/          ← Referenzbild hier ablegen
├── scripts/         ← Textskripte (.txt)
├── output/
│   ├── scripts/     ← Aufgeteilte Chunks (automatisch)
│   ├── audio/       ← Generierte MP3-Dateien
│   └── videos/      ← Fertige MP4-Videos
├── generate.py      ← Haupt-Pipeline
├── config.json      ← Einstellungen
└── .env             ← API-Keys (nicht committen!)
```

## State & Wiederaufnahme

`state.json` speichert den Fortschritt jedes Chunks. Bei Unterbrechung einfach erneut starten — abgeschlossene Schritte werden übersprungen.

## Tipps für Claude Code

- "Füge Skript 2 hinzu für [Thema]"
- "Zeige mir den aktuellen Status"
- "Chunk-Größe auf 80 Wörter reduzieren"
- "Teil 1 ist fehlgeschlagen — hilf mir beim Debuggen"
