/**
 * Saha İçi - Canlı Reel Maç Takip & AI Futbol Arkadaşı
 * İstemci Tarafı Uygulama Mantığı (JavaScript)
 */

document.addEventListener("DOMContentLoaded", () => {
  // Uygulama Durumu
  const state = {
    currentLeague: "all",
    currentDate: getTodayFormatted(), // 'YYYYMMDD'
    currentStatus: "all",
    searchQuery: "",
    matches: [],
    selectedMatch: null,
    chatHistory: [],
    apiKey: localStorage.getItem("sahaici_gemini_key") || "",
    isTtsEnabled: false,
    couponDate: getTodayFormatted(),
    couponSession: (new Date().getHours() >= 18 ? "night" : "day"),
    couponType: "value",
    couponsData: null,
    modalPollInterval: null,
    modalAbortController: null,
    authToken: localStorage.getItem("saha_auth_token") || sessionStorage.getItem("saha_auth_token") || null,
    isAuthenticated: false
  };

  // DOM Elemanları
  const dom = {
    // Sekmeler
    tabButtons: document.querySelectorAll(".tab-btn"),
    tabContents: document.querySelectorAll(".tab-content"),
    
    // Filtreler & Kontroller
    btnPrevDay: document.getElementById("btnPrevDay"),
    btnToday: document.getElementById("btnToday"),
    btnNextDay: document.getElementById("btnNextDay"),
    datePicker: document.getElementById("datePicker"),
    searchInput: document.getElementById("searchInput"),
    statusChips: document.querySelectorAll(".filter-chip"),
    leaguesContainer: document.getElementById("leaguesContainer"),
    currentLeagueTitle: document.getElementById("currentLeagueTitle"),
    currentDateDisplay: document.getElementById("currentDateDisplay"),
    lastUpdatedText: document.getElementById("lastUpdatedText"),
    btnRefresh: document.getElementById("btnRefresh"),
    
    // Maç Izgarası & Canlı/Biten Maçlar Paneli
    liveFinishedShowcase: document.getElementById("liveFinishedShowcase"),
    showcaseCardsContainer: document.getElementById("showcaseCardsContainer"),
    showcaseLiveCount: document.getElementById("showcaseLiveCount"),
    showcaseFinishedCount: document.getElementById("showcaseFinishedCount"),
    matchesGrid: document.getElementById("matchesGrid"),
    countAll: document.getElementById("count-all"),
    countLive: document.getElementById("count-live"),
    countScheduled: document.getElementById("count-scheduled"),
    countFinished: document.getElementById("count-finished"),
    
    // Analiz Modalı
    analysisModal: document.getElementById("analysisModal"),
    btnCloseModal: document.getElementById("btnCloseModal"),
    modalLeague: document.getElementById("modalLeague"),
    modalHomeLogo: document.getElementById("modalHomeLogo"),
    modalHomeName: document.getElementById("modalHomeName"),
    modalAwayLogo: document.getElementById("modalAwayLogo"),
    modalAwayName: document.getElementById("modalAwayName"),
    modalScoreDisplay: document.getElementById("modalScoreDisplay"),
    modalStatusBadge: document.getElementById("modalStatusBadge"),
    modalVenue: document.getElementById("modalVenue"),
    modalCommentaryText: document.getElementById("modalCommentaryText"),
    modalSmartBetsSection: document.getElementById("modalSmartBetsSection"),
    modalSmartBetsList: document.getElementById("modalSmartBetsList"),
    btnReadAloud: document.getElementById("btnReadAloud"),
    btnAskAboutMatch: document.getElementById("btnAskAboutMatch"),
    
    // Olasılık Barları & Metrikler
    barHome: document.getElementById("barHome"),
    barDraw: document.getElementById("barDraw"),
    barAway: document.getElementById("barAway"),
    labelHomeWin: document.getElementById("labelHomeWin"),
    labelDraw: document.getElementById("labelDraw"),
    labelAwayWin: document.getElementById("labelAwayWin"),
    valOver25: document.getElementById("valOver25"),
    valUnder25: document.getElementById("valUnder25"),
    valBtts: document.getElementById("valBtts"),
    valBttsNo: document.getElementById("valBttsNo"),
    valTopScore: document.getElementById("valTopScore"),
    valTopScoreProb: document.getElementById("valTopScoreProb"),
    valRisk: document.getElementById("valRisk"),
    valPickSub: document.getElementById("valPickSub"),
    modalFormGrid: document.getElementById("modalFormGrid"),
    modalOddsList: document.getElementById("modalOddsList"),
    modalBoxscoreContainer: document.getElementById("modalBoxscoreContainer"),
    modalRostersGrid: document.getElementById("modalRostersGrid"),

    // Canlı İstatistikler & Yeniden Değerlendirme (In-Play)
    modalLiveSection: document.getElementById("modalLiveSection"),
    liveClockBadge: document.getElementById("liveClockBadge"),
    liveHomePoss: document.getElementById("liveHomePoss"),
    liveAwayPoss: document.getElementById("liveAwayPoss"),
    barLiveHomePoss: document.getElementById("barLiveHomePoss"),
    barLiveAwayPoss: document.getElementById("barLiveAwayPoss"),
    liveHomeShots: document.getElementById("liveHomeShots"),
    liveAwayShots: document.getElementById("liveAwayShots"),
    liveHomeOnGoal: document.getElementById("liveHomeOnGoal"),
    liveAwayOnGoal: document.getElementById("liveAwayOnGoal"),
    liveHomeCorners: document.getElementById("liveHomeCorners"),
    liveAwayCorners: document.getElementById("liveAwayCorners"),
    liveHomeFouls: document.getElementById("liveHomeFouls"),
    liveAwayFouls: document.getElementById("liveAwayFouls"),
    liveLblHome: document.getElementById("liveLblHome"),
    livePctHome: document.getElementById("livePctHome"),
    livePctDraw: document.getElementById("livePctDraw"),
    liveLblAway: document.getElementById("liveLblAway"),
    livePctAway: document.getElementById("livePctAway"),
    liveNextHomeName: document.getElementById("liveNextHomeName"),
    liveNextHomePct: document.getElementById("liveNextHomePct"),
    liveNextNoGoalPct: document.getElementById("liveNextNoGoalPct"),
    liveNextAwayName: document.getElementById("liveNextAwayName"),
    liveNextAwayPct: document.getElementById("liveNextAwayPct"),
    liveCornerPick: document.getElementById("liveCornerPick"),
    liveCornerProjDetail: document.getElementById("liveCornerProjDetail"),
    liveLine1Name: document.getElementById("liveLine1Name"),
    liveLine1Pct: document.getElementById("liveLine1Pct"),
    liveLine2Name: document.getElementById("liveLine2Name"),
    liveLine2Pct: document.getElementById("liveLine2Pct"),
    
    // Sohbet (Chat)
    chatMatchSelect: document.getElementById("chatMatchSelect"),
    chatSelectedMatchPreview: document.getElementById("chatSelectedMatchPreview"),
    prevHomeName: document.getElementById("prevHomeName"),
    prevAwayName: document.getElementById("prevAwayName"),
    prevStatus: document.getElementById("prevStatus"),
    prevPick: document.getElementById("prevPick"),
    quickButtons: document.querySelectorAll(".quick-btn"),
    chatMessages: document.getElementById("chatMessages"),
    chatForm: document.getElementById("chatForm"),
    chatInput: document.getElementById("chatInput"),
    btnTtsToggle: document.getElementById("btnTtsToggle"),
    chatInlineApiKey: document.getElementById("chatInlineApiKey"),
    btnSaveInlineApiKey: document.getElementById("btnSaveInlineApiKey"),
    chatApiStatusBadge: document.getElementById("chatApiStatusBadge"),
    
    // Puan Durumu
    standingsSelect: document.getElementById("standingsSelect"),
    standingsLeagueName: document.getElementById("standingsLeagueName"),
    standingsBody: document.getElementById("standingsBody"),
    
    // Kuponlar & Başarı Takibi
    statOverallWinRate: document.getElementById("statOverallWinRate"),
    kpiWonCoupons: document.getElementById("kpiWonCoupons"),
    kpiDayWinRate: document.getElementById("kpiDayWinRate"),
    kpiNightWinRate: document.getElementById("kpiNightWinRate"),
    kpiAvgOdds: document.getElementById("kpiAvgOdds"),
    kpiSelectionRate: document.getElementById("kpiSelectionRate"),
    couponDateSelect: document.getElementById("couponDateSelect"),
    btnRegenCoupons: document.getElementById("btnRegenCoupons"),
    btnCouponToday: document.getElementById("btnCouponToday"),
    btnCouponTomorrow: document.getElementById("btnCouponTomorrow"),
    couponSessionBtns: document.querySelectorAll(".session-tab-btn"),
    couponTypeBtns: document.querySelectorAll(".coupon-type-btn"),
    couponDisplayContainer: document.getElementById("couponDisplayContainer"),

    // Ayarlar Modalı
    settingsModal: document.getElementById("settingsModal"),
    btnSettings: document.getElementById("btnSettings"),
    btnCloseSettings: document.getElementById("btnCloseSettings"),
    inputApiKey: document.getElementById("inputApiKey"),
    btnSaveApiKey: document.getElementById("btnSaveApiKey"),
    btnClearApiKey: document.getElementById("btnClearApiKey"),

    // Kimlik Doğrulama (Auth) & Şifreli Giriş
    authOverlay: document.getElementById("authOverlay"),
    authForm: document.getElementById("authForm"),
    authPassword: document.getElementById("authPassword"),
    btnTogglePassword: document.getElementById("btnTogglePassword"),
    togglePwIcon: document.getElementById("togglePwIcon"),
    authRememberMe: document.getElementById("authRememberMe"),
    authErrorMsg: document.getElementById("authErrorMsg"),
    authErrorText: document.getElementById("authErrorText"),
    btnAuthSubmit: document.getElementById("btnAuthSubmit"),
    btnAuthText: document.getElementById("btnAuthText"),
    btnAuthSpinner: document.getElementById("btnAuthSpinner"),
    btnAuthLogout: document.getElementById("btnAuthLogout"),
    inputOldPassword: document.getElementById("inputOldPassword"),
    inputNewPassword: document.getElementById("inputNewPassword"),
    btnChangePassword: document.getElementById("btnChangePassword"),
    pwChangeMsg: document.getElementById("pwChangeMsg")
  };

  // ==========================================
  // FETCH GÜVENLİK VE AUTH KATMANI
  // ==========================================
  const originalFetch = window.fetch;
  window.fetch = async function (url, options = {}) {
    const urlStr = String(url || "");
    if (urlStr.startsWith("/api/") && !urlStr.startsWith("/api/auth/login")) {
      options.headers = options.headers || {};
      if (state.authToken) {
        if (options.headers instanceof Headers) {
          options.headers.set("Authorization", "Bearer " + state.authToken);
        } else {
          options.headers["Authorization"] = "Bearer " + state.authToken;
        }
      }
    }
    const res = await originalFetch(url, options);
    if (res.status === 401 && !urlStr.startsWith("/api/auth/login") && !urlStr.startsWith("/api/auth/check")) {
      console.warn("[AUTH] Yetkisiz erişim veya oturum zaman aşımı (401).");
      state.authToken = null;
      state.isAuthenticated = false;
      localStorage.removeItem("saha_auth_token");
      sessionStorage.removeItem("saha_auth_token");
      showAuthOverlay();
    }
    return res;
  };

  async function checkInitialAuth() {
    if (!state.authToken) {
      showAuthOverlay();
      return false;
    }
    try {
      const res = await originalFetch("/api/auth/check", {
        headers: { "Authorization": "Bearer " + state.authToken }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.authenticated) {
          state.isAuthenticated = true;
          hideAuthOverlay();
          return true;
        }
      }
    } catch (e) {
      console.error("[AUTH] Kontrol hatası:", e);
    }
    state.authToken = null;
    state.isAuthenticated = false;
    localStorage.removeItem("saha_auth_token");
    sessionStorage.removeItem("saha_auth_token");
    showAuthOverlay();
    return false;
  }

  function showAuthOverlay() {
    if (!dom.authOverlay) return;
    dom.authOverlay.classList.remove("hidden");
    if (dom.authPassword) {
      dom.authPassword.value = "";
      setTimeout(() => dom.authPassword.focus(), 80);
    }
    if (dom.authErrorMsg) dom.authErrorMsg.classList.add("hidden");
  }

  function hideAuthOverlay() {
    if (!dom.authOverlay) return;
    dom.authOverlay.classList.add("hidden");
  }

  function togglePasswordVisibility() {
    if (!dom.authPassword || !dom.togglePwIcon) return;
    if (dom.authPassword.type === "password") {
      dom.authPassword.type = "text";
      dom.togglePwIcon.className = "fa-solid fa-eye-slash";
    } else {
      dom.authPassword.type = "password";
      dom.togglePwIcon.className = "fa-solid fa-eye";
    }
  }

  async function handleLogin(e) {
    if (e) e.preventDefault();
    const pw = dom.authPassword.value.trim();
    if (!pw) {
      dom.authErrorText.textContent = "Lütfen bir şifre girin.";
      dom.authErrorMsg.classList.remove("hidden");
      return;
    }

    dom.btnAuthText.classList.add("hidden");
    dom.btnAuthSpinner.classList.remove("hidden");
    dom.btnAuthSubmit.disabled = true;
    dom.authErrorMsg.classList.add("hidden");

    try {
      const res = await originalFetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: pw })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        state.authToken = data.token;
        state.isAuthenticated = true;
        if (dom.authRememberMe && dom.authRememberMe.checked) {
          localStorage.setItem("saha_auth_token", data.token);
        } else {
          sessionStorage.setItem("saha_auth_token", data.token);
        }
        hideAuthOverlay();
        loadInitialData();
      } else {
        dom.authErrorText.textContent = data.detail || "Hatalı şifre. Lütfen tekrar deneyin.";
        dom.authErrorMsg.classList.remove("hidden");
        dom.authPassword.select();
      }
    } catch (err) {
      console.error("[AUTH LOGIN ERROR]", err);
      dom.authErrorText.textContent = "Bağlantı hatası oluştu. Lütfen tekrar deneyin.";
      dom.authErrorMsg.classList.remove("hidden");
    } finally {
      dom.btnAuthText.classList.remove("hidden");
      dom.btnAuthSpinner.classList.add("hidden");
      dom.btnAuthSubmit.disabled = false;
    }
  }

  async function handleLogout() {
    if (confirm("Oturumu kapatmak istediğinize emin misiniz?")) {
      try {
        await originalFetch("/api/auth/logout", {
          method: "POST",
          headers: state.authToken ? { "Authorization": "Bearer " + state.authToken } : {}
        });
      } catch (e) {}
      state.authToken = null;
      state.isAuthenticated = false;
      localStorage.removeItem("saha_auth_token");
      sessionStorage.removeItem("saha_auth_token");
      showAuthOverlay();
    }
  }

  async function handleChangePassword() {
    if (!dom.inputOldPassword || !dom.inputNewPassword) return;
    const oldPw = dom.inputOldPassword.value.trim();
    const newPw = dom.inputNewPassword.value.trim();
    if (!oldPw || !newPw) {
      alert("Lütfen hem mevcut şifreyi hem de yeni şifreyi girin.");
      return;
    }
    if (newPw.length < 3) {
      alert("Yeni şifre en az 3 karakter olmalıdır.");
      return;
    }

    try {
      const res = await originalFetch("/api/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + state.authToken
        },
        body: JSON.stringify({ old_password: oldPw, new_password: newPw })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        if (data.token) {
          state.authToken = data.token;
          if (localStorage.getItem("saha_auth_token")) {
            localStorage.setItem("saha_auth_token", data.token);
          }
        }
        dom.inputOldPassword.value = "";
        dom.inputNewPassword.value = "";
        alert("Giriş şifreniz başarıyla değiştirildi!");
        closeModal(dom.settingsModal);
      } else {
        alert(data.detail || "Şifre değiştirilemedi. Lütfen mevcut şifrenizi kontrol edin.");
      }
    } catch (e) {
      alert("Şifre güncellenirken bağlantı hatası oluştu.");
    }
  }

  // ==========================================
  // BAŞLATMA
  // ==========================================
  init();

  async function init() {
    setupEventListeners();
    updateDatePickerUI();
    updateChatApiUI();

    const isAuthed = await checkInitialAuth();
    if (isAuthed) {
      loadInitialData();
    }

    // Canlı maçlar için 20 saniyede bir otomatik tazeleyici
    setInterval(() => {
      if (!state.isAuthenticated) return;
      const activeTab = document.querySelector(".tab-btn.active")?.dataset.tab;
      if (activeTab === "matches") {
        loadMatches(true);
      }
    }, 20000);
  }

  let isDataLoaded = false;
  function loadInitialData() {
    if (isDataLoaded) return;
    isDataLoaded = true;
    loadLeagues();
    loadMatches();
    loadStandings(state.currentLeague === "all" ? "tur.1" : state.currentLeague);
    loadCoupons(state.couponDate);
  }

  function updateChatApiUI() {
    if (dom.chatInlineApiKey) {
      dom.chatInlineApiKey.value = state.apiKey ? "••••••••••••••••" : "";
    }
    if (dom.chatApiStatusBadge) {
      if (state.apiKey) {
        dom.chatApiStatusBadge.className = "api-badge badge-emerald";
        dom.chatApiStatusBadge.innerHTML = `<i class="fa-solid fa-bolt"></i> Gemini Canlı AI Aktif`;
        dom.chatApiStatusBadge.style.color = "var(--primary)";
      } else {
        dom.chatApiStatusBadge.className = "api-badge badge-local";
        dom.chatApiStatusBadge.innerHTML = `<i class="fa-solid fa-microchip"></i> Dahili Akıllı Motor (Canlı)`;
        dom.chatApiStatusBadge.style.color = "var(--blue)";
      }
    }
  }

  // ==========================================
  // EVENT LISTENERS
  // ==========================================
  function setupEventListeners() {
    // Sekme Değişimi
    dom.tabButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        dom.tabButtons.forEach(b => b.classList.remove("active"));
        dom.tabContents.forEach(c => c.classList.remove("active"));
        btn.classList.add("active");
        const tabTarget = document.getElementById(`tab-${btn.dataset.tab}`);
        if (tabTarget) tabTarget.classList.add("active");

        if (btn.dataset.tab === "standings") {
          loadStandings(dom.standingsSelect.value);
        } else if (btn.dataset.tab === "coupons") {
          loadCoupons(state.couponDate);
        }
      });
    });

    // Kupon Tarih Seçimi
    if (dom.couponDateSelect) {
      dom.couponDateSelect.addEventListener("change", (e) => {
        state.couponDate = e.target.value;
        loadCoupons(state.couponDate);
      });
    }

    // Hızlı Gün Geçişi: Bugün
    if (dom.btnCouponToday) {
      dom.btnCouponToday.addEventListener("click", () => {
        const todayStr = (state.couponsData && state.couponsData.today) || getTodayFormatted();
        state.couponDate = todayStr;
        loadCoupons(todayStr);
      });
    }

    // Hızlı Gün Geçişi: Ertesi Gün (Yarın)
    if (dom.btnCouponTomorrow) {
      dom.btnCouponTomorrow.addEventListener("click", () => {
        const tomorrowStr = (state.couponsData && state.couponsData.tomorrow) || "";
        if (tomorrowStr) {
          state.couponDate = tomorrowStr;
          loadCoupons(tomorrowStr);
        } else {
          const d = new Date();
          d.setDate(d.getDate() + 1);
          const y = d.getFullYear();
          const m = String(d.getMonth() + 1).padStart(2, "0");
          const day = String(d.getDate()).padStart(2, "0");
          const tStr = `${y}${m}${day}`;
          state.couponDate = tStr;
          loadCoupons(tStr);
        }
      });
    }

    // Kupon Yeniden Üret
    if (dom.btnRegenCoupons) {
      dom.btnRegenCoupons.addEventListener("click", () => {
        regenerateCoupons();
      });
    }

    // Kupon Seansı Seçimi (Gündüz: 18:00 Öncesi / Akşam: 18:00 Sonrası)
    dom.couponSessionBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        dom.couponSessionBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.couponSession = btn.dataset.session;
        renderCouponSlip();
      });
    });

    // Kupon Tipi Seçimi (Value / Banko / High Odds)
    dom.couponTypeBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        dom.couponTypeBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.couponType = btn.dataset.type;
        renderCouponSlip();
      });
    });

    // Tarih Kontrolleri
    dom.btnPrevDay.addEventListener("click", () => changeDate(-1));
    dom.btnToday.addEventListener("click", () => {
      state.currentDate = getTodayFormatted();
      updateDatePickerUI();
      loadMatches();
    });
    dom.btnNextDay.addEventListener("click", () => changeDate(1));
    dom.datePicker.addEventListener("change", (e) => {
      if (e.target.value) {
        state.currentDate = e.target.value.replace(/-/g, "");
        updateDateButtons();
        loadMatches();
      }
    });

    // Arama Çubuğu
    dom.searchInput.addEventListener("input", (e) => {
      state.searchQuery = e.target.value.trim().toLowerCase();
      renderMatchesGrid();
    });

    // Durum Filtreleri
    dom.statusChips.forEach(chip => {
      chip.addEventListener("click", () => {
        dom.statusChips.forEach(c => c.classList.remove("active"));
        chip.classList.add("active");
        state.currentStatus = chip.dataset.status;
        renderMatchesGrid();
      });
    });

    // Manuel Yenileme
    dom.btnRefresh.addEventListener("click", () => {
      dom.btnRefresh.querySelector("i").classList.add("fa-spin");
      loadMatches(false).finally(() => {
        setTimeout(() => dom.btnRefresh.querySelector("i").classList.remove("fa-spin"), 600);
      });
    });

    // Modal Kapatma
    dom.btnCloseModal.addEventListener("click", () => closeModal(dom.analysisModal));
    dom.analysisModal.addEventListener("click", (e) => {
      if (e.target === dom.analysisModal) closeModal(dom.analysisModal);
    });

    // Ayarlar Modalı
    dom.btnSettings.addEventListener("click", () => {
      dom.inputApiKey.value = state.apiKey;
      openModal(dom.settingsModal);
    });
    dom.btnCloseSettings.addEventListener("click", () => closeModal(dom.settingsModal));
    dom.settingsModal.addEventListener("click", (e) => {
      if (e.target === dom.settingsModal) closeModal(dom.settingsModal);
    });
    dom.btnSaveApiKey.addEventListener("click", () => {
      state.apiKey = dom.inputApiKey.value.trim();
      localStorage.setItem("sahaici_gemini_key", state.apiKey);
      updateChatApiUI();
      alert("Ayarlar kaydedildi! Artık Google Gemini destekli canlı sohbet aktif.");
      closeModal(dom.settingsModal);
    });
    dom.btnClearApiKey.addEventListener("click", () => {
      state.apiKey = "";
      localStorage.removeItem("sahaici_gemini_key");
      dom.inputApiKey.value = "";
      updateChatApiUI();
      alert("API anahtarı temizlendi. Dahili uzman motor kullanılacak.");
    });

    // Sohbet Sekmesi İçi Canlı Gemini API Kaydetme
    if (dom.btnSaveInlineApiKey && dom.chatInlineApiKey) {
      dom.btnSaveInlineApiKey.addEventListener("click", () => {
        const val = dom.chatInlineApiKey.value.trim();
        if (val && !val.startsWith("•••")) {
          state.apiKey = val;
          localStorage.setItem("sahaici_gemini_key", val);
          dom.inputApiKey.value = val;
          updateChatApiUI();
          addPalMessage("Harika dostum! Google Gemini API anahtarın kaydedildi. Artık sorularını Gemini 2.5 Flash canlı olarak anında yanıtlayacak!");
        } else if (!val) {
          state.apiKey = "";
          localStorage.removeItem("sahaici_gemini_key");
          dom.inputApiKey.value = "";
          updateChatApiUI();
          addPalMessage("API anahtarı kaldırıldı. Dahili akıllı motorumuzla canlı sohbete devam ediyoruz.");
        }
      });
    }

    // Sesli Okuma (TTS)
    dom.btnReadAloud.addEventListener("click", () => {
      const text = dom.modalCommentaryText.innerText;
      speakText(text);
    });

    // Analiz Modalından Sohbete Geçiş
    dom.btnAskAboutMatch.addEventListener("click", () => {
      closeModal(dom.analysisModal);
      switchToChatWithMatch(state.selectedMatch);
    });

    // Sohbet Formu
    dom.chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = dom.chatInput.value.trim();
      if (!text) return;
      sendMessageToPal(text);
      dom.chatInput.value = "";
    });

    // Hazır Soru Butonları
    dom.quickButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        const query = btn.dataset.query;
        sendMessageToPal(query);
      });
    });

    // Sohbet Maç Seçimi
    dom.chatMatchSelect.addEventListener("change", (e) => {
      const eventId = e.target.value;
      if (!eventId) {
        state.selectedMatch = null;
        dom.chatSelectedMatchPreview.classList.add("hidden");
      } else {
        const match = state.matches.find(m => String(m.id) === String(eventId));
        if (match) {
          selectMatchForChat(match);
        }
      }
    });

    // Ses Aç/Kapat Butonu
    dom.btnTtsToggle.addEventListener("click", () => {
      state.isTtsEnabled = !state.isTtsEnabled;
      dom.btnTtsToggle.classList.toggle("active", state.isTtsEnabled);
      if (state.isTtsEnabled) {
        speakText("Sesli yanıt aktif edildi dostum!");
      } else {
        window.speechSynthesis?.cancel();
      }
    });

    // Puan Durumu Lig Değişimi
    dom.standingsSelect.addEventListener("change", (e) => {
      loadStandings(e.target.value);
    });

    // Auth & Şifreli Giriş Olayları
    if (dom.authForm) {
      dom.authForm.addEventListener("submit", handleLogin);
    }
    if (dom.btnTogglePassword) {
      dom.btnTogglePassword.addEventListener("click", togglePasswordVisibility);
    }
    if (dom.btnAuthLogout) {
      dom.btnAuthLogout.addEventListener("click", handleLogout);
    }
    if (dom.btnChangePassword) {
      dom.btnChangePassword.addEventListener("click", handleChangePassword);
    }
  }

  // ==========================================
  // TARİH YÖNETİMİ
  // ==========================================
  function getTodayFormatted() {
    const now = new Date();
    // 2026 zaman uyumluluğu için mevcut yerel yılı kullan
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, "0");
    const d = String(now.getDate()).padStart(2, "0");
    return `${y}${m}${d}`;
  }

  function changeDate(daysOffset) {
    const y = parseInt(state.currentDate.substring(0, 4));
    const m = parseInt(state.currentDate.substring(4, 6)) - 1;
    const d = parseInt(state.currentDate.substring(6, 8));
    
    const curDate = new Date(y, m, d);
    curDate.setDate(curDate.getDate() + daysOffset);

    const ny = curDate.getFullYear();
    const nm = String(curDate.getMonth() + 1).padStart(2, "0");
    const nd = String(curDate.getDate()).padStart(2, "0");
    state.currentDate = `${ny}${nm}${nd}`;

    updateDatePickerUI();
    loadMatches();
  }

  function updateDatePickerUI() {
    const y = state.currentDate.substring(0, 4);
    const m = state.currentDate.substring(4, 6);
    const d = state.currentDate.substring(6, 8);
    dom.datePicker.value = `${y}-${m}-${d}`;
    updateDateButtons();
  }

  function updateDateButtons() {
    const today = getTodayFormatted();
    if (state.currentDate === today) {
      dom.btnToday.classList.add("active-date");
      dom.currentDateDisplay.textContent = "Bugün";
    } else {
      dom.btnToday.classList.remove("active-date");
      const d = state.currentDate.substring(6, 8);
      const m = state.currentDate.substring(4, 6);
      dom.currentDateDisplay.textContent = `${d}.${m}.${state.currentDate.substring(0, 4)}`;
    }
  }

  // ==========================================
  // LİGLERİ YÜKLE
  // ==========================================
  async function loadLeagues() {
    try {
      const res = await fetch("/api/leagues");
      const leagues = await res.json();

      dom.leaguesContainer.innerHTML = "";
      leagues.forEach(l => {
        const btn = document.createElement("button");
        btn.className = `league-pill ${l.slug === state.currentLeague ? "active" : ""}`;
        btn.innerHTML = `<span>${l.flag}</span> <span>${l.name.replace(/^[^\s]+\s*/, '')}</span>`;
        btn.addEventListener("click", () => {
          document.querySelectorAll(".league-pill").forEach(p => p.classList.remove("active"));
          btn.classList.add("active");
          state.currentLeague = l.slug;
          dom.currentLeagueTitle.textContent = l.name;
          loadMatches();
        });
        dom.leaguesContainer.appendChild(btn);
      });
    } catch (e) {
      console.error("Ligler yüklenemedi:", e);
    }
  }

  // ==========================================
  // MAÇLARI YÜKLE
  // ==========================================
  async function loadMatches(isSilent = false) {
    if (!isSilent) {
      dom.matchesGrid.innerHTML = `
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Reel maçlar canlı veri akışından çekiliyor...</p>
        </div>
      `;
    }

    try {
      const url = `/api/matches?league=${state.currentLeague}&date=${state.currentDate}`;
      const res = await fetch(url);
      const data = await res.json();

      state.matches = data.matches || [];
      dom.lastUpdatedText.textContent = `Son güncelleme: ${new Date().toLocaleTimeString("tr-TR")}`;
      
      updateChatMatchesDropdown();
      renderMatchesGrid();
    } catch (e) {
      console.error("Maçlar yüklenirken hata:", e);
      dom.matchesGrid.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-triangle-exclamation text-yellow" style="font-size: 2rem; margin-bottom: 0.8rem;"></i>
          <p>Canlı maç verisi alınırken bir aksaklık oldu. Lütfen tekrar deneyin.</p>
          <button class="btn-primary-tool" style="margin-top: 1rem;" onclick="location.reload()">Sayfayı Yenile</button>
        </div>
      `;
    }
  }

  // ==========================================
  // MAÇ KARTLARINI ÇİZ
  // ==========================================
  // ==========================================
  // MAÇ KARTLARINI ÇİZ
  // ==========================================
  function renderMatchesGrid() {
    let filtered = [...state.matches];

    // Durum Filtresi
    if (state.currentStatus === "live") {
      filtered = filtered.filter(m => m.state === "in");
    } else if (state.currentStatus === "scheduled") {
      filtered = filtered.filter(m => m.state === "pre");
    } else if (state.currentStatus === "finished") {
      filtered = filtered.filter(m => m.state === "post");
    }

    // Arama Filtresi
    if (state.searchQuery) {
      filtered = filtered.filter(m => 
        m.home.name.toLowerCase().includes(state.searchQuery) ||
        m.away.name.toLowerCase().includes(state.searchQuery) ||
        m.league_name.toLowerCase().includes(state.searchQuery) ||
        (m.venue && m.venue.toLowerCase().includes(state.searchQuery))
      );
    }

    // Sıralama Mantığı: Canlı (0) -> Bitenler (1) -> Oynanacaklar (2, saate göre)
    filtered.sort((a, b) => {
      const stateOrder = { "in": 0, "post": 1, "pre": 2 };
      const orderA = stateOrder[a.state] ?? 2;
      const orderB = stateOrder[b.state] ?? 2;
      if (orderA !== orderB) return orderA - orderB;
      return (a.date || "").localeCompare(b.date || "");
    });

    // Sayaçları Güncelle
    const allCount = state.matches.length;
    const liveCount = state.matches.filter(m => m.state === "in").length;
    const schedCount = state.matches.filter(m => m.state === "pre").length;
    const finCount = state.matches.filter(m => m.state === "post").length;

    dom.countAll.textContent = allCount;
    dom.countLive.textContent = liveCount;
    dom.countScheduled.textContent = schedCount;
    dom.countFinished.textContent = finCount;

    // CANLI VE BİTEN MAÇLAR ÖZEL SKOR PANOSU (Ana Sayfada hemen görünsün)
    const liveMatches = state.matches.filter(m => m.state === "in");
    const finishedMatches = state.matches.filter(m => m.state === "post");

    if (dom.liveFinishedShowcase && dom.showcaseCardsContainer) {
      if (liveMatches.length > 0 || finishedMatches.length > 0) {
        dom.liveFinishedShowcase.classList.remove("hidden");
        if (dom.showcaseLiveCount) {
          dom.showcaseLiveCount.innerHTML = `<span class="live-indicator"></span> ${liveMatches.length} Canlı`;
        }
        if (dom.showcaseFinishedCount) {
          dom.showcaseFinishedCount.innerHTML = `<i class="fa-solid fa-flag-checkered"></i> ${finishedMatches.length} Bitti`;
        }

        dom.showcaseCardsContainer.innerHTML = "";
        [...liveMatches, ...finishedMatches].forEach(sm => {
          const scCard = createShowcaseCard(sm);
          dom.showcaseCardsContainer.appendChild(scCard);
        });
      } else {
        dom.liveFinishedShowcase.classList.add("hidden");
      }
    }

    if (filtered.length === 0) {
      dom.matchesGrid.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-futbol text-muted" style="font-size: 2.4rem; margin-bottom: 0.8rem;"></i>
          <h3>Bu kriterlere uygun maç bulunamadı</h3>
          <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.4rem;">
            Seçilen ligde veya tarihte maç görünmüyor. Üstteki lig rozetlerinden "Tüm Dünya Maçları" veya başka bir tarihi deneyebilirsiniz.
          </p>
        </div>
      `;
      return;
    }

    dom.matchesGrid.innerHTML = "";
    filtered.forEach(m => {
      const card = createMatchCard(m);
      dom.matchesGrid.appendChild(card);
    });
  }

  function createShowcaseCard(m) {
    const card = document.createElement("div");
    const isLive = m.state === "in";
    card.className = `showcase-card ${isLive ? "is-live" : "is-finished"}`;

    const homeLogo = m.home.logo
      ? `<img src="${m.home.logo}" alt="${m.home.name}" style="width:20px; height:20px; object-fit:contain;" onerror="this.src='/static/fallback.png'">`
      : `<i class="fa-solid fa-shield text-muted" style="font-size:14px;"></i>`;
    const awayLogo = m.away.logo
      ? `<img src="${m.away.logo}" alt="${m.away.name}" style="width:20px; height:20px; object-fit:contain;" onerror="this.src='/static/fallback.png'">`
      : `<i class="fa-solid fa-shield text-muted" style="font-size:14px;"></i>`;

    let badge = "";
    if (isLive) {
      badge = `<span class="showcase-pill pill-live"><span class="live-dot-pulse"></span> ${m.clock ? m.clock + "'" : "CANLI"}</span>`;
    } else {
      badge = `<span class="showcase-pill pill-finished"><i class="fa-solid fa-flag-checkered"></i> MS Bitti</span>`;
    }

    let statsRow = "";
    if (m.live_stats) {
      const ls = m.live_stats;
      const hPoss = Math.round(parseFloat(ls.homePossession || 50));
      const aPoss = 100 - hPoss;
      const hShots = ls.homeShots ?? 0;
      const aShots = ls.awayShots ?? 0;
      const hCorners = ls.homeCorners ?? 0;
      const aCorners = ls.awayCorners ?? 0;
      statsRow = `
        <div class="showcase-card-stats">
          <span>%${hPoss}-%${aPoss}</span>
          <span>Şut: ${hShots}-${aShots}</span>
          <span>Krn: ${hCorners}-${aCorners}</span>
        </div>
      `;
    }

    card.innerHTML = `
      <div class="showcase-card-top">
        <span class="showcase-league-name" title="${m.league_name}">${m.league_name}</span>
        ${badge}
      </div>

      <div class="showcase-card-matchup">
        <div class="showcase-team">
          ${homeLogo}
          <span class="showcase-team-name">${m.home.name}</span>
        </div>

        <div class="showcase-score ${isLive ? 'score-live' : 'score-finished'}">
          ${m.home.score} - ${m.away.score}
        </div>

        <div class="showcase-team away">
          <span class="showcase-team-name">${m.away.name}</span>
          ${awayLogo}
        </div>
      </div>

      ${statsRow}
    `;

    card.addEventListener("click", () => openAnalysisModal(m));
    return card;
  }

  function createMatchCard(m) {
    const card = document.createElement("div");
    const isLive = m.state === "in";
    const isPost = m.state === "post";
    card.className = `mackolik-row ${isLive ? "is-live" : (isPost ? "is-finished" : "is-pre")}`;

    // Maçkolik stili durum rozeti / dakika
    let statusColHtml = "";
    if (isLive) {
      statusColHtml = `
        <div class="row-status-col live" title="Canlı Maç">
          <span class="live-dot-pulse"></span>
          <span class="row-clock">${m.clock ? m.clock + "'" : "CANLI"}</span>
        </div>
      `;
    } else if (isPost) {
      statusColHtml = `
        <div class="row-status-col finished" title="Maç Sonu (Bitti)">
          <span class="row-ms-tag">MS</span>
        </div>
      `;
    } else {
      let timeStr = m.status_tr;
      if (m.date) {
        try {
          const d = new Date(m.date);
          timeStr = d.toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" });
        } catch (e) {}
      }
      statusColHtml = `
        <div class="row-status-col pre" title="Başlama Saati">
          <span class="row-time">${timeStr}</span>
        </div>
      `;
    }

    // Skor Kutusu
    let scoreColHtml = "";
    if (["in", "post"].includes(m.state)) {
      scoreColHtml = `
        <div class="row-score-col ${isLive ? 'score-live' : 'score-finished'}">
          <span class="score-num home-sc">${m.home.score}</span>
          <span class="score-sep">-</span>
          <span class="score-num away-sc">${m.away.score}</span>
        </div>
      `;
    } else {
      scoreColHtml = `
        <div class="row-score-col score-pre">
          <span class="vs-text">v</span>
        </div>
      `;
    }

    // Takım logoları
    const homeLogo = m.home.logo 
      ? `<img src="${m.home.logo}" alt="${m.home.name}" class="row-crest" onerror="this.src='/static/fallback.png'">`
      : `<i class="fa-solid fa-shield text-muted row-fallback-icon"></i>`;
    
    const awayLogo = m.away.logo 
      ? `<img src="${m.away.logo}" alt="${m.away.name}" class="row-crest" onerror="this.src='/static/fallback.png'">`
      : `<i class="fa-solid fa-shield text-muted row-fallback-icon"></i>`;

    // Mini İstatistik hapı (Canlı ve biten maçlar için)
    let miniStatsHtml = "";
    if ((isLive || isPost) && m.live_stats) {
      const ls = m.live_stats;
      const hPoss = Math.round(parseFloat(ls.homePossession || 50));
      const aPoss = 100 - hPoss;
      const hShots = ls.homeShots ?? 0;
      const aShots = ls.awayShots ?? 0;
      const hCorners = ls.homeCorners ?? 0;
      const aCorners = ls.awayCorners ?? 0;
      miniStatsHtml = `
        <div class="row-mini-stats" title="Topla Oynama: %${hPoss}-%${aPoss} | Şut: ${hShots}-${aShots} | Korner: ${hCorners}-${aCorners}">
          <span><i class="fa-solid fa-chart-pie text-emerald"></i> %${hPoss}-%${aPoss}</span>
          <span><i class="fa-solid fa-bullseye text-blue"></i> ${hShots}-${aShots}</span>
          <span><i class="fa-solid fa-flag text-yellow"></i> ${hCorners}-${aCorners}</span>
        </div>
      `;
    } else {
      miniStatsHtml = `
        <div class="row-league-tag" title="${m.league_name}">
          <span>${m.league_name}</span>
        </div>
      `;
    }

    card.innerHTML = `
      <div class="row-left-main" title="Detaylı Analizi Aç">
        ${statusColHtml}

        <div class="row-teams-matchup">
          <div class="row-team row-home ${isPost && parseInt(m.home.score) > parseInt(m.away.score) ? 'team-winner' : ''}">
            <span class="row-team-title">${m.home.name}</span>
            ${homeLogo}
          </div>

          ${scoreColHtml}

          <div class="row-team row-away ${isPost && parseInt(m.away.score) > parseInt(m.home.score) ? 'team-winner' : ''}">
            ${awayLogo}
            <span class="row-team-title">${m.away.name}</span>
          </div>
        </div>
      </div>

      <div class="row-right-tools">
        ${miniStatsHtml}

        <div class="row-btn-group">
          <button class="btn-row-analyze" title="Detaylı Analiz, Tahmin ve İstatistikler">
            <i class="fa-solid ${isPost ? 'fa-clipboard-check' : (isLive ? 'fa-chart-pie' : 'fa-chart-simple')}"></i>
            <span>${isPost ? 'Rapor' : (isLive ? 'Canlı' : 'Analiz')}</span>
          </button>
          <button class="btn-row-ask" title="Taktik Serdar'a Bu Maçı Sor">
            <i class="fa-solid fa-comments"></i>
            <span>Serdar</span>
          </button>
        </div>
      </div>
    `;

    // Tıklama olayları: Satırın herhangi bir yerine tıklayınca analiz modalı açılır, Serdar'a tıklandığında sohbete geçer
    card.querySelector(".row-left-main").addEventListener("click", () => openAnalysisModal(m));
    card.querySelector(".btn-row-analyze").addEventListener("click", (e) => {
      e.stopPropagation();
      openAnalysisModal(m);
    });
    card.querySelector(".btn-row-ask").addEventListener("click", (e) => {
      e.stopPropagation();
      switchToChatWithMatch(m);
    });

    return card;
  }

  // ==========================================
  // DERİN MAÇ ANALİZ MODALI
  // ==========================================
  function resetModalLiveSection() {
    if (!dom.modalLiveSection) return;
    dom.modalLiveSection.classList.add("hidden");
    if (dom.liveClockBadge) dom.liveClockBadge.textContent = "CANLI";
    if (dom.liveHomePoss) dom.liveHomePoss.textContent = "%50";
    if (dom.liveAwayPoss) dom.liveAwayPoss.textContent = "%50";
    if (dom.barLiveHomePoss) dom.barLiveHomePoss.style.width = "50%";
    if (dom.barLiveAwayPoss) dom.barLiveAwayPoss.style.width = "50%";
    if (dom.liveHomeShots) dom.liveHomeShots.textContent = "0";
    if (dom.liveAwayShots) dom.liveAwayShots.textContent = "0";
    if (dom.liveHomeOnGoal) dom.liveHomeOnGoal.textContent = "0";
    if (dom.liveAwayOnGoal) dom.liveAwayOnGoal.textContent = "0";
    if (dom.liveHomeCorners) dom.liveHomeCorners.textContent = "0";
    if (dom.liveAwayCorners) dom.liveAwayCorners.textContent = "0";
    if (dom.liveHomeFouls) dom.liveHomeFouls.textContent = "0";
    if (dom.liveAwayFouls) dom.liveAwayFouls.textContent = "0";
    if (dom.liveLblHome) dom.liveLblHome.textContent = "MS 1";
    if (dom.liveLblAway) dom.liveLblAway.textContent = "MS 2";
    if (dom.livePctHome) dom.livePctHome.textContent = "%0";
    if (dom.livePctDraw) dom.livePctDraw.textContent = "%0";
    if (dom.livePctAway) dom.livePctAway.textContent = "%0";
    if (dom.liveNextHomeName) dom.liveNextHomeName.textContent = "Ev Sahibi";
    if (dom.liveNextAwayName) dom.liveNextAwayName.textContent = "Deplasman";
    if (dom.liveNextHomePct) dom.liveNextHomePct.textContent = "%0";
    if (dom.liveNextNoGoalPct) dom.liveNextNoGoalPct.textContent = "%0";
    if (dom.liveNextAwayPct) dom.liveNextAwayPct.textContent = "%0";
    if (dom.liveCornerPick) dom.liveCornerPick.textContent = "Canlı Korner Bekleniyor";
    if (dom.liveCornerProjDetail) dom.liveCornerProjDetail.textContent = "-";
    if (dom.liveLine1Name) dom.liveLine1Name.textContent = "Canlı Gol 1";
    if (dom.liveLine1Pct) dom.liveLine1Pct.textContent = "%0";
    if (dom.liveLine2Name) dom.liveLine2Name.textContent = "Canlı Gol 2";
    if (dom.liveLine2Pct) dom.liveLine2Pct.textContent = "%0";
  }

  async function openAnalysisModal(m) {
    // 1. Önceki tüm periyodik sorguları ve bekleyen HTTP isteklerini anında iptal et
    if (state.modalPollInterval) {
      clearInterval(state.modalPollInterval);
      state.modalPollInterval = null;
    }
    if (state.modalAbortController) {
      state.modalAbortController.abort();
      state.modalAbortController = null;
    }

    state.selectedMatch = m;
    openModal(dom.analysisModal);

    // 2. Canlı istatistik ve maç istatistikleri kutularını sıfırla ve gizle (Kesinlikle başka maçın verisi sızamaz)
    resetModalLiveSection();
    const statsSec = document.getElementById("modalStatsSection");
    if (statsSec) statsSec.style.display = "none";
    const boxContainer = document.getElementById("modalBoxscoreContainer");
    if (boxContainer) boxContainer.innerHTML = "";

    // 3. Başlık bilgilerini doldur
    dom.modalLeague.textContent = m.league_name;
    dom.modalHomeName.textContent = m.home.name;
    dom.modalAwayName.textContent = m.away.name;
    dom.modalHomeLogo.src = m.home.logo || "";
    dom.modalAwayLogo.src = m.away.logo || "";
    dom.modalVenue.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${m.venue || "Stadyum Belirtilmedi"}`;

    if (["in", "post"].includes(m.state)) {
      dom.modalScoreDisplay.textContent = `${m.home.score} : ${m.away.score}`;
      dom.modalStatusBadge.textContent = m.status_tr;
    } else {
      dom.modalScoreDisplay.textContent = "VS";
      dom.modalStatusBadge.textContent = m.status_tr;
    }

    // Yükleniyor durumu
    dom.modalCommentaryText.innerHTML = `
      <div style="display:flex; align-items:center; gap:0.6rem; color:var(--text-muted);">
        <div class="spinner" style="width:24px; height:24px; margin:0;"></div>
        <span>Taktik Serdar maç verilerini masaya yatırıyor, canlı istatistik ve formül çalıştırılıyor...</span>
      </div>
    `;

    if (dom.modalSmartBetsList) {
      dom.modalSmartBetsList.innerHTML = `
        <div style="display:flex; align-items:center; gap:0.6rem; color:var(--text-muted); padding:0.8rem 0.2rem; grid-column: 1 / -1;">
          <div class="spinner" style="width:20px; height:20px; margin:0;"></div>
          <span>Bu maç için en mantıklı ve oynanabilir bahis seçenekleri hesaplanıyor...</span>
        </div>
      `;
    }

    const controller = new AbortController();
    state.modalAbortController = controller;

    async function fetchAnalysis(isSilent = false) {
      try {
        const res = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
          body: JSON.stringify({
            league: m.league_key || state.currentLeague,
            event_id: String(m.id)
          })
        });

        if (!res.ok) throw new Error("HTTP error " + res.status);
        const data = await res.json();

        // Yanıt geldiğinde modal hala açık mı ve bu maç mı seçili? (Race condition koruması)
        if (!state.selectedMatch || String(data.match?.id) !== String(m.id) || String(state.selectedMatch.id) !== String(m.id)) {
          console.warn("Farklı maçın analiz yanıtı atlandı:", data.match?.id);
          return;
        }

        renderAnalysisContent(data, isSilent);

        // Yalnızca bu maç GERÇEKTEN canlıysa (state === 'in') ve modal açıksa periyodik güncelleme başlat
        if (data.inPlay && data.inPlay.isLive && data.match?.state === "in" && !state.modalPollInterval) {
          state.modalPollInterval = setInterval(() => {
            if (dom.analysisModal.classList.contains("hidden") || !state.selectedMatch || String(state.selectedMatch.id) !== String(m.id)) {
              clearInterval(state.modalPollInterval);
              state.modalPollInterval = null;
              return;
            }
            fetchAnalysis(true);
          }, 12000);
        }
      } catch (e) {
        if (e.name === "AbortError") {
          return;
        }
        console.error("Analiz yüklenemedi:", e);
        if (!isSilent) {
          dom.modalCommentaryText.textContent = "Analiz hazırlanırken bir sorun oluştu. Lütfen tekrar deneyin.";
        }
      }
    }

    await fetchAnalysis(false);
  }

  function renderAnalysisContent(data, isSilent = false) {
    // KORUMA: Eğer gelen veri şu an modalda açık olan maça ait değilse ASLA EKRANA BASMA!
    if (!state.selectedMatch || (data.match && String(data.match.id) !== String(state.selectedMatch.id))) {
      console.warn("Farklı maça ait analiz yanıtı engellendi:", data.match?.id, "Aktif maç:", state.selectedMatch?.id);
      return;
    }

    const { probabilities: probs, commentary, detail, inPlay, match } = data;

    // Başlık skor ve dakikayı canlı güncelle (Sadece bu maç için)
    if (match && String(match.id) === String(state.selectedMatch.id)) {
      if (["in", "post"].includes(match.state)) {
        dom.modalScoreDisplay.textContent = `${match.home.score} : ${match.away.score}`;
        dom.modalStatusBadge.textContent = match.status_tr;
      }
    }

    // Serdar'ın Yorumu
    dom.modalCommentaryText.innerText = commentary;

    // Mantıklı & Oynanabilir Bahis Önerileri
    renderSmartRecommendations(data.smartRecommendations || []);

    // CANLI OYUN MERKEZİ & İSTATİSTİKSEL YENİDEN DEĞERLENDİRME
    // KORUMA: Maç ID + state kontrolü — başka maçın canlı verisi KESİNLİKLE sızamaz
    const isActuallyLive = (match?.state === "in");
    const liveMatchIdValid = match && state.selectedMatch && String(match.id) === String(state.selectedMatch.id);
    if (inPlay && inPlay.isLive && isActuallyLive && liveMatchIdValid && dom.modalLiveSection) {
      dom.modalLiveSection.classList.remove("hidden");
      const ls = inPlay.liveStats || {};
      const lp = inPlay.liveProbabilities || {};

      dom.liveClockBadge.textContent = `CANLI ${inPlay.elapsedMin}'`;

      // Topla Oynama
      const hPoss = Math.round(parseFloat(ls.homePossession || 50));
      const aPoss = 100 - hPoss;
      dom.liveHomePoss.textContent = `%${hPoss}`;
      dom.liveAwayPoss.textContent = `%${aPoss}`;
      dom.barLiveHomePoss.style.width = `${hPoss}%`;
      dom.barLiveAwayPoss.style.width = `${aPoss}%`;

      // Şut, İsabetli Şut, Korner, Faul
      dom.liveHomeShots.textContent = ls.homeShots ?? 0;
      dom.liveAwayShots.textContent = ls.awayShots ?? 0;
      dom.liveHomeOnGoal.textContent = ls.homeShotsOnTarget ?? 0;
      dom.liveAwayOnGoal.textContent = ls.awayShotsOnTarget ?? 0;
      dom.liveHomeCorners.textContent = ls.homeCorners ?? 0;
      dom.liveAwayCorners.textContent = ls.awayCorners ?? 0;
      dom.liveHomeFouls.textContent = ls.homeFouls ?? 0;
      dom.liveAwayFouls.textContent = ls.awayFouls ?? 0;

      // Canlı 1X2 İhtimalleri (Sadece seçili maçın takımları!)
      const homeShort = match?.home?.shortName || match?.home?.name || state.selectedMatch?.home?.shortName || state.selectedMatch?.home?.name || "Ev";
      const awayShort = match?.away?.shortName || match?.away?.name || state.selectedMatch?.away?.shortName || state.selectedMatch?.away?.name || "Dep";
      dom.liveLblHome.textContent = `MS 1 (${homeShort})`;
      dom.liveLblAway.textContent = `MS 2 (${awayShort})`;
      dom.livePctHome.textContent = `%${lp.homeWinPct ?? 0}`;
      dom.livePctDraw.textContent = `%${lp.drawPct ?? 0}`;
      dom.livePctAway.textContent = `%${lp.awayWinPct ?? 0}`;

      // Sıradaki Golü Kim Atar?
      dom.liveNextHomeName.textContent = homeShort;
      dom.liveNextAwayName.textContent = awayShort;
      dom.liveNextHomePct.textContent = `%${lp.nextHomePct ?? 0}`;
      dom.liveNextNoGoalPct.textContent = `%${lp.noMoreGoalsPct ?? 0}`;
      dom.liveNextAwayPct.textContent = `%${lp.nextAwayPct ?? 0}`;

      // Canlı Korner Projeksiyonu
      dom.liveCornerPick.textContent = lp.cornerPick || "Canlı Korner Analiz Ediliyor";
      dom.liveCornerProjDetail.textContent = `Şu an: ${ls.totalCorners ?? 0} Korner | Tahmini Bitiş: ~${lp.projectedCorners ?? 0} Korner`;

      // Canlı Dinamik Gol Barajı
      dom.liveLine1Name.textContent = lp.line1Name || "Canlı Gol 1";
      dom.liveLine1Pct.textContent = `%${lp.line1Pct ?? 0}`;
      dom.liveLine2Name.textContent = lp.line2Name || "Canlı Gol 2";
      dom.liveLine2Pct.textContent = `%${lp.line2Pct ?? 0}`;
    } else {
      // Maç canlı değilse canlı bölümünü KESİNLİKLE gizle ve sıfırla
      resetModalLiveSection();
    }

    // 1-X-2 Olasılık Barı
    dom.barHome.style.width = `${probs.homeWinPct}%`;
    dom.barDraw.style.width = `${probs.drawPct}%`;
    dom.barAway.style.width = `${probs.awayWinPct}%`;

    dom.labelHomeWin.textContent = `MS 1 (%${probs.homeWinPct})`;
    dom.labelDraw.textContent = `Beraberlik (%${probs.drawPct})`;
    dom.labelAwayWin.textContent = `MS 2 (%${probs.awayWinPct})`;

    // Mini Kart Metrikleri
    dom.valOver25.textContent = `%${probs.over25Pct}`;
    dom.valUnder25.textContent = `Alt: %${probs.under25Pct}`;
    
    dom.valBtts.textContent = `%${probs.bttsYesPct}`;
    dom.valBttsNo.textContent = `KG Yok: %${probs.bttsNoPct}`;

    const topScore = probs.topScores?.[0];
    dom.valTopScore.textContent = topScore ? topScore.score : "-";
    dom.valTopScoreProb.textContent = topScore ? `İhtimal: %${topScore.prob}` : "";

    dom.valRisk.textContent = probs.riskLevel || "Dengeli";
    dom.valPickSub.textContent = `Öneri: ${probs.primaryPick}`;

    // Son 5 Maç (Form)
    if (detail?.lastFive && detail.lastFive.length > 0) {
      dom.modalFormGrid.innerHTML = "";
      detail.lastFive.forEach(tf => {
        const teamBlock = document.createElement("div");
        teamBlock.className = "form-team-card";
        
        let gamesHtml = "";
        (tf.games || []).slice(0, 5).forEach(g => {
          const resClass = g.result === "W" ? "res-w" : (g.result === "D" ? "res-d" : "res-l");
          const resTr = g.result === "W" ? "G" : (g.result === "D" ? "B" : "M");
          gamesHtml += `
            <div class="form-match-row">
              <span class="res-tag ${resClass}">${resTr}</span>
              <span style="flex:1; margin-left:0.5rem; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">vs ${g.opponent}</span>
              <strong style="color:var(--text-primary); font-family:monospace;">${g.score}</strong>
            </div>
          `;
        });

        teamBlock.innerHTML = `
          <div class="form-team-header">
            ${tf.logo ? `<img src="${tf.logo}" style="width:20px; height:20px; object-fit:contain;">` : ""}
            <span>${tf.team}</span>
          </div>
          <div>${gamesHtml || "<small style='color:var(--text-muted);'>Kayıt bulunamadı</small>"}</div>
        `;
        dom.modalFormGrid.appendChild(teamBlock);
      });
      document.getElementById("modalFormSection").style.display = "block";
    } else {
      document.getElementById("modalFormSection").style.display = "none";
    }

    // Bahis Oranları (Odds)
    if (detail?.odds && detail.odds.length > 0) {
      dom.modalOddsList.innerHTML = "";
      detail.odds.forEach(o => {
        const oddCard = document.createElement("div");
        oddCard.className = "odd-card";
        oddCard.innerHTML = `
          <div class="odd-title">${o.provider} - Detay: ${o.details || "Standart"}</div>
          <div class="odd-value">Alt/Üst: ${o.overUnder || "2.5"} Gol</div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">
            Handikap: ${o.spread || "0"} | Ev: ${o.homeOdds || "-"} | Dep: ${o.awayOdds || "-"}
          </div>
        `;
        dom.modalOddsList.appendChild(oddCard);
      });
      document.getElementById("modalOddsSection").style.display = "block";
    } else {
      document.getElementById("modalOddsSection").style.display = "none";
    }

    // Kadrolar (Rosters)
    if (detail?.rosters && detail.rosters.length > 0) {
      dom.modalRostersGrid.innerHTML = "";
      detail.rosters.forEach(r => {
        const rBlock = document.createElement("div");
        rBlock.className = "form-team-card";
        let playersHtml = "";
        (r.players || []).forEach(p => {
          playersHtml += `
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; padding:2px 0;">
              <span><strong>#${p.jersey || "-"}</strong> ${p.name}</span>
              <span style="color:var(--blue); font-weight:600;">${p.pos || ""}</span>
            </div>
          `;
        });
        rBlock.innerHTML = `
          <div class="form-team-header">
            <span>${r.team}</span>
            <small style="color:var(--primary);">${r.formation ? `Diziliş: ${r.formation}` : ""}</small>
          </div>
          <div>${playersHtml}</div>
        `;
        dom.modalRostersGrid.appendChild(rBlock);
      });
      document.getElementById("modalRostersSection").style.display = "block";
    } else {
      document.getElementById("modalRostersSection").style.display = "none";
    }

    // Maç İstatistikleri (Boxscore - Biten ve Canlı Maçlar İçin)
    // KORUMA: Üç katmanlı doğrulama - yanlış maçın istatistiği KESİNLİKLE gösterilemez
    const statsSec = document.getElementById("modalStatsSection");
    const boxContainer = document.getElementById("modalBoxscoreContainer");
    const hasLiveStats = (match?.live_stats && Object.keys(match.live_stats).length > 0);
    const hasBoxscore = (detail?.boxscore && detail.boxscore.length > 0);

    // Katman 1: Maç ID doğrulaması — modal hala aynı maça mı bakıyor?
    const boxscoreMatchValid = match && state.selectedMatch && String(match.id) === String(state.selectedMatch.id);

    // Katman 2: State kontrolü — sadece canlı veya bitmiş maçlar istatistik gösterebilir
    const boxscoreStateValid = ["post", "in"].includes(match?.state);

    // Katman 3: Boxscore takım ismi doğrulaması — detail.boxscore'daki takımlar gerçekten bu maçın takımları mı?
    let boxscoreTeamsValid = true;
    if (hasBoxscore && match) {
      const modalHome = (match.home?.name || "").toLowerCase();
      const modalAway = (match.away?.name || "").toLowerCase();
      const boxTeamNames = detail.boxscore.map(b => (b.team || "").toLowerCase());
      const homeFoundInBox = boxTeamNames.some(bt => bt.includes(modalHome) || modalHome.includes(bt));
      const awayFoundInBox = boxTeamNames.some(bt => bt.includes(modalAway) || modalAway.includes(bt));
      if (!homeFoundInBox || !awayFoundInBox) {
        console.warn(`[BOXSCORE KORUMA] Takım ismi uyuşmazlığı! Modal: ${modalHome} vs ${modalAway}, Boxscore: ${boxTeamNames.join(", ")}`);
        boxscoreTeamsValid = false;
      }
    }

    if (boxscoreMatchValid && boxscoreStateValid && (hasLiveStats || (hasBoxscore && boxscoreTeamsValid)) && statsSec && boxContainer) {
      boxContainer.innerHTML = "";
      statsSec.style.display = "block";

      let hPoss = 50, aPoss = 50, hShots = 0, aShots = 0, hOnGoal = 0, aOnGoal = 0;
      let hCorners = 0, aCorners = 0, hFouls = 0, aFouls = 0;

      if (hasLiveStats) {
        const ls = match.live_stats;
        hPoss = Math.round(parseFloat(ls.homePossession || 50));
        aPoss = 100 - hPoss;
        hShots = ls.homeShots ?? 0;
        aShots = ls.awayShots ?? 0;
        hOnGoal = ls.homeShotsOnTarget ?? 0;
        aOnGoal = ls.awayShotsOnTarget ?? 0;
        hCorners = ls.homeCorners ?? 0;
        aCorners = ls.awayCorners ?? 0;
        hFouls = ls.homeFouls ?? 0;
        aFouls = ls.awayFouls ?? 0;
      }

      const homeName = match?.home?.name || "Ev Sahibi";
      const awayName = match?.away?.name || "Deplasman";
      const homeScore = match?.home?.score || "0";
      const awayScore = match?.away?.score || "0";
      const isFinished = match?.state === "post";

      boxContainer.innerHTML = `
        <div class="boxscore-card">
          <div class="boxscore-header-teams">
            <span style="color:var(--primary); font-size:0.95rem;">${homeName} (${homeScore})</span>
            <span style="color:var(--text-muted); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.5px;">
              ${isFinished ? '🏁 NİHAİ MAÇ İSTATİSTİKLERİ' : '🔴 CANLI MAÇ İSTATİSTİKLERİ'}
            </span>
            <span style="color:var(--blue); font-size:0.95rem;">(${awayScore}) ${awayName}</span>
          </div>

          <!-- Topla Oynama -->
          <div class="boxscore-stat-row">
            <div class="boxscore-stat-labels">
              <span style="color:var(--primary); font-weight:800;">%${hPoss}</span>
              <span class="boxscore-stat-name">Topla Oynama</span>
              <span style="color:var(--blue); font-weight:800;">%${aPoss}</span>
            </div>
            <div class="dual-progress-bar">
              <div class="dual-bar-home" style="width: ${hPoss}%;"></div>
              <div class="dual-bar-away" style="width: ${aPoss}%;"></div>
            </div>
          </div>

          <!-- Şutlar -->
          <div class="boxscore-stat-row">
            <div class="boxscore-stat-labels">
              <span><strong>${hShots}</strong> (${hOnGoal} İsabetli)</span>
              <span class="boxscore-stat-name">Toplam Şut (İsabetli)</span>
              <span><strong>${aShots}</strong> (${aOnGoal} İsabetli)</span>
            </div>
          </div>

          <!-- Kornerler -->
          <div class="boxscore-stat-row">
            <div class="boxscore-stat-labels">
              <span style="color:var(--yellow); font-weight:800;">${hCorners}</span>
              <span class="boxscore-stat-name">Kornerler (Toplam: ${hCorners + aCorners})</span>
              <span style="color:var(--yellow); font-weight:800;">${aCorners}</span>
            </div>
          </div>

          <!-- Fauller -->
          <div class="boxscore-stat-row" style="margin-bottom:0;">
            <div class="boxscore-stat-labels">
              <span>${hFouls}</span>
              <span class="boxscore-stat-name">Fauller</span>
              <span>${aFouls}</span>
            </div>
          </div>
        </div>
      `;
    } else {
      if (statsSec) statsSec.style.display = "none";
      if (boxContainer) boxContainer.innerHTML = "";
    }
  }

  function renderSmartRecommendations(smartRecs) {
    if (!dom.modalSmartBetsList) return;
    dom.modalSmartBetsList.innerHTML = "";

    if (!smartRecs || smartRecs.length === 0) {
      if (dom.modalSmartBetsSection) dom.modalSmartBetsSection.classList.add("hidden");
      return;
    }

    if (dom.modalSmartBetsSection) dom.modalSmartBetsSection.classList.remove("hidden");

    smartRecs.forEach(rec => {
      const card = document.createElement("div");
      card.className = `smart-bet-card cat-${rec.category || 'value'}`;

      const iconClass = rec.icon || "fa-bullseye";
      const oddsDisplay = rec.odds ? `x${Number(rec.odds).toFixed(2)}` : "-";
      const confDisplay = rec.confidence ? `%${rec.confidence}` : "";

      card.innerHTML = `
        <div class="smart-bet-top">
          <span class="rec-badge ${rec.badge_class || 'rec-badge-value'}">
            <i class="fa-solid ${iconClass}"></i> ${rec.category_title || 'Öneri'}
          </span>
          ${confDisplay ? `<span class="smart-bet-confidence" title="Algoritma Güven Derecesi"><i class="fa-solid fa-gauge-high"></i> Güven: <span class="confidence-val">${confDisplay}</span></span>` : ''}
        </div>
        <div class="smart-bet-main">
          <div class="smart-bet-market">${rec.market || 'Bahis Pazarı'}</div>
          <div class="smart-bet-pick-row">
            <div class="smart-bet-pick">${rec.pick || ''}</div>
            <div class="smart-bet-odds" title="Bilyoner / İddaa Oranı">${oddsDisplay}</div>
          </div>
        </div>
        <div class="smart-bet-reason">
          <i class="fa-solid fa-circle-info"></i> ${rec.reason || ''}
        </div>
      `;
      dom.modalSmartBetsList.appendChild(card);
    });
  }

  // ==========================================
  // SOHBET (FUTBOL ARKADAŞI SERDAR)
  // ==========================================
  function updateChatMatchesDropdown() {
    dom.chatMatchSelect.innerHTML = `<option value="">🌍 Genel Futbol Sohbeti</option>`;
    state.matches.forEach(m => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = `${m.home.name} vs ${m.away.name} (${m.league_name})`;
      dom.chatMatchSelect.appendChild(opt);
    });
  }

  function switchToChatWithMatch(m) {
    selectMatchForChat(m);
    
    // Sohbete geç
    dom.tabButtons.forEach(b => b.classList.remove("active"));
    dom.tabContents.forEach(c => c.classList.remove("active"));
    const chatTabBtn = document.querySelector(`.tab-btn[data-tab="chat"]`);
    if (chatTabBtn) chatTabBtn.classList.add("active");
    const chatTabContent = document.getElementById("tab-chat");
    if (chatTabContent) chatTabContent.classList.add("active");

    // Otomatik selamlama ve soru tetikle
    addPalMessage(`Hocam ${m.home.name} - ${m.away.name} maçını masaya getirdin, harika tercih! Bu maç hakkında kafana ne takıldı? KG Var mı, 2.5 üst mü, yoksa sürpriz ihtimali mi konuşalım?`);
  }

  function selectMatchForChat(m) {
    state.selectedMatch = m;
    dom.chatMatchSelect.value = m.id;
    dom.prevHomeName.textContent = m.home.name;
    dom.prevAwayName.textContent = m.away.name;
    dom.prevStatus.textContent = m.status_tr;
    dom.prevPick.textContent = `Lig: ${m.league_name}`;
    dom.chatSelectedMatchPreview.classList.remove("hidden");
  }

  async function sendMessageToPal(text) {
    addUserMessage(text);
    const thinkingId = addPalThinkingMessage();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: text,
          league: state.selectedMatch ? (state.selectedMatch.league_key || state.currentLeague) : "all",
          event_id: state.selectedMatch ? String(state.selectedMatch.id) : null,
          match_data: state.selectedMatch || null,
          history: state.chatHistory,
          api_key: state.apiKey || null
        })
      });

      const data = await res.json();
      removeThinkingMessage(thinkingId);
      addPalMessage(data.reply);

      if (state.isTtsEnabled) {
        speakText(data.reply);
      }
    } catch (e) {
      console.error("Sohbet hatası:", e);
      removeThinkingMessage(thinkingId);
      addPalMessage("Hocam küçük bir bağlantı pürüzü oldu, tekrar sorar mısın?");
    }
  }

  function addUserMessage(text) {
    state.chatHistory.push({ role: "user", content: text });
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble user-bubble";
    bubble.innerHTML = `
      <div class="bubble-avatar">
        <i class="fa-solid fa-user"></i>
      </div>
      <div class="bubble-content">
        <div class="bubble-header">
          <strong>Sen</strong>
          <small>${new Date().toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })}</small>
        </div>
        <p>${escapeHtml(text)}</p>
      </div>
    `;
    dom.chatMessages.appendChild(bubble);
    dom.chatMessages.scrollTop = dom.chatMessages.scrollHeight;
  }

  function addPalMessage(text) {
    state.chatHistory.push({ role: "assistant", content: text });
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble pal-bubble";
    bubble.innerHTML = `
      <div class="bubble-avatar">
        <i class="fa-solid fa-user-ninja"></i>
      </div>
      <div class="bubble-content">
        <div class="bubble-header">
          <strong>Taktik Serdar</strong>
          <small>${new Date().toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })}</small>
        </div>
        <p style="white-space: pre-line;">${formatMarkdown(text)}</p>
      </div>
    `;
    dom.chatMessages.appendChild(bubble);
    dom.chatMessages.scrollTop = dom.chatMessages.scrollHeight;
  }

  function addPalThinkingMessage() {
    const id = "thinking-" + Date.now();
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble pal-bubble";
    bubble.id = id;
    bubble.innerHTML = `
      <div class="bubble-avatar">
        <i class="fa-solid fa-user-ninja"></i>
      </div>
      <div class="bubble-content">
        <div class="bubble-header">
          <strong>Taktik Serdar</strong>
          <small>Düşünüyor...</small>
        </div>
        <div style="display:flex; align-items:center; gap:0.4rem; color:var(--text-muted);">
          <div class="spinner" style="width:16px; height:16px; margin:0;"></div>
          <span style="font-size:0.85rem;">Maç taktiklerini ve istatistikleri tartıyor...</span>
        </div>
      </div>
    `;
    dom.chatMessages.appendChild(bubble);
    dom.chatMessages.scrollTop = dom.chatMessages.scrollHeight;
    return id;
  }

  function removeThinkingMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // ==========================================
  // KUPONLAR & BAŞARI TAKİBİ
  // ==========================================
  async function loadCoupons(dateStr) {
    if (!dateStr) dateStr = state.couponDate;

    dom.couponDisplayContainer.innerHTML = `
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Günün yüksek ihtimalli değer kuponu ve geçmiş başarı istatistikleri taranıyor...</p>
      </div>
    `;

    try {
      const res = await fetch(`/api/coupons?date=${dateStr}`);
      const data = await res.json();
      state.couponsData = data;

      // Başarı Karnesi İstatistiklerini Güncelle
      if (data.stats) {
        dom.statOverallWinRate.textContent = `%${data.stats.winRatePct} Başarı Oranı`;
        dom.kpiWonCoupons.textContent = `${data.stats.wonCoupons} / ${data.stats.wonCoupons + data.stats.lostCoupons}`;
        if (dom.kpiDayWinRate) {
          dom.kpiDayWinRate.textContent = `%${data.stats.dayWinRatePct}`;
        }
        if (dom.kpiNightWinRate) {
          dom.kpiNightWinRate.textContent = `%${data.stats.nightWinRatePct}`;
        }
        dom.kpiAvgOdds.textContent = `x${data.stats.averageOdds.toFixed(2)}`;
        dom.kpiSelectionRate.textContent = `%${data.stats.selectionWinRatePct}`;
      }

      // Seans butonlarının aktiflik durumunu doğrula
      if (state.couponSession === "day" && !data.has_day_session && data.has_night_session) {
        state.couponSession = "night";
      } else if (state.couponSession === "night" && !data.has_night_session && data.has_day_session) {
        state.couponSession = "day";
      }
      dom.couponSessionBtns.forEach(btn => {
        btn.classList.toggle("active", btn.dataset.session === state.couponSession);
      });

      // Hızlı Gün Butonlarının aktiflik durumunu güncelle
      const todayStr = (data && data.today) || getTodayFormatted();
      const tomorrowStr = (data && data.tomorrow) || "";
      if (dom.btnCouponToday) {
        dom.btnCouponToday.classList.toggle("active", dateStr === todayStr);
      }
      if (dom.btnCouponTomorrow) {
        dom.btnCouponTomorrow.classList.toggle("active", dateStr === tomorrowStr);
      }

      // Tarih Açılır Kutusunu Güncelle
      if (data.available_dates && dom.couponDateSelect) {
        dom.couponDateSelect.innerHTML = "";
        data.available_dates.forEach(d => {
          const opt = document.createElement("option");
          opt.value = d;
          const y = d.substring(0, 4);
          const m = d.substring(4, 6);
          const day = d.substring(6, 8);
          let suffix = "";
          if (d === tomorrowStr || parseInt(d) > parseInt(todayStr)) {
            suffix = " (🔮 Yarın - Ertesi Gün Kuponları)";
          } else if (d === todayStr) {
            suffix = " (☀️ Bugün)";
          } else if (parseInt(d) === parseInt(todayStr) - 1) {
            suffix = " (Dün - Sonuçlandı)";
          } else {
            suffix = " (Sonuçlandı)";
          }
          opt.textContent = `${day}.${m}.${y}${suffix}`;
          dom.couponDateSelect.appendChild(opt);
        });
        dom.couponDateSelect.value = dateStr;
      }

      renderCouponSlip();
    } catch (e) {
      console.error("Kuponlar yüklenemedi:", e);
      dom.couponDisplayContainer.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-triangle-exclamation text-yellow" style="font-size:2rem; margin-bottom:0.8rem;"></i>
          <p>Kuponlar yüklenirken bir sorun oluştu. Lütfen tekrar deneyin.</p>
        </div>
      `;
    }
  }

  function renderCouponSlip() {
    if (!state.couponsData || !state.couponsData.coupons || state.couponsData.coupons.length === 0) {
      dom.couponDisplayContainer.innerHTML = `
        <div class="empty-state">
          <p>Bu tarih için kayıtlı kupon bulunamadı.</p>
        </div>
      `;
      return;
    }

    // Önce seçili seans ve tipe göre kuponu ara
    let coupon = (state.couponsData.coupons || []).find(
      c => c.session === state.couponSession && c.type === state.couponType
    );

    // Eğer o tip bulunamazsa o seanstaki ilk kupon
    if (!coupon) {
      coupon = (state.couponsData.coupons || []).find(c => c.session === state.couponSession);
    }

    // Eğer seçili seansta kupon yoksa, ASLA diğer seansın kuponunu gösterme!
    if (!coupon) {
      const isDay = (state.couponSession === "day");
      dom.couponDisplayContainer.innerHTML = `
        <div class="empty-state" style="padding: 3rem 1.5rem; text-align: center;">
          <i class="fa-solid ${isDay ? 'fa-sun text-yellow' : 'fa-moon text-blue'}" style="font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.85;"></i>
          <h3 style="font-size: 1.25rem; color: #fff; margin-bottom: 0.5rem; font-weight: 700;">
            ${isDay ? 'Gündüz Seansı (18:00 Öncesi)' : 'Akşam Seansı (18:00 Sonrası)'} Kuponu Bulunmuyor
          </h3>
          <p style="color: var(--text-muted); max-width: 480px; margin: 0 auto; line-height: 1.5; font-size: 0.95rem;">
            ${isDay 
              ? 'Seçili tarihte 18:00 öncesinde bültende yeterli resmi maç bulunmadığı için kuponlar Akşam Seansı (18:00 sonrası) için üretilmiştir. Lütfen yukarıdan <strong>🌙 Akşam</strong> sekmesini seçin.' 
              : 'Seçili tarihte akşam seansı için kayıtlı kupon bulunmuyor.'}
          </p>
        </div>
      `;
      return;
    }

    // Kupon Durum Rozeti
    let statusBar = "";
    if (coupon.status === "won") {
      statusBar = `<div class="slip-status-bar status-won"><i class="fa-solid fa-circle-check"></i> BU KUPON KAZANDI (TUTTU) ✅ <span>Mükemmel İsabet!</span></div>`;
    } else if (coupon.status === "lost") {
      statusBar = `<div class="slip-status-bar status-lost"><i class="fa-solid fa-circle-xmark"></i> BU KUPON KAYBETTİ ❌ <span>Bir sonraki bültende telafi zamanı</span></div>`;
    } else {
      statusBar = `<div class="slip-status-bar status-pending"><i class="fa-solid fa-clock"></i> MAÇLAR DEVAM EDİYOR / BEKLENİYOR ⏳ <span>Canlı Takipteyiz</span></div>`;
    }

    // Seans Bilgi Şeridi (Ribbon)
    const isDaySession = (coupon.session === "day");
    const sessionRibbon = `
      <div class="slip-session-ribbon ${isDaySession ? 'session-ribbon-day' : 'session-ribbon-night'}">
        <span><i class="fa-solid ${isDaySession ? 'fa-sun text-yellow' : 'fa-moon text-blue'}"></i> ${coupon.sessionName || (isDaySession ? "☀️ Gündüz Seansı (18:00'a Kadar)" : "🌙 Akşam Seansı (18:00 Sonrası)")}</span>
        <span><i class="fa-solid fa-clock"></i> ${isDaySession ? "18:00 Öncesi Maçlar" : "18:00 Sonrası Dev Maçlar"}</span>
      </div>
    `;

    // Seçimler HTML
    let selectionsHtml = "";
    (coupon.selections || []).forEach(sel => {
      let resBadge = "";
      if (sel.status === "won") {
        resBadge = `<span class="slip-item-result-badge result-won"><i class="fa-solid fa-check"></i> ${sel.actual_result || "TUTTU ✅"}</span>`;
      } else if (sel.status === "lost") {
        resBadge = `<span class="slip-item-result-badge result-lost"><i class="fa-solid fa-xmark"></i> ${sel.actual_result || "YATTI ❌"}</span>`;
      } else if (sel.status === "live") {
        resBadge = `<span class="slip-item-result-badge result-pending"><span class="live-indicator"></span> ${sel.actual_result || "Canlı"}</span>`;
      } else {
        resBadge = `<span class="slip-item-result-badge result-pending"><i class="fa-regular fa-clock"></i> Henüz Başlamadı</span>`;
      }

      selectionsHtml += `
        <div class="slip-item-card clickable-coupon-match" data-id="${sel.match_id}" title="Bu maçın canlı analizini ve istatistiklerini açmak için tıkla">
          <div class="slip-item-header">
            <span><i class="fa-regular fa-calendar"></i> ${sel.league || "Lig"}</span>
            <span><i class="fa-regular fa-clock"></i> ${sel.time || ""}</span>
          </div>
          <div class="slip-item-teams">
            ${sel.home} <span style="color:var(--text-muted); font-size:0.85rem;">vs</span> ${sel.away}
            <span class="view-match-link"><i class="fa-solid fa-chart-pie"></i> Analizi İncele</span>
          </div>
          <div class="slip-item-pick-row">
            <div class="pick-left">
              <span class="market-pill"><i class="fa-solid ${sel.market_icon || 'fa-tag'}"></i> ${sel.market}</span>
              <span class="pick-name">${sel.pick}</span>
            </div>
            <div class="pick-right">
              <span class="pick-odds-pill bilyoner-odds-pill">
                <span class="bilyoner-tag">BİLYONER</span> x${sel.bilyonerOdds || sel.odds}
              </span>
              <span class="pick-prob-pill"><i class="fa-solid fa-chart-line"></i> %${sel.prob} İhtimal</span>
            </div>
          </div>
          <div class="slip-item-note">
            <i class="fa-solid fa-comment-dots text-yellow"></i> <em>${sel.palNote || ""}</em>
          </div>
          <div style="margin-top:0.4rem;">
            ${resBadge}
          </div>
        </div>
      `;
    });

    const isTomorrow = (state.couponDate === state.couponsData?.tomorrow) || (parseInt(state.couponDate) > parseInt(state.couponsData?.today || getTodayFormatted()));
    const slipCard = document.createElement("div");
    slipCard.className = "coupon-slip-card";
    const totalOddsVal = coupon.bilyonerTotalOdds || coupon.totalOdds;
    slipCard.innerHTML = `
      ${sessionRibbon}
      ${statusBar}
      <div class="slip-header-banner">
        <div class="slip-title-meta">
          <h3>${coupon.title}</h3>
          <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap; margin-top:0.35rem;">
            ${isTomorrow ? '<span class="slip-badge-pill badge-yellow"><i class="fa-solid fa-forward-step"></i> 🔮 Ertesi Gün (Yarın)</span>' : ''}
            <span class="slip-badge-pill ${coupon.badge_class || 'badge-emerald'}">${coupon.badge || 'Seçilmiş Maçlar'}</span>
            <span class="bilyoner-verified-badge"><i class="fa-solid fa-circle-check"></i> Bilyoner & İddaa Bülteni</span>
          </div>
        </div>
        <div class="slip-odds-box">
          <span class="slip-odds-label">Bilyoner Toplam Oran</span>
          <span class="slip-odds-value">x${totalOddsVal}</span>
          <span class="slip-conf-badge"><i class="fa-solid fa-shield"></i> Güven Endeksi: %${coupon.confidenceScore}</span>
        </div>
      </div>

      <div class="slip-pal-commentary">
        <div class="slip-pal-avatar">
          <i class="fa-solid fa-user-ninja"></i>
        </div>
        <div class="slip-pal-text">
          <strong style="color:var(--primary); display:block; margin-bottom:0.2rem;">Taktik Serdar'ın Kupon Değerlendirmesi:</strong>
          ${coupon.palCommentary || ""}
        </div>
      </div>

      <div class="slip-selections-list">
        ${selectionsHtml}
      </div>

      <div class="slip-footer">
        <div class="stake-calc-box">
          <label for="couponStakeInput">Kupon Tutarı:</label>
          <input type="number" id="couponStakeInput" class="stake-input" value="100" min="10" step="10">
          <span style="font-weight:700;">TL</span>
        </div>
        <div class="payout-box">
          <span>Olası Kazanç:</span>
          <span class="payout-amount" id="couponPayoutAmount">${(100 * totalOddsVal).toFixed(2)} TL</span>
        </div>
        <div class="slip-footer-actions">
          <a href="${coupon.bilyonerUrl || 'https://www.bilyoner.com/iddaa/futbol'}" target="_blank" rel="noopener noreferrer" class="btn-bilyoner-action" title="Bilyoner sitesinde resmi bülteni incele">
            <i class="fa-solid fa-arrow-up-right-from-square"></i> Bilyoner'de Oyna
          </a>
          <button type="button" class="btn-copy-slip" id="btnCopyCoupon" title="Kupon tercihlerini panoya kopyala">
            <i class="fa-regular fa-copy"></i> Kuponu Kopyala
          </button>
          <button class="btn-tool" id="btnListenCoupon" title="Serdar'dan sesli dinle">
            <i class="fa-solid fa-volume-high"></i> Dinle
          </button>
        </div>
      </div>
    `;

    dom.couponDisplayContainer.innerHTML = "";
    dom.couponDisplayContainer.appendChild(slipCard);

    // Kazanç Hesaplayıcı Dinleyicisi
    const stakeInput = slipCard.querySelector("#couponStakeInput");
    const payoutAmount = slipCard.querySelector("#couponPayoutAmount");
    if (stakeInput && payoutAmount) {
      stakeInput.addEventListener("input", (e) => {
        const val = parseFloat(e.target.value) || 0;
        payoutAmount.textContent = `${(val * totalOddsVal).toFixed(2)} TL`;
      });
    }

    // Kuponu Panoya Kopyala Dinleyicisi
    const btnCopy = slipCard.querySelector("#btnCopyCoupon");
    if (btnCopy) {
      btnCopy.addEventListener("click", () => {
        let text = `⚽ ${coupon.title || 'Saha İçi Kuponu'} (Toplam Oran: x${totalOddsVal})\n`;
        (coupon.selections || []).forEach((s, idx) => {
          text += `${idx + 1}. ${s.home} vs ${s.away} | ${s.pick} @ x${s.bilyonerOdds || s.odds} (${s.time || ''})\n`;
        });
        const currentStake = parseFloat(stakeInput?.value || 100);
        text += `💰 Olası Kazanç (${currentStake} TL): ${(currentStake * totalOddsVal).toFixed(2)} TL\n`;
        text += `📊 Saha İçi Canlı Futbol Analiz Platformu`;
        
        navigator.clipboard.writeText(text).then(() => {
          btnCopy.innerHTML = `<i class="fa-solid fa-check text-emerald"></i> Kopyalandı!`;
          setTimeout(() => {
            btnCopy.innerHTML = `<i class="fa-regular fa-copy"></i> Kuponu Kopyala`;
          }, 2000);
        }).catch(() => {
          alert("Kupon panoya kopyalanamadı.");
        });
      });
    }

    // Kupon içindeki maçlara tıklayınca doğrudan analiz modalını aç
    slipCard.querySelectorAll(".clickable-coupon-match").forEach(item => {
      item.addEventListener("click", () => {
        const mId = item.dataset.id;
        let match = (state.matches || []).find(m => String(m.id) === String(mId));
        if (!match) {
          match = {
            id: mId,
            home: { name: item.querySelector(".slip-item-teams")?.textContent.split("vs")[0]?.trim() || "Ev Sahibi" },
            away: { name: item.querySelector(".slip-item-teams")?.textContent.split("vs")[1]?.replace("Analizi İncele", "")?.trim() || "Deplasman" },
            league_name: item.querySelector(".slip-item-header span:first-child")?.textContent?.trim() || "Futbol",
            league_key: "all",
            state: "pre",
            status_tr: item.querySelector(".slip-item-header span:last-child")?.textContent?.trim() || "Planlandı"
          };
        }
        openAnalysisModal(match);
      });
    });

    // Sesli Okuma Dinleyicisi
    const btnListen = slipCard.querySelector("#btnListenCoupon");
    if (btnListen) {
      btnListen.addEventListener("click", () => {
        const text = `${coupon.title}. Bilyoner toplam oranı: ${totalOddsVal}. ${coupon.palCommentary}`;
        speakText(text);
      });
    }
  }

  async function regenerateCoupons() {
    if (!dom.btnRegenCoupons) return;
    const icon = dom.btnRegenCoupons.querySelector("i");
    if (icon) icon.classList.add("fa-spin");

    try {
      const res = await fetch(`/api/coupons/regenerate?date=${state.couponDate}`, { method: "POST" });
      const data = await res.json();
      state.couponsData = data;
      renderCouponSlip();
    } catch (e) {
      console.error("Kupon yeniden üretilemedi:", e);
    } finally {
      if (icon) icon.classList.remove("fa-spin");
    }
  }

  // ==========================================
  // PUAN DURUMU (STANDINGS)
  // ==========================================
  async function loadStandings(leagueSlug) {
    dom.standingsBody.innerHTML = `
      <tr>
        <td colspan="10" style="text-align:center; padding:2rem;">
          <div class="spinner"></div>
          <p>Puan durumu yükleniyor...</p>
        </td>
      </tr>
    `;

    try {
      const res = await fetch(`/api/standings?league=${leagueSlug}`);
      const data = await res.json();
      dom.standingsLeagueName.textContent = `${data.league?.name || "Lig"} Puan Durumu`;

      dom.standingsBody.innerHTML = "";
      (data.standings || []).forEach(row => {
        const tr = document.createElement("tr");
        const rankClass = row.rank <= 4 ? "rank-cl" : (row.rank >= 16 ? "rank-rel" : "");
        tr.innerHTML = `
          <td><span class="rank-badge ${rankClass}">${row.rank}</span></td>
          <td>
            <div class="team-td-wrap">
              ${row.logo ? `<img src="${row.logo}" class="team-td-logo">` : ""}
              <span>${row.team}</span>
            </div>
          </td>
          <td>${row.gamesPlayed}</td>
          <td>${row.wins}</td>
          <td>${row.ties}</td>
          <td>${row.losses}</td>
          <td>${row.goalsFor}</td>
          <td>${row.goalsAgainst}</td>
          <td>${row.goalDiff}</td>
          <td style="font-weight:800; color:var(--primary); font-size:1rem;">${row.points}</td>
        `;
        dom.standingsBody.appendChild(tr);
      });
    } catch (e) {
      console.error("Puan durumu hatası:", e);
    }
  }

  // ==========================================
  // YARDIMCI FONKSİYONLAR
  // ==========================================
  function openModal(m) {
    m.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  }

  function closeModal(m) {
    if (m === dom.analysisModal) {
      if (state.modalPollInterval) {
        clearInterval(state.modalPollInterval);
        state.modalPollInterval = null;
      }
      if (state.modalAbortController) {
        state.modalAbortController.abort();
        state.modalAbortController = null;
      }
      state.selectedMatch = null;
      resetModalLiveSection();
    }
    m.classList.add("hidden");
    document.body.style.overflow = "auto";
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  }

  // ESC Tuşu ile Modal Kapatma
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (dom.analysisModal && !dom.analysisModal.classList.contains("hidden")) {
        closeModal(dom.analysisModal);
      }
      if (dom.settingsModal && !dom.settingsModal.classList.contains("hidden")) {
        closeModal(dom.settingsModal);
      }
    }
  });

  function speakText(text) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();

    // Markdown ve emojileri temizle
    const cleanText = text.replace(/[*_#`]/g, "").replace(/🎯|💡|👉|⚽|💣|⏱️|📊/g, "");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = "tr-TR";
    utterance.rate = 1.05;
    window.speechSynthesis.speak(utterance);
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function formatMarkdown(text) {
    let out = escapeHtml(text);
    out = out.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    out = out.replace(/\*(.*?)\*/g, "<em>$1</em>");
    return out;
  }
});
