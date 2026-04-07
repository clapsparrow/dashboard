# Dashboard Online deployen

## Schritt 1 — GitHub Repository erstellen

1. Gehe auf https://github.com/new
2. Name: `clapsparrow-dashboard`
3. **Private** auswählen (empfohlen)
4. Kein README, kein .gitignore — leer lassen
5. Repository erstellen

## Schritt 2 — Dateien hochladen

Im Terminal (in diesem Ordner):

```bash
git init
git add .
git commit -m "initial: clapsparrow dashboard"
git remote add origin https://github.com/DEIN-USERNAME/clapsparrow-dashboard.git
git branch -M main
git push -u origin main
```

## Schritt 3 — GitHub Pages aktivieren

1. Repository → **Settings** → **Pages**
2. Source: `Deploy from a branch`
3. Branch: `main` / Ordner: `/ (root)`
4. Speichern

→ Dashboard ist erreichbar unter:
`https://DEIN-USERNAME.github.io/clapsparrow-dashboard/dashboard.html`

## Schritt 4 — Netlify für bessere URL (optional)

1. https://netlify.com → Login mit GitHub
2. "Add new site" → "Import an existing project"
3. GitHub → `clapsparrow-dashboard` auswählen
4. Deploy — fertig

→ Du bekommst eine URL wie `https://clapsparrow-dashboard.netlify.app`
→ Optional: eigene Domain unter Site Settings → Domain Management

## Schritt 5 — Instagram Session für Auto-Updates

Damit GitHub Actions auch Instagram-Daten holen kann:

```bash
# Einmalig lokal ausführen:
python3 -c "import instaloader; L = instaloader.Instaloader(); L.interactive_login('clapsparrow')"
# Session-Datei base64 kodieren:
base64 session-clapsparrow | pbcopy
```

Dann in GitHub:
1. Repository → **Settings** → **Secrets and variables** → **Actions**
2. "New repository secret"
3. Name: `INSTAGRAM_SESSION`
4. Value: (Inhalt der Zwischenablage einfügen)
5. Speichern

## Auto-Update testen

GitHub → Repository → **Actions** → "Dashboard Auto-Update" → "Run workflow"

Das Dashboard wird ab jetzt täglich um 10:00 Uhr MESZ automatisch aktualisiert.
