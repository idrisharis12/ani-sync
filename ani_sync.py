#!/usr/bin/env bash
# -*- coding: utf-8 -*-
""":"
exec python3 "$0" "$@"
"""

import html
import json
import os
import re
import secrets
import subprocess
import sys
import threading
import urllib.parse
import webbrowser
from pathlib import Path

import requests

# ----------------------------------------------------------------------
# Constants & Paths
# ----------------------------------------------------------------------
VERSION = "2.0.0"
CONFIG_DIR = Path.home() / ".config" / "ani-sync"
CONFIG_PATH = CONFIG_DIR / "config.env"
HISTORY_PATH = CONFIG_DIR / "history.json"

ANIDB_BASE = "https://anidb.app"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
AUTH_URL = "https://myanimelist.net/v1/oauth2/authorize"
API_URL = "https://api.myanimelist.net/v2"

# Terminal Colors
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_MAGENTA = "\033[95m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RESET = "\033[0m"


# ----------------------------------------------------------------------
# Config & Environment Handling
# ----------------------------------------------------------------------
def load_config():
    """Load configuration from ~/.config/ani-sync/config.env if present."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        key = key.replace("export ", "").strip()
                        val = val.strip().strip("'\"")
                        if key not in os.environ:
                            os.environ[key] = val
        except Exception:
            pass


def save_config(client_id, client_secret, refresh_token):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(f'export MAL_CLIENT_ID="{client_id}"\n')
        f.write(f'export MAL_CLIENT_SECRET="{client_secret}"\n')
        f.write(f'export MAL_REFRESH_TOKEN="{refresh_token}"\n')


def get_mal_env():
    load_config()
    client_id = os.getenv("MAL_CLIENT_ID", "").strip()
    client_secret = os.getenv("MAL_CLIENT_SECRET", "").strip()
    refresh_token = os.getenv("MAL_REFRESH_TOKEN", "").strip()
    return client_id, client_secret, refresh_token


def is_mal_configured():
    client_id, _, refresh_token = get_mal_env()
    return bool(client_id and refresh_token)


# ----------------------------------------------------------------------
# Interactive MAL Authentication Helper
# ----------------------------------------------------------------------
def run_auth():
    print(
        f"\n{C_CYAN}{C_BOLD}============================================================{C_RESET}"
    )
    print(
        f"{C_MAGENTA}{C_BOLD}         ani-sync — MyAnimeList Authentication Setup        {C_RESET}"
    )
    print(
        f"{C_CYAN}{C_BOLD}============================================================{C_RESET}"
    )
    print(f"\n1. Go to: {C_BLUE}https://myanimelist.net/apiconfig{C_RESET}")
    print(f"2. Click {C_BOLD}'Create ID'{C_RESET} with the following settings:")
    print(f"   - {C_BOLD}App Name:{C_RESET} ani-sync")
    print(f"   - {C_BOLD}App Type:{C_RESET} other")
    print(f"   - {C_BOLD}Redirect URL:{C_RESET} http://localhost")
    print(
        f"{C_CYAN}------------------------------------------------------------{C_RESET}"
    )

    client_id = input(f"\n{C_BOLD}Enter your MAL Client ID: {C_RESET}").strip()
    if not client_id:
        print(f"{C_RED}Error: Client ID is required.{C_RESET}")
        return

    client_secret = input(
        f"{C_BOLD}Enter your MAL Client Secret (press Enter if none): {C_RESET}"
    ).strip()
    code_verifier = secrets.token_urlsafe(100)[:128]

    params = {
        "response_type": "code",
        "client_id": client_id,
        "code_challenge": code_verifier,
        "code_challenge_method": "plain",
    }
    auth_link = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    print(f"\n{C_YELLOW}Opening browser for authorization...{C_RESET}")
    print(f"If your browser doesn't open automatically, visit this URL:")
    print(f"{C_BLUE}{auth_link}{C_RESET}\n")

    try:
        webbrowser.open(auth_link)
    except Exception:
        pass

    print(
        f"After logging in and clicking '{C_BOLD}Allow{C_RESET}', you will be redirected to:"
    )
    print(f"  {C_DIM}http://localhost/?code=AUTHORIZATION_CODE{C_RESET}")

    auth_input = input(
        f"\n{C_BOLD}Paste the redirected URL (or the 'code' parameter): {C_RESET}"
    ).strip()
    if "code=" in auth_input:
        parsed = urllib.parse.urlparse(auth_input)
        query_params = urllib.parse.parse_qs(parsed.query)
        auth_code = query_params.get(
            "code", [auth_input.split("code=")[1].split("&")[0]]
        )[0]
    else:
        auth_code = auth_input

    if not auth_code:
        print(f"{C_RED}Error: Authorization code cannot be empty.{C_RESET}")
        return

    print(f"\n{C_CYAN}Exchanging authorization code for tokens...{C_RESET}")
    data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "code": auth_code,
        "code_verifier": code_verifier,
    }
    if client_secret:
        data["client_secret"] = client_secret

    try:
        res = requests.post(TOKEN_URL, data=data, timeout=15)
        if res.status_code != 200:
            print(f"{C_RED}❌ OAuth Error ({res.status_code}): {res.text}{C_RESET}")
            return
        tokens = res.json()
        refresh_token = tokens.get("refresh_token")
        save_config(client_id, client_secret, refresh_token)
        print(f"\n{C_GREEN}{C_BOLD}✅ Authorization Successful!{C_RESET}")
        print(f"📁 Credentials saved to: {C_CYAN}{CONFIG_PATH}{C_RESET}")
    except Exception as e:
        print(f"{C_RED}❌ Connection error: {e}{C_RESET}")


# ----------------------------------------------------------------------
# MyAnimeList Syncing
# ----------------------------------------------------------------------
def refresh_mal_token():
    client_id, client_secret, refresh_token = get_mal_env()
    if not client_id or not refresh_token:
        return None
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    if client_secret:
        data["client_secret"] = client_secret
    try:
        r = requests.post(TOKEN_URL, data=data, timeout=10)
        if r.status_code == 200:
            token_json = r.json()
            new_refresh = token_json.get("refresh_token")
            if new_refresh and new_refresh != refresh_token:
                save_config(client_id, client_secret, new_refresh)
            return token_json.get("access_token")
    except Exception:
        pass
    return None


def sync_episode_to_mal(anime_title, episode_num, mal_id=None):
    if not is_mal_configured():
        print(
            f"{C_YELLOW}ℹ️  MAL sync skipped (Run 'ani-sync auth' to connect MyAnimeList){C_RESET}"
        )
        return False

    print(f"\n{C_CYAN}🔄  Syncing episode {episode_num} to MyAnimeList...{C_RESET}")
    access_token = refresh_mal_token()
    if not access_token:
        print(
            f"{C_RED}⚠️  Failed to refresh MyAnimeList access token. Try running 'ani-sync auth'.{C_RESET}"
        )
        return False

    headers = {"Authorization": f"Bearer {access_token}"}

    # If MAL ID not provided, search by title
    if not mal_id:
        try:
            search_res = requests.get(
                f"{API_URL}/anime",
                params={"q": anime_title, "limit": 1},
                headers=headers,
                timeout=10,
            )
            if search_res.status_code == 200:
                data = search_res.json()
                if data.get("data"):
                    mal_id = data["data"][0]["node"]["id"]
                    found_title = data["data"][0]["node"].get("title", anime_title)
        except Exception:
            pass

    if not mal_id:
        print(f"{C_YELLOW}⚠️  Could not find MAL entry for '{anime_title}'{C_RESET}")
        return False

    try:
        update_url = f"{API_URL}/anime/{mal_id}/my_list_status"
        payload = {
            "num_watched_episodes": episode_num,
            "status": "watching",
        }
        res = requests.patch(
            update_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=10,
        )
        if res.status_code in (200, 201):
            print(
                f"{C_GREEN}{C_BOLD}✅  MAL Synced:{C_RESET} Episode {episode_num} marked as watched!"
            )
            return True
        else:
            print(
                f"{C_RED}❌  MAL Sync update failed ({res.status_code}): {res.text}{C_RESET}"
            )
    except Exception as e:
        print(f"{C_RED}❌  MAL Sync error: {e}{C_RESET}")
    return False


# ----------------------------------------------------------------------
# AniDB Scraper & Video Stream Extraction
# ----------------------------------------------------------------------
_HTTP_SESSION = None


def get_http_session():
    global _HTTP_SESSION
    if _HTTP_SESSION is None:
        _HTTP_SESSION = requests.Session()
        _HTTP_SESSION.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://anidb.app/",
                "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Chromium";v="124", "Google Chrome";v="124"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Linux"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
        )
    return _HTTP_SESSION


def http_get(url, is_json=False):
    """Fetch URL using session with automatic curl fallback to prevent timeouts."""
    session = get_http_session()

    # 1. Try requests with robust headers
    try:
        res = session.get(url, timeout=12)
        if res.status_code == 200:
            return res.json() if is_json else res.text
    except Exception:
        pass

    # 2. Fallback to curl with browser headers
    try:
        cmd = [
            "curl",
            "-sL",
            "-A",
            USER_AGENT,
            "--max-time",
            "15",
            "-H",
            "Referer: https://anidb.app/",
            "-H",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            url,
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode(
            "utf-8", errors="ignore"
        )
        if out.strip():
            return json.loads(out) if is_json else out
    except Exception:
        pass

    # 3. Last retry with higher timeout
    res = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Referer": "https://anidb.app/"},
        timeout=20,
    )
    res.raise_for_status()
    return res.json() if is_json else res.text


def search_anime(query):
    """Search for anime on AniDB provider."""
    url = f"{ANIDB_BASE}/browse?q={urllib.parse.quote_plus(query)}"
    html_text = http_get(url)
    matches = re.findall(
        r"/anime/([a-z0-9-]+-[0-9]+).*?alt=\"([^\"]+)\"", html_text, re.DOTALL
    )
    results = []
    seen = set()
    for slug, raw_title in matches:
        if slug not in seen:
            seen.add(slug)
            title = html.unescape(raw_title).strip()
            results.append({"slug": slug, "title": title})
    return results


def get_anime_details(slug):
    """Fetch anime seasons and mal_id if present."""
    url = f"{ANIDB_BASE}/anime/{slug}"
    html_text = http_get(url)
    mal_id_match = re.search(r"myanimelist\.net/anime/([0-9]+)", html_text)
    mal_id = int(mal_id_match.group(1)) if mal_id_match else None

    # Parse related seasons / franchise entries
    seasons = []
    season_section = re.search(r">Seasons<.*?>Details<", html_text, re.DOTALL)
    if season_section:
        sec_text = season_section.group(0)
        s_matches = re.findall(
            r"/anime/([a-z0-9-]+-[0-9]+)\"[^>]*title=\"([^\"]+)\"", sec_text
        )
        seen = {slug}
        for s_slug, s_title in s_matches:
            if s_slug not in seen:
                seen.add(s_slug)
                seasons.append(
                    {"slug": s_slug, "title": html.unescape(s_title).strip()}
                )
    return {"mal_id": mal_id, "seasons": seasons}


def get_episodes(slug):
    """Fetch available episodes for an anime."""
    anime_id = slug.split("-")[-1]
    url = f"{ANIDB_BASE}/api/frontend/anime/{anime_id}/episodes"
    data = http_get(url, is_json=True)
    return data.get("episodes", [])


def get_episode_streams(episode_id, mode="sub"):
    """Fetch m3u8 streams and available qualities for an episode."""
    url = f"{ANIDB_BASE}/api/frontend/episode/{episode_id}/languages"
    data = http_get(url, is_json=True)
    languages = data.get("languages", [])

    target_code = "eng" if mode == "dub" else "jpn"
    embed_url = None
    for lang in languages:
        if lang.get("code") == target_code:
            embed_url = lang.get("embed_url")
            break
    if not embed_url and languages:
        embed_url = languages[0].get("embed_url")

    if not embed_url:
        return {}

    embed_html = http_get(embed_url)
    m3u8_match = re.search(r"file:\s*['\"]([^'\"]+)['\"]", embed_html)
    if not m3u8_match:
        return {}

    master_m3u8_url = m3u8_match.group(1)
    master_content = http_get(master_m3u8_url)

    streams = {}
    lines = master_content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#EXT-X-STREAM-INF"):
            res_match = re.search(r"RESOLUTION=\d+x(\d+)", line)
            quality_label = f"{res_match.group(1)}p" if res_match else "Auto"
            if i + 1 < len(lines):
                stream_link = lines[i + 1].strip()
                if not stream_link.startswith("http"):
                    stream_link = urllib.parse.urljoin(master_m3u8_url, stream_link)
                streams[quality_label] = stream_link

    if not streams:
        streams["Auto / Best"] = master_m3u8_url
    return streams


# ----------------------------------------------------------------------
# Player Launch & Playback Management
# ----------------------------------------------------------------------
def launch_player(stream_url, title, ep_num, player="mpv"):
    """Launch the chosen media player with title, stream, and optimal smooth playback."""
    media_title = f"{title} - Episode {ep_num}"
    cmd = []
    if player == "mpv":
        cmd = [
            "mpv",
            f"--force-media-title={media_title}",
            f"--user-agent={USER_AGENT}",
            "--referrer=https://anidb.app/",
            "--hwdec=auto-safe",
            "--profile=fast",
            "--audio-buffer=0.8",
            stream_url,
        ]
    elif player == "vlc":
        cmd = [
            "vlc",
            "--play-and-exit",
            f"--meta-title={media_title}",
            stream_url,
        ]
    elif player == "iina":
        cmd = [
            "iina",
            f"--mpv-force-media-title={media_title}",
            stream_url,
        ]
    else:
        cmd = [player, stream_url]

    print(f"\n{C_BOLD}▶️  Now Playing:{C_RESET} {C_CYAN}{media_title}{C_RESET}")
    print(f"{C_DIM}Player: {player} | Smooth playback active{C_RESET}\n")

    proc = subprocess.run(cmd)
    return proc.returncode == 0


# ----------------------------------------------------------------------
# Interactive Menus
# ----------------------------------------------------------------------
def pick_option(title, options, default_idx=0):
    """Render a clean numbered CLI selection menu."""
    print(f"\n{C_CYAN}{C_BOLD}{title}{C_RESET}")
    print(f"{C_DIM}{'-' * len(title)}{C_RESET}")
    for idx, opt in enumerate(options, 1):
        prefix = f"{C_GREEN}{C_BOLD}[{idx}]{C_RESET}"
        print(f"  {prefix} {opt}")

    while True:
        try:
            choice = input(
                f"\n{C_BOLD}Select [1-{len(options)}] (default: {default_idx+1}): {C_RESET}"
            ).strip()
            if not choice:
                return default_idx
            val = int(choice)
            if 1 <= val <= len(options):
                return val - 1
            print(
                f"{C_RED}Please enter a number between 1 and {len(options)}.{C_RESET}"
            )
        except ValueError:
            print(f"{C_RED}Invalid input. Please enter a number.{C_RESET}")
        except (KeyboardInterrupt, EOFError):
            print("\n")
            sys.exit(0)


# ----------------------------------------------------------------------
# Main Interactive Flow
# ----------------------------------------------------------------------
def play_loop(
    anime, initial_ep_idx=0, preferred_quality=None, mode="sub", player="mpv"
):
    """Watch loop with next, replay, previous, change episode/quality/season."""
    slug = anime["slug"]
    title = anime["title"]

    print(f"{C_YELLOW}Fetching episodes for {title}...{C_RESET}")
    episodes = get_episodes(slug)
    if not episodes:
        print(f"{C_RED}❌ No episodes found for {title}.{C_RESET}")
        return

    # Check for details and MAL ID
    details = get_anime_details(slug)
    mal_id = details.get("mal_id")
    seasons = details.get("seasons", [])

    current_idx = initial_ep_idx

    while True:
        if current_idx < 0 or current_idx >= len(episodes):
            print(f"{C_YELLOW}No more episodes in this list.{C_RESET}")
            break

        ep_data = episodes[current_idx]
        ep_num = ep_data.get("number", current_idx + 1)
        ep_id = ep_data.get("id")

        print(
            f"\n{C_CYAN}Resolving streams for Episode {ep_num} ({mode.upper()})...{C_RESET}"
        )
        streams = get_episode_streams(ep_id, mode=mode)
        if not streams:
            print(
                f"{C_RED}❌ Could not resolve video streams for Episode {ep_num}.{C_RESET}"
            )
            break

        # Quality Selection
        selected_url = None
        if preferred_quality and preferred_quality in streams:
            selected_url = streams[preferred_quality]
            quality_used = preferred_quality
        elif "720p" in streams:
            # 720p is optimal for zero-buffering instant start on any Wi-Fi
            selected_url = streams["720p"]
            quality_used = "720p"
        else:
            # Fallback to available quality
            qualities = list(streams.keys())
            if len(qualities) == 1:
                quality_used = qualities[0]
                selected_url = streams[quality_used]
            else:

                def sort_key(q):
                    num = re.findall(r"\d+", q)
                    return int(num[0]) if num else 0

                sorted_qualities = sorted(qualities, key=sort_key, reverse=True)
                quality_used = sorted_qualities[0]
                selected_url = streams[quality_used]

        print(f"{C_GREEN}✓ Stream ready ({quality_used}){C_RESET}")

        # Launch Player
        launch_player(selected_url, title, ep_num, player=player)

        # Auto-sync to MyAnimeList
        sync_episode_to_mal(title, ep_num, mal_id=mal_id)

        # Interactive post-playback controls
        while True:
            print(
                f"\n{C_MAGENTA}{C_BOLD}------------------- Playback Controls -------------------{C_RESET}"
            )
            has_next = (current_idx + 1) < len(episodes)
            has_prev = (current_idx - 1) >= 0

            controls = []
            if has_next:
                controls.append(
                    f"{C_GREEN}[n] Next Ep ({episodes[current_idx+1].get('number')}){C_RESET}"
                )
            controls.append(f"{C_CYAN}[r] Replay Ep {ep_num}{C_RESET}")
            if has_prev:
                controls.append(
                    f"{C_BLUE}[p] Previous Ep ({episodes[current_idx-1].get('number')}){C_RESET}"
                )
            controls.append(f"{C_YELLOW}[s] Select Episode{C_RESET}")
            controls.append(f"{C_YELLOW}[q] Change Quality{C_RESET}")
            if seasons:
                controls.append(f"{C_YELLOW}[S] Change Season/Movie{C_RESET}")
            controls.append(f"{C_RED}[x] Quit{C_RESET}")

            print("  " + "  |  ".join(controls))

            try:
                cmd = input(f"{C_BOLD}Choice: {C_RESET}").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n")
                return

            if not cmd and has_next:
                current_idx += 1
                break
            elif cmd.lower() in ("n", "next") and has_next:
                current_idx += 1
                break
            elif cmd.lower() in ("r", "replay"):
                break  # loops same ep
            elif cmd.lower() in ("p", "prev", "previous") and has_prev:
                current_idx -= 1
                break
            elif cmd.lower() in ("s", "select", "ep"):
                ep_options = [
                    f"Episode {e.get('number', i+1)}" for i, e in enumerate(episodes)
                ]
                current_idx = pick_option(
                    "Select Episode:", ep_options, default_idx=current_idx
                )
                break
            elif cmd.lower() in ("q", "quality"):
                q_options = list(streams.keys())
                q_idx = pick_option("Select Quality:", q_options, default_idx=0)
                preferred_quality = q_options[q_idx]
                break
            elif cmd.lower() in ("s", "season") and seasons:
                s_options = [s["title"] for s in seasons]
                s_idx = pick_option("Select Season / Movie:", s_options, default_idx=0)
                return play_loop(
                    seasons[s_idx],
                    initial_ep_idx=0,
                    preferred_quality=preferred_quality,
                    mode=mode,
                    player=player,
                )
            elif cmd.lower() in ("x", "quit", "exit"):
                print(f"{C_GREEN}Thanks for using ani-sync! Sayonara! 👋{C_RESET}\n")
                return
            else:
                print(f"{C_RED}Invalid option.{C_RESET}")


# ----------------------------------------------------------------------
# Self-Updater
# ----------------------------------------------------------------------
def update_self(quiet=False):
    """Update ani-sync to the latest version directly from GitHub."""
    if not quiet:
        print(
            f"\n{C_CYAN}{C_BOLD}🔄 Checking for ani-sync updates from GitHub...{C_RESET}"
        )
    url = "https://raw.githubusercontent.com/idrisharis12/ani-sync/main/ani_sync.py"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        remote_code = r.text

        v_match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', remote_code)
        remote_version = v_match.group(1) if v_match else "latest"

        targets = [
            Path(__file__).resolve(),
            Path.home() / ".local" / "share" / "ani-sync" / "ani_sync.py",
            Path("/usr/local/share/ani-sync/ani_sync.py"),
            Path("/usr/share/ani-sync/ani_sync.py"),
        ]

        updated = False
        for target in set(targets):
            if target.exists():
                try:
                    with open(target, "w", encoding="utf-8") as f:
                        f.write(remote_code)
                    os.chmod(target, 0o755)
                    updated = True
                except PermissionError:
                    if not quiet:
                        print(
                            f"{C_YELLOW}Notice: Permission denied writing to {target}. Run with sudo to update system-wide install.{C_RESET}"
                        )

        if updated and not quiet:
            print(
                f"{C_GREEN}{C_BOLD}✅ Successfully updated ani-sync to v{remote_version}!{C_RESET}\n"
            )
        elif not quiet:
            print(
                f"{C_GREEN}{C_BOLD}✅ ani-sync is already up to date (v{remote_version}).{C_RESET}\n"
            )
    except Exception as e:
        if not quiet:
            print(f"{C_RED}❌ Failed to update ani-sync: {e}{C_RESET}")


# ----------------------------------------------------------------------
# CLI Interface & Entry Point
# ----------------------------------------------------------------------
def print_help():
    print(
        f"""{C_CYAN}{C_BOLD}ani-sync v{VERSION}{C_RESET} — Stream anime in terminal and auto-sync progress to MyAnimeList

{C_BOLD}Usage:{C_RESET}
    ani-sync <anime name> [options]
    ani-sync watch <url> [--player <player>]
    ani-sync update
    ani-sync auth
    ani-sync --help

{C_BOLD}Examples:{C_RESET}
    {C_GREEN}ani-sync naruto{C_RESET}
    {C_GREEN}ani-sync "frieren" -q 1080p{C_RESET}
    {C_GREEN}ani-sync "attack on titan" --dub{C_RESET}
    {C_GREEN}ani-sync "jujutsu kaisen" -e 5 --player vlc{C_RESET}

{C_BOLD}Options:{C_RESET}
    -e, --episode <num>   Jump directly to specified episode number
    -q, --quality <res>   Preferred quality (e.g. 1080p, 720p, 480p, 360p)
    --dub                 Play English dub if available (default: Japanese sub)
    --player <player>     Media player executable (default: mpv)
    -U, --update, update  Check and update ani-sync to the latest version
    auth                  Run interactive MyAnimeList OAuth2 setup wizard
    -h, --help            Show this help menu
"""
    )


def main():
    args = sys.argv[1:]

    # Asynchronous background auto-updater for all Linux distributions & macOS
    if not (args and args[0] in ("-h", "--help", "help", "auth", "setup", "--auth")):
        threading.Thread(
            target=update_self, kwargs={"quiet": True}, daemon=True
        ).start()

    if not args or args[0] in ("-h", "--help", "help"):
        if not args:
            # Interactive prompt if no arguments
            pass
        else:
            print_help()
            return

    if args and args[0] in ("-U", "--update", "update"):
        quiet = "--quiet" in args or "-q" in args
        update_self(quiet=quiet)
        return

    if args and args[0] in ("auth", "setup", "--auth"):
        run_auth()
        return

    # Check for legacy watch <url> syntax
    if args and args[0] == "watch" and len(args) >= 2:
        url = args[1]
        player = "mpv"
        if "--player" in args:
            p_idx = args.index("--player")
            if p_idx + 1 < len(args):
                player = args[p_idx + 1]
        launch_player(url, "Anime Episode", 1, player=player)
        return

    # Parse Flags
    query_parts = []
    episode_target = None
    preferred_quality = None
    mode = "sub"
    player = "mpv"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-e", "--episode", "-r", "--range"):
            if i + 1 < len(args):
                episode_target = int(args[i + 1])
                i += 1
        elif arg in ("-q", "--quality"):
            if i + 1 < len(args):
                preferred_quality = args[i + 1]
                if not preferred_quality.endswith("p") and preferred_quality.isdigit():
                    preferred_quality += "p"
                i += 1
        elif arg == "--dub":
            mode = "dub"
        elif arg == "--player":
            if i + 1 < len(args):
                player = args[i + 1]
                i += 1
        elif not arg.startswith("-"):
            query_parts.append(arg)
        i += 1

    query = " ".join(query_parts).strip()
    if not query:
        print(
            f"\n{C_CYAN}{C_BOLD}============================================================{C_RESET}"
        )
        print(
            f"{C_MAGENTA}{C_BOLD}              ani-sync — Terminal Anime Player              {C_RESET}"
        )
        print(
            f"{C_CYAN}{C_BOLD}============================================================{C_RESET}"
        )
        try:
            query = input(f"\n{C_BOLD}🔍 Search anime title: {C_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            return
        if not query:
            print(f"{C_RED}No search query entered.{C_RESET}")
            return

    print(f"\n{C_YELLOW}Searching for '{query}'...{C_RESET}")
    try:
        results = search_anime(query)
    except Exception as e:
        print(f"{C_RED}❌ Search error: {e}{C_RESET}")
        return

    if not results:
        print(
            f"{C_RED}❌ No anime found matching '{query}'. Try another search term!{C_RESET}"
        )
        return

    # Pick Anime
    if len(results) == 1:
        chosen_anime = results[0]
    else:
        options = [r["title"] for r in results]
        selected_idx = pick_option("Search Results:", options, default_idx=0)
        chosen_anime = results[selected_idx]

    # Check for seasons / movies franchise options
    details = get_anime_details(chosen_anime["slug"])
    seasons = details.get("seasons", [])
    if seasons:
        franchise_options = [f"{chosen_anime['title']} (Selected)"] + [
            s["title"] for s in seasons
        ]
        f_idx = pick_option(
            f"Seasons & Movies for '{chosen_anime['title']}':",
            franchise_options,
            default_idx=0,
        )
        if f_idx > 0:
            chosen_anime = seasons[f_idx - 1]

    # Fetch episodes
    episodes = get_episodes(chosen_anime["slug"])
    if not episodes:
        print(f"{C_RED}❌ No episodes found for {chosen_anime['title']}.{C_RESET}")
        return

    # Pick Episode
    ep_idx = 0
    if episode_target:
        for idx, ep in enumerate(episodes):
            if ep.get("number") == episode_target:
                ep_idx = idx
                break
    elif len(episodes) > 1:
        ep_options = [f"Episode {e.get('number', i+1)}" for i, e in enumerate(episodes)]
        ep_idx = pick_option(
            f"Select Episode for '{chosen_anime['title']}':", ep_options, default_idx=0
        )

    # Launch Playback Loop
    play_loop(
        chosen_anime,
        initial_ep_idx=ep_idx,
        preferred_quality=preferred_quality,
        mode=mode,
        player=player,
    )


if __name__ == "__main__":
    main()
