"""
Dashboard Generator — kombiniert SoundCloud + Instagram Daten
Generiert eine interaktive HTML-Datei

Voraussetzung: soundcloud_data.json + instagram_data.json müssen existieren
(erst soundcloud_analyze.py und instagram_analyze.py ausführen)
"""

import json
import os
from datetime import datetime

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def fmt(n):
    if n is None:
        return "–"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

def generate():
    sc = load_json("soundcloud_data.json")
    ig = load_json("instagram_data.json")

    if not sc and not ig:
        print("Keine Daten gefunden. Bitte zuerst die Analyse-Scripts ausführen.")
        return

    # --- SoundCloud Daten aufbereiten ---
    sc_profile = sc.get("profile", {}) if sc else {}
    sc_tracks  = sc.get("tracks", []) if sc else []
    sc_top     = sorted(sc_tracks, key=lambda t: t.get("playback_count", 0) or 0, reverse=True)[:10]
    sc_total_plays = sum(t.get("playback_count", 0) or 0 for t in sc_tracks)
    sc_total_likes = sum(t.get("likes_count", 0) or 0 for t in sc_tracks)
    sc_eng = (sc_total_likes / sc_total_plays * 100) if sc_total_plays > 0 else 0

    # --- Instagram Daten aufbereiten ---
    ig_profile = ig.get("profile", {}) if ig else {}
    ig_posts   = ig.get("posts", []) if ig else []
    ig_top     = sorted(ig_posts, key=lambda p: p.get("likes", 0), reverse=True)[:10]
    ig_total_likes    = sum(p.get("likes", 0) for p in ig_posts)
    ig_total_comments = sum(p.get("comments", 0) for p in ig_posts)
    ig_avg_likes      = ig_total_likes / len(ig_posts) if ig_posts else 0
    ig_eng = ((ig_avg_likes + (ig_total_comments / len(ig_posts) if ig_posts else 0)) / ig_profile.get("followers", 1) * 100) if ig_profile.get("followers") else 0

    # Chart-Daten für SoundCloud
    sc_labels = json.dumps([t.get("title", "")[:30] for t in sc_top])
    sc_plays   = json.dumps([t.get("playback_count", 0) or 0 for t in sc_top])
    sc_likes_c = json.dumps([t.get("likes_count", 0) or 0 for t in sc_top])

    # Chart-Daten für Instagram
    ig_labels = json.dumps([p.get("date", "") for p in ig_top])
    ig_likes_d = json.dumps([p.get("likes", 0) for p in ig_top])
    ig_comms   = json.dumps([p.get("comments", 0) for p in ig_top])

    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Pre-build table rows (Python 3.9 compat)
    sc_rows = ""
    for i, t in enumerate(sc_top):
        sc_rows += "<tr>"
        sc_rows += f"<td>{i+1}</td>"
        sc_rows += f"<td>{t.get('title','–')[:55]}</td>"
        sc_rows += f"<td>{fmt(t.get('playback_count'))}</td>"
        sc_rows += f"<td>{fmt(t.get('likes_count'))}</td>"
        sc_rows += f"<td>{fmt(t.get('reposts_count'))}</td>"
        sc_rows += f"<td>{(t.get('created_at') or '')[:10]}</td>"
        sc_rows += "</tr>\n"

    ig_rows = ""
    for i, p in enumerate(ig_top):
        badge_cls = "badge-video" if p.get("is_video") else "badge-image"
        badge_txt = "Video" if p.get("is_video") else "Bild"
        caption = (p.get("caption") or "")[:60]
        ig_rows += "<tr>"
        ig_rows += f"<td>{i+1}</td>"
        ig_rows += f'<td><span class="badge {badge_cls}">{badge_txt}</span></td>'
        ig_rows += f"<td>{p.get('date','–')}</td>"
        ig_rows += f"<td>{fmt(p.get('likes'))}</td>"
        ig_rows += f"<td>{fmt(p.get('comments'))}</td>"
        ig_rows += f'<td style="color:#888;font-size:0.8rem">{caption}</td>'
        ig_rows += "</tr>\n"

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Clapsparrow — Social Media Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f0f13; color: #e0e0e0; }}
  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px 40px; border-bottom: 1px solid #2a2a3e; }}
  .header h1 {{ font-size: 2rem; color: #fff; letter-spacing: 2px; }}
  .header p  {{ color: #888; margin-top: 5px; font-size: 0.9rem; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 30px 40px; }}
  .section-title {{ font-size: 1.3rem; font-weight: 700; margin: 30px 0 15px; display: flex; align-items: center; gap: 10px; }}
  .sc-color {{ color: #ff5500; }}
  .ig-color {{ color: #e1306c; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 30px; }}
  .stat-card {{ background: #1a1a24; border-radius: 12px; padding: 20px; border: 1px solid #2a2a3e; text-align: center; }}
  .stat-card .value {{ font-size: 2rem; font-weight: 700; margin-bottom: 5px; }}
  .stat-card .label {{ font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }}
  .sc-card .value {{ color: #ff5500; }}
  .ig-card .value {{ color: #e1306c; }}
  .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
  .chart-box {{ background: #1a1a24; border-radius: 12px; padding: 20px; border: 1px solid #2a2a3e; }}
  .chart-box h3 {{ font-size: 0.95rem; color: #aaa; margin-bottom: 15px; }}
  .chart-box canvas {{ max-height: 280px; }}
  .tracks-table {{ width: 100%; border-collapse: collapse; background: #1a1a24; border-radius: 12px; overflow: hidden; border: 1px solid #2a2a3e; }}
  .tracks-table th {{ background: #12121a; padding: 12px 15px; text-align: left; font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }}
  .tracks-table td {{ padding: 12px 15px; border-top: 1px solid #22222e; font-size: 0.9rem; }}
  .tracks-table tr:hover td {{ background: #22222e; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 0.75rem; }}
  .badge-video {{ background: #e1306c22; color: #e1306c; border: 1px solid #e1306c44; }}
  .badge-image {{ background: #3d9be922; color: #3d9be9; border: 1px solid #3d9be944; }}
  .eng-bar {{ height: 6px; border-radius: 3px; background: #2a2a3e; margin-top: 8px; }}
  .eng-fill {{ height: 100%; border-radius: 3px; }}
  .footer {{ text-align: center; padding: 30px; color: #444; font-size: 0.8rem; border-top: 1px solid #1a1a24; margin-top: 30px; }}
  @media (max-width: 768px) {{ .charts-grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<div class="header">
  <h1>CLAPSPARROW</h1>
  <p>Social Media Dashboard &nbsp;·&nbsp; Analysiert am {now}</p>
</div>

<div class="container">

  <!-- SOUNDCLOUD -->
  <div class="section-title sc-color">
    &#9658; SoundCloud
  </div>
  <div class="stats-grid">
    <div class="stat-card sc-card"><div class="value">{fmt(sc_profile.get('followers_count'))}</div><div class="label">Followers</div></div>
    <div class="stat-card sc-card"><div class="value">{fmt(sc_profile.get('track_count'))}</div><div class="label">Tracks</div></div>
    <div class="stat-card sc-card"><div class="value">{fmt(sc_total_plays)}</div><div class="label">Gesamt-Plays</div></div>
    <div class="stat-card sc-card"><div class="value">{fmt(sc_total_likes)}</div><div class="label">Gesamt-Likes</div></div>
    <div class="stat-card sc-card"><div class="value">{sc_eng:.2f}%</div><div class="label">Engagement-Rate</div></div>
  </div>

  <div class="charts-grid">
    <div class="chart-box">
      <h3>Top Tracks — Plays</h3>
      <canvas id="scPlaysChart"></canvas>
    </div>
    <div class="chart-box">
      <h3>Top Tracks — Likes</h3>
      <canvas id="scLikesChart"></canvas>
    </div>
  </div>

  <!-- Top Tracks Tabelle -->
  <table class="tracks-table" style="margin-bottom:30px">
    <thead>
      <tr><th>#</th><th>Track</th><th>Plays</th><th>Likes</th><th>Reposts</th><th>Datum</th></tr>
    </thead>
    <tbody>
      {sc_rows}
    </tbody>
  </table>

  <!-- INSTAGRAM -->
  <div class="section-title ig-color">
    &#9658; Instagram
  </div>
  <div class="stats-grid">
    <div class="stat-card ig-card"><div class="value">{fmt(ig_profile.get('followers'))}</div><div class="label">Followers</div></div>
    <div class="stat-card ig-card"><div class="value">{fmt(ig_profile.get('following'))}</div><div class="label">Following</div></div>
    <div class="stat-card ig-card"><div class="value">{fmt(ig_profile.get('posts'))}</div><div class="label">Posts</div></div>
    <div class="stat-card ig-card"><div class="value">{fmt(ig_total_likes)}</div><div class="label">Likes (20 Posts)</div></div>
    <div class="stat-card ig-card"><div class="value">{ig_eng:.2f}%</div><div class="label">Engagement-Rate</div></div>
  </div>

  <div class="charts-grid">
    <div class="chart-box">
      <h3>Top Posts — Likes</h3>
      <canvas id="igLikesChart"></canvas>
    </div>
    <div class="chart-box">
      <h3>Top Posts — Kommentare</h3>
      <canvas id="igCommsChart"></canvas>
    </div>
  </div>

  <!-- Instagram Posts Tabelle -->
  <table class="tracks-table">
    <thead>
      <tr><th>#</th><th>Typ</th><th>Datum</th><th>Likes</th><th>Kommentare</th><th>Caption</th></tr>
    </thead>
    <tbody>
      {ig_rows}
    </tbody>
  </table>

</div>

<div class="footer">
  Clapsparrow Dashboard &nbsp;·&nbsp; Generiert {now} &nbsp;·&nbsp; via Claude Code
</div>

<script>
const scLabels  = {sc_labels};
const scPlays   = {sc_plays};
const scLikes   = {sc_likes_c};
const igLabels  = {ig_labels};
const igLikes   = {ig_likes_d};
const igComments = {ig_comms};

const chartDefaults = {{
  responsive: true,
  maintainAspectRatio: true,
  plugins: {{ legend: {{ display: false }} }},
  scales: {{
    x: {{ ticks: {{ color: '#666', font: {{ size: 10 }} }}, grid: {{ color: '#1e1e2a' }} }},
    y: {{ ticks: {{ color: '#666' }}, grid: {{ color: '#1e1e2a' }} }}
  }}
}};

new Chart(document.getElementById('scPlaysChart'), {{
  type: 'bar',
  data: {{ labels: scLabels, datasets: [{{ data: scPlays, backgroundColor: '#ff550088', borderColor: '#ff5500', borderWidth: 1 }}] }},
  options: chartDefaults
}});

new Chart(document.getElementById('scLikesChart'), {{
  type: 'bar',
  data: {{ labels: scLabels, datasets: [{{ data: scLikes, backgroundColor: '#ff880088', borderColor: '#ff8800', borderWidth: 1 }}] }},
  options: chartDefaults
}});

new Chart(document.getElementById('igLikesChart'), {{
  type: 'bar',
  data: {{ labels: igLabels, datasets: [{{ data: igLikes, backgroundColor: '#e1306c88', borderColor: '#e1306c', borderWidth: 1 }}] }},
  options: chartDefaults
}});

new Chart(document.getElementById('igCommsChart'), {{
  type: 'bar',
  data: {{ labels: igLabels, datasets: [{{ data: igComments, backgroundColor: '#833ab488', borderColor: '#833ab4', borderWidth: 1 }}] }},
  options: chartDefaults
}});
</script>
</body>
</html>"""

    output = "dashboard.html"
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard gespeichert: {output}")
    print(f"Öffne die Datei im Browser: open {output}")

    # Browser öffnen
    import webbrowser
    webbrowser.open(f"file://{os.path.abspath(output)}")

if __name__ == "__main__":
    generate()
