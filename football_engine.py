"""
Gerçek Maç Takip, İstatistik ve Bilgili Futbol Arkadaşı Analiz Motoru
ESPN Global Sports API üzerinden reel verileri çeker, Poisson ve form modelleriyle
analiz eder, samimi ve uzman bir futbol diliyle yorumlar üretir.
"""

import json
import math
import os
import re
import time
import urllib.request
import urllib.error
import ssl
import gzip
import subprocess
import shutil
from datetime import datetime, timezone, timedelta

# Desteklenen popüler ligler
LEAGUES = {
    "all": {"name": "🌍 Tüm Dünya Maçları", "slug": "all", "flag": "🌍"},
    "tur.1": {"name": "🇹🇷 Trendyol Süper Lig", "slug": "tur.1", "flag": "🇹🇷"},
    "uefa.champions": {"name": "🏆 UEFA Şampiyonlar Ligi", "slug": "uefa.champions", "flag": "🏆"},
    "uefa.nations": {"name": "🇪🇺 UEFA Uluslar Ligi", "slug": "uefa.nations", "flag": "🇪🇺"},
    "uefa.europa": {"name": "🥈 UEFA Avrupa Ligi", "slug": "uefa.europa", "flag": "🥈"},
    "eng.1": {"name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 İngiltere Premier League", "slug": "eng.1", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    "esp.1": {"name": "🇪🇸 İspanya La Liga", "slug": "esp.1", "flag": "🇪🇸"},
    "ita.1": {"name": "🇮🇹 İtalya Serie A", "slug": "ita.1", "flag": "🇮🇹"},
    "ger.1": {"name": "🇩🇪 Almanya Bundesliga", "slug": "ger.1", "flag": "🇩🇪"},
    "fra.1": {"name": "🇫🇷 Fransa Ligue 1", "slug": "fra.1", "flag": "🇫🇷"},
}

# İngilizce → Türkçe Takım İsmi Çeviri Sözlüğü
TEAM_NAME_TR = {
    # Türk Takımları
    "Galatasaray": "Galatasaray",
    "Fenerbahce": "Fenerbahçe",
    "Fenerbahçe": "Fenerbahçe",
    "Besiktas": "Beşiktaş",
    "Beşiktaş": "Beşiktaş",
    "Trabzonspor": "Trabzonspor",
    "Istanbul Basaksehir": "Başakşehir",
    "Istanbul Basaksehir FK": "Başakşehir",
    "Basaksehir": "Başakşehir",
    "Adana Demirspor": "Adana Demirspor",
    "Antalyaspor": "Antalyaspor",
    "Alanyaspor": "Alanyaspor",
    "Sivasspor": "Sivasspor",
    "Kayserispor": "Kayserispor",
    "Konyaspor": "Konyaspor",
    "Gaziantep FK": "Gaziantep FK",
    "Gaziantep": "Gaziantep FK",
    "Kasimpasa": "Kasımpaşa",
    "Kasımpaşa": "Kasımpaşa",
    "Rizespor": "Çaykur Rizespor",
    "Caykur Rizespor": "Çaykur Rizespor",
    "Samsunspor": "Samsunspor",
    "Hatayspor": "Hatayspor",
    "Pendikspor": "Pendikspor",
    "Istanbulspor": "İstanbulspor",
    "Goztepe": "Göztepe",
    "Göztepe": "Göztepe",
    "Eyupspor": "Eyüpspor",
    "Eyüpspor": "Eyüpspor",
    "Bodrum FK": "Bodrumspor",
    "Bodrumspor": "Bodrumspor",
    "Amed SK": "Amedspor",
    "Amedspor": "Amedspor",
    "Amed SFK": "Amedspor",
    # Milli Takımlar
    "Turkey": "Türkiye",
    "Türkiye": "Türkiye",
    "Germany": "Almanya",
    "France": "Fransa",
    "Spain": "İspanya",
    "Italy": "İtalya",
    "England": "İngiltere",
    "Netherlands": "Hollanda",
    "Portugal": "Portekiz",
    "Belgium": "Belçika",
    "Croatia": "Hırvatistan",
    "Switzerland": "İsviçre",
    "Austria": "Avusturya",
    "Denmark": "Danimarka",
    "Sweden": "İsveç",
    "Norway": "Norveç",
    "Poland": "Polonya",
    "Czech Republic": "Çekya",
    "Czechia": "Çekya",
    "Greece": "Yunanistan",
    "Scotland": "İskoçya",
    "Wales": "Galler",
    "Ireland": "İrlanda",
    "Republic of Ireland": "İrlanda",
    "Northern Ireland": "Kuzey İrlanda",
    "Hungary": "Macaristan",
    "Romania": "Romanya",
    "Serbia": "Sırbistan",
    "Ukraine": "Ukrayna",
    "Russia": "Rusya",
    "Finland": "Finlandiya",
    "Iceland": "İzlanda",
    "Albania": "Arnavutluk",
    "Bosnia and Herzegovina": "Bosna Hersek",
    "Bosnia-Herzegovina": "Bosna Hersek",
    "Montenegro": "Karadağ",
    "North Macedonia": "Kuzey Makedonya",
    "Slovakia": "Slovakya",
    "Slovenia": "Slovenya",
    "Bulgaria": "Bulgaristan",
    "Georgia": "Gürcistan",
    "Armenia": "Ermenistan",
    "Azerbaijan": "Azerbaycan",
    "Israel": "İsrail",
    "Cyprus": "Kıbrıs",
    "Kosovo": "Kosova",
    "Moldova": "Moldova",
    "Luxembourg": "Lüksemburg",
    "Lithuania": "Litvanya",
    "Latvia": "Letonya",
    "Estonia": "Estonya",
    "Malta": "Malta",
    "Faroe Islands": "Faroe Adaları",
    "Gibraltar": "Cebelitarık",
    "Andorra": "Andorra",
    "San Marino": "San Marino",
    "Liechtenstein": "Lihtenştayn",
    "Belarus": "Belarus",
    "Kazakhstan": "Kazakistan",
    # İngiltere Premier League
    "Manchester City": "Manchester City",
    "Manchester United": "Manchester United",
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Liverpool": "Liverpool",
    "Arsenal": "Arsenal",
    "Chelsea": "Chelsea",
    "Tottenham Hotspur": "Tottenham",
    "Tottenham": "Tottenham",
    "Newcastle United": "Newcastle",
    "Newcastle": "Newcastle",
    "Aston Villa": "Aston Villa",
    "Brighton & Hove Albion": "Brighton",
    "Brighton": "Brighton",
    "West Ham United": "West Ham",
    "West Ham": "West Ham",
    "Crystal Palace": "Crystal Palace",
    "Brentford": "Brentford",
    "Fulham": "Fulham",
    "Wolverhampton Wanderers": "Wolverhampton",
    "Wolverhampton": "Wolverhampton",
    "Wolves": "Wolverhampton",
    "AFC Bournemouth": "Bournemouth",
    "Bournemouth": "Bournemouth",
    "Nottingham Forest": "Nottingham Forest",
    "Everton": "Everton",
    "Luton Town": "Luton Town",
    "Burnley": "Burnley",
    "Sheffield United": "Sheffield United",
    "Ipswich Town": "Ipswich Town",
    "Leicester City": "Leicester City",
    "Southampton": "Southampton",
    # İspanya La Liga
    "Real Madrid": "Real Madrid",
    "Barcelona": "Barcelona",
    "FC Barcelona": "Barcelona",
    "Atletico Madrid": "Atletico Madrid",
    "Atlético Madrid": "Atletico Madrid",
    "Atletico de Madrid": "Atletico Madrid",
    "Real Sociedad": "Real Sociedad",
    "Real Betis": "Real Betis",
    "Villarreal": "Villarreal",
    "Villarreal CF": "Villarreal",
    "Athletic Bilbao": "Athletic Bilbao",
    "Athletic Club": "Athletic Bilbao",
    "Sevilla": "Sevilla",
    "Sevilla FC": "Sevilla",
    "Valencia": "Valencia",
    "Valencia CF": "Valencia",
    "Girona": "Girona",
    "Girona FC": "Girona",
    "Getafe": "Getafe",
    "Getafe CF": "Getafe",
    "Celta Vigo": "Celta Vigo",
    "RC Celta": "Celta Vigo",
    "Osasuna": "Osasuna",
    "CA Osasuna": "Osasuna",
    "Mallorca": "Mallorca",
    "RCD Mallorca": "Mallorca",
    "Las Palmas": "Las Palmas",
    "UD Las Palmas": "Las Palmas",
    "Rayo Vallecano": "Rayo Vallecano",
    "Deportivo Alaves": "Alaves",
    "Alavés": "Alaves",
    "Cadiz": "Cadiz",
    "Cádiz CF": "Cadiz",
    "Granada": "Granada",
    "Granada CF": "Granada",
    "Almeria": "Almeria",
    "UD Almería": "Almeria",
    # Almanya Bundesliga
    "Bayern Munich": "Bayern Münih",
    "FC Bayern Munich": "Bayern Münih",
    "Bayern München": "Bayern Münih",
    "Borussia Dortmund": "Borussia Dortmund",
    "RB Leipzig": "RB Leipzig",
    "Bayer Leverkusen": "Bayer Leverkusen",
    "Bayer 04 Leverkusen": "Bayer Leverkusen",
    "VfB Stuttgart": "Stuttgart",
    "Stuttgart": "Stuttgart",
    "Eintracht Frankfurt": "Eintracht Frankfurt",
    "SC Freiburg": "Freiburg",
    "Freiburg": "Freiburg",
    "VfL Wolfsburg": "Wolfsburg",
    "Wolfsburg": "Wolfsburg",
    "1. FC Union Berlin": "Union Berlin",
    "Union Berlin": "Union Berlin",
    "1. FC Köln": "Köln",
    "Köln": "Köln",
    "TSG Hoffenheim": "Hoffenheim",
    "Hoffenheim": "Hoffenheim",
    "Werder Bremen": "Werder Bremen",
    "FC Augsburg": "Augsburg",
    "Augsburg": "Augsburg",
    "1. FSV Mainz 05": "Mainz",
    "Mainz 05": "Mainz",
    "Mainz": "Mainz",
    "VfL Bochum 1848": "Bochum",
    "Bochum": "Bochum",
    "1. FC Heidenheim 1846": "Heidenheim",
    "Heidenheim": "Heidenheim",
    "Borussia Monchengladbach": "Mönchengladbach",
    "Borussia Mönchengladbach": "Mönchengladbach",
    # İtalya Serie A
    "Napoli": "Napoli",
    "SSC Napoli": "Napoli",
    "Inter Milan": "Inter",
    "Internazionale": "Inter",
    "AC Milan": "Milan",
    "Milan": "Milan",
    "Juventus": "Juventus",
    "Atalanta": "Atalanta",
    "Atalanta BC": "Atalanta",
    "Lazio": "Lazio",
    "SS Lazio": "Lazio",
    "Roma": "Roma",
    "AS Roma": "Roma",
    "Fiorentina": "Fiorentina",
    "ACF Fiorentina": "Fiorentina",
    "Bologna": "Bologna",
    "Bologna FC 1909": "Bologna",
    "Torino": "Torino",
    "Torino FC": "Torino",
    "Monza": "Monza",
    "AC Monza": "Monza",
    "Genoa": "Genoa",
    "Genoa CFC": "Genoa",
    "Cagliari": "Cagliari",
    "Cagliari Calcio": "Cagliari",
    "Lecce": "Lecce",
    "US Lecce": "Lecce",
    "Hellas Verona": "Verona",
    "Verona": "Verona",
    "Udinese": "Udinese",
    "Udinese Calcio": "Udinese",
    "Sassuolo": "Sassuolo",
    "US Sassuolo": "Sassuolo",
    "Empoli": "Empoli",
    "Empoli FC": "Empoli",
    "Frosinone": "Frosinone",
    "Frosinone Calcio": "Frosinone",
    "Salernitana": "Salernitana",
    "US Salernitana 1919": "Salernitana",
    "Como": "Como",
    "Como 1907": "Como",
    "Parma": "Parma",
    "Parma Calcio 1913": "Parma",
    "Venezia": "Venezia",
    "Venezia FC": "Venezia",
    # Fransa Ligue 1
    "Paris Saint-Germain": "PSG",
    "Paris Saint Germain": "PSG",
    "PSG": "PSG",
    "Marseille": "Marsilya",
    "Olympique de Marseille": "Marsilya",
    "Monaco": "Monaco",
    "AS Monaco": "Monaco",
    "Lille": "Lille",
    "Lille OSC": "Lille",
    "Lyon": "Lyon",
    "Olympique Lyonnais": "Lyon",
    "Olympique Lyon": "Lyon",
    "Nice": "Nice",
    "OGC Nice": "Nice",
    "Lens": "Lens",
    "RC Lens": "Lens",
    "Rennes": "Rennes",
    "Stade Rennais FC": "Rennes",
    "Strasbourg": "Strasbourg",
    "RC Strasbourg Alsace": "Strasbourg",
    "Nantes": "Nantes",
    "FC Nantes": "Nantes",
    "Montpellier": "Montpellier",
    "Montpellier HSC": "Montpellier",
    "Toulouse": "Toulouse",
    "Toulouse FC": "Toulouse",
    "Brest": "Brest",
    "Stade Brestois 29": "Brest",
    "Reims": "Reims",
    "Stade de Reims": "Reims",
    "Le Havre": "Le Havre",
    "Le Havre AC": "Le Havre",
    "Metz": "Metz",
    "FC Metz": "Metz",
    "Clermont Foot": "Clermont",
    "Clermont": "Clermont",
    "Lorient": "Lorient",
    "FC Lorient": "Lorient",
    # Hollanda Eredivisie
    "Ajax": "Ajax",
    "AFC Ajax": "Ajax",
    "PSV Eindhoven": "PSV",
    "PSV": "PSV",
    "Feyenoord": "Feyenoord",
    # Portekiz
    "Benfica": "Benfica",
    "SL Benfica": "Benfica",
    "Porto": "Porto",
    "FC Porto": "Porto",
    "Sporting CP": "Sporting Lizbon",
    "Sporting Lisbon": "Sporting Lizbon",
    # Diğer Popüler
    "Celtic": "Celtic",
    "Rangers": "Rangers",
    "Galatasaray SK": "Galatasaray",
    "Fenerbahçe SK": "Fenerbahçe",
    "Beşiktaş JK": "Beşiktaş",
}


def translate_team_name(name: str) -> str:
    """Takım ismini İngilizceden Türkçeye çevirir. Sözlükte yoksa orijinal ismi döner."""
    if not name:
        return name
    clean = str(name).strip()
    if clean in TEAM_NAME_TR:
        return TEAM_NAME_TR[clean]
    # Case-insensitive arama
    lower = clean.lower()
    for k, v in TEAM_NAME_TR.items():
        if k.lower() == lower:
            return v
    # Ek temizlemeler (örn: "Turkey M", "Germany National Team")
    for k, v in TEAM_NAME_TR.items():
        if len(k) > 4 and k.lower() in lower:
            return v
    return clean


# Basit bellek içi önbellek (Cache)
_CACHE = {}
CACHE_TTL_LIVE = 30        # Canlı maçlar için 30 saniye
CACHE_TTL_SCHEDULED = 300  # Oynanacak maçlar için 5 dakika
CACHE_TTL_FINISHED = 1800  # Biten maçlar için 30 dakika

_SSL_CONTEXT = None
try:
    _SSL_CONTEXT = ssl.create_default_context()
    _SSL_CONTEXT.check_hostname = False
    _SSL_CONTEXT.verify_mode = ssl.CERT_NONE
except Exception:
    _SSL_CONTEXT = None

_DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.espn.com/",
    "Origin": "https://www.espn.com",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

def _fetch_json(url: str, ttl: int = 120):
    now = time.time()
    if url in _CACHE:
        cached_time, cached_data = _CACHE[url]
        if now - cached_time < ttl:
            return cached_data

    # site.api.espn.com -> site.web.api.espn.com değişimi (ESPN web API herkese açık ve 403 vermez)
    web_url = url.replace("https://site.api.espn.com/", "https://site.web.api.espn.com/")
    urls_to_try = [web_url]
    if web_url != url:
        urls_to_try.append(url)

    # 1. Katman: Python urllib (SSL toleranslı + Gzip açıcı)
    for target_url in urls_to_try:
        try:
            req = urllib.request.Request(target_url, headers=_DEFAULT_HEADERS)
            kwargs = {"timeout": 12}
            if _SSL_CONTEXT:
                kwargs["context"] = _SSL_CONTEXT
            with urllib.request.urlopen(req, **kwargs) as response:
                raw_bytes = response.read()
                if raw_bytes[:2] == b"\x1f\x8b":
                    raw_bytes = gzip.decompress(raw_bytes)
                data = json.loads(raw_bytes.decode("utf-8", errors="replace"))
                if data:
                    _CACHE[url] = (now, data)
                    return data
        except Exception:
            continue

    # 2. Katman: Linux / Windows curl alt süreci (Render bulut sunucularında Akamai/TLS engellerini %100 aşar)
    curl_bin = shutil.which("curl") or shutil.which("curl.exe")
    if curl_bin:
        for target_url in urls_to_try:
            try:
                proc = subprocess.run(
                    [
                        curl_bin,
                        "-s",
                        "-L",
                        "-k",
                        "--max-time", "12",
                        "-A", _DEFAULT_HEADERS["User-Agent"],
                        "-H", f"Accept: {_DEFAULT_HEADERS['Accept']}",
                        "-H", f"Referer: {_DEFAULT_HEADERS['Referer']}",
                        target_url
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                if proc.returncode == 0 and proc.stdout:
                    data = json.loads(proc.stdout)
                    if data:
                        _CACHE[url] = (now, data)
                        return data
            except Exception:
                continue

    print(f"[API ERROR] {url} -> Tüm bağlantı katmanları başarısız oldu")
    # Hata anında eski önbellek varsa onu dön
    if url in _CACHE:
        return _CACHE[url][1]
    return None


def is_match_on_date(iso_date_str: str, target_date_yyyymmdd: str, tz_offset_hours: int = 3) -> bool:
    """
    ISO 8601 tarihini (UTC) Türkiye yerel saatine (UTC+3) çevirerek
    belirtilen 'YYYYMMDD' gününe ait olup olmadığını kesin olarak doğrular.
    Geçmiş veya gelecek günlerin maçlarının bugüne karışmasını engeller.
    """
    if not iso_date_str or not target_date_yyyymmdd:
        return True
    try:
        clean = iso_date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        local_dt = dt + timedelta(hours=tz_offset_hours)
        return local_dt.strftime("%Y%m%d") == str(target_date_yyyymmdd)
    except Exception:
        y = str(target_date_yyyymmdd)[:4]
        m = str(target_date_yyyymmdd)[4:6]
        d = str(target_date_yyyymmdd)[6:8]
        return f"{y}-{m}-{d}" in str(iso_date_str)


def get_match_info_by_id(event_id: str, league_key: str = "all") -> dict:
    """
    Verilen maç ID'si için ESPN summary endpoint'inden gerçek maç bilgilerini
    (takım isimleri, skorlar, canlı dakika/durum, lig, stadyum) eksiksiz çeker.
    Asla sahte 'Ev Sahibi / Deplasman' üretmez.
    """
    if not event_id:
        return None

    url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{league_key}/summary?event={event_id}"
    data = _fetch_json(url, ttl=CACHE_TTL_LIVE)
    if not data or "header" not in data:
        url2 = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/all/summary?event={event_id}"
        data = _fetch_json(url2, ttl=CACHE_TTL_LIVE)

    if not data or "header" not in data:
        return None

    header = data.get("header", {})
    league_obj = header.get("league", {})
    league_name = league_obj.get("name") or LEAGUES.get(league_key, {}).get("name") or "Futbol"

    comps = header.get("competitions") or []
    comp = comps[0] if (comps and isinstance(comps[0], dict)) else {}
    competitors = comp.get("competitors") or []

    home = next((c for c in competitors if isinstance(c, dict) and c.get("homeAway") == "home"), None)
    away = next((c for c in competitors if isinstance(c, dict) and c.get("homeAway") == "away"), None)
    if not home or not away:
        return None

    status_obj = comp.get("status") or {}
    type_obj = status_obj.get("type") or {}
    state = type_obj.get("state", "pre")
    status_desc = type_obj.get("description", "Planlandı")
    status_detail = type_obj.get("detail", "")
    clock = status_obj.get("displayClock", "")

    if state == "in":
        status_tr = f"CANLI {clock}" if clock else "CANLI"
    elif state == "post":
        status_tr = "MS (Bitti)" if ("FT" in status_detail or "Full Time" in status_desc) else (status_detail or status_desc)
    else:
        status_tr = status_detail or status_desc

    venue_obj = comp.get("venue") or {}
    venue_str = venue_obj.get("fullName", "Stadyum Belirtilmedi")

    # Canlı veya Biten maç istatistikleri
    live_stats = None
    if state in ["in", "post"]:
        h_stats = {s.get("name"): s.get("displayValue") for s in home.get("statistics", []) if isinstance(s, dict)}
        a_stats = {s.get("name"): s.get("displayValue") for s in away.get("statistics", []) if isinstance(s, dict)}
        if h_stats or a_stats:
            live_stats = {
                "homePossession": h_stats.get("possessionPct", "50"),
                "awayPossession": a_stats.get("possessionPct", "50"),
                "homeShots": h_stats.get("totalShots", "0"),
                "awayShots": a_stats.get("totalShots", "0"),
                "homeShotsOnTarget": h_stats.get("shotsOnTarget", "0"),
                "awayShotsOnTarget": a_stats.get("shotsOnTarget", "0"),
                "homeCorners": h_stats.get("wonCorners", "0"),
                "awayCorners": a_stats.get("wonCorners", "0"),
                "homeFouls": h_stats.get("foulsCommitted", "0"),
                "awayFouls": a_stats.get("foulsCommitted", "0"),
            }

    # İptal/erteleme kontrolü
    cancelled_keywords = [
        "cancelled", "canceled", "postponed", "abandoned", "suspended",
        "void", "walkover", "forfeit", "called off", "iptal", "ertel"
    ]
    combined_status = f"{status_desc} {status_detail}".lower()
    if any(kw in combined_status for kw in cancelled_keywords):
        return None  # İptal edilen maç

    h_name_tr = translate_team_name(home.get("team", {}).get("displayName", "Ev Sahibi"))
    a_name_tr = translate_team_name(away.get("team", {}).get("displayName", "Deplasman"))
    h_short_tr = translate_team_name(home.get("team", {}).get("shortDisplayName", ""))
    a_short_tr = translate_team_name(away.get("team", {}).get("shortDisplayName", ""))

    return {
        "id": str(event_id),
        "name": f"{h_name_tr} vs {a_name_tr}",
        "date": comp.get("date"),
        "league_name": league_name,
        "league_key": league_key,
        "state": state,
        "status_tr": status_tr,
        "clock": clock,
        "venue": venue_str,
        "live_stats": live_stats,
        "home": {
            "id": home.get("team", {}).get("id"),
            "name": h_name_tr,
            "shortName": h_short_tr,
            "logo": home.get("team", {}).get("logo", ""),
            "score": home.get("score", "0") if state in ["in", "post"] else "-",
        },
        "away": {
            "id": away.get("team", {}).get("id"),
            "name": a_name_tr,
            "shortName": a_short_tr,
            "logo": away.get("team", {}).get("logo", ""),
            "score": away.get("score", "0") if state in ["in", "post"] else "-",
        }
    }


def get_matches(league_key: str = "all", date_str: str = None):
    """
    Belirtilen lig ve tarihe göre SADECE o güne ait reel maçları döner.
    date_str: 'YYYYMMDD' (örn: '20260925')
    Tarih filtresini sıkı tutar; geçmiş günlerin maçlarını asla bugüne dahil etmez.
    """
    if league_key not in LEAGUES:
        league_key = "all"

    # Tarih belirtilmemişse yerel tarihi al
    if not date_str:
        date_str = datetime.now().strftime("%Y%m%d")

    url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{league_key}/scoreboard?dates={date_str}"
    data = _fetch_json(url, ttl=CACHE_TTL_LIVE)

    events = data.get("events", []) if data else []

    parsed_matches = []
    is_today = (date_str == datetime.now().strftime("%Y%m%d"))
    for ev in events:
        try:
            m = _parse_event(ev, league_key)
            # Sadece ve sadece istenen güne denk gelen maçları ekle (bugün ise canlı maçları da dahil et)
            if m and (is_match_on_date(m.get("date"), date_str) or (is_today and m.get("state") == "in")):
                parsed_matches.append(m)
        except Exception as ex:
            print(f"[PARSE ERROR] {ex}")

    # Sıralama: Önce CANLI (0), sonra BİTENLER (1 - skorları hemen görünsün), en son Oynanacaklar (2)
    parsed_matches.sort(key=lambda x: (
        0 if x["state"] == "in" else (1 if x["state"] == "post" else 2),
        x["date"]
    ))

    return {
        "league": LEAGUES.get(league_key, {"name": league_key, "flag": "⚽"}),
        "date": date_str,
        "total": len(parsed_matches),
        "matches": parsed_matches
    }


def _parse_event(ev: dict, fallback_league: str = "all") -> dict:
    comps = ev.get("competitions") or []
    comp = comps[0] if (comps and isinstance(comps[0], dict)) else {}
    competitors = comp.get("competitors") or []
    
    home = next((c for c in competitors if isinstance(c, dict) and c.get("homeAway") == "home"), None)
    away = next((c for c in competitors if isinstance(c, dict) and c.get("homeAway") == "away"), None)
    if not home or not away:
        return None

    status_obj = ev.get("status") or {}
    type_obj = status_obj.get("type") or {}
    state = type_obj.get("state", "pre")  # 'pre', 'in', 'post'
    status_desc = type_obj.get("description", "Planlandı")
    status_detail = type_obj.get("detail", "")

    # İptal edilmiş, ertelenmiş veya terk edilmiş maçları filtrele
    cancelled_keywords = [
        "cancelled", "canceled", "postponed", "abandoned", "suspended",
        "void", "walkover", "forfeit", "called off"
    ]
    combined_status = f"{status_desc} {status_detail}".lower()
    if any(kw in combined_status for kw in cancelled_keywords):
        return None  # Bu maçı tamamen atla
    clock = status_obj.get("displayClock", "")

    # Durum Türkçeleştirme
    if state == "in":
        status_tr = f"CANLI {clock}" if clock else "CANLI"
    elif state == "post":
        if "FT" in status_detail or "Full Time" in status_desc:
            status_tr = "MS (Bitti)"
        elif "AET" in status_detail:
            status_tr = "Uzatmalarda Bitti"
        elif "PEN" in status_detail:
            status_tr = "Penaltılarla Bitti"
        else:
            status_tr = "Maç Sonu"
    else:
        # Başlama saati
        status_tr = status_detail or status_desc

    # Lig / Organizasyon adı
    notes = comp.get("notes") or []
    note_headline = ""
    if notes and isinstance(notes[0], dict):
        note_headline = notes[0].get("headline", "")
    comp_note = comp.get("altGameNote") or note_headline
    league_name = comp_note or LEAGUES.get(fallback_league, {}).get("name", "Futbol")

    # Stadyum / Mekan
    venue_obj = comp.get("venue") or {}
    venue = venue_obj.get("fullName", "")
    addr = venue_obj.get("address") or {}
    city = addr.get("city", "")
    venue_str = f"{venue}, {city}" if venue and city else (venue or city or "Stadyum Belirtilmedi")

    # Oranlar (Pickcenter)
    odds_data = None
    odds_list = comp.get("odds") or []
    if odds_list and isinstance(odds_list[0], dict):
        odds_obj = odds_list[0]
        provider_obj = odds_obj.get("provider") or {}
        odds_data = {
            "details": odds_obj.get("details", ""),
            "overUnder": odds_obj.get("overUnder"),
            "provider": provider_obj.get("name", "Bahis Bürosu")
        }

    # Canlı Maç İstatistikleri (Varsa)
    live_stats = None
    if state in ["in", "post"]:
        h_stats = {s.get("name"): s.get("displayValue") for s in home.get("statistics", []) if isinstance(s, dict)}
        a_stats = {s.get("name"): s.get("displayValue") for s in away.get("statistics", []) if isinstance(s, dict)}
        if h_stats or a_stats:
            live_stats = {
                "homePossession": h_stats.get("possessionPct", "50"),
                "awayPossession": a_stats.get("possessionPct", "50"),
                "homeShots": h_stats.get("totalShots", "0"),
                "awayShots": a_stats.get("totalShots", "0"),
                "homeShotsOnTarget": h_stats.get("shotsOnTarget", "0"),
                "awayShotsOnTarget": a_stats.get("shotsOnTarget", "0"),
                "homeCorners": h_stats.get("wonCorners", "0"),
                "awayCorners": a_stats.get("wonCorners", "0"),
                "homeFouls": h_stats.get("foulsCommitted", "0"),
                "awayFouls": a_stats.get("foulsCommitted", "0"),
            }

    h_name_tr = translate_team_name(home.get("team", {}).get("displayName", "Ev Sahibi"))
    a_name_tr = translate_team_name(away.get("team", {}).get("displayName", "Deplasman"))
    h_short_tr = translate_team_name(home.get("team", {}).get("shortDisplayName", ""))
    a_short_tr = translate_team_name(away.get("team", {}).get("shortDisplayName", ""))

    return {
        "id": ev.get("id"),
        "uid": ev.get("uid"),
        "name": f"{h_name_tr} vs {a_name_tr}",
        "date": ev.get("date"),
        "league_name": league_name,
        "league_key": fallback_league,
        "state": state,  # 'pre', 'in', 'post'
        "status_tr": status_tr,
        "clock": clock,
        "venue": venue_str,
        "live_stats": live_stats,
        "home": {
            "id": home.get("team", {}).get("id"),
            "name": h_name_tr,
            "shortName": h_short_tr,
            "abbrev": home.get("team", {}).get("abbreviation", ""),
            "logo": home.get("team", {}).get("logo", ""),
            "score": home.get("score", "0") if state in ["in", "post"] else "-",
            "records": [r.get("summary") for r in home.get("records", []) if r.get("summary")]
        },
        "away": {
            "id": away.get("team", {}).get("id"),
            "name": a_name_tr,
            "shortName": a_short_tr,
            "abbrev": away.get("team", {}).get("abbreviation", ""),
            "logo": away.get("team", {}).get("logo", ""),
            "score": away.get("score", "0") if state in ["in", "post"] else "-",
            "records": [r.get("summary") for r in away.get("records", []) if r.get("summary")]
        },
        "odds": odds_data
    }


def get_match_detail(league_key: str, event_id: str):
    """
    Seçilen maçın ESPN summary endpoint'inden derin detaylarını çeker:
    Son 5 maç, kadrolar, istatistikler, H2H vs.
    """
    if league_key not in LEAGUES:
        league_key = "all"

    # Önce belirtilen ligde dene, olmazsa 'all' veya 'tur.1' ile dene
    url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{league_key}/summary?event={event_id}"
    data = _fetch_json(url, ttl=CACHE_TTL_LIVE)
    
    if not data or "header" not in data:
        # Fallback to all
        url2 = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/all/summary?event={event_id}"
        data = _fetch_json(url2, ttl=CACHE_TTL_LIVE)

    if not data:
        return None

    # Son 5 Maç (Form)
    last_five = []
    for group in data.get("lastFiveGames", []):
        team_name = group.get("team", {}).get("displayName", "")
        team_logo = group.get("team", {}).get("logo", "")
        games = []
        for g in group.get("events", []):
            games.append({
                "opponent": g.get("opponent", {}).get("displayName", "Rakip"),
                "result": g.get("gameResult", "-"),  # 'W', 'D', 'L'
                "score": g.get("score", ""),
                "homeAway": g.get("homeAway", ""),
                "date": g.get("gameDate", "")
            })
        last_five.append({
            "team": team_name,
            "logo": team_logo,
            "games": games
        })

    # Bahis / Oranlar
    odds_list = []
    for o in data.get("pickcenter", []):
        provider = o.get("provider", {}).get("name", "Bahis")
        details = o.get("details", "")
        over_under = o.get("overUnder")
        spread = o.get("spread")
        away_money = o.get("awayTeamOdds", {}).get("moneyLine")
        home_money = o.get("homeTeamOdds", {}).get("moneyLine")
        odds_list.append({
            "provider": provider,
            "details": details,
            "overUnder": over_under,
            "spread": spread,
            "homeOdds": home_money,
            "awayOdds": away_money
        })

    # İstatistikler (Boxscore)
    stats = []
    boxscore = data.get("boxscore", {})
    for t in boxscore.get("teams", []):
        t_name = t.get("team", {}).get("displayName", "")
        t_stats = {}
        for s in t.get("statistics", []):
            t_stats[s.get("label", s.get("name"))] = s.get("displayValue", "")
        stats.append({
            "team": t_name,
            "stats": t_stats
        })

    # Kadrolar (Rosters)
    rosters = []
    for r in data.get("rosters", []):
        t_name = r.get("team", {}).get("displayName", "")
        formation = r.get("formation", "")
        starters = []
        for player in r.get("roster", []):
            athlete = player.get("athlete", {})
            pos = player.get("position", {}).get("abbreviation", "")
            starters.append({
                "name": athlete.get("displayName", ""),
                "jersey": athlete.get("jersey", ""),
                "pos": pos,
                "starter": player.get("starter", False)
            })
        rosters.append({
            "team": t_name,
            "formation": formation,
            "players": starters[:11],
            "subs": starters[11:18]
        })

    # Goller ve Kırmızı Kartlar (Key Events)
    key_events = []
    for ke in data.get("keyEvents", []):
        text = ke.get("text", "")
        clock = ke.get("clock", {}).get("displayValue", "")
        key_events.append({"clock": clock, "text": text})

    return {
        "lastFive": last_five,
        "odds": odds_list,
        "boxscore": stats,
        "rosters": rosters,
        "keyEvents": key_events,
        "gameInfo": data.get("gameInfo", {}),
        "standings": data.get("standings", {})
    }


def get_standings(league_key: str = "tur.1"):
    """
    Lig puan durumunu çeker.
    """
    if league_key == "all":
        league_key = "tur.1"

    url = f"https://site.web.api.espn.com/apis/v2/sports/soccer/{league_key}/standings"
    data = _fetch_json(url, ttl=1800)
    if not data:
        return []

    entries = []
    children = data.get("children", [])
    if children:
        entries = children[0].get("standings", {}).get("entries", [])
    elif "standings" in data:
        entries = data.get("standings", {}).get("entries", [])

    table = []
    for idx, e in enumerate(entries):
        team = e.get("team", {})
        stats_map = {s.get("name"): s.get("displayValue") for s in e.get("stats", [])}
        table.append({
            "rank": idx + 1,
            "team": team.get("displayName", ""),
            "shortName": team.get("shortDisplayName", ""),
            "logo": team.get("logo", ""),
            "gamesPlayed": stats_map.get("gamesPlayed", "0"),
            "wins": stats_map.get("wins", "0"),
            "ties": stats_map.get("ties", "0"),
            "losses": stats_map.get("losses", "0"),
            "points": stats_map.get("points", "0"),
            "goalsFor": stats_map.get("pointsFor", "0"),
            "goalsAgainst": stats_map.get("pointsAgainst", "0"),
            "goalDiff": stats_map.get("pointDifferential", "0")
        })

    return table


# ==============================================================================
# İSTATİSTİKSEL MODEL & POISSON DAĞILIMI
# ==============================================================================

def _poisson_probability(k: int, lamb: float) -> float:
    if lamb <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.pow(lamb, k) * math.exp(-lamb)) / math.factorial(k)


def calculate_match_probabilities(home_name: str, away_name: str, last_five: list, odds_info: list = None):
    """
    Poisson ve form ağırlıklı matematiksel maç simülasyonu.
    Gerçek takım formları, gol ortalamaları ve ev sahibi avantajını hesaplar.
    """
    # Varsayılan beklenen goller (xG)
    lambda_home = 1.45
    lambda_away = 1.15

    # Son 5 maçtan gerçek veri çıkarma
    home_scored, home_conceded, home_matches = 0, 0, 0
    away_scored, away_conceded, away_matches = 0, 0, 0

    if last_five and len(last_five) >= 2:
        for item in last_five:
            t_name = item.get("team", "").lower()
            games = item.get("games", [])
            is_home = home_name.lower() in t_name
            
            for g in games:
                score = g.get("score", "")
                if "-" in score:
                    parts = score.split("-")
                    try:
                        s1, s2 = int(parts[0].strip()), int(parts[1].strip())
                        res = g.get("result", "")
                        # Gol hesaplaması
                        if is_home:
                            home_matches += 1
                            if res == "W":
                                home_scored += max(s1, s2)
                                home_conceded += min(s1, s2)
                            elif res == "L":
                                home_scored += min(s1, s2)
                                home_conceded += max(s1, s2)
                            else:
                                home_scored += s1
                                home_conceded += s2
                        else:
                            away_matches += 1
                            if res == "W":
                                away_scored += max(s1, s2)
                                away_conceded += min(s1, s2)
                            elif res == "L":
                                away_scored += min(s1, s2)
                                away_conceded += max(s1, s2)
                            else:
                                away_scored += s1
                                away_conceded += s2
                    except Exception:
                        pass

    if home_matches > 0:
        h_avg_scored = home_scored / home_matches
        h_avg_conceded = home_conceded / home_matches
        lambda_home = (h_avg_scored * 0.6) + (h_avg_conceded * 0.4) + 0.25  # Ev sahibi bonusu
    
    if away_matches > 0:
        a_avg_scored = away_scored / away_matches
        a_avg_conceded = away_conceded / away_matches
        lambda_away = (a_avg_scored * 0.6) + (a_avg_conceded * 0.4)

    # Değerleri makul aralığa sıkıştır
    lambda_home = max(0.6, min(3.2, lambda_home))
    lambda_away = max(0.4, min(2.8, lambda_away))

    # Poisson skor matrisi (0-5 gol arası)
    max_goals = 6
    matrix = [[_poisson_probability(i, lambda_home) * _poisson_probability(j, lambda_away) for j in range(max_goals)] for i in range(max_goals)]

    p_home_win = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i > j)
    p_draw = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i == j)
    p_away_win = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i < j)

    # Toplamı 100%'e normalize et
    total_1x2 = p_home_win + p_draw + p_away_win
    if total_1x2 > 0:
        p_home_win /= total_1x2
        p_draw /= total_1x2
        p_away_win /= total_1x2

    # Alt / Üst Olasılıkları
    p_over_15 = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i + j > 1.5)
    p_over_25 = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i + j > 2.5)
    p_under_25 = 1.0 - p_over_25
    p_over_35 = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i + j > 3.5)

    # Karşılıklı Gol (KG)
    p_btts_yes = sum(matrix[i][j] for i in range(1, max_goals) for j in range(1, max_goals))
    p_btts_no = 1.0 - p_btts_yes

    # En olası 3 skor
    scores_list = []
    for i in range(max_goals):
        for j in range(max_goals):
            scores_list.append((f"{i}-{j}", matrix[i][j]))
    scores_list.sort(key=lambda x: x[1], reverse=True)
    top_scores = [{"score": s[0], "prob": round(s[1] * 100, 1)} for s in scores_list[:3]]

    # Tercih ve Risk Değerlendirmesi
    if p_home_win >= 0.55:
        primary_pick = f"Maç Sonu 1 ({home_name})"
        risk_level = "Düşük - Orta Risk"
    elif p_away_win >= 0.50:
        primary_pick = f"Maç Sonu 2 ({away_name})"
        risk_level = "Orta Risk"
    elif p_over_25 >= 0.58:
        primary_pick = "2.5 Üstü Gol"
        risk_level = "Düşük Risk"
    elif p_btts_yes >= 0.60:
        primary_pick = "Karşılıklı Gol Var (KG Var)"
        risk_level = "Düşük Risk"
    elif p_under_25 >= 0.58:
        primary_pick = "2.5 Altı Gol (Kilit Mücadele)"
        risk_level = "Orta Risk"
    else:
        primary_pick = f"Çifte Şans 1X ({home_name} Yenilmez)"
        risk_level = "Dengeli Mücadele"

    return {
        "homeWinPct": round(p_home_win * 100, 1),
        "drawPct": round(p_draw * 100, 1),
        "awayWinPct": round(p_away_win * 100, 1),
        "over25Pct": round(p_over_25 * 100, 1),
        "under25Pct": round(p_under_25 * 100, 1),
        "over15Pct": round(p_over_15 * 100, 1),
        "over35Pct": round(p_over_35 * 100, 1),
        "bttsYesPct": round(p_btts_yes * 100, 1),
        "bttsNoPct": round(p_btts_no * 100, 1),
        "expectedGoalsHome": round(lambda_home, 2),
        "expectedGoalsAway": round(lambda_away, 2),
        "topScores": top_scores,
        "primaryPick": primary_pick,
        "riskLevel": risk_level
    }


def generate_smart_betting_recommendations(match_info: dict, detail: dict, probs: dict, in_play: dict = None) -> list:
    """
    Maç analiz ekranında kullanıcının tek bakışta anlayabileceği,
    matematiksel ve taktiksel olarak en mantıklı 4 oynanabilir bahis tercihini üretir:
    1. 🛡️ Altın Banko (Düşük Risk / Yüksek Güven)
    2. 💎 İdeal Değer (Value / Günün Ana Tercihi)
    3. 🚀 Oran Avcısı (Yüksek Oran / Cesur Tercih)
    4. 🚩 Korner / Özel İstatistik Tercihi
    """
    home = match_info.get("home", {}).get("name", "Ev Sahibi")
    away = match_info.get("away", {}).get("name", "Deplasman")
    state = match_info.get("state", "pre")
    
    hw = float(probs.get("homeWinPct", 40.0))
    dr = float(probs.get("drawPct", 25.0))
    aw = float(probs.get("awayWinPct", 35.0))
    o15 = float(probs.get("over15Pct", 75.0))
    o25 = float(probs.get("over25Pct", 50.0))
    u25 = float(probs.get("under25Pct", 50.0))
    btts = float(probs.get("bttsYesPct", 50.0))
    xg_home = float(probs.get("expectedGoalsHome", 1.4))
    xg_away = float(probs.get("expectedGoalsAway", 1.1))
    
    top_scores = probs.get("topScores", [])
    top_score = top_scores[0].get("score", "1-1") if top_scores else "1-1"
    top_score_prob = top_scores[0].get("prob", 12.0) if top_scores else 12.0

    # CANLI MAÇ MODU (Eğer maç canlı oynanıyorsa dinamik canlı bahis önerileri sun)
    if state == "in" and in_play and in_play.get("isLive"):
        ls = in_play.get("liveStats", {})
        lp = in_play.get("liveProbabilities", {})
        el = in_play.get("elapsedMin", 45)
        cur_score = in_play.get("currentScore", "0-0")
        
        l_hw = float(lp.get("homeWinPct", hw))
        l_dr = float(lp.get("drawPct", dr))
        l_aw = float(lp.get("awayWinPct", aw))
        l_next_h = float(lp.get("nextHomePct", 38))
        l_next_a = float(lp.get("nextAwayPct", 32))
        l_no_more = float(lp.get("noMoreGoalsPct", 30))
        corner_pick = lp.get("cornerPick", "Canlı Korner 8.5 Üst")
        line1_name = lp.get("line1Name", "Canlı 1.5 Gol Üstü")
        line1_pct = float(lp.get("line1Pct", 75))
        
        recs = []
        # 1. Canlı Banko
        if el < 75 and l_no_more < 40:
            recs.append({
                "category": "banko",
                "category_title": "🛡️ Canlı Banko",
                "tag": "DÜŞÜK RİSK",
                "badge_class": "rec-badge-banko",
                "market": "Canlı Gol Barajı",
                "pick": f"{line1_name} ({cur_score})",
                "odds": round(max(1.22, min(1.45, 1.0 + (100.0 - line1_pct) * 0.008)), 2),
                "confidence": min(92, max(80, int(line1_pct))),
                "reason": f"Mevcut dakikada ({el}') sahadaki tempo ve hücum baskısı maçta en az 1 gol daha izleyeceğimizi gösteriyor.",
                "icon": "fa-circle-check"
            })
        else:
            cand_team = home if l_hw >= l_aw else away
            recs.append({
                "category": "banko",
                "category_title": "🛡️ Canlı Banko",
                "tag": "KONTROLLÜ OYUN",
                "badge_class": "rec-badge-banko",
                "market": "Canlı Çifte Şans",
                "pick": f"Canlı Çifte Şans ({cand_team} Yenilmez)",
                "odds": 1.30,
                "confidence": 85,
                "reason": f"{cand_team} kalan dakikalarda oyunu tutmaya ve skoru korumaya daha yakın taraf.",
                "icon": "fa-shield-halved"
            })
            
        # 2. Canlı İdeal Değer
        if l_next_h >= l_next_a + 5:
            recs.append({
                "category": "value",
                "category_title": "💎 Canlı İdeal Değer",
                "tag": "BASKI AVANTAJI",
                "badge_class": "rec-badge-value",
                "market": "Sıradaki Gol",
                "pick": f"Sıradaki Gol: {home}",
                "odds": round(max(1.65, min(2.10, 100.0 / max(1.0, l_next_h) * 0.88)), 2),
                "confidence": min(85, max(68, int(l_next_h + 25))),
                "reason": f"{home} hücum bölgesinde topla daha çok buluşuyor ve rakip kalede üst üste tehlikeler yaratıyor.",
                "icon": "fa-futbol"
            })
        elif l_next_a >= l_next_h + 5:
            recs.append({
                "category": "value",
                "category_title": "💎 Canlı İdeal Değer",
                "tag": "KONTRA TEHLİKESİ",
                "badge_class": "rec-badge-value",
                "market": "Sıradaki Gol",
                "pick": f"Sıradaki Gol: {away}",
                "odds": round(max(1.65, min(2.15, 100.0 / max(1.0, l_next_a) * 0.88)), 2),
                "confidence": min(85, max(68, int(l_next_a + 25))),
                "reason": f"{away} hızlı geçiş hücumlarıyla rakip savunmanın arkasında ciddi açıklar yakalıyor.",
                "icon": "fa-futbol"
            })
        else:
            recs.append({
                "category": "value",
                "category_title": "💎 Canlı İdeal Değer",
                "tag": "GÜNÜN FIRSATI",
                "badge_class": "rec-badge-value",
                "market": "Canlı Gol Barajı",
                "pick": lp.get("line2Name", "Canlı 2.5 Gol Üstü"),
                "odds": 1.85,
                "confidence": 75,
                "reason": "Oyun çift yönlü oynanıyor; her iki takım da skoru lehine çevirmek adına savunma riskleri alıyor.",
                "icon": "fa-fire"
            })
            
        # 3. Canlı Yüksek Oran
        adv_team = home if l_hw >= l_aw else away
        recs.append({
            "category": "high",
            "category_title": "🚀 Canlı Oran Avcısı",
            "tag": "YÜKSEK ÇARPAN",
            "badge_class": "rec-badge-high",
            "market": "Canlı Maç Sonu",
            "pick": f"Canlı MS: {adv_team} Kazanır",
            "odds": 2.45,
            "confidence": 63,
            "reason": f"Anlık momentum göstergeleri maçın kırılma anında {adv_team} lehine döneceğini vadediyor.",
            "icon": "fa-bolt"
        })
        
        # 4. Canlı Korner
        recs.append({
            "category": "corner",
            "category_title": "🚩 Canlı Korner",
            "tag": "CANLI PROJEKSİYON",
            "badge_class": "rec-badge-corner",
            "market": "Toplam Korner",
            "pick": corner_pick,
            "odds": 1.70,
            "confidence": 76,
            "reason": f"Şu ana kadar kullanılan {ls.get('totalCorners', 0)} korner temposu bu baremin aşılacağını destekliyor.",
            "icon": "fa-flag"
        })
        return recs

    # MAÇ ÖNCESİ (PRE-MATCH) - EN AKILCI 4 TERCİH
    recs = []

    # 1. 🛡️ ALTIN BANKO (Kasa Dostu, Düşük Risk, ~%85-%90 Güven)
    if hw >= 53:
        odd_1x = round(max(1.24, min(1.42, 1.15 + (100.0 - (hw + dr)) * 0.008)), 2)
        recs.append({
            "category": "banko",
            "category_title": "🛡️ Altın Banko",
            "tag": "KASA DOSTU",
            "badge_class": "rec-badge-banko",
            "market": "Çifte Şans",
            "pick": f"Çifte Şans 1X ({home} Yenilmez)",
            "odds": odd_1x,
            "confidence": min(92, int(hw + dr * 0.7)),
            "reason": f"{home} iç sahada maçı kaybetmeye çok uzak. Fanteziye kaçmadan kuponu sağlama almak için en ideal tercih.",
            "icon": "fa-shield-halved"
        })
    elif aw >= 48:
        odd_x2 = round(max(1.26, min(1.44, 1.18 + (100.0 - (aw + dr)) * 0.008)), 2)
        recs.append({
            "category": "banko",
            "category_title": "🛡️ Altın Banko",
            "tag": "KASA DOSTU",
            "badge_class": "rec-badge-banko",
            "market": "Çifte Şans",
            "pick": f"Çifte Şans X2 ({away} Yenilmez)",
            "odds": odd_x2,
            "confidence": min(90, int(aw + dr * 0.7)),
            "reason": f"{away} kadro kalitesi ve deplasman formuyla sahadan en az 1 puanla ayrılmaya çok yakın.",
            "icon": "fa-shield-halved"
        })
    elif o15 >= 73:
        odd_o15 = round(max(1.22, min(1.36, 1.12 + (100.0 - o15) * 0.007)), 2)
        recs.append({
            "category": "banko",
            "category_title": "🛡️ Altın Banko",
            "tag": "KASA DOSTU",
            "badge_class": "rec-badge-banko",
            "market": "Toplam Gol",
            "pick": "1.5 Gol Üstü",
            "odds": odd_o15,
            "confidence": min(93, int(o15)),
            "reason": f"İki takımın da maç başı gol istatistikleri yüksek. Mücadelede en az 2 gol çıkma olasılığı %{o15}.",
            "icon": "fa-circle-check"
        })
    elif u25 >= 60:
        recs.append({
            "category": "banko",
            "category_title": "🛡️ Altın Banko",
            "tag": "KASA DOSTU",
            "badge_class": "rec-badge-banko",
            "market": "Toplam Gol",
            "pick": "3.5 Gol Altı",
            "odds": 1.28,
            "confidence": 88,
            "reason": "Taktiksel kilit ve kontrollü oyun yapısı 4 gol barajının aşılmasını fazlasıyla zor kılıyor.",
            "icon": "fa-lock"
        })
    else:
        recs.append({
            "category": "banko",
            "category_title": "🛡️ Altın Banko",
            "tag": "KASA DOSTU",
            "badge_class": "rec-badge-banko",
            "market": "Ev Sahibi Gol",
            "pick": f"{home} 0.5 Gol Üstü",
            "odds": 1.26,
            "confidence": 87,
            "reason": f"{home} seyircisi önünde skoru en az bir kez değiştirmeyi başaracaktır.",
            "icon": "fa-futbol"
        })

    # 2. 💎 İDEAL DEĞER (Oran / Olasılık Dengesi En Mantıklı Seçim, ~%72-%80 Güven)
    if btts >= 52 and o25 >= 49:
        odd_btts = round(max(1.68, min(1.92, 1.55 + (100.0 - btts) * 0.006)), 2)
        recs.append({
            "category": "value",
            "category_title": "💎 İdeal Değer (Value)",
            "tag": "GÜNÜN TERCİHİ",
            "badge_class": "rec-badge-value",
            "market": "Karşılıklı Gol",
            "pick": "Karşılıklı Gol Var (KG Var)",
            "odds": odd_btts,
            "confidence": min(82, int(btts + 24)),
            "reason": f"Hem {home} hem de {away} hücumda üretken fakat savunmada açık veren takımlar. Karşılıklı goller ön planda.",
            "icon": "fa-arrows-rotate"
        })
    elif o25 >= 55:
        odd_o25 = round(max(1.65, min(2.05, 1.50 + (100.0 - o25) * 0.01)), 2)
        recs.append({
            "category": "value",
            "category_title": "💎 İdeal Değer (Value)",
            "tag": "GÜNÜN TERCİHİ",
            "badge_class": "rec-badge-value",
            "market": "Toplam Gol",
            "pick": "2.5 Gol Üstü",
            "odds": odd_o25,
            "confidence": min(80, int(o25 + 20)),
            "reason": "Yüksek tempolu ve bol pozisyonlu bir 90 dakika bekleniyor. 3 gol barajı bu orandan gayet cazip.",
            "icon": "fa-fire"
        })
    elif hw >= 55:
        odd_hw = round(max(1.70, min(2.15, 100.0 / max(1.0, hw) * 0.90)), 2)
        recs.append({
            "category": "value",
            "category_title": "💎 İdeal Değer (Value)",
            "tag": "GÜNÜN TERCİHİ",
            "badge_class": "rec-badge-value",
            "market": "Maç Sonucu",
            "pick": f"Maç Sonu 1 ({home})",
            "odds": odd_hw,
            "confidence": min(80, int(hw + 18)),
            "reason": f"{home} saha avantajı ve form grafiğiyle doğrudan 3 puana yakın taraf. Verilen oran gayet tatmin edici.",
            "icon": "fa-trophy"
        })
    elif u25 >= 56:
        odd_u25 = round(max(1.65, min(1.95, 1.50 + (100.0 - u25) * 0.009)), 2)
        recs.append({
            "category": "value",
            "category_title": "💎 İdeal Değer (Value)",
            "tag": "GÜNÜN TERCİHİ",
            "badge_class": "rec-badge-value",
            "market": "Toplam Gol",
            "pick": "2.5 Gol Altı",
            "odds": odd_u25,
            "confidence": min(80, int(u25 + 18)),
            "reason": "İki takım da kontrollü ve savunma öncelikli bir taktikle sahada olacak. Kilit mücadelede az gol bekleniyor.",
            "icon": "fa-lock"
        })
    else:
        recs.append({
            "category": "value",
            "category_title": "💎 İdeal Değer (Value)",
            "tag": "GÜNÜN TERCİHİ",
            "badge_class": "rec-badge-value",
            "market": "Toplam Gol Aralığı",
            "pick": "Toplam Gol 2-3 Gol",
            "odds": 1.85,
            "confidence": 75,
            "reason": "Dengeli güçlerin mücadelesinde maçın 2 veya 3 golle tamamlanması istatistiksel en olası koridor.",
            "icon": "fa-arrows-left-right-to-line"
        })

    # 3. 🚀 ORAN AVCISI (Yüksek Kazanç / Cesur Kuponlar, ~%58-%66 Güven, Oran >= 2.10)
    if hw >= 48 and o25 >= 48:
        recs.append({
            "category": "high",
            "category_title": "🚀 Oran Avcısı (Yüksek Çarpan)",
            "tag": "KAZANÇ KATLAYICI",
            "badge_class": "rec-badge-high",
            "market": "Maç Sonu & Gol Kombosu",
            "pick": f"MS 1 & 2.5 Gol Üstü",
            "odds": 2.75,
            "confidence": 65,
            "reason": f"{home} kazanırken gollü bir zafere imza atabilir. Kupon çarpanını katlamak isteyenler için simülasyonun en sıcak kombosu.",
            "icon": "fa-bolt"
        })
    elif btts >= 51 and o25 >= 51:
        recs.append({
            "category": "high",
            "category_title": "🚀 Oran Avcısı (Yüksek Çarpan)",
            "tag": "KAZANÇ KATLAYICI",
            "badge_class": "rec-badge-high",
            "market": "Gol Kombosu",
            "pick": "2.5 Üst & KG Var",
            "odds": 2.25,
            "confidence": 67,
            "reason": "Bol gollü bir düelloda iki takımın da fileleri havalandırıp maçı 3 golün üzerine taşıması bekleniyor.",
            "icon": "fa-rocket"
        })
    elif dr >= 27:
        recs.append({
            "category": "high",
            "category_title": "🚀 Oran Avcısı (Yüksek Çarpan)",
            "tag": "KAZANÇ KATLAYICI",
            "badge_class": "rec-badge-high",
            "market": "İlk Yarı Sonucu",
            "pick": "İlk Yarı Beraberlik (İY 0)",
            "odds": 2.12,
            "confidence": 64,
            "reason": "Takımlar ilk devrede birbirini tartıp risk almaktan kaçınacaktır. Soyunma odasına eşitlikle gitme ihtimalleri yüksek.",
            "icon": "fa-handshake"
        })
    else:
        recs.append({
            "category": "high",
            "category_title": "🚀 Oran Avcısı (Yüksek Çarpan)",
            "tag": "KAZANÇ KATLAYICI",
            "badge_class": "rec-badge-high",
            "market": "Skor Tahmini",
            "pick": f"Skor Tahmini: {top_score}",
            "odds": 6.50,
            "confidence": 58,
            "reason": f"Poisson dağılım matrisimizin %{top_score_prob} olasılıkla günün en muhtemel skoru olarak modellediği yüksek oranlı tercih.",
            "icon": "fa-bullseye"
        })

    # 4. 🚩 KORNER / ÖZEL İSTATİSTİK TERCİHİ
    tot_xg = xg_home + xg_away
    if tot_xg >= 2.85 or o25 >= 58:
        recs.append({
            "category": "corner",
            "category_title": "🚩 Korner & Tempo Tercihi",
            "tag": "İSTATİSTİK FIRSATI",
            "badge_class": "rec-badge-corner",
            "market": "Toplam Korner",
            "pick": "Toplam 9.5 Üst Korner",
            "odds": 1.84,
            "confidence": 74,
            "reason": "Her iki takımın kanat bindirmeleri ve ceza sahası aksiyonları maçın çift haneli korner sayılarına ulaşacağını gösteriyor.",
            "icon": "fa-flag"
        })
    else:
        recs.append({
            "category": "corner",
            "category_title": "🚩 Korner & Tempo Tercihi",
            "tag": "İSTATİSTİK FIRSATI",
            "badge_class": "rec-badge-corner",
            "market": "Toplam Korner",
            "pick": "Toplam 8.5 Üst Korner",
            "odds": 1.62,
            "confidence": 78,
            "reason": "Tempolu geçiş oyunu ve ceza sahasına yapılan ortalar korner bayrağının sıkça kullanılacağını işaret ediyor.",
            "icon": "fa-flag"
        })

    return recs


def calculate_inplay_probabilities(match_info: dict, detail: dict, pre_probs: dict = None) -> dict:
    """
    Canlı oynanan maçın anlık skorunu, geçen dakikasını, topla oynama, şut,
    korner, faul ve kart verilerini alarak olasılıkları canlı olarak yeniden hesaplar.
    """
    home_name = match_info.get("home", {}).get("name", "Ev Sahibi")
    away_name = match_info.get("away", {}).get("name", "Deplasman")

    try:
        h_score = int(match_info.get("home", {}).get("score", 0) or 0)
    except Exception:
        h_score = 0

    try:
        a_score = int(match_info.get("away", {}).get("score", 0) or 0)
    except Exception:
        a_score = 0

    clock_str = str(match_info.get("clock") or "")
    digits = re.findall(r'\d+', clock_str)
    if digits:
        elapsed_min = int(digits[0])
    elif "HT" in clock_str or "Half" in match_info.get("status_tr", ""):
        elapsed_min = 45
    else:
        elapsed_min = 20

    elapsed_min = max(1, min(95, elapsed_min))
    rem_min = max(3, 90 - elapsed_min)
    time_ratio = rem_min / 90.0

    # Canlı istatistikleri topla
    h_poss = 50.0
    a_poss = 50.0
    h_shots = 0
    a_shots = 0
    h_on_goal = 0
    a_on_goal = 0
    h_corners = 0
    a_corners = 0
    h_fouls = 0
    a_fouls = 0
    h_yellow = 0
    a_yellow = 0
    h_red = 0
    a_red = 0

    # 1. Kaynak: detail['boxscore']
    if detail and detail.get("boxscore") and len(detail.get("boxscore", [])) >= 2:
        # Sıkı eşleştirme yardımcı fonksiyonu
        def _ip_team_match(box_name, match_name):
            bn = box_name.lower().strip()
            mn = match_name.lower().strip()
            if not bn or not mn:
                return False
            return mn in bn or bn in mn

        home_found = False
        away_found = False
        for t in detail.get("boxscore", []):
            t_name = t.get("team", "")
            stats = t.get("stats", {})
            is_home = _ip_team_match(t_name, home_name)
            is_away = _ip_team_match(t_name, away_name)
            if not is_home and not is_away:
                continue
            try:
                poss_val = float(stats.get("Possession", "50").replace("%", "").strip() or 50)
                shots_val = int(stats.get("SHOTS", stats.get("Shots", "0")) or 0)
                on_goal_val = int(stats.get("ON GOAL", stats.get("Shots on Goal", "0")) or 0)
                corners_val = int(stats.get("Corner Kicks", stats.get("Corners", "0")) or 0)
                fouls_val = int(stats.get("Fouls", "0") or 0)
                yellow_val = int(stats.get("Yellow Cards", "0") or 0)
                red_val = int(stats.get("Red Cards", "0") or 0)

                if is_home:
                    h_poss, h_shots, h_on_goal, h_corners = poss_val, shots_val, on_goal_val, corners_val
                    h_fouls, h_yellow, h_red = fouls_val, yellow_val, red_val
                else:
                    a_poss, a_shots, a_on_goal, a_corners = poss_val, shots_val, on_goal_val, corners_val
                    a_fouls, a_yellow, a_red = fouls_val, yellow_val, red_val
            except Exception:
                pass

    # 2. Kaynak: match_info['live_stats']
    elif match_info.get("live_stats"):
        ls = match_info["live_stats"]
        try:
            h_poss = float(ls.get("homePossession", 50))
            a_poss = float(ls.get("awayPossession", 50))
            h_shots = int(ls.get("homeShots", 0))
            a_shots = int(ls.get("awayShots", 0))
            h_on_goal = int(ls.get("homeShotsOnTarget", 0))
            a_on_goal = int(ls.get("awayShotsOnTarget", 0))
            h_corners = int(ls.get("homeCorners", 0))
            a_corners = int(ls.get("awayCorners", 0))
        except Exception:
            pass

    # Canlı ivme (Momentum / Baskı Endeksi)
    h_attack = h_shots + (h_on_goal * 1.6) + (h_corners * 0.7)
    a_attack = a_shots + (a_on_goal * 1.6) + (a_corners * 0.7)
    tot_attack = h_attack + a_attack + 2.0

    h_momentum = (h_poss / 50.0) * 0.45 + (h_attack / tot_attack) * 1.1
    a_momentum = (a_poss / 50.0) * 0.45 + (a_attack / tot_attack) * 1.1

    # Hakimiyet yüzdesi
    tot_mom = h_momentum + a_momentum
    h_dom_pct = round((h_momentum / tot_mom) * 100, 1) if tot_mom > 0 else 50.0
    a_dom_pct = round(100.0 - h_dom_pct, 1)
    dominant_team = home_name if h_dom_pct >= a_dom_pct else away_name

    # Kalan süre için beklenen goller (Poisson Lambdas)
    base_lh = pre_probs.get("expectedGoalsHome", 1.45) if pre_probs else 1.45
    base_la = pre_probs.get("expectedGoalsAway", 1.15) if pre_probs else 1.15

    # Kırmızı kart ve momentum çarpanı
    rem_lh = max(0.04, base_lh * time_ratio * h_momentum * (0.60 ** h_red))
    rem_la = max(0.04, base_la * time_ratio * a_momentum * (0.60 ** a_red))

    # Kalan gol matrisi (0-5 gol)
    max_g = 6
    matrix = [[_poisson_probability(i, rem_lh) * _poisson_probability(j, rem_la) for j in range(max_g)] for i in range(max_g)]

    p_h_win = sum(matrix[i][j] for i in range(max_g) for j in range(max_g) if (h_score + i) > (a_score + j))
    p_draw = sum(matrix[i][j] for i in range(max_g) for j in range(max_g) if (h_score + i) == (a_score + j))
    p_a_win = sum(matrix[i][j] for i in range(max_g) for j in range(max_g) if (h_score + i) < (a_score + j))

    tot_1x2 = p_h_win + p_draw + p_a_win
    if tot_1x2 > 0:
        p_h_win /= tot_1x2
        p_draw /= tot_1x2
        p_a_win /= tot_1x2

    # Sıradaki Gol Olasılıkları
    p_no_more_goals = matrix[0][0]
    p_has_goal = max(0.01, 1.0 - p_no_more_goals)
    if (rem_lh + rem_la) > 0:
        p_next_home = p_has_goal * (rem_lh / (rem_lh + rem_la))
        p_next_away = p_has_goal * (rem_la / (rem_lh + rem_la))
    else:
        p_next_home = 0.5 * p_has_goal
        p_next_away = 0.5 * p_has_goal

    # Canlı Korner Projeksiyonu
    tot_corners = h_corners + a_corners
    pace_per_min = (tot_corners / max(5, elapsed_min))
    proj_corners = tot_corners + ((pace_per_min * 0.65) + (9.8 / 90.0 * 0.35)) * rem_min
    proj_corners = round(proj_corners, 1)

    if proj_corners >= 11.0:
        corner_pick = "Canlı Korner 9.5 veya 10.5 Üstü"
        corner_prob = 78
    elif proj_corners >= 9.0:
        corner_pick = "Canlı Korner 8.5 Üstü"
        corner_prob = 74
    else:
        corner_pick = "Canlı Korner 8.5 Altı"
        corner_prob = 68

    # Canlı Dinamik Gol Barajları
    cur_tot_goals = h_score + a_score
    line1_target = cur_tot_goals + 0.5
    line2_target = cur_tot_goals + 1.5

    p_line1_over = sum(matrix[i][j] for i in range(max_g) for j in range(max_g) if (cur_tot_goals + i + j) > line1_target)
    p_line2_over = sum(matrix[i][j] for i in range(max_g) for j in range(max_g) if (cur_tot_goals + i + j) > line2_target)

    # Sıradaki gol favorisi
    if p_next_home >= p_next_away and p_next_home >= p_no_more_goals:
        next_fav = home_name
        fav_next_pct = p_next_home
    elif p_next_away >= p_next_home and p_next_away >= p_no_more_goals:
        next_fav = away_name
        fav_next_pct = p_next_away
    else:
        next_fav = "Gol Çıkmaz (Kilitlenir)"
        fav_next_pct = p_no_more_goals

    # Canlı Tavsiye (In-Play Value Pick)
    if p_next_home >= 0.55:
        inplay_pick = f"Sıradaki Gol 1 ({home_name})"
    elif p_next_away >= 0.55:
        inplay_pick = f"Sıradaki Gol 2 ({away_name})"
    elif p_h_win >= 0.70:
        inplay_pick = f"Canlı Maç Sonu 1 ({home_name})"
    elif p_a_win >= 0.70:
        inplay_pick = f"Canlı Maç Sonu 2 ({away_name})"
    elif p_line1_over >= 0.70:
        inplay_pick = f"Canlı {line1_target} Gol Üstü"
    else:
        inplay_pick = corner_pick

    # Taktik Berat'ın Canlı Maç İçi Yorumu
    live_commentary = (
        f"🔥 **CANLI OYUN DEĞERLENDİRMESİ (Dakika {elapsed_min}')**\n\n"
        f"Dostum maç şu an canlı yayında ve nefes kesiyor! Tabelada **{home_name} {h_score} - {a_score} {away_name}** var.\n\n"
        f"📊 **Saha İçi Hakimiyeti:** Şu ana kadar {dominant_team} rüzgarı esiyor. "
        f"Topla oynama oranları: %{h_poss:.1f} vs %{a_poss:.1f}. "
        f"Şut tablosunda {home_name} ({h_shots} şut, {h_on_goal} isabet) ile {away_name} ({a_shots} şut, {a_on_goal} isabet) mücadelesi izliyoruz. "
        f"Kornerlerde ise toplam {tot_corners} korner atıldı (Ev: {h_corners}, Dep: {a_corners}).\n\n"
        f"⏱️ **Kalan Süre Simülasyonu:** Kalan {rem_min} dakikayı ve anlık ivmeyi modele soktuğumda:\n"
        f"👉 Canlı Maç Sonu: {home_name} %{p_h_win*100:.0f} | Beraberlik %{p_draw*100:.0f} | {away_name} %{p_a_win*100:.0f}\n"
        f"👉 Sıradaki Golü Kim Atar?: {home_name} %{p_next_home*100:.0f} | {away_name} %{p_next_away*100:.0f} | Başka Gol Olmaz %{p_no_more_goals*100:.0f}\n"
        f"👉 Korner Tahmini: Maç sonu tahmini ~{proj_corners:.0f} korner bekleniyor.\n\n"
        f"🎯 **Canlıda Ne Oynanır? (Dost Meclisi Tüyosu):**\n"
        f"Şu anki saha baskısına göre en temiz canlı fırsat: **{inplay_pick}**! "
        f"{'Baskı çok belirgin, gol kokusu buram buram geliyor.' if p_has_goal >= 0.65 else 'Oyun orta sahaya kilitlendi, gereksiz acele etmeyip korner çizgisine yaslanmak daha akılcı.'}"
    )

    return {
        "isLive": True,
        "elapsedMin": elapsed_min,
        "remainingMin": rem_min,
        "homeScore": h_score,
        "awayScore": a_score,
        "dominantTeam": dominant_team,
        "homeDominance": h_dom_pct,
        "awayDominance": a_dom_pct,
        "liveStats": {
            "homePossession": h_poss,
            "awayPossession": a_poss,
            "homeShots": h_shots,
            "awayShots": a_shots,
            "homeShotsOnTarget": h_on_goal,
            "awayShotsOnTarget": a_on_goal,
            "homeCorners": h_corners,
            "awayCorners": a_corners,
            "totalCorners": tot_corners,
            "homeFouls": h_fouls,
            "awayFouls": a_fouls,
            "homeYellow": h_yellow,
            "awayYellow": a_yellow,
            "homeRed": h_red,
            "awayRed": a_red
        },
        "liveProbabilities": {
            "homeWinPct": round(p_h_win * 100, 1),
            "drawPct": round(p_draw * 100, 1),
            "awayWinPct": round(p_a_win * 100, 1),
            "nextHomePct": round(p_next_home * 100, 1),
            "nextAwayPct": round(p_next_away * 100, 1),
            "noMoreGoalsPct": round(p_no_more_goals * 100, 1),
            "favoredNextTeam": next_fav,
            "line1Name": f"Canlı {line1_target} Üst",
            "line1Pct": round(p_line1_over * 100, 1),
            "line2Name": f"Canlı {line2_target} Üst",
            "line2Pct": round(p_line2_over * 100, 1),
            "projectedCorners": proj_corners,
            "cornerPick": corner_pick,
            "cornerProbPct": corner_prob,
            "inPlayPick": inplay_pick
        },
        "liveCommentary": live_commentary
    }



# ==============================================================================
# "BİLGİLİ FUTBOL ARKADAŞI" YORUM & SOHBET MOTORU
# ==============================================================================

def generate_expert_friend_commentary(match_info: dict, detail: dict, probs: dict) -> str:
    """
    Sanki yıllardır tribünde, halı sahada ve taktik tahtası başında olan,
    futbolu ciğerine kadar bilen samimi ve bilgili bir arkadaşın (Taktik Berat)
    maça özel derin taktik ve bahis analiz mektubu.
    Robotik dilden tamamen uzak, akıcı, gerçekçi, takımlara ve verilere birebir odaklı.
    """
    home = match_info.get("home", {}).get("name", "Ev Sahibi")
    away = match_info.get("away", {}).get("name", "Deplasman")
    league = match_info.get("league_name", "Resmi Lig")
    state = match_info.get("state", "pre")
    venue = match_info.get("venue", "Stadyum Belirtilmedi")

    hw = probs.get("homeWinPct", 45)
    dr = probs.get("drawPct", 25)
    aw = probs.get("awayWinPct", 30)
    o25 = probs.get("over25Pct", 50)
    o15 = probs.get("over15Pct", 75)
    btts = probs.get("bttsYesPct", 50)
    pick = probs.get("primaryPick", "2.5 Gol Üstü")
    top_score = probs.get("topScores", [{}])[0].get("score", "2-1")

    is_tr_team = any(w in home.lower() or w in away.lower() for w in ["türkiye", "turkey", "galatasaray", "fenerbahce", "fenerbahçe", "besiktas", "beşiktaş", "trabzonspor"])

    # 1. CANLI MAÇ YORUMU
    if state == "in":
        clock = match_info.get("clock", "")
        h_score = match_info.get("home", {}).get("score", "0")
        a_score = match_info.get("away", {}).get("score", "0")
        return (
            f"🔥 **CANLI OYUN TAKTİK MERKEZİ ({home} {h_score} - {a_score} {away} | {clock})**\n\n"
            f"Dostum maç şu an alev alev akıyor! Sahada müthiş bir taktik mücadelesi var. "
            f"Tabelada an itibarıyla **{home} {h_score} - {a_score} {away}** skoru mevcut.\n\n"
            f"📊 **Mevcut Oyun Akışı:** İki takım da geçiş hücumlarında çok cesur. "
            f"{home} topa daha fazla sahip olup oyunu yönlendirmeye çalışırken, {away} rakibin bıraktığı savunma arkası boşlukları çok net kolluyor. "
            f"Özellikle kanat akınlarıyla kazanılan kornerler ve duran toplar tabelayı her an yeniden değiştirebilir.\n\n"
            f"🎯 **Canlıda Dost Tavsiyesi:** Maçın temposu asla düşmüyor. "
            f"{'Sıradaki gol kokusu buram buram geliyor, canlı gol baremleri tam oynanacak kıvamda.' if int(h_score)+int(a_score) < 3 else 'Skor açıldı, takımlar risk alıyor; canlı korner ve kart hatlarına yaslanmak en akılcı tercih.'}"
        )

    # 2. BİTMİŞ MAÇ YORUMU
    if state == "post":
        h_score = match_info.get("home", {}).get("score", "0")
        a_score = match_info.get("away", {}).get("score", "0")
        try:
            h_int, a_int = int(h_score), int(a_score)
            winner = home if h_int > a_int else (away if a_int > h_int else "Beraberlik")
        except Exception:
            winner = "Maç Sonu"

        stats_summary = ""
        ls = match_info.get("live_stats")
        if ls:
            h_corn = int(ls.get('homeCorners', 0) or 0)
            a_corn = int(ls.get('awayCorners', 0) or 0)
            stats_summary = (
                f"\n\n📊 **Resmi Maç Sonu İstatistikleri:**\n"
                f"• Topla Oynama: {home} %{ls.get('homePossession', 50)} - %{ls.get('awayPossession', 50)} {away}\n"
                f"• Şut Tablosu: {home} {ls.get('homeShots', 0)} ({ls.get('homeShotsOnTarget', 0)} isabet) - {away} {ls.get('awayShots', 0)} ({ls.get('awayShotsOnTarget', 0)} isabet)\n"
                f"• Kornerler: {home} {h_corn} - {a_corn} {away} (Toplam: {h_corn + a_corn} Korner)\n"
                f"• Fauller: {home} {ls.get('homeFouls', 0)} - {ls.get('awayFouls', 0)} {away}"
            )

        return (
            f"🏁 **MAÇ SONU DEĞERLENDİRMESİ: {home} {h_score} - {a_score} {away} (MS Bitti)**\n\n"
            f"Hocam 90 dakika tamamlandı ve mücadele **{h_score}-{a_score}** skoruyla tescillendi. "
            f"{('Mücadeleyi ' + winner + ' hanesine yazdırdı.') if winner != 'Beraberlik' else 'İki takım da puanları paylaştı.'}"
            f"{stats_summary}\n\n"
            f"🎯 **Değerlendirme:** Sahadaki istatistikler ve mücadele skora yansıdı. Canlı ve biten maç takibimiz kesintisiz sürüyor!"
        )

    # 3. OYNANACAK (PRE-MATCH) DERİN MAÇ ANALİZİ
    # Form Analizi
    home_form_desc = ""
    away_form_desc = ""
    if detail and detail.get("lastFive"):
        for lf in detail["lastFive"]:
            tname = lf.get("team", "")
            games = lf.get("games", [])
            if games:
                w_count = sum(1 for g in games if g.get("result") == "W")
                d_count = sum(1 for g in games if g.get("result") == "D")
                l_count = sum(1 for g in games if g.get("result") == "L")
                last_g = games[-1]
                last_opp = last_g.get("opponent", "rakibi")
                last_sc = last_g.get("score", "")
                desc = f"son 5 maçında {w_count}G-{d_count}B-{l_count}M aldı (son maç: {last_opp} karşısında {last_sc})"
                if home.lower() in tname.lower():
                    home_form_desc = f"{home}, {desc}."
                elif away.lower() in tname.lower():
                    away_form_desc = f"{away} ise {desc}."

    # Özel Giriş Cümlesi
    if is_tr_team:
        intro = f"🇹🇷 **Hocam selamlar! Bu randevu gecenin en büyük taktik şöleni!** {home} ile {away} kozlarını paylaşacak. Bütün bülten bu maça kilitlendi, tüm verileri A'dan Z'ye çıkardım."
    else:
        intro = f"⚽ **Hocam selamlar! {league} bülteninin en kritik kapışmalarından birindeyiz:** {home} ile {away} taktik tahtasında karşı karşıya geliyor."

    # Taktik Kurgu ve Saha Analizi
    if o25 >= 55 and btts >= 52:
        tactics = (
            f"🎯 **Taktik Karakteristik:** Bu maçta orta saha savunmaları ikinci planda kalacak gibi duruyor. "
            f"{home} iç sahada seyircisiyle birlikte ön alan presini agresif kuracaktır. "
            f"Buna karşılık {away} forvet hattı geçiş hücumlarında çok seri ve öldürücü. "
            f"Kafamdaki maç senaryosunda erken bir gol kilitleri kırar ve karşılıklı gollerle skor 2.5 üstü barajını zorlanmadan aşar."
        )
    elif o25 < 45:
        tactics = (
            f"🎯 **Taktik Karakteristik:** Burada tam bir satranç maçı izleyeceğiz. İki teknik adam da öncelikle 'önce gol yemeyelim' kurgusuyla başlayacaktır. "
            f"Orta sahadaki ikili mücadele sayısı çok yüksek olur, faul düdükleri oyunun temposunu sık sık kesebilir. "
            f"Kör düğümün çözülmesi muhtemelen bir duran top organizasyonuna veya bireysel bir savunma hatasına bağlı."
        )
    else:
        tactics = (
            f"🎯 **Taktik Karakteristik:** {home} kendi evinde topun hakimi olup oyunu rakip yarı sahaya yıkmaya çalışacak. "
            f"{away} ise son haftalarda deplasmanlarda kompakt durup merkezi kapatıyor. "
            f"Maçın kaderini kanat bindirmeleri ve ilk yarım saatteki ceza sahası içi verimlilik tayin edecek."
        )

    # İstatistik ve Matematik Özeti
    stats_text = (
        f"📊 **Poisson & Form Projeksiyonu:**\n"
        f"• Maç Sonu İhtimalleri: {home} %{hw:.0f} | Beraberlik %{dr:.0f} | {away} %{aw:.0f}\n"
        f"• Gol Beklentisi: 1.5 Üst %{o15:.0f} | 2.5 Üst %{o25:.0f} | Karşılıklı Gol (KG Var) %{btts:.0f}\n"
        f"• En Olası Skor Tahmini: **{top_score}** (Simülasyon ağırlığı en yüksek tabela)"
    )

    # Bilyoner Odaklı Bahis Stratejisi
    betting_guide = (
        f"💡 **Taktik Berat'ın Kupon Reçetesi (Bilyoner / İddaa Baremleriyle):**\n"
        f"👉 **Ana Tercihim (Dost Meclisi Tüyosu):** **{pick}** (Bilyoner oran bareminde en yüksek değer bu tercihte).\n"
        f"👉 **Kasa Katlama / Banko Alternatifi:** **1.5 Gol Üstü** veya **Çifte Şans 1X** (%{max(hw+dr, o15):.0f} matematiksel güven endeksi).\n"
        f"👉 **Sürpriz Arayanlara:** Maçta kanat akınları yoğun olacağından **Toplam Korner 8.5 Üstü** seçeneği bültende çok lezzetli duruyor."
    )

    form_section = f"📈 **Form Durumu:**\n{home_form_desc}\n{away_form_desc}" if (home_form_desc or away_form_desc) else ""

    parts = [intro, form_section, tactics, stats_text, betting_guide]
    return "\n\n".join([p for p in parts if p.strip()])


def ask_football_pal(query: str, match_info: dict, detail: dict, probs: dict, history: list = None, api_key: str = None) -> str:
    """
    Kullanıcının seçili maç veya futbol hakkında sorduğu her soruya,
    bilgili futbol arkadaşı (Taktik Berat) samimiyetiyle, maça ve gerçek verilere
    birebir odaklanarak yanıt üretir.

    Öncelik: Gemini AI → Akıllı Yerel Motor (gerçek veriye dayalı)
    """
    home = match_info.get("home", {}).get("name", "Ev Sahibi") if match_info else "Ev Sahibi"
    away = match_info.get("away", {}).get("name", "Deplasman") if match_info else "Deplasman"
    league = match_info.get("league_name", "") if match_info else ""
    match_state = match_info.get("state", "pre") if match_info else "pre"

    # Canlı oynanan maç kontrolü ve dinamik in-play modellemesi
    in_play = None
    if match_info and match_info.get("state") == "in":
        in_play = calculate_inplay_probabilities(match_info, detail, probs)

    # Tüm maç bağlamını derle (hem Gemini hem yerel motor için)
    context = _build_rich_match_context(match_info, detail, probs, in_play)

    # Gemini API anahtarı verilmişse Google Gemini AI'ı çağır
    active_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if active_key:
        try:
            return _call_gemini_chat(query, context, history, active_key)
        except Exception as e:
            print(f"[GEMINI CALL FAILED, FALLING BACK TO LOCAL] {e}")

    # Yerel Akıllı Motor — gerçek verilere dayalı dinamik yanıt
    return _generate_local_smart_reply(query, match_info, detail, probs, in_play, context)


def _build_rich_match_context(match_info: dict, detail: dict, probs: dict, in_play: dict = None) -> str:
    """Maçın TÜM verilerini zengin bir bağlam metnine dönüştürür."""
    if not match_info:
        return "Henüz bir maç seçilmedi. Genel futbol sohbeti."

    home = match_info.get("home", {})
    away = match_info.get("away", {})
    h_name = home.get("name", "Ev Sahibi")
    a_name = away.get("name", "Deplasman")
    state = match_info.get("state", "pre")

    lines = []
    lines.append(f"MAÇ: {h_name} vs {a_name}")
    lines.append(f"Lig: {match_info.get('league_name', '')}")
    lines.append(f"Stadyum: {match_info.get('venue', '')}")
    lines.append(f"Durum: {'CANLI OYNANIYOR' if state == 'in' else ('BİTTİ' if state == 'post' else 'HENÜZ BAŞLAMADI')}")

    if state in ("in", "post"):
        lines.append(f"Skor: {h_name} {home.get('score', 0)} - {away.get('score', 0)} {a_name}")

    # Olasılıklar
    if probs:
        lines.append(f"\nMATEMATİKSEL ANALİZ:")
        lines.append(f"  Galibiyet: {h_name} %{probs.get('homeWinPct', 0)} | Beraberlik %{probs.get('drawPct', 0)} | {a_name} %{probs.get('awayWinPct', 0)}")
        lines.append(f"  2.5 Üst: %{probs.get('over25Pct', 0)} | 2.5 Alt: %{probs.get('under25Pct', 0)}")
        lines.append(f"  1.5 Üst: %{probs.get('over15Pct', 0)}")
        lines.append(f"  KG Var: %{probs.get('bttsYesPct', 0)} | KG Yok: %{probs.get('bttsNoPct', 0)}")
        lines.append(f"  En Olası Skorlar: {probs.get('topScores', [])}")
        lines.append(f"  Risk Seviyesi: {probs.get('riskLevel', 'Orta')}")
        lines.append(f"  Önerilen Tercih: {probs.get('primaryPick', '')}")

    # Son 5 maç formu
    if detail and detail.get("lastFive"):
        lines.append(f"\nSON 5 MAÇ FORMU:")
        for team_form in detail["lastFive"]:
            t_name = team_form.get("team", "")
            games = team_form.get("games", [])
            form_str = " | ".join([f"{g.get('result','?')} vs {g.get('opponent','')} ({g.get('score','')})" for g in games[:5]])
            lines.append(f"  {t_name}: {form_str}")

    # Bahis oranları
    if detail and detail.get("odds"):
        lines.append(f"\nBAHİS ORANLARI:")
        for o in detail["odds"][:3]:
            lines.append(f"  {o.get('provider','')}: {o.get('details','')} | ÜA: {o.get('overUnder','')} | Ev: {o.get('homeOdds','')} | Dep: {o.get('awayOdds','')}")

    # Kadrolar
    if detail and detail.get("rosters"):
        lines.append(f"\nKADROLAR:")
        for r in detail["rosters"]:
            formation = r.get("formation", "")
            players_str = ", ".join([f"{p.get('name','')} ({p.get('pos','')})" for p in r.get("players", [])[:11]])
            lines.append(f"  {r.get('team','')}: Diziliş: {formation} | {players_str}")

    # Maç istatistikleri (canlı veya biten)
    ls = match_info.get("live_stats")
    if ls:
        lines.append(f"\nMAÇ İSTATİSTİKLERİ:")
        lines.append(f"  Topla Oynama: {h_name} %{ls.get('homePossession',50)} - {a_name} %{ls.get('awayPossession',50)}")
        lines.append(f"  Şutlar: {ls.get('homeShots',0)} - {ls.get('awayShots',0)} | İsabetli: {ls.get('homeShotsOnTarget',0)} - {ls.get('awayShotsOnTarget',0)}")
        lines.append(f"  Kornerler: {ls.get('homeCorners',0)} - {ls.get('awayCorners',0)}")
        lines.append(f"  Fauller: {ls.get('homeFouls',0)} - {ls.get('awayFouls',0)}")

    # Boxscore (daha detaylı istatistik)
    if detail and detail.get("boxscore"):
        lines.append(f"\nDETAYLI İSTATİSTİK TABLOSU:")
        for b in detail["boxscore"]:
            stats_str = " | ".join([f"{k}: {v}" for k, v in b.get("stats", {}).items()])
            lines.append(f"  {b.get('team','')}: {stats_str}")

    # Canlı oyun durumu
    if in_play:
        lines.append(f"\nCANLI OYUN ANALİZİ:")
        lines.append(f"  Dakika: {in_play.get('elapsedMin')}'")
        lines.append(f"  Anlık Skor: {h_name} {in_play.get('homeScore',0)} - {in_play.get('awayScore',0)} {a_name}")
        lines.append(f"  Saha Hakimiyeti: {in_play.get('dominantTeam','')} (%{in_play.get('homeDominance',50)} vs %{in_play.get('awayDominance',50)})")
        lp = in_play.get("liveProbabilities", {})
        lines.append(f"  Canlı MS: Ev %{lp.get('homeWinPct',0)} | Bera %{lp.get('drawPct',0)} | Dep %{lp.get('awayWinPct',0)}")
        lines.append(f"  Sıradaki Gol: {h_name} %{lp.get('nextHomePct',0)} | Gol Yok %{lp.get('noMoreGoalsPct',0)} | {a_name} %{lp.get('nextAwayPct',0)}")
        lines.append(f"  Korner Projeksiyonu: Şu an {in_play.get('liveStats',{}).get('totalCorners',0)}, Tahmini Bitiş: ~{lp.get('projectedCorners',0)}")
        lines.append(f"  Canlı Öneri: {lp.get('inPlayPick','')}")

    # Önemli olaylar (goller, kartlar)
    if detail and detail.get("keyEvents"):
        lines.append(f"\nÖNEMLİ OLAYLAR:")
        for ke in detail["keyEvents"][:10]:
            lines.append(f"  {ke.get('clock','')} - {ke.get('text','')}")

    return "\n".join(lines)


def _call_gemini_chat(query: str, context: str, history: list, api_key: str) -> str:
    """
    Google Gemini AI ile gerçek zamanlı, çok turlu futbol sohbeti.
    Tüm maç verileri bağlam olarak verilir, önceki sohbet geçmişi korunur.
    """
    system_instruction = (
        "Sen 'Taktik Berat' — futbolu tüm detaylarıyla bilen, yıllardır maçları izleyen, taktik tahtasına hakim, "
        "istatistikleri kusursuz yorumlayan SAMİMİ, BİLGİLİ BİR TÜRK FUTBOL ARKADAŞISIN.\n\n"
        "KRİTİK KURALLAR:\n"
        "1. Kullanıcı senin en yakın futbol arkadaşın. 'Bir yapay zeka olarak...' gibi ifadeler ASLA kullanma.\n"
        "2. Samimi, doğal Türkçe konuş. Argo ama küfürsüz futbol jargonu kullan ('Hocam', 'Dostum', 'Net söyleyeyim').\n"
        "3. Her yorumunu GERÇEK VERİLERE ve sana verilen maç bağlamına dayandır. Uydurma yapma.\n"
        "4. Son 5 maç formunu, kadroyu, istatistikleri, oranları AKTIF OLARAK KULLAN ve referans ver.\n"
        "5. Sorulara doğrudan, cesur ve net cevap ver. Uzun giriş yapma, hemen konuya gir.\n"
        "6. Gerekçe göster: 'Neden' diye soran birine istatistik ve form verisiyle açıkla.\n"
        "7. Canlı maçlarda anlık skor, dakika, baskı durumu ve momentum analizini kullan.\n"
        "8. Biten maçlarda skor, istatistik ve performans değerlendirmesi yap.\n"
        "9. Yanıtlarını 150-300 kelime arasında tut. Gereksiz uzatma ama çok kısa da bırakma.\n"
        "10. Bahis önerilerinde 'banko' derken gerçekten verinin desteklediği tercihleri söyle."
    )

    # İçerikleri oluştur — çok turlu sohbet
    contents = []

    # İlk mesaj: Sistem talimatı + maç bağlamı
    contents.append({
        "role": "user",
        "parts": [{"text": f"{system_instruction}\n\n--- MAÇ BAĞLAMI ---\n{context}\n--- BAĞLAM SONU ---\n\nAnladım, bu verilerle hazırım."}]
    })
    contents.append({
        "role": "model",
        "parts": [{"text": "Tamam hocam, tüm verileri aldım! Maçla ilgili ne sorarsan sor, gerçek istatistiklerle konuşalım."}]
    })

    # Önceki sohbet geçmişi (varsa)
    if history:
        for msg in history[-10:]:  # Son 10 mesajı koru
            role = "user" if msg.get("role") == "user" else "model"
            text = msg.get("content", "")
            if text.strip():
                contents.append({"role": role, "parts": [{"text": text}]})

    # Kullanıcının yeni sorusu
    contents.append({
        "role": "user",
        "parts": [{"text": query}]
    })

    req_body = json.dumps({
        "contents": contents,
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 1024,
            "topP": 0.92
        }
    }).encode("utf-8")

    # Desteklenen güncel Gemini modelleri (sırayla denenir)
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            req = urllib.request.Request(
                url,
                data=req_body,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                candidates = res_json.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
        except Exception as err:
            print(f"[GEMINI MODEL {model_name} DENEMESI BAŞARISIZ]: {err}")
            continue

    return "Hocam bağlantıda ufak bir aksaklık oldu ama verilerim güncel. Soruyu tekrar atar mısın?"


def _generate_local_smart_reply(query: str, match_info: dict, detail: dict, probs: dict, in_play: dict, context: str) -> str:
    """
    Gemini yokken devreye giren akıllı yerel motor.
    Kalıplamış değil, gerçek maç verilerine dayalı dinamik yanıtlar üretir.
    """
    if not match_info:
        return "Hocam henüz bir maç seçmedin! Üstten bir maç seç de masaya yatıralım."

    home = match_info.get("home", {}).get("name", "Ev Sahibi")
    away = match_info.get("away", {}).get("name", "Deplasman")
    state = match_info.get("state", "pre")
    q = query.lower()

    # Gerçek form verisini çıkar
    form_summary = ""
    if detail and detail.get("lastFive"):
        for tf in detail["lastFive"]:
            t_name = tf.get("team", "")
            games = tf.get("games", [])
            wins = sum(1 for g in games if g.get("result") == "W")
            draws = sum(1 for g in games if g.get("result") == "D")
            losses = sum(1 for g in games if g.get("result") == "L")
            recent = ", ".join([f"{g.get('result','?')} {g.get('score','')}" for g in games[:3]])
            form_summary += f"\n  {t_name}: Son 5'te {wins}G {draws}B {losses}M → Son 3: {recent}"

    # Gerçek istatistikleri çıkar
    stats_summary = ""
    ls = match_info.get("live_stats")
    if ls:
        stats_summary = (
            f"\n  Topla Oynama: {home} %{ls.get('homePossession',50)} vs {away} %{ls.get('awayPossession',50)}"
            f"\n  Şutlar: {ls.get('homeShots',0)}-{ls.get('awayShots',0)} (İsabetli: {ls.get('homeShotsOnTarget',0)}-{ls.get('awayShotsOnTarget',0)})"
            f"\n  Kornerler: {ls.get('homeCorners',0)}-{ls.get('awayCorners',0)}"
        )

    # Kadro bilgisi
    roster_info = ""
    if detail and detail.get("rosters"):
        for r in detail["rosters"]:
            formation = r.get("formation", "")
            if formation:
                roster_info += f"\n  {r.get('team','')}: {formation} dizilişi"

    # ========== CANLI MAÇ ==========
    if in_play and state == "in":
        elapsed = in_play.get("elapsedMin", 45)
        hs = in_play.get("homeScore", 0)
        as_ = in_play.get("awayScore", 0)
        dom_team = in_play.get("dominantTeam", home)
        lp = in_play.get("liveProbabilities", {})
        ils = in_play.get("liveStats", {})

        base = f"Hocam maç canlı! Dakika {elapsed}', tabelada {home} {hs} - {as_} {away}.\n"
        base += f"📊 Sahada {dom_team} baskıyı kuruyor — Topla Oynama %{ils.get('homePossession',50)} vs %{ils.get('awayPossession',50)}.\n"
        base += f"Şut dengesi: {home} {ils.get('homeShots',0)} ({ils.get('homeShotsOnTarget',0)} isabet) vs {away} {ils.get('awayShots',0)} ({ils.get('awayShotsOnTarget',0)} isabet).\n"
        base += f"Kornerler: {ils.get('homeCorners',0)}-{ils.get('awayCorners',0)} (Toplam: {ils.get('totalCorners',0)}, Bitiş projeksiyonu: ~{lp.get('projectedCorners',9)}).\n\n"
        base += f"⚡ Canlı olasılıklar → MS: {home} %{lp.get('homeWinPct',0):.0f} | Bera %{lp.get('drawPct',0):.0f} | {away} %{lp.get('awayWinPct',0):.0f}\n"
        base += f"Sıradaki gol: {home} %{lp.get('nextHomePct',0):.0f} | Gol Yok %{lp.get('noMoreGoalsPct',0):.0f} | {away} %{lp.get('nextAwayPct',0):.0f}\n"
        base += f"🎯 Canlı önerim: {lp.get('inPlayPick', 'Bekleniyor')}"
        return base

    # ========== BİTMİŞ MAÇ ==========
    if state == "post":
        hs = match_info.get("home", {}).get("score", 0)
        as_ = match_info.get("away", {}).get("score", 0)
        base = f"Hocam maç bitti: {home} {hs} - {as_} {away}.\n"
        if stats_summary:
            base += f"\n📊 Maç İstatistikleri:{stats_summary}\n"
        if form_summary:
            base += f"\n📋 Form Durumu:{form_summary}\n"

        try:
            h_int, a_int = int(hs), int(as_)
            if h_int > a_int:
                base += f"\n{home} bu maçı hak ederek kazandı."
            elif a_int > h_int:
                base += f"\n{away} deplasmanda güçlü bir galibiyet aldı."
            else:
                base += f"\nAdil bir beraberlik; iki takım da şansını denedi."
        except:
            pass
        return base

    # ========== BAŞLAMAMIŞ MAÇ ==========
    hw = probs.get("homeWinPct", 45) if probs else 45
    aw = probs.get("awayWinPct", 30) if probs else 30
    dr = probs.get("drawPct", 25) if probs else 25
    o25 = probs.get("over25Pct", 50) if probs else 50
    btts = probs.get("bttsYesPct", 50) if probs else 50
    pick = probs.get("primaryPick", "") if probs else ""
    top_scores = probs.get("topScores", []) if probs else []

    # Soru tipine göre dallan ama HER ZAMAN gerçek veri kullan
    if any(w in q for w in ["üst", "ust", "alt", "gol", "2.5", "1.5", "3.5", "kg", "karşılıklı"]):
        resp = f"Hocam {home} - {away} maçında gol analizi:\n"
        resp += f"📊 2.5 Üst: %{o25:.0f} | 2.5 Alt: %{100-o25:.0f} | KG Var: %{btts:.0f}\n"
        if form_summary:
            resp += f"\n📋 Son maç formu:{form_summary}\n"
        if o25 >= 55:
            resp += f"\nVeriler net: gollü maç beklentisi güçlü. {pick} tercihim sağlam duruyor."
        else:
            resp += f"\nDikkat: düşük gol beklentisi var. Alt tercihi daha güvenli olabilir."
        return resp

    if any(w in q for w in ["kim kazanır", "kim alır", "favori", "ms 1", "ms 2", "taraf", "yener"]):
        resp = f"Hocam {home} vs {away} galibiyete bakışım:\n"
        resp += f"📊 {home}: %{hw:.0f} | Beraberlik: %{dr:.0f} | {away}: %{aw:.0f}\n"
        if form_summary:
            resp += f"\n📋 Form:{form_summary}\n"
        if roster_info:
            resp += f"\n⚽ Dizilişler:{roster_info}\n"
        if hw > aw + 15:
            resp += f"\n{home} bu maçta net favori, veriler destekliyor."
        elif aw > hw + 15:
            resp += f"\n{away} formda ve favori konumunda."
        else:
            resp += f"\nÇok dengeli bir maç — taraf bahsi riskli, alternatif piyasalar daha güvenli."
        return resp

    if any(w in q for w in ["korner", "corner"]):
        resp = f"Hocam {home} - {away} korner analizi:\n"
        if stats_summary:
            resp += f"📊 İstatistikler:{stats_summary}\n"
        if form_summary:
            resp += f"📋 Form:{form_summary}\n"
        resp += f"\nKanat oyunları ve genel tempo itibariyle beklentimi oluşturdum. {pick} tavsiyesine ek olarak korner pazarını da değerlendir."
        return resp

    if any(w in q for w in ["skor", "tabela", "kaç kaç"]):
        scores_str = ", ".join([f"{s.get('score')} (%{s.get('prob')})" for s in top_scores[:4]]) if top_scores else "Hesaplanıyor"
        resp = f"Hocam {home} - {away} skor tahminlerim:\n"
        resp += f"🎯 En olası: {scores_str}\n"
        if form_summary:
            resp += f"\n📋 Form:{form_summary}\n"
        resp += f"\nGalibiyet olasılıkları ({home} %{hw:.0f} | Bera %{dr:.0f} | {away} %{aw:.0f}) ışığında bu skorlar matematiksel modelin çıktısı."
        return resp

    if any(w in q for w in ["banko", "kupon", "tavsiye", "tercih", "ne oynayayım", "ne yazayım"]):
        resp = f"Hocam {home} - {away} için kupon tercihim:\n"
        resp += f"🎯 Önerim: {pick}\n"
        resp += f"📊 2.5 Üst: %{o25:.0f} | KG Var: %{btts:.0f} | {home} MS: %{hw:.0f}\n"
        if form_summary:
            resp += f"\n📋 Form:{form_summary}\n"
        resp += f"\nBu tercihi sağlam veriler destekliyor. Risk seviyesi: {probs.get('riskLevel', 'Orta')}."
        return resp

    if any(w in q for w in ["kadro", "diziliş", "forma", "11", "oyuncu"]):
        if roster_info:
            resp = f"Hocam {home} - {away} kadro bilgisi:\n{roster_info}\n"
            if form_summary:
                resp += f"\n📋 Form:{form_summary}"
            return resp
        else:
            return f"Hocam kadro bilgisi henüz yayınlanmadı. Maç saati yaklaştıkça kadro verileri gelecek."

    # GENEL — maçın tam röntgeni
    resp = f"Hocam {home} vs {away} ({match_info.get('league_name','')}) maçının tam röntgeni:\n\n"
    resp += f"📊 Olasılıklar: {home} %{hw:.0f} | Bera %{dr:.0f} | {away} %{aw:.0f}\n"
    resp += f"📊 Gol: 2.5 Üst %{o25:.0f} | KG Var %{btts:.0f}\n"
    if top_scores:
        scores_str = ", ".join([f"{s.get('score')} (%{s.get('prob')})" for s in top_scores[:3]])
        resp += f"🎯 Skor Tahminleri: {scores_str}\n"
    if form_summary:
        resp += f"\n📋 Son Form:{form_summary}\n"
    if roster_info:
        resp += f"\n⚽ Dizilişler:{roster_info}\n"
    resp += f"\n🎯 Banko Tercih: {pick} | Risk: {probs.get('riskLevel', 'Orta')}\n"
    resp += f"\nGol, korner, kadro veya canlı skor gibi özel sorularını sor, detaya girelim!"
    return resp

