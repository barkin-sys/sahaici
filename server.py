"""
Canlı Futbol Analiz & Bilgili Futbol Arkadaşı Web Sunucusu
FastAPI + Uvicorn tabanlı, REST API ve modern ön yüz sunar.
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Query, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import football_engine
import auth_engine

app = FastAPI(
    title="Saha İçi - Reel Maç Takip & AI Futbol Arkadaşı",
    description="Reel futbol maçlarını canlı takip eden, analiz eden ve samimi bir arkadaş gibi yorumlayan platform.",
    version="1.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statik dosya dizini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AnalyzeRequest(BaseModel):
    league: str
    event_id: str


class ChatRequest(BaseModel):
    query: str
    league: Optional[str] = "all"
    event_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None
    api_key: Optional[str] = None
    match_data: Optional[Dict[str, Any]] = None


@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "ok", "message": "Sunucu hazır. Arayüz hazırlanıyor..."})


@app.get("/favicon.ico")
def get_favicon():
    return JSONResponse(status_code=204, content={})


class LoginRequest(BaseModel):
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


def require_auth(authorization: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    if not token or not auth_engine.validate_token(token):
        raise HTTPException(status_code=401, detail="Lütfen önce şifrenizle giriş yapın.")
    return token


@app.post("/api/auth/login")
def login_endpoint(req: LoginRequest):
    if auth_engine.verify_password(req.password):
        token = auth_engine.create_session()
        return {"success": True, "token": token, "message": "Giriş başarılı"}
    raise HTTPException(status_code=401, detail="Hatalı şifre. Lütfen tekrar deneyin.")


@app.get("/api/auth/check")
def check_auth_endpoint(authorization: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    valid = auth_engine.validate_token(token) if token else False
    return {"authenticated": valid}


@app.post("/api/auth/logout")
def logout_endpoint(authorization: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    if token:
        auth_engine.revoke_session(token)
    return {"success": True, "message": "Oturum başarıyla kapatıldı"}


@app.post("/api/auth/change-password")
def change_password_endpoint(req: ChangePasswordRequest, authorization: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    if not token or not auth_engine.validate_token(token):
        raise HTTPException(status_code=401, detail="Yetkisiz işlem")
    
    ok, msg = auth_engine.change_password(req.old_password, req.new_password)
    if ok:
        new_token = auth_engine.create_session()
        return {"success": True, "message": msg, "token": new_token}
    raise HTTPException(status_code=400, detail=msg)


@app.get("/api/leagues")
def get_leagues():
    """Desteklenen liglerin listesini döner."""
    return list(football_engine.LEAGUES.values())


@app.get("/api/matches")
def get_matches_endpoint(
    league: str = Query("all", description="Lig kodu (all, tur.1, uefa.nations vb.)"),
    date: Optional[str] = Query(None, description="Tarih formatı: YYYYMMDD"),
    status: Optional[str] = Query("all", description="Filtre: all, live, scheduled, finished"),
    _token: str = Depends(require_auth)
):
    """
    Belirtilen lig ve tarihe göre reel maçları listeler.
    """
    if not date:
        date = datetime.now().strftime("%Y%m%d")

    res = football_engine.get_matches(league, date)

    # Durum filtresi uygulama
    matches = res.get("matches", [])
    if status == "live":
        matches = [m for m in matches if m["state"] == "in"]
    elif status == "scheduled":
        matches = [m for m in matches if m["state"] == "pre"]
    elif status == "finished":
        matches = [m for m in matches if m["state"] == "post"]

    res["matches"] = matches
    res["total"] = len(matches)
    return res


@app.get("/api/match-detail")
def get_match_detail_endpoint(
    league: str = Query(..., description="Lig kodu"),
    event_id: str = Query(..., description="Maç ID"),
    _token: str = Depends(require_auth)
):
    """Seçilen maçın derin detaylarını döner (son maçlar, oranlar, kadro, istatistik)."""
    detail = football_engine.get_match_detail(league, event_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Maç detayı bulunamadı veya henüz güncellenmedi.")
    return detail


@app.post("/api/analyze")
def analyze_match_endpoint(req: AnalyzeRequest, _token: str = Depends(require_auth)):
    """
    Seçilen maç için matematiksel modellemeyi (Poisson, form xG) çalıştırır
    ve 'Bilgili Futbol Arkadaşı'nın samimi detaylı analiz mektubunu üretir.
    """
    # Önce maçın temel özetini bul
    matches_data = football_engine.get_matches(req.league)
    match_info = next((m for m in matches_data.get("matches", []) if str(m["id"]) == str(req.event_id)), None)

    # Bulunamazsa 'all' liginde de ara
    if not match_info:
        matches_all = football_engine.get_matches("all")
        match_info = next((m for m in matches_all.get("matches", []) if str(m["id"]) == str(req.event_id)), None)

    # Hala bulunamazsa doğrudan ESPN event header'ından gerçek bilgileri çek
    if not match_info:
        match_info = football_engine.get_match_info_by_id(req.event_id, req.league)

    if not match_info:
        match_info = {
            "id": req.event_id,
            "home": {"name": "Ev Sahibi"},
            "away": {"name": "Deplasman"},
            "league_name": req.league,
            "state": "pre"
        }

    detail = football_engine.get_match_detail(req.league, req.event_id)
    last_five = detail.get("lastFive", []) if detail else []
    odds = detail.get("odds", []) if detail else []

    # Eğer canlı/bitmiş maçın live_stats alanı boşsa boxscore'dan doldur
    # KORUMA: Sadece state 'in' veya 'post' ise ve boxscore verisi gerçekten bu maça aitse
    if (not match_info.get("live_stats")
        and match_info.get("state") in ("in", "post")
        and detail
        and detail.get("boxscore")
        and len(detail["boxscore"]) >= 2):

        h_name = match_info.get("home", {}).get("name", "").lower().strip()
        a_name = match_info.get("away", {}).get("name", "").lower().strip()

        # Sıkı eşleştirme: Boxscore takım ismi, maç takım ismini içermeli VEYA tam tersi
        def _team_match(box_team: str, match_team: str) -> bool:
            bt = box_team.lower().strip()
            mt = match_team.lower().strip()
            if not bt or not mt:
                return False
            return mt in bt or bt in mt

        h_box = next((b for b in detail["boxscore"] if _team_match(b.get("team", ""), h_name)), None)
        a_box = next((b for b in detail["boxscore"] if _team_match(b.get("team", ""), a_name)), None)

        # Her iki takım da eşleşmeli — yarım eşleşme başka maçın verisidir!
        if h_box and a_box:
            h_s = h_box.get("stats", {})
            a_s = a_box.get("stats", {})
            match_info["live_stats"] = {
                "homePossession": h_s.get("Possession", "50").replace("%", "").strip() or "50",
                "awayPossession": a_s.get("Possession", "50").replace("%", "").strip() or "50",
                "homeShots": h_s.get("SHOTS", h_s.get("Shots", "0")),
                "awayShots": a_s.get("SHOTS", a_s.get("Shots", "0")),
                "homeShotsOnTarget": h_s.get("ON GOAL", h_s.get("Shots on Goal", "0")),
                "awayShotsOnTarget": a_s.get("ON GOAL", a_s.get("Shots on Goal", "0")),
                "homeCorners": h_s.get("Corner Kicks", h_s.get("Corners", "0")),
                "awayCorners": a_s.get("Corner Kicks", a_s.get("Corners", "0")),
                "homeFouls": h_s.get("Fouls", "0"),
                "awayFouls": a_s.get("Fouls", "0")
            }

    # Olasılıkları hesapla
    probs = football_engine.calculate_match_probabilities(
        home_name=match_info.get("home", {}).get("name", "Ev Sahibi"),
        away_name=match_info.get("away", {}).get("name", "Deplasman"),
        last_five=last_five,
        odds_info=odds
    )

    # Samimi arkadaş yorumunu üret
    commentary = football_engine.generate_expert_friend_commentary(
        match_info=match_info,
        detail=detail,
        probs=probs
    )

    # Canlı maç ise anlık oyun içi istatistiksel yeniden değerlendirmeyi çalıştır
    in_play = None
    if match_info.get("state") == "in":
        in_play = football_engine.calculate_inplay_probabilities(match_info, detail, probs)
        commentary = in_play.get("liveCommentary", commentary)

    # Mantıklı ve oynanabilir akılcı bahis önerilerini üret
    smart_recs = football_engine.generate_smart_betting_recommendations(
        match_info=match_info,
        detail=detail,
        probs=probs,
        in_play=in_play
    )

    return {
        "match": match_info,
        "detail": detail,
        "probabilities": probs,
        "inPlay": in_play,
        "commentary": commentary,
        "smartRecommendations": smart_recs
    }


@app.post("/api/chat")
def chat_with_pal_endpoint(req: ChatRequest, _token: str = Depends(require_auth)):
    """
    Futbol arkadaşı Taktik Serdar ile interaktif sohbet.
    """
    match_info = req.match_data
    detail = None
    probs = {}

    if req.event_id:
        detail = football_engine.get_match_detail(req.league or "all", req.event_id)
        if not match_info:
            matches_data = football_engine.get_matches(req.league or "all")
            match_info = next((m for m in matches_data.get("matches", []) if str(m["id"]) == str(req.event_id)), None)
        if not match_info:
            match_info = football_engine.get_match_info_by_id(req.event_id, req.league or "all")

        if match_info:
            probs = football_engine.calculate_match_probabilities(
                home_name=match_info.get("home", {}).get("name", "Ev Sahibi"),
                away_name=match_info.get("away", {}).get("name", "Deplasman"),
                last_five=detail.get("lastFive", []) if detail else [],
                odds_info=detail.get("odds", []) if detail else []
            )

    answer = football_engine.ask_football_pal(
        query=req.query,
        match_info=match_info,
        detail=detail,
        probs=probs,
        history=req.history,
        api_key=req.api_key
    )

    return {
        "reply": answer,
        "event_id": req.event_id
    }


import coupon_engine


@app.get("/api/coupons")
def get_coupons_endpoint(date: Optional[str] = Query(None, description="Tarih formatı: YYYYMMDD"), _token: str = Depends(require_auth)):
    """
    Günün en yüksek ihtimalli değer kuponlarını ve geçmiş başarı karnesini döner.
    """
    if not date:
        date = datetime.now().strftime("%Y%m%d")
    return coupon_engine.get_daily_coupons(date)


@app.post("/api/coupons/regenerate")
def regenerate_coupons_endpoint(date: Optional[str] = Query(None, description="Tarih formatı: YYYYMMDD"), _token: str = Depends(require_auth)):
    """
    Belirtilen gün için kuponları yeniden analiz edip taze kupon üretir.
    """
    if not date:
        date = datetime.now().strftime("%Y%m%d")
    storage = coupon_engine.load_storage()
    coupons = coupon_engine._generate_coupons_for_date(date)
    storage[date] = coupons
    coupon_engine.save_storage(storage)
    return coupon_engine.get_daily_coupons(date)


@app.get("/api/standings")
def get_standings_endpoint(league: str = Query("tur.1", description="Lig kodu (tur.1, eng.1, esp.1 vb.)"), _token: str = Depends(require_auth)):
    """
    Seçilen lig için güncel puan durumunu döner.
    """
    if league == "all" or not league:
        league = "tur.1"

    league_info = football_engine.LEAGUES.get(league, {"name": "Futbol Ligi", "slug": league})
    table = football_engine.get_standings(league)
    return {
        "league": league_info,
        "standings": table,
        "total": len(table)
    }




if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Saha İçi Futbol Analiz Platformu Başlatılıyor... (Port: {port})")
    print(f"Tarayıcınızdan http://localhost:{port} adresine gidebilirsiniz.")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
