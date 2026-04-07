# Clapsparrow — Social Media Analyzer

## Schnellstart

### 1. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 2. SoundCloud analysieren
```bash
python soundcloud_analyze.py
```
→ Erstellt `soundcloud_data.json`

### 3. Instagram analysieren
```bash
python instagram_analyze.py
```
→ Erstellt `instagram_data.json`

### 4. Dashboard generieren
```bash
python generate_dashboard.py
```
→ Öffnet `dashboard.html` im Browser

---

## Troubleshooting

### Instagram: "LoginRequired" oder Rate-Limit
Instagram blockiert manchmal anonyme Anfragen. Lösung:

```bash
# Mit deinem IG-Account einloggen (einmalig)
instaloader --login clapsparrow
```
Dann in `instagram_analyze.py` Zeile 30 ändern:
```python
L.load_session_from_file("clapsparrow")
```

### SoundCloud: Keine API-Daten
Falls die automatische client_id Extraktion scheitert, SoundCloud lädt
die Daten trotzdem über oEmbed (Basis-Infos).

---

## Dateien

| Datei | Beschreibung |
|-------|-------------|
| `soundcloud_analyze.py` | SoundCloud Profil + Tracks analysieren |
| `instagram_analyze.py`  | Instagram Profil + Posts analysieren |
| `generate_dashboard.py` | HTML-Dashboard aus den JSON-Daten erzeugen |
| `soundcloud_data.json`  | SoundCloud Export (wird erstellt) |
| `instagram_data.json`   | Instagram Export (wird erstellt) |
| `dashboard.html`        | Interaktives Dashboard (wird erstellt) |
