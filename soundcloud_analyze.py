"""
SoundCloud Profile Analyzer for @clapsparrow
Holt öffentliche Daten via SoundCloud oEmbed + inoffizielle API
"""

import requests
import json
import re
import sys
from datetime import datetime

PROFILE_URL = "https://soundcloud.com/clapsparrow"

def get_client_id():
    """Versucht eine client_id aus der SoundCloud-Seite zu extrahieren"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get("https://soundcloud.com", headers=headers, timeout=10)
        # Suche nach JS-Bundle-URLs
        scripts = re.findall(r'https://a-v2\.sndcdn\.com/assets/[^"]+\.js', r.text)
        for script_url in scripts[:5]:
            sr = requests.get(script_url, headers=headers, timeout=10)
            match = re.search(r'client_id:"([a-zA-Z0-9]+)"', sr.text)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"  Warnung: client_id Extraktion fehlgeschlagen: {e}")
    return None

def get_profile_oembed():
    """Holt Basis-Profildaten via oEmbed (kein Auth nötig)"""
    url = f"https://soundcloud.com/oembed?url={PROFILE_URL}&format=json"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def get_profile_data(client_id):
    """Holt detaillierte Profildaten via API"""
    url = f"https://api-v2.soundcloud.com/resolve?url={PROFILE_URL}&client_id={client_id}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def get_tracks(user_id, client_id):
    """Holt alle Tracks des Profils"""
    url = f"https://api-v2.soundcloud.com/users/{user_id}/tracks?client_id={client_id}&limit=50"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json().get("collection", [])

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
    print("  SOUNDCLOUD ANALYZER — @clapsparrow")
    print("=" * 60)

    # 1. Basis-Info via oEmbed
    print("\n[1/3] Lade Basis-Profildaten...")
    try:
        oembed = get_profile_oembed()
        print(f"  Name:     {oembed.get('author_name', '–')}")
        print(f"  Profil:   {oembed.get('author_url', '–')}")
    except Exception as e:
        print(f"  Fehler: {e}")
        oembed = {}

    # 2. client_id für erweiterte API
    print("\n[2/3] Versuche erweiterte API-Daten zu laden...")
    client_id = get_client_id()

    if not client_id:
        print("  Konnte keine client_id finden. Nur Basis-Daten verfügbar.")
        print("\n" + "=" * 60)
        print("  ERGEBNIS (Basis)")
        print("=" * 60)
        print(f"  Profil-Name:  {oembed.get('author_name', '–')}")
        print(f"  URL:          {oembed.get('author_url', '–')}")
        print("\n  Für vollständige Daten: Siehe SETUP.md für API-Key Anleitung")
        return

    print(f"  client_id gefunden!")

    try:
        profile = get_profile_data(client_id)
        user_id = profile.get("id")

        print("\n[3/3] Lade Tracks...")
        tracks = get_tracks(user_id, client_id)

        # Ausgabe
        print("\n" + "=" * 60)
        print("  PROFIL-ÜBERSICHT")
        print("=" * 60)
        print(f"  Name:          {profile.get('username', '–')}")
        print(f"  Full Name:     {profile.get('full_name', '–')}")
        print(f"  Followers:     {format_number(profile.get('followers_count'))}")
        print(f"  Following:     {format_number(profile.get('followings_count'))}")
        print(f"  Tracks:        {format_number(profile.get('track_count'))}")
        print(f"  Plays total:   {format_number(profile.get('public_favorites_count'))}")
        print(f"  Stadt:         {profile.get('city', '–')}")
        print(f"  Land:          {profile.get('country_code', '–')}")

        if tracks:
            print("\n" + "=" * 60)
            print("  TOP TRACKS (nach Plays)")
            print("=" * 60)
            sorted_tracks = sorted(tracks, key=lambda t: t.get("playback_count", 0), reverse=True)
            for i, t in enumerate(sorted_tracks[:10], 1):
                plays    = format_number(t.get("playback_count"))
                likes    = format_number(t.get("likes_count"))
                reposts  = format_number(t.get("reposts_count"))
                comments = format_number(t.get("comment_count"))
                date     = t.get("created_at", "")[:10]
                title    = t.get("title", "–")[:50]
                print(f"  {i:2}. {title}")
                print(f"      Plays: {plays:>8}  |  Likes: {likes:>7}  |  Reposts: {reposts:>6}  |  Kommentare: {comments}")
                print(f"      Datum: {date}")
                print()

            # Engagement-Berechnung
            total_plays  = sum(t.get("playback_count", 0) or 0 for t in tracks)
            total_likes  = sum(t.get("likes_count", 0) or 0 for t in tracks)
            avg_plays    = total_plays / len(tracks) if tracks else 0
            avg_likes    = total_likes / len(tracks) if tracks else 0
            engagement   = (total_likes / total_plays * 100) if total_plays > 0 else 0

            print("=" * 60)
            print("  ENGAGEMENT-ANALYSE")
            print("=" * 60)
            print(f"  Tracks analysiert:  {len(tracks)}")
            print(f"  Gesamt-Plays:       {format_number(total_plays)}")
            print(f"  Gesamt-Likes:       {format_number(total_likes)}")
            print(f"  Ø Plays/Track:      {format_number(int(avg_plays))}")
            print(f"  Ø Likes/Track:      {format_number(int(avg_likes))}")
            print(f"  Engagement-Rate:    {engagement:.2f}%  (Likes/Plays)")

        # JSON Export
        export = {
            "profile": profile,
            "tracks": tracks,
            "analyzed_at": datetime.now().isoformat()
        }
        with open("soundcloud_data.json", "w", encoding="utf-8") as f:
            json.dump(export, f, ensure_ascii=False, indent=2)
        print(f"\n  Daten gespeichert: soundcloud_data.json")

    except requests.HTTPError as e:
        print(f"  API-Fehler: {e}")
        print("  Tipp: SoundCloud blockiert gelegentlich automatische Anfragen.")
        print("        Versuche es erneut oder nutze ein VPN.")

if __name__ == "__main__":
    analyze()
