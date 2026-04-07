"""
Instagram Profile Analyzer für @clapsparrow
Verwendet instaloader (kein API-Key nötig für öffentliche Profile)

Installation: pip install instaloader
"""

import json
import sys
from datetime import datetime

try:
    import instaloader
except ImportError:
    print("instaloader nicht installiert.")
    print("Bitte ausführen: pip install instaloader")
    sys.exit(1)

USERNAME = "clapsparrow"

def format_number(n):
    if n is None:
        return "–"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

def analyze():
    print("=" * 60)
    print("  INSTAGRAM ANALYZER — @clapsparrow")
    print("=" * 60)

    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        quiet=True
    )

    # Session laden falls vorhanden
    try:
        L.load_session_from_file(USERNAME)
        print(f"  Session für @{USERNAME} geladen.")
    except FileNotFoundError:
        print("  Keine Session gefunden, versuche anonymen Zugriff...")
    except Exception as e:
        print(f"  Session-Warnung: {e}")

    print(f"\n[1/2] Lade Profil @{USERNAME}...")
    try:
        profile = instaloader.Profile.from_username(L.context, USERNAME)
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"  Profil @{USERNAME} nicht gefunden.")
        return
    except Exception as e:
        print(f"  Fehler beim Laden: {e}")
        print("\n  Tipp: Instagram limitiert Anfragen von unbekannten IPs.")
        print("  Lösung: Füge deine IG-Session hinzu (siehe SETUP.md)")
        return

    print("\n" + "=" * 60)
    print("  PROFIL-ÜBERSICHT")
    print("=" * 60)
    print(f"  Username:       @{profile.username}")
    print(f"  Name:           {profile.full_name or '–'}")
    print(f"  Bio:            {profile.biography[:80] if profile.biography else '–'}")
    print(f"  Followers:      {format_number(profile.followers)}")
    print(f"  Following:      {format_number(profile.followees)}")
    print(f"  Posts gesamt:   {format_number(profile.mediacount)}")
    print(f"  Verifiziert:    {'Ja' if profile.is_verified else 'Nein'}")
    print(f"  Business:       {'Ja' if profile.is_business_account else 'Nein'}")
    if profile.external_url:
        print(f"  Website:        {profile.external_url}")

    # Posts analysieren
    print(f"\n[2/2] Analysiere letzte 20 Posts...")
    posts_data = []
    try:
        for i, post in enumerate(profile.get_posts()):
            if i >= 20:
                break
            posts_data.append({
                "shortcode":  post.shortcode,
                "date":       post.date_local.strftime("%Y-%m-%d"),
                "type":       post.typename,
                "likes":      post.likes,
                "comments":   post.comments,
                "caption":    (post.caption or "")[:100],
                "is_video":   post.is_video,
                "views":      post.video_view_count if post.is_video else None,
            })
            print(f"  Post {i+1:2}/20 geladen...", end="\r")
    except Exception as e:
        print(f"\n  Warnung: Konnte nicht alle Posts laden: {e}")

    if posts_data:
        print(f"\n  {len(posts_data)} Posts geladen.          ")

        # Sortiert nach Likes
        top_posts = sorted(posts_data, key=lambda p: p["likes"], reverse=True)

        print("\n" + "=" * 60)
        print("  TOP POSTS (nach Likes)")
        print("=" * 60)
        for i, p in enumerate(top_posts[:10], 1):
            ptype = "Video" if p["is_video"] else "Bild/Reel"
            views = f"  Views: {format_number(p['views'])}" if p["views"] else ""
            caption = p["caption"][:50] + "..." if len(p["caption"]) > 50 else p["caption"]
            print(f"  {i:2}. [{ptype}] {p['date']}")
            print(f"      Likes: {format_number(p['likes']):>8}  |  Kommentare: {format_number(p['comments'])}{views}")
            if caption:
                print(f"      Caption: {caption}")
            print()

        # Engagement-Analyse
        total_likes    = sum(p["likes"] for p in posts_data)
        total_comments = sum(p["comments"] for p in posts_data)
        avg_likes      = total_likes / len(posts_data)
        avg_comments   = total_comments / len(posts_data)
        eng_rate       = ((avg_likes + avg_comments) / profile.followers * 100) if profile.followers > 0 else 0

        # Content-Mix
        videos = sum(1 for p in posts_data if p["is_video"])
        images = len(posts_data) - videos

        print("=" * 60)
        print("  ENGAGEMENT-ANALYSE")
        print("=" * 60)
        print(f"  Posts analysiert:     {len(posts_data)}")
        print(f"  Gesamt-Likes:         {format_number(total_likes)}")
        print(f"  Gesamt-Kommentare:    {format_number(total_comments)}")
        print(f"  Ø Likes/Post:         {format_number(int(avg_likes))}")
        print(f"  Ø Kommentare/Post:    {format_number(int(avg_comments))}")
        print(f"  Engagement-Rate:      {eng_rate:.2f}%")
        print()
        print(f"  Content-Mix:")
        print(f"    Videos/Reels:  {videos} Posts ({videos/len(posts_data)*100:.0f}%)")
        print(f"    Bilder:        {images} Posts ({images/len(posts_data)*100:.0f}%)")

        # Beste Posting-Zeiten
        from collections import Counter
        weekdays = {0:"Mo", 1:"Di", 2:"Mi", 3:"Do", 4:"Fr", 5:"Sa", 6:"So"}
        day_counts = Counter()
        for p in posts_data:
            d = datetime.strptime(p["date"], "%Y-%m-%d").weekday()
            day_counts[d] += 1

        print(f"\n  Posting-Tage (letzte {len(posts_data)} Posts):")
        for day, count in sorted(day_counts.items()):
            bar = "█" * count
            print(f"    {weekdays[day]}: {bar} ({count})")

        # Bewertung
        print("\n" + "=" * 60)
        print("  BEWERTUNG")
        print("=" * 60)
        if eng_rate >= 6:
            rating = "Ausgezeichnet"
        elif eng_rate >= 3:
            rating = "Gut"
        elif eng_rate >= 1:
            rating = "Durchschnitt"
        else:
            rating = "Ausbaufähig"
        print(f"  Engagement-Rate {eng_rate:.2f}% → {rating}")
        print(f"  (Branchenschnitt für Music/DJ: ~2-4%)")

    # Export
    export = {
        "profile": {
            "username": profile.username,
            "full_name": profile.full_name,
            "followers": profile.followers,
            "following": profile.followees,
            "posts": profile.mediacount,
            "bio": profile.biography,
            "is_verified": profile.is_verified,
        },
        "posts": posts_data,
        "analyzed_at": datetime.now().isoformat()
    }
    with open("instagram_data.json", "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=2)
    print(f"\n  Daten gespeichert: instagram_data.json")

if __name__ == "__main__":
    analyze()
