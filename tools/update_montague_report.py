#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Detroit")
LAT = 43.4148
LON = -86.3560
BUSINESS_ADDRESS = "5123 Osmun Street, Montague, Michigan 49437"
LAUNCH_ADDRESS = "Montague Municipal Boat Launch, 8500 Ramp Rd, Montague, MI 49437"

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
LOG_FILE = DATA_DIR / "report_logs" / "report.log"
JSON_PATH = DATA_DIR / "montague_report_latest.json"
HTML_PATH = ROOT / "montague-wave-report.html"
LOCK_PATH = DATA_DIR / ".report.lock"


def log(msg: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    os.replace(tmp, path)


def get_text(url: str, timeout: int = 20, retries: int = 3) -> str:
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DFC-WeatherBot/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            log(f"GET fail {i+1}/{retries} {url} :: {e}")
            time.sleep(min(8, 2 * (i + 1)))
    raise RuntimeError(f"GET failed: {url}; {last}")


def get_json(url: str, timeout: int = 20, retries: int = 3):
    return json.loads(get_text(url, timeout, retries))


def m_to_ft(v):
    return None if v is None else v * 3.28084


def c_to_f(v):
    return None if v is None else v * 9.0 / 5.0 + 32.0


def nearest(series, target: datetime, max_hours: int = 4):
    best_d = 10**18
    best_v = None
    for dt, val in series:
        if val is None:
            continue
        d = abs((dt - target).total_seconds())
        if d < best_d:
            best_d, best_v = d, val
    if best_v is None or best_d > max_hours * 3600:
        return None
    return best_v


def avg(vals):
    g = [v for v in vals if v is not None]
    return None if not g else sum(g) / len(g)


def wave_condition(ft):
    if ft is None:
        return "Unknown"
    if ft < 1.5:
        return "Calm"
    if ft < 3.0:
        return "Light chop"
    if ft < 4.5:
        return "Moderate chop"
    if ft < 6.0:
        return "Rough"
    return "Very rough"


def fmt_ft(v):
    return "n/a" if v is None else f"{v:.1f} ft"


def fmt_f(v):
    return "n/a" if v is None else f"{v:.0f}F"

def fmt_time(v):
    return "n/a" if not v else v


def fetch_openmeteo(first_t, last_t, no_network=False):
    if no_network:
        return {
            "name": "Open-Meteo",
            "ok": True,
            "first_wave_ft": 2.0,
            "last_wave_ft": 1.6,
            "first_temp_f": 48.0,
            "high_temp_f": 57.0,
            "low_temp_f": 43.0,
            "first_light_time_local": "7:12 AM",
            "last_light_time_local": "6:31 PM",
            "details": "offline sample",
        }

    marine_q = urllib.parse.urlencode({
        "latitude": LAT,
        "longitude": LON,
        "hourly": "wave_height",
        "timezone": "America/Detroit",
        "past_days": 2,
        "forecast_days": 1,
    })
    weather_q = urllib.parse.urlencode({
        "latitude": LAT,
        "longitude": LON,
        "hourly": "temperature_2m",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",
        "timezone": "America/Detroit",
        "past_days": 1,
        "forecast_days": 1,
    })
    m = get_json(f"https://marine-api.open-meteo.com/v1/marine?{marine_q}")
    w = get_json(f"https://api.open-meteo.com/v1/forecast?{weather_q}")

    # Waves
    m_times = m.get("hourly", {}).get("time", [])
    m_waves = m.get("hourly", {}).get("wave_height", [])
    wave_series = []
    for t, val in zip(m_times, m_waves):
        dt = datetime.fromisoformat(t).replace(tzinfo=TZ)
        wave_series.append((dt, m_to_ft(val) if val is not None else None))

    # Temps
    w_times = w.get("hourly", {}).get("time", [])
    w_temps = w.get("hourly", {}).get("temperature_2m", [])
    temp_series = []
    for t, val in zip(w_times, w_temps):
        dt = datetime.fromisoformat(t).replace(tzinfo=TZ)
        temp_series.append((dt, c_to_f(val) if val is not None else None))

    daily = w.get("daily", {})
    high = None
    low = None
    sunrise = None
    sunset = None
    try:
        high = c_to_f(daily.get("temperature_2m_max", [None])[0])
        low = c_to_f(daily.get("temperature_2m_min", [None])[0])
        sunrise_raw = daily.get("sunrise", [None])[0]
        sunset_raw = daily.get("sunset", [None])[0]
        if sunrise_raw:
            s = datetime.fromisoformat(sunrise_raw).replace(tzinfo=TZ)
            sunrise = s.strftime("%I:%M %p").lstrip("0")
        if sunset_raw:
            s = datetime.fromisoformat(sunset_raw).replace(tzinfo=TZ)
            sunset = s.strftime("%I:%M %p").lstrip("0")
    except Exception:
        pass

    return {
        "name": "Open-Meteo",
        "ok": True,
        "first_wave_ft": nearest(wave_series, first_t),
        "last_wave_ft": nearest(wave_series, last_t),
        "first_temp_f": nearest(temp_series, first_t),
        "high_temp_f": high,
        "low_temp_f": low,
        "first_light_time_local": sunrise,
        "last_light_time_local": sunset,
        "details": "marine+weather",
    }


def parse_ndbc(station: str, text: str, first_t, last_t):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    i = next((k for k, ln in enumerate(lines) if ln.startswith("#YY")), -1)
    if i < 0:
        return None
    hdr = lines[i].lstrip("#").split()
    need = ["YY", "MM", "DD", "hh", "mm", "WVHT", "ATMP"]
    if any(n not in hdr for n in need):
        return None
    idx = {n: hdr.index(n) for n in need}
    wave_series = []
    temp_series = []
    for ln in lines[i + 2 :]:
        p = ln.split()
        if len(p) <= max(idx.values()):
            continue
        try:
            y = int(p[idx["YY"]]); y = 2000 + y if y < 100 else y
            mo = int(p[idx["MM"]]); d = int(p[idx["DD"]]); h = int(p[idx["hh"]]); mi = int(p[idx["mm"]])
            dt_local = datetime(y, mo, d, h, mi, tzinfo=ZoneInfo("UTC")).astimezone(TZ)
            wv = None if p[idx["WVHT"]] == "MM" else m_to_ft(float(p[idx["WVHT"]]))
            at = None if p[idx["ATMP"]] == "MM" else c_to_f(float(p[idx["ATMP"]]))
            wave_series.append((dt_local, wv))
            temp_series.append((dt_local, at))
        except Exception:
            continue
    return {
        "name": f"NOAA NDBC {station}",
        "ok": True,
        "first_wave_ft": nearest(wave_series, first_t),
        "last_wave_ft": nearest(wave_series, last_t),
        "first_temp_f": nearest(temp_series, first_t),
        "high_temp_f": None,
        "low_temp_f": None,
        "first_light_time_local": None,
        "last_light_time_local": None,
        "details": f"station {station}",
    }


def fetch_ndbc(first_t, last_t, no_network=False):
    if no_network:
        return {
            "name": "NOAA NDBC",
            "ok": True,
            "first_wave_ft": 2.4,
            "last_wave_ft": 2.0,
            "first_temp_f": 47.0,
            "high_temp_f": None,
            "low_temp_f": None,
            "first_light_time_local": None,
            "last_light_time_local": None,
            "details": "offline sample",
        }

    stations = ["45029", "45161", "MKGM4", "45167", "45024"]
    errs = []
    for st in stations:
        try:
            txt = get_text(f"https://www.ndbc.noaa.gov/data/realtime2/{st}.txt")
            parsed = parse_ndbc(st, txt, first_t, last_t)
            if not parsed:
                errs.append(f"{st}: parse")
                continue
            if parsed["first_wave_ft"] is None and parsed["last_wave_ft"] is None:
                errs.append(f"{st}: no wave near target")
                continue
            return parsed
        except Exception as e:
            errs.append(f"{st}: {e}")
    return {
        "name": "NOAA NDBC",
        "ok": False,
        "first_wave_ft": None,
        "last_wave_ft": None,
        "first_temp_f": None,
        "high_temp_f": None,
        "low_temp_f": None,
        "first_light_time_local": None,
        "last_light_time_local": None,
        "details": "; ".join(errs)[:600],
    }


def load_prev():
    if not JSON_PATH.exists():
        return None
    try:
        return json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"prev load fail: {e}")
        return None


def acquire_lock():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    if LOCK_PATH.exists():
        age = now - LOCK_PATH.stat().st_mtime
        if age < 1800:
            log("fresh lock exists; skip")
            return False
        try:
            LOCK_PATH.unlink()
        except Exception:
            pass
    LOCK_PATH.write_text(str(now), encoding="utf-8")
    return True


def release_lock():
    try:
        LOCK_PATH.unlink(missing_ok=True)
    except Exception:
        pass


def render_html(report):
    rows = []
    for s in report["sources"]:
        rows.append(
            f"<tr><td>{s['name']}</td><td>{fmt_ft(s['first_wave_ft'])}</td><td>{fmt_ft(s['last_wave_ft'])}</td><td>{fmt_f(s['first_temp_f'])}</td><td>{'OK' if s['ok'] else 'Issue'}</td></tr>"
        )
    rows_html = "".join(rows)

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Montague Daily Wave & Weather Report</title>
  <meta name=\"description\" content=\"Daily first-light and last-night wave conditions for Montague, plus morning temp and expected high/low.\" />
  <link rel=\"stylesheet\" href=\"assets/css/styles.css\" />
  <link rel=\"canonical\" href=\"https://www.davesfishingcharters.com/montague-wave-report.html\" />
</head>
<body>
<header>
  <div class=\"topbar\">
    <div class=\"container topbar-inner\">
      <div>Call today: <strong><a href=\"tel:+12316720399\">231-672-0399</a></strong></div>
      <div><a href=\"contact.html\">Book your trip</a> | Business Address: {BUSINESS_ADDRESS}</div>
    </div>
  </div>
  <div class=\"container navbar\">
    <a class=\"brand\" href=\"index.html\">Dave's Fishing Charters</a>
    <nav aria-label=\"Primary\">
      <ul>
        <li><a href=\"index.html\">Home</a></li>
        <li><a href=\"about.html\">About</a></li>
        <li><a href=\"services.html\">Services</a></li>
        <li><a href=\"faqs.html\">FAQs</a></li>
        <li><a href=\"rates.html\">Rates</a></li>
        <li><a href=\"resources.html\">Resources</a></li>
        <li><a href=\"reviews.html\">Reviews</a></li>
        <li><a href=\"montague-wave-report.html\" aria-current=\"page\">Wave Report</a></li>
        <li><a href=\"destinations.html\">Travelers</a></li>
        <li><a href=\"blog/index.html\">Blog</a></li>
        <li><a href=\"contact.html\">Contact</a></li>
        <li><a class=\"btn btn-accent\" href=\"contact.html\">Book Now</a></li>
      </ul>
    </nav>
  </div>
</header>
<main class=\"section\">
  <div class=\"container\">
    <h1>Montague Daily Wave & Weather Report</h1>
    <p class=\"lead\">Launch planning snapshot for {LAUNCH_ADDRESS}</p>
    <div class=\"grid-3\">
      <article class=\"card\"><h3>First Light Wave</h3><p><strong>{fmt_ft(report['averages']['first_wave_ft'])}</strong> ({wave_condition(report['averages']['first_wave_ft'])})</p></article>
      <article class=\"card\"><h3>Last Night Wave</h3><p><strong>{fmt_ft(report['averages']['last_wave_ft'])}</strong> ({wave_condition(report['averages']['last_wave_ft'])})</p></article>
      <article class=\"card\"><h3>First / Last Light</h3><p><strong>{fmt_time(report['averages']['first_light_time_local'])} / {fmt_time(report['averages']['last_light_time_local'])}</strong></p></article>
      <article class=\"card\"><h3>Morning Temp</h3><p><strong>{fmt_f(report['averages']['first_temp_f'])}</strong></p></article>
      <article class=\"card\"><h3>Today Hi / Low</h3><p><strong>{fmt_f(report['averages']['high_temp_f'])} / {fmt_f(report['averages']['low_temp_f'])}</strong></p></article>
    </div>
    <div class=\"card\" style=\"margin-top:1rem\">
      <h2>Source Average Details</h2>
      <table class=\"table\"><thead><tr><th>Source</th><th>First Light Wave</th><th>Last Night Wave</th><th>Morning Temp</th><th>Status</th></tr></thead><tbody>{rows_html}</tbody></table>
      <p><small>Last updated: {report['updated_local']} | stale fallback: {str(report['stale']).lower()}</small></p>
      <p><small>Method: average of available sources. If one source fails, report still publishes. If all fail, it reuses last good report.</small></p>
      <p><small>Safety note: this is planning info only. Always verify official marine advisories before launch.</small></p>
    </div>
    <div class=\"card\" style=\"margin-top:1rem\">
      <h2>Family Trip Read</h2>
      <p>If first-light waves are under about 3.0 ft and wind is stable, most family groups are usually more comfortable. We still verify conditions day-of before launch.</p>
    </div>
  </div>
</main>
<footer><div class=\"container\"><p class=\"small\">&copy; {datetime.now(TZ).year} Dave's Fishing Charters</p></div></footer>
<script src=\"assets/js/main.js\"></script>
</body>
</html>
"""


def run(no_network=False):
    if not acquire_lock():
        return 0
    try:
        now = datetime.now(TZ)
        first_t = now.replace(hour=6, minute=0, second=0, microsecond=0)
        last_t = (first_t - timedelta(days=1)).replace(hour=22)

        src1 = fetch_openmeteo(first_t, last_t, no_network=no_network)
        src2 = fetch_ndbc(first_t, last_t, no_network=no_network)
        srcs = [src1, src2]

        prev = load_prev()

        first_wave = avg([s["first_wave_ft"] for s in srcs if s["ok"]])
        last_wave = avg([s["last_wave_ft"] for s in srcs if s["ok"]])
        first_temp = avg([s["first_temp_f"] for s in srcs if s["ok"]])
        first_light_time = next((s.get("first_light_time_local") for s in srcs if s["ok"] and s.get("first_light_time_local")), None)
        last_light_time = next((s.get("last_light_time_local") for s in srcs if s["ok"] and s.get("last_light_time_local")), None)

        high_vals = [s["high_temp_f"] for s in srcs if s.get("high_temp_f") is not None]
        low_vals = [s["low_temp_f"] for s in srcs if s.get("low_temp_f") is not None]
        high_temp = avg(high_vals)
        low_temp = avg(low_vals)

        stale = False
        if prev:
            if first_wave is None:
                first_wave = prev.get("averages", {}).get("first_wave_ft")
                stale = True
            if last_wave is None:
                last_wave = prev.get("averages", {}).get("last_wave_ft")
                stale = True
            if first_temp is None:
                first_temp = prev.get("averages", {}).get("first_temp_f")
                stale = True
            if high_temp is None:
                high_temp = prev.get("averages", {}).get("high_temp_f")
            if low_temp is None:
                low_temp = prev.get("averages", {}).get("low_temp_f")
            if not first_light_time:
                first_light_time = prev.get("averages", {}).get("first_light_time_local")
            if not last_light_time:
                last_light_time = prev.get("averages", {}).get("last_light_time_local")

        if first_wave is None and last_wave is None and first_temp is None:
            # nothing useful and no previous fallback
            raise RuntimeError("All sources failed and no previous report available")

        report = {
            "updated_utc": datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_local": now.strftime("%Y-%m-%d %H:%M %Z"),
            "stale": stale,
            "location": {
                "business_address": BUSINESS_ADDRESS,
                "launch_address": LAUNCH_ADDRESS,
                "lat": LAT,
                "lon": LON,
            },
            "averages": {
                "first_wave_ft": first_wave,
                "last_wave_ft": last_wave,
                "first_temp_f": first_temp,
                "high_temp_f": high_temp,
                "low_temp_f": low_temp,
                "first_light_time_local": first_light_time,
                "last_light_time_local": last_light_time,
            },
            "sources": srcs,
        }

        atomic_write(JSON_PATH, json.dumps(report, indent=2))
        atomic_write(HTML_PATH, render_html(report))
        log("update complete")
        return 0
    except Exception as e:
        log(f"fatal: {e}")
        return 1
    finally:
        release_lock()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-network", action="store_true", help="Use deterministic local sample data")
    args = ap.parse_args()
    raise SystemExit(run(no_network=args.no_network))


if __name__ == "__main__":
    main()

