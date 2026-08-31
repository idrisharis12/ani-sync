# -*- coding: utf-8 -*-
"""AniSkip frame-accurate OP/ED community timestamp parser and MPV Lua script generator."""

import requests
from ani_sync.config import get_cache_dir, log_debug


def fetch_aniskip_times(mal_id, ep_num):
    """Fetch frame-accurate opening and ending timestamps from AniSkip API."""
    if not mal_id:
        return None
    try:
        url = f"https://api.aniskip.com/v2/skip-times/{mal_id}/{ep_num}"
        r = requests.get(
            url,
            params={"types[]": ["op", "ed", "recap", "mixed-op"], "episodeLength": 0},
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("found"):
                results = data.get("results", [])
                op_times = None
                ed_times = None
                for res in results:
                    skip_type = res.get("skipType")
                    interval = res.get("interval", {})
                    start = interval.get("startTime")
                    end = interval.get("endTime")
                    if start is not None and end is not None and end > start:
                        if skip_type in ("op", "mixed-op", "recap") and not op_times:
                            op_times = (float(start), float(end))
                        elif skip_type in ("ed", "mixed-ed") and not ed_times:
                            ed_times = (float(start), float(end))
                if op_times or ed_times:
                    return {"op": op_times, "ed": ed_times}
    except Exception as e:
        log_debug(f"AniSkip API fetch error: {e}")
    return None


def get_auto_skip_script(auto_skip=False, aniskip_data=None):
    """Generate dynamic lightweight MPV Lua script for AniSkip."""
    cache_dir = get_cache_dir()
    script_path = cache_dir / "ani_skip.lua"

    op_start = aniskip_data.get("op")[0] if (aniskip_data and aniskip_data.get("op")) else 0.0
    op_end = aniskip_data.get("op")[1] if (aniskip_data and aniskip_data.get("op")) else 85.0
    has_exact_op = bool(aniskip_data and aniskip_data.get("op"))

    ed_start = aniskip_data.get("ed")[0] if (aniskip_data and aniskip_data.get("ed")) else None
    ed_end = aniskip_data.get("ed")[1] if (aniskip_data and aniskip_data.get("ed")) else None
    has_exact_ed = bool(aniskip_data and aniskip_data.get("ed"))

    lua_code = f"""
-- ani-sync Auto-Skip & AniSkip Lua Integration
local auto_skip = {str(auto_skip).lower()}
local op_start = {op_start}
local op_end = {op_end}
local has_exact_op = {str(has_exact_op).lower()}
local ed_start = {ed_start if ed_start is not None else "nil"}
local ed_end = {ed_end if ed_end is not None else "nil"}
local has_exact_ed = {str(has_exact_ed).lower()}
local skipped_op = false
local skipped_ed = false

function on_time_pos(name, pos)
    if not pos then return end
    if auto_skip and not skipped_op and has_exact_op then
        if pos >= op_start and pos < (op_end - 1.0) then
            skipped_op = true
            mp.osd_message("⏩ AniSkip: Skipping Opening...", 2)
            mp.commandv("seek", op_end, "absolute", "exact")
        end
    end
    if auto_skip and not skipped_ed and has_exact_ed and ed_start then
        if pos >= ed_start and pos < (ed_end - 1.0) then
            skipped_ed = true
            mp.osd_message("⏩ AniSkip: Skipping Ending...", 2)
            mp.commandv("seek", ed_end, "absolute", "exact")
        end
    end
end

function manual_skip_op()
    mp.osd_message("⏩ Skipping Opening...", 2)
    mp.commandv("seek", op_end, "absolute", "exact")
end

function manual_skip_ed()
    if ed_end then
        mp.osd_message("⏩ Skipping Ending...", 2)
        mp.commandv("seek", ed_end, "absolute", "exact")
    else
        mp.osd_message("⏩ Skipping 90s (Outro)...", 2)
        mp.commandv("seek", 90, "relative", "exact")
    end
end

mp.observe_property("time-pos", "number", on_time_pos)
mp.add_key_binding("Tab", "manual_skip_intro_tab", manual_skip_op)
mp.add_key_binding("i", "manual_skip_intro_i", manual_skip_op)
mp.add_key_binding("o", "manual_skip_outro", manual_skip_ed)
"""
    try:
        script_path.write_text(lua_code.strip(), encoding="utf-8")
        return str(script_path)
    except Exception:
        return None
